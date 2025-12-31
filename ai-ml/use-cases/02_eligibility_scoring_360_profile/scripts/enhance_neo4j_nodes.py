#!/usr/bin/env python3
"""
Enhance Neo4j nodes with names and additional properties from PostgreSQL
Adds full_name, age, gender to nodes for better visualization
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector
from neo4j_connector import Neo4jConnector


def main():
    """Enhance Neo4j nodes with names"""
    print("=" * 70)
    print("Enhancing Neo4j Nodes with Names and Properties")
    print("=" * 70)
    
    # Load configs
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # PostgreSQL connection
    db = DBConnector(
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['dbname'],
        user=config['database']['user'],
        password=config['database']['password']
    )
    db.connect()
    
    # Neo4j connection
    neo4j_config = config['neo4j']
    neo4j = Neo4jConnector(
        uri=neo4j_config['uri'],
        user=neo4j_config['user'],
        password=neo4j_config['password'],
        database=neo4j_config['database']
    )
    neo4j.connect()
    
    # Load names from PostgreSQL
    print("\nLoading names from PostgreSQL...")
    query = """
    SELECT 
        gr_id,
        full_name,
        age,
        gender,
        city_village,
        jan_aadhaar
    FROM golden_records
    WHERE status = 'active'
    """
    
    df = db.execute_query(query)
    print(f"✅ Loaded {len(df)} records with names")
    
    # Update Neo4j nodes
    print("\nUpdating Neo4j nodes...")
    
    update_query = """
    UNWIND $records AS record
    MATCH (n:GoldenRecord {gr_id: record.gr_id})
    SET n.full_name = record.full_name,
        n.age = record.age,
        n.gender = record.gender,
        n.city_village = record.city_village,
        n.jan_aadhaar = record.jan_aadhaar
    """
    
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    # Batch update
    batch_size = 5000
    updated = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        neo4j.execute_write(update_query, {'records': batch})
        updated += len(batch)
        if updated % 10000 == 0:
            print(f"  Updated {updated}/{len(records)} nodes...")
    
    print(f"✅ Updated {len(records)} nodes with names and properties")
    
    # Verify
    result = neo4j.execute_query(
        "MATCH (n:GoldenRecord) WHERE n.full_name IS NOT NULL RETURN count(n) AS count"
    )
    with_names = result[0]['count'] if result else 0
    print(f"✅ Nodes with names: {with_names:,}")
    
    db.disconnect()
    neo4j.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ Enhancement complete!")
    print("=" * 70)
    print("\nNow you can use enhanced queries in Neo4j Browser:")
    print("  - Nodes will show names instead of IDs")
    print("  - Relationship types will display on arrows")
    print("  - See docs/NEO4J_ENHANCED_QUERIES.md for examples")


if __name__ == "__main__":
    main()

