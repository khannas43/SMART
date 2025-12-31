"""
Graph Clustering using NetworkX (Louvain Algorithm) - DEPRECATED
Use Case: AI-PLATFORM-02

NOTE: This file is kept for fallback. Use graph_clustering_neo4j.py for production.
Neo4j provides better performance for large graphs.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime
import yaml
import json

# Community detection
from networkx.algorithms import community

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


class GraphClustering:
    """Perform graph clustering on Golden Records"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database connection
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
        
        self.db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        self.db.connect()
        
        # Graph config
        self.graph_config = self.config['graph_clustering']
        self.relationship_weights = self.graph_config['relationship_weights']
        
    def load_relationships(self):
        """Load relationships from database"""
        print("Loading relationships...")
        
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
    
    def build_graph(self, relationships_df):
        """Build NetworkX graph from relationships"""
        print("Building graph...")
        
        G = nx.Graph()
        
        # Add edges with weights
        for _, row in relationships_df.iterrows():
            from_gr = str(row['from_gr_id'])
            to_gr = str(row['to_gr_id'])
            rel_type = row['relationship_type']
            
            # Get weight for relationship type
            weight = self.relationship_weights.get(rel_type, 1.0)
            
            # Adjust weight by confidence if inferred
            if not row.get('is_verified', True) and pd.notna(row.get('inference_confidence')):
                weight *= row['inference_confidence']
            
            # Add edge
            if G.has_edge(from_gr, to_gr):
                # If edge exists, take maximum weight
                G[from_gr][to_gr]['weight'] = max(G[from_gr][to_gr].get('weight', 1.0), weight)
                G[from_gr][to_gr]['relationship_types'] = G[from_gr][to_gr].get('relationship_types', []) + [rel_type]
            else:
                G.add_edge(from_gr, to_gr, weight=weight, relationship_types=[rel_type])
        
        print(f"✅ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G
    
    def detect_communities(self, G):
        """Detect communities using Louvain algorithm"""
        print("Detecting communities...")
        
        # Use Louvain community detection
        resolution = self.graph_config['resolution']
        
        # Convert to undirected if needed
        if G.is_directed():
            G = G.to_undirected()
        
        # Run Louvain
        communities = community.louvain_communities(G, weight='weight', resolution=resolution, seed=42)
        
        # Assign cluster IDs
        cluster_assignments = {}
        for cluster_id, community_nodes in enumerate(communities):
            cluster_name = f"cluster_{cluster_id}"
            for node in community_nodes:
                cluster_assignments[node] = cluster_name
        
        print(f"✅ Detected {len(communities)} communities")
        print(f"   Largest community: {max(len(c) for c in communities)} nodes")
        print(f"   Smallest community: {min(len(c) for c in communities)} nodes")
        
        return cluster_assignments, communities
    
    def calculate_centrality(self, G, gr_ids):
        """Calculate centrality measures for nodes (optimized - compute once for all nodes)"""
        print("Calculating centrality measures...")
        
        centrality_metrics = self.graph_config['centrality_metrics']
        centrality_data = {}
        
        # Convert to undirected for centrality
        if G.is_directed():
            G_undirected = G.to_undirected()
        else:
            G_undirected = G
        
        # Compute centrality ONCE for all nodes (not in loop!)
        print("  Computing degree centrality...")
        degree_dict = dict(G_undirected.degree())
        
        # Only compute expensive metrics if requested and graph is not too large
        node_count = len(G_undirected.nodes())
        compute_expensive = node_count < 50000  # Skip expensive metrics for very large graphs
        
        betweenness_dict = {}
        closeness_dict = {}
        pagerank_dict = {}
        
        if 'betweenness' in centrality_metrics:
            if compute_expensive:
                print("  Computing betweenness centrality (this may take a while for large graphs)...")
                # Use approximate betweenness for large graphs
                if node_count > 10000:
                    print("    Using approximate betweenness (k=50) for performance...")
                    betweenness_dict = nx.betweenness_centrality(G_undirected, weight='weight', k=50)
                else:
                    betweenness_dict = nx.betweenness_centrality(G_undirected, weight='weight')
            else:
                print("  ⚠️  Skipping betweenness centrality (graph too large, >50K nodes)")
        
        if 'closeness' in centrality_metrics:
            if compute_expensive:
                print("  Computing closeness centrality...")
                try:
                    closeness_dict = nx.closeness_centrality(G_undirected, distance='weight')
                except:
                    print("    ⚠️  Closeness calculation failed (graph may be disconnected)")
                    closeness_dict = {}
            else:
                print("  ⚠️  Skipping closeness centrality (graph too large, >50K nodes)")
        
        if 'pagerank' in centrality_metrics:
            print("  Computing PageRank...")
            pagerank_dict = nx.pagerank(G_undirected, weight='weight', max_iter=100)
        
        # Now extract values for each node (fast)
        print("  Extracting centrality values...")
        for gr_id in gr_ids:
            gr_str = str(gr_id)
            if gr_str not in G_undirected:
                continue
            
            metrics = {}
            
            if 'degree' in centrality_metrics:
                metrics['degree_centrality'] = degree_dict.get(gr_str, 0)
            
            if 'betweenness' in centrality_metrics and betweenness_dict:
                metrics['betweenness_centrality'] = betweenness_dict.get(gr_str, 0)
            
            if 'closeness' in centrality_metrics and closeness_dict:
                metrics['closeness_centrality'] = closeness_dict.get(gr_str, 0)
            
            if 'pagerank' in centrality_metrics:
                metrics['pagerank'] = pagerank_dict.get(gr_str, 0)
            
            centrality_data[gr_str] = metrics
        
        print(f"✅ Calculated centrality for {len(centrality_data)} nodes")
        return centrality_data
    
    def save_clusters(self, cluster_assignments, centrality_data):
        """Save cluster assignments to database"""
        print("Saving cluster assignments...")
        
        # Update profile_360 table with cluster_id
        cursor = self.db.connection.cursor()
        
        updated = 0
        for gr_id_str, cluster_id in cluster_assignments.items():
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
        
        print(f"✅ Updated {updated} profiles with cluster assignments")
        
        # Save cluster metadata (optional - could create a separate table)
        cluster_summary = {
            'total_clusters': len(set(cluster_assignments.values())),
            'total_nodes': len(cluster_assignments),
            'computed_at': datetime.now().isoformat()
        }
        
        return cluster_summary
    
    def run(self):
        """Run complete clustering pipeline"""
        print("="*80)
        print("Graph Clustering Pipeline")
        print("="*80)
        print()
        
        # Load relationships
        relationships_df = self.load_relationships()
        
        if len(relationships_df) == 0:
            print("⚠️  No relationships found. Cannot build graph.")
            return
        
        # Build graph
        G = self.build_graph(relationships_df)
        
        # Detect communities
        cluster_assignments, communities = self.detect_communities(G)
        
        # Calculate centrality
        gr_ids = list(cluster_assignments.keys())
        centrality_data = self.calculate_centrality(G, gr_ids)
        
        # Save clusters
        cluster_summary = self.save_clusters(cluster_assignments, centrality_data)
        
        print("\n" + "="*80)
        print("✅ Clustering completed!")
        print(f"   Clusters: {cluster_summary['total_clusters']}")
        print(f"   Nodes: {cluster_summary['total_nodes']}")
        print("="*80)
        
        return cluster_assignments, centrality_data
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.disconnect()


def main():
    """Main function"""
    clustering = GraphClustering()
    
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


