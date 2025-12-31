# Fix: Switch to Correct Database in Neo4j Browser

## Problem

Getting errors like:
- "Label does not exist: GoldenRecord"
- "Relationship type does not exist: RELATED_TO"

This means you're connected to the **wrong database** (`neo4j` instead of `smartgraphdb`).

## Solution: Switch Database in Browser

### Method 1: Change Database in Browser

1. **In Neo4j Browser**, look at the **top of the query panel**
2. You'll see a **database selector** (dropdown) showing current database
3. **Click the dropdown** and select **`smartgraphdb`**
4. **Run your query again**

### Method 2: Use USE Command

At the top of your query, add:
```cypher
USE smartgraphdb;
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
RETURN n, r, m
LIMIT 100
```

### Method 3: Check Available Databases

First, see what databases exist:
```cypher
SHOW DATABASES;
```

Then switch to the one you need.

## If No Data Exists

If you switch to `smartgraphdb` and still see no nodes, you need to **run the graph clustering script**:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile/src
python graph_clustering_neo4j.py
```

This script:
1. Loads relationships from PostgreSQL
2. Creates nodes and relationships in Neo4j
3. Detects communities
4. Saves clusters to PostgreSQL

## Verify Data Exists

Run this to check if nodes exist:
```cypher
MATCH (n)
RETURN count(n) AS node_count;

MATCH ()-[r]->()
RETURN count(r) AS relationship_count;
```

If both return 0, run the clustering script first!

---

**Most likely fix: Switch database dropdown from `neo4j` to `smartgraphdb` in Browser!**

