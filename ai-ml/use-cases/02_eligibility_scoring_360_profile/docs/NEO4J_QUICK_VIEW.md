# Quick Start: View Your Graph in Neo4j Browser

## Step 1: Open Neo4j Browser

1. **Neo4j Desktop** → Click on **"SMART_GRAPH"** instance
2. Click **"Open"** button (or click on `smartgraphdb` database)
3. **Enter password**: `anjali143`
4. Browser opens at: `http://localhost:7474`

## Step 2: Run These Queries (in order)

### 1. See Your Graph Overview
```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
RETURN n, r, m
LIMIT 100
```
Click the **play button** (▶️) to execute. You'll see a visual graph!

### 2. Count Your Data
```cypher
MATCH (n:GoldenRecord)
RETURN count(n) AS total_nodes;

MATCH ()-[r:RELATED_TO]->()
RETURN count(r) AS total_relationships;
```

### 3. View Family Clusters (from your PostgreSQL results)
Since your clusters are stored in PostgreSQL, view by family_id:

```cypher
MATCH (n:GoldenRecord)
WHERE n.family_id IS NOT NULL
RETURN n.family_id AS family, collect(n.gr_id) AS members, count(n) AS size
ORDER BY size DESC
LIMIT 20;
```

### 4. Visualize a Family Network
Pick a family_id from the results above and visualize:

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]-(m:GoldenRecord)
WHERE n.family_id = 'some-family-id' OR m.family_id = 'some-family-id'
RETURN n, r, m;
```

### 5. Find Highly Connected Nodes (Hubs)
```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]-()
WITH n, count(r) AS connections
ORDER BY connections DESC
LIMIT 20
MATCH (n)-[r2:RELATED_TO]-(connected:GoldenRecord)
RETURN n, r2, connected;
```

## Pro Tips

- **Drag nodes** around to rearrange the graph
- **Click nodes** to see properties
- **Hover over edges** to see relationship types
- **Use the filter icon** to focus on specific patterns
- **Fullscreen mode** for better visualization

## If You See "No Results"

1. Make sure graph_clustering_neo4j.py completed successfully
2. Check if nodes were created:
   ```cypher
   MATCH (n:GoldenRecord) RETURN count(n);
   ```
3. If count is 0, re-run the clustering script

---

**Start with query #1 - it's the most visual!**

