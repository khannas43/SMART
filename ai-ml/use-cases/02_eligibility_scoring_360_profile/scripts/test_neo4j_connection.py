#!/usr/bin/env python3
"""
Test Neo4j Connection - Troubleshooting Script
Tests multiple connection methods to find what works
"""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ neo4j package not installed")
    print("   Run: pip install neo4j")
    sys.exit(1)

# Test URIs to try
TEST_URIS = [
    "bolt://127.0.0.1:7687",
    "bolt://localhost:7687",
    "neo4j://127.0.0.1:7687",
    "neo4j://localhost:7687",
]

# Get Windows host IP from WSL (if in WSL)
import subprocess
try:
    result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        windows_host = result.stdout.split()[2] if len(result.stdout.split()) > 2 else None
        if windows_host:
            TEST_URIS.extend([
                f"bolt://{windows_host}:7687",
                f"neo4j://{windows_host}:7687"
            ])
except:
    pass

USER = "neo4j"
PASSWORD = "anjali143"
DATABASE = "smartgraphdb"

print("=" * 70)
print("Neo4j Connection Troubleshooting")
print("=" * 70)
print(f"User: {USER}")
print(f"Database: {DATABASE}")
print(f"Testing {len(TEST_URIS)} connection URIs...")
print()

successful_uri = None

for uri in TEST_URIS:
    print(f"Testing: {uri}")
    try:
        driver = GraphDatabase.driver(uri, auth=(USER, PASSWORD))
        with driver.session(database=DATABASE) as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print(f"  ✅ SUCCESS! Connection works with: {uri}")
                successful_uri = uri
                
                # Get database stats
                try:
                    stats_query = "MATCH (n) RETURN count(n) as nodes"
                    stats = session.run(stats_query).single()
                    nodes = stats["nodes"] if stats else 0
                    
                    rel_query = "MATCH ()-[r]->() RETURN count(r) as rels"
                    rels = session.run(rel_query).single()
                    relationships = rels["rels"] if rels else 0
                    
                    print(f"  📊 Current graph: {nodes} nodes, {relationships} relationships")
                except:
                    pass
                
                driver.close()
                break
        driver.close()
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:80]}")
    print()

print("=" * 70)
if successful_uri:
    print(f"✅ Working URI: {successful_uri}")
    print()
    print("Update config/db_config.yaml with:")
    print(f'  uri: {successful_uri}')
else:
    print("❌ All connection attempts failed")
    print()
    print("Troubleshooting steps:")
    print("  1. Ensure Neo4j Desktop is running")
    print("  2. Ensure the 'smartgraphdb' database is started")
    print("  3. Check if Neo4j Desktop is configured to accept connections")
    print("  4. Try opening Neo4j Browser and connecting manually")
    print("  5. Check firewall settings")

print("=" * 70)

