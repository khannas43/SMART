#!/usr/bin/env python3
"""
Direct Neo4j Connection Test
Tests connection and lists available databases
"""

import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ neo4j package not installed")
    print("   Run: pip install neo4j")
    sys.exit(1)

# Connection settings (using Windows host IP for WSL)
URI = "bolt://172.17.16.1:7687"  # Windows host IP from WSL
USER = "neo4j"
PASSWORD = "anjali143"

print("=" * 70)
print("Direct Neo4j Connection Test")
print("=" * 70)
print(f"URI: {URI}")
print(f"User: {USER}")
print()

try:
    # Connect without specifying database (uses default)
    print("1. Testing connection without database specification...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    # List available databases
    print("\n2. Listing available databases...")
    with driver.session(database="system") as session:
        result = session.run("SHOW DATABASES")
        databases = [record["name"] for record in result]
        print("   Available databases:")
        for db in databases:
            if db not in ["system", "neo4j"]:  # These are special
                status = "✅"
            else:
                status = "   "
            print(f"   {status} {db}")
    
    # Try connecting to smartgraphdb
    print("\n3. Testing connection to 'smartgraphdb' database...")
    try:
        with driver.session(database="smartgraphdb") as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("   ✅ SUCCESS! Can connect to 'smartgraphdb'")
                
                # Get node count
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"   📊 Nodes in database: {count}")
                
                # Get relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rels = result.single()["count"]
                print(f"   📊 Relationships: {rels}")
        driver.close()
        
        print("\n" + "=" * 70)
        print("✅ Connection successful!")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        print("\n   Trying default 'neo4j' database instead...")
        
        # Try default neo4j database
        try:
            with driver.session(database="neo4j") as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print("   ✅ SUCCESS! Can connect to 'neo4j' database")
                    print("\n   Recommendation: Use 'neo4j' database or create 'smartgraphdb' properly")
                    driver.close()
                    sys.exit(0)
        except Exception as e2:
            print(f"   ❌ Default database also failed: {e2}")
    
    driver.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("  1. Ensure Neo4j Desktop is running")
    print("  2. Check password is correct: anjali143")
    print("  3. Verify instance is started")
    sys.exit(1)

print("\n" + "=" * 70)
print("❌ Could not connect to any database")
print("=" * 70)

