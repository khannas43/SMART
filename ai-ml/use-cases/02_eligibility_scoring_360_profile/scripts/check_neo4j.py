#!/usr/bin/env python3
"""
Check Neo4j Connection and Configuration
"""

import sys
from pathlib import Path
import yaml

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from neo4j_connector import Neo4jConnector


def main():
    """Check Neo4j connection"""
    print("=" * 60)
    print("Neo4j Connection Check")
    print("=" * 60)
    
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    neo4j_config = config.get('neo4j', {})
    
    if not neo4j_config.get('enabled', False):
        print("❌ Neo4j is not enabled in config")
        print("   Set neo4j.enabled: true in config/db_config.yaml")
        return 1
    
    print(f"\n📋 Configuration:")
    print(f"   URI: {neo4j_config['uri']}")
    print(f"   User: {neo4j_config['user']}")
    print(f"   Database: {neo4j_config.get('database', 'neo4j')}")
    
    # Test connection
    print(f"\n🔌 Testing connection...")
    try:
        neo4j = Neo4jConnector(
            uri=neo4j_config['uri'],
            user=neo4j_config['user'],
            password=neo4j_config['password'],
            database=neo4j_config.get('database', 'neo4j')
        )
        neo4j.connect()
        
        # Get stats
        stats = neo4j.get_stats()
        print(f"✅ Connected successfully!")
        print(f"   Nodes: {stats['nodes']:,}")
        print(f"   Relationships: {stats['relationships']:,}")
        
        # Check GDS
        print(f"\n📊 Checking GDS library...")
        try:
            gds_query = "CALL gds.version() YIELD version RETURN version"
            result = neo4j.execute_query(gds_query)
            if result:
                print(f"   ✅ GDS available: {result[0].get('version', 'unknown')}")
            else:
                print(f"   ⚠️  GDS not available (will use fallback methods)")
        except:
            print(f"   ⚠️  GDS not available (will use fallback methods)")
        
        neo4j.disconnect()
        return 0
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"  1. Ensure Neo4j Desktop is running")
        print(f"  2. Check URI: {neo4j_config['uri']}")
        print(f"  3. Verify password in config/db_config.yaml")
        print(f"  4. Make sure database '{neo4j_config.get('database', 'neo4j')}' exists")
        return 1


if __name__ == "__main__":
    sys.exit(main())

