#!/usr/bin/env python3
"""
Check if data exists in Neo4j database
"""

import sys
from pathlib import Path
import yaml

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from neo4j_connector import Neo4jConnector


def main():
    """Check Neo4j data"""
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    neo4j_config = config.get('neo4j', {})
    db_name = neo4j_config.get('database', 'neo4j')
    
    print("=" * 60)
    print("Neo4j Data Check")
    print("=" * 60)
    print(f"Database: {db_name}")
    print()
    
    try:
        neo4j = Neo4jConnector(
            uri=neo4j_config['uri'],
            user=neo4j_config['user'],
            password=neo4j_config['password'],
            database=db_name
        )
        neo4j.connect()
        
        # Check nodes
        result = neo4j.execute_query('MATCH (n:GoldenRecord) RETURN count(n) AS count')
        node_count = result[0]['count'] if result else 0
        print(f"✅ GoldenRecord nodes: {node_count:,}")
        
        # Check relationships
        result = neo4j.execute_query('MATCH ()-[r:RELATED_TO]->() RETURN count(r) AS count')
        rel_count = result[0]['count'] if result else 0
        print(f"✅ RELATED_TO relationships: {rel_count:,}")
        
        # Check all nodes
        result = neo4j.execute_query('MATCH (n) RETURN count(n) AS count')
        all_nodes = result[0]['count'] if result else 0
        print(f"   Total nodes: {all_nodes:,}")
        
        print()
        if node_count == 0:
            print("⚠️  No data found in Neo4j!")
            print("   Run: python src/graph_clustering_neo4j.py")
        else:
            print("✅ Data exists in Neo4j!")
            print("   You can now query in Neo4j Browser")
        
        neo4j.disconnect()
        return 0 if node_count > 0 else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

