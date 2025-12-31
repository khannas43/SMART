"""
Graph Clustering using Neo4j
Use Case: AI-PLATFORM-02 - Eligibility Scoring & 360° Profiles
Uses Neo4j for efficient graph operations and community detection
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import yaml
import json

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector
from neo4j_connector import Neo4jConnector


class GraphClusteringNeo4j:
    """Perform graph clustering using Neo4j"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # PostgreSQL connection (for reading relationships)
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)
        
        self.db = DBConnector(
            host=db_config['database']['host'],
            port=db_config['database']['port'],
            database=db_config['database']['dbname'],
            user=db_config['database']['user'],
            password=db_config['database']['password']
        )
        self.db.connect()
        
        # Neo4j connection
        neo4j_config = db_config.get('neo4j', {})
        if not neo4j_config.get('enabled', False):
            raise ValueError("Neo4j is not enabled in config. Set neo4j.enabled: true in db_config.yaml")
        
        self.neo4j = Neo4jConnector(
            uri=neo4j_config['uri'],
            user=neo4j_config['user'],
            password=neo4j_config['password'],
            database=neo4j_config.get('database', 'neo4j')
        )
        self.neo4j.connect()
        
        # Graph config
        self.graph_config = self.config['graph_clustering']
        self.relationship_weights = self.graph_config['relationship_weights']
        
        # Create indexes
        self.neo4j.create_indexes()
    
    def load_relationships(self):
        """Load relationships from PostgreSQL"""
        print("Loading relationships from PostgreSQL...")
        
        query = """
        SELECT 
            from_gr_id,
            to_gr_id,
            relationship_type,
            is_verified,
            inference_confidence
        FROM gr_relationships
        WHERE valid_to IS NULL OR valid_to >= CURRENT_DATE
        """
        
        df = self.db.execute_query(query)
        print(f"✅ Loaded {len(df)} relationships")
        return df
    
    def load_golden_records(self):
        """Load Golden Records for node properties"""
        print("Loading Golden Records...")
        
        query = """
        SELECT 
            gr_id,
            family_id,
            district_id,
            caste_id,
            is_urban
        FROM golden_records
        WHERE status = 'active'
        """
        
        df = self.db.execute_query(query)
        print(f"✅ Loaded {len(df)} Golden Records")
        return df
    
    def build_graph_in_neo4j(self, golden_records_df, relationships_df):
        """Build graph in Neo4j from relationships"""
        print("Building graph in Neo4j...")
        
        # Clear existing graph (optional - comment out if you want to keep existing data)
        print("  Clearing existing graph...")
        self.neo4j.clear_database()
        
        # Create nodes (Golden Records)
        print("  Creating nodes...")
        node_query = """
        UNWIND $records AS record
        CREATE (n:GoldenRecord {
            gr_id: record.gr_id,
            family_id: record.family_id,
            district_id: record.district_id,
            caste_id: record.caste_id,
            is_urban: record.is_urban
        })
        """
        
        records = golden_records_df.to_dict('records')
        # Convert None to null for Neo4j
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        # Batch insert nodes
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            self.neo4j.execute_write(node_query, {'records': batch})
            if (i + batch_size) % 10000 == 0:
                print(f"    Created {min(i+batch_size, len(records))}/{len(records)} nodes...")
        
        print(f"✅ Created {len(records)} nodes")
        
        # Create relationships
        print("  Creating relationships...")
        rel_query = """
        UNWIND $relationships AS rel
        MATCH (from:GoldenRecord {gr_id: rel.from_gr_id})
        MATCH (to:GoldenRecord {gr_id: rel.to_gr_id})
        CREATE (from)-[r:RELATED_TO {
            type: rel.relationship_type,
            weight: rel.weight,
            is_verified: rel.is_verified,
            confidence: rel.confidence
        }]->(to)
        """
        
        relationships = []
        for _, row in relationships_df.iterrows():
            rel_type = row['relationship_type']
            weight = self.relationship_weights.get(rel_type, 1.0)
            
            # Adjust weight by confidence
            if not row.get('is_verified', True) and pd.notna(row.get('inference_confidence')):
                weight *= row['inference_confidence']
            
            relationships.append({
                'from_gr_id': str(row['from_gr_id']),
                'to_gr_id': str(row['to_gr_id']),
                'relationship_type': rel_type,
                'weight': float(weight),
                'is_verified': bool(row.get('is_verified', True)),
                'confidence': float(row.get('inference_confidence', 1.0)) if pd.notna(row.get('inference_confidence')) else 1.0
            })
        
        # Batch insert relationships
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i+batch_size]
            self.neo4j.execute_write(rel_query, {'relationships': batch})
            if (i + batch_size) % 10000 == 0:
                print(f"    Created {min(i+batch_size, len(relationships))}/{len(relationships)} relationships...")
        
        print(f"✅ Created {len(relationships)} relationships")
        
        # Get graph stats
        stats = self.neo4j.get_stats()
        print(f"✅ Graph built: {stats['nodes']} nodes, {stats['relationships']} edges")
    
    def detect_communities_neo4j(self):
        """Detect communities using Neo4j GDS (Graph Data Science) library"""
        print("Detecting communities using Neo4j GDS...")
        
        # Check if GDS is available
        try:
            # Drop existing projection if it exists
            try:
                drop_query = "CALL gds.graph.drop('smart-graph', false) YIELD graphName"
                self.neo4j.execute_write(drop_query)
            except:
                pass  # Projection doesn't exist, that's fine
            
            # Try to use GDS Louvain algorithm
            print("  Creating GDS graph projection...")
            gds_query = """
            CALL gds.graph.project(
                'smart-graph',
                'GoldenRecord',
                'RELATED_TO',
                {
                    relationshipProperties: 'weight',
                    nodeProperties: ['gr_id', 'family_id']
                }
            )
            YIELD graphName, nodeCount, relationshipCount
            """
            result = self.neo4j.execute_query(gds_query)
            if result:
                print(f"  ✅ GDS graph projected: {result[0].get('nodeCount', 0)} nodes, {result[0].get('relationshipCount', 0)} relationships")
            
            # Run Louvain community detection
            print("  Running Louvain community detection...")
            louvain_query = """
            CALL gds.louvain.stream('smart-graph', {
                relationshipWeightProperty: 'weight',
                includeIntermediateCommunities: false
            })
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).gr_id AS gr_id, communityId AS cluster_id
            """
            
            results = self.neo4j.execute_query(louvain_query)
            cluster_assignments = {r['gr_id']: f"cluster_{r['cluster_id']}" for r in results}
            
            # Clean up projection
            try:
                cleanup_query = "CALL gds.graph.drop('smart-graph')"
                self.neo4j.execute_write(cleanup_query)
            except:
                pass
            
        except Exception as e:
            print(f"  ⚠️  GDS not available or error: {e}")
            print("  Falling back to relationship-based clustering...")
            
            # Fallback: Use family_id and relationship-based clustering
            # Group by family_id first, then by connected components
            cluster_query = """
            // First, assign family-based clusters
            MATCH (n:GoldenRecord)
            WHERE n.family_id IS NOT NULL
            WITH n.family_id AS familyId, collect(n.gr_id) AS members
            UNWIND members AS gr_id
            WITH gr_id, 'family_' + toString(familyId) AS cluster_id
            
            UNION
            
            // For nodes without family_id, use connected components via relationships
            MATCH (n:GoldenRecord)
            WHERE n.family_id IS NULL
            WITH n
            MATCH path = (n)-[:RELATED_TO*1..3]-(connected:GoldenRecord)
            WHERE connected.family_id IS NULL
            WITH n, collect(DISTINCT connected) AS component
            WITH n.gr_id AS gr_id, 
                 'cluster_' + toString(id(n)) AS cluster_id
            RETURN gr_id, cluster_id
            """
            
            try:
                results = self.neo4j.execute_query(cluster_query)
                cluster_assignments = {r['gr_id']: r['cluster_id'] for r in results}
            except:
                # Ultimate fallback: one cluster per node
                print("    Using simple node-based clustering...")
                simple_query = """
                MATCH (n:GoldenRecord)
                RETURN n.gr_id AS gr_id, 'cluster_' + toString(id(n)) AS cluster_id
                """
                results = self.neo4j.execute_query(simple_query)
                cluster_assignments = {r['gr_id']: r['cluster_id'] for r in results}
        
        print(f"✅ Detected {len(set(cluster_assignments.values()))} communities")
        return cluster_assignments
    
    def calculate_centrality_neo4j(self, gr_ids):
        """Calculate centrality measures using Neo4j"""
        print("Calculating centrality measures...")
        
        centrality_metrics = self.graph_config['centrality_metrics']
        centrality_data = {}
        
        # Degree centrality (fast - built-in)
        if 'degree' in centrality_metrics:
            print("  Computing degree centrality...")
            degree_query = """
            MATCH (n:GoldenRecord)
            OPTIONAL MATCH (n)-[r:RELATED_TO]-()
            WITH n.gr_id AS gr_id, count(r) AS degree
            RETURN gr_id, degree AS degree_centrality
            """
            results = self.neo4j.execute_query(degree_query)
            for r in results:
                if r['gr_id'] not in centrality_data:
                    centrality_data[r['gr_id']] = {}
                centrality_data[r['gr_id']]['degree_centrality'] = r['degree_centrality']
        
        # PageRank (using GDS if available, else fallback)
        if 'pagerank' in centrality_metrics:
            print("  Computing PageRank...")
            try:
                # Recreate projection if needed
                try:
                    drop_query = "CALL gds.graph.drop('smart-graph', false)"
                    self.neo4j.execute_write(drop_query)
                except:
                    pass
                
                gds_query = """
                CALL gds.graph.project(
                    'smart-graph',
                    'GoldenRecord',
                    'RELATED_TO',
                    {relationshipProperties: 'weight'}
                )
                YIELD graphName
                """
                self.neo4j.execute_write(gds_query)
                
                # Try GDS PageRank
                pagerank_query = """
                CALL gds.pageRank.stream('smart-graph', {
                    relationshipWeightProperty: 'weight',
                    maxIterations: 20
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).gr_id AS gr_id, score AS pagerank
                """
                results = self.neo4j.execute_query(pagerank_query)
                for r in results:
                    if r['gr_id'] not in centrality_data:
                        centrality_data[r['gr_id']] = {}
                    centrality_data[r['gr_id']]['pagerank'] = r['pagerank']
                
                # Clean up
                try:
                    self.neo4j.execute_write("CALL gds.graph.drop('smart-graph')")
                except:
                    pass
            except Exception as e:
                # Fallback: Simple degree-based approximation
                print(f"    ⚠️  GDS PageRank failed ({e}), using degree-based approximation")
                max_degree = max([centrality_data.get(gr_id, {}).get('degree_centrality', 0) for gr_id in gr_ids], default=1)
                for gr_id in gr_ids:
                    if gr_id not in centrality_data:
                        centrality_data[gr_id] = {}
                    # Use normalized degree as PageRank approximation
                    degree = centrality_data.get(gr_id, {}).get('degree_centrality', 0)
                    centrality_data[gr_id]['pagerank'] = degree / max(max_degree, 1)
        
        # Betweenness and Closeness are expensive - skip for large graphs or use GDS
        if 'betweenness' in centrality_metrics:
            print("  ⚠️  Betweenness centrality skipped (use GDS for large graphs)")
        
        if 'closeness' in centrality_metrics:
            print("  ⚠️  Closeness centrality skipped (use GDS for large graphs)")
        
        print(f"✅ Calculated centrality for {len(centrality_data)} nodes")
        return centrality_data
    
    def save_clusters(self, cluster_assignments, centrality_data):
        """Save cluster assignments to PostgreSQL profile_360 table"""
        print("Saving cluster assignments to PostgreSQL...")
        
        # Update profile_360 table with cluster_id
        cursor = self.db.connection.cursor()
        
        updated = 0
        created = 0
        
        # Batch insert/update for better performance
        for gr_id_str, cluster_id in cluster_assignments.items():
            # First ensure profile_360 entry exists
            check_query = "SELECT gr_id FROM profile_360 WHERE gr_id = %s"
            cursor.execute(check_query, (gr_id_str,))
            if cursor.fetchone() is None:
                # Create profile entry if it doesn't exist
                insert_query = """
                INSERT INTO profile_360 (gr_id, profile_data, created_at, updated_at)
                VALUES (%s, '{}'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (gr_id) DO NOTHING
                """
                cursor.execute(insert_query, (gr_id_str,))
                created += cursor.rowcount
            
            # Update cluster_id
            update_query = """
            UPDATE profile_360
            SET cluster_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE gr_id = %s
            """
            cursor.execute(update_query, (cluster_id, gr_id_str))
            updated += cursor.rowcount
        
        self.db.connection.commit()
        cursor.close()
        
        print(f"✅ Created {created} new profiles, updated {updated} profiles with cluster assignments")
        
        return {
            'total_clusters': len(set(cluster_assignments.values())),
            'total_nodes': len(cluster_assignments),
            'computed_at': datetime.now().isoformat()
        }
    
    def run(self):
        """Run complete clustering pipeline"""
        print("="*80)
        print("Graph Clustering Pipeline (Neo4j)")
        print("="*80)
        print()
        
        # Load data from PostgreSQL
        relationships_df = self.load_relationships()
        golden_records_df = self.load_golden_records()
        
        if len(relationships_df) == 0:
            print("⚠️  No relationships found. Cannot build graph.")
            return
        
        # Build graph in Neo4j
        self.build_graph_in_neo4j(golden_records_df, relationships_df)
        
        # Detect communities
        cluster_assignments = self.detect_communities_neo4j()
        
        # Calculate centrality
        gr_ids = list(cluster_assignments.keys())
        centrality_data = self.calculate_centrality_neo4j(gr_ids)
        
        # Save clusters to PostgreSQL
        cluster_summary = self.save_clusters(cluster_assignments, centrality_data)
        
        print("\n" + "="*80)
        print("✅ Clustering completed!")
        print(f"   Clusters: {cluster_summary['total_clusters']}")
        print(f"   Nodes: {cluster_summary['total_nodes']}")
        print("="*80)
        
        return cluster_assignments, centrality_data
    
    def close(self):
        """Close database connections"""
        if self.db:
            self.db.disconnect()
        if self.neo4j:
            self.neo4j.disconnect()


def main():
    """Main function"""
    clustering = GraphClusteringNeo4j()
    
    try:
        clustering.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        clustering.close()


if __name__ == "__main__":
    main()

