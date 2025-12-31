# Neo4j Browser Queries Guide

## How to Open Neo4j Browser

1. **Open Neo4j Desktop**
2. **Click on your "SMART_GRAPH" instance**
3. **Click "Open" button** (or click on `smartgraphdb` database and select "Open Browser")
4. **Enter password**: `anjali143`
5. **Neo4j Browser will open** in your default web browser

## Basic Queries

### 1. View Sample Nodes and Relationships

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
RETURN n, r, m
LIMIT 50
```

This shows up to 50 nodes and their relationships in a visual graph.

### 2. Count Total Nodes and Relationships

```cypher
MATCH (n:GoldenRecord)
RETURN count(n) AS total_nodes;

MATCH ()-[r:RELATED_TO]->()
RETURN count(r) AS total_relationships;
```

### 3. View Graph Statistics

```cypher
MATCH (n:GoldenRecord)
OPTIONAL MATCH (n)-[r:RELATED_TO]-()
RETURN 
    count(DISTINCT n) AS nodes,
    count(r)/2 AS relationships,
    avg(apoc.node.degree(n)) AS avg_degree
LIMIT 1;
```

## Cluster/Community Queries

### 4. View Nodes by Family ID (Family Clusters)

```cypher
MATCH (n:GoldenRecord)
WHERE n.family_id IS NOT NULL
RETURN n.family_id AS family_cluster, collect(n.gr_id) AS members, count(n) AS size
ORDER BY size DESC
LIMIT 20;
```

### 5. Visualize a Specific Family Cluster

Replace `'your-family-id'` with an actual family_id:

```cypher
MATCH (n:GoldenRecord {family_id: 'your-family-id'})-[r:RELATED_TO]-(m:GoldenRecord)
RETURN n, r, m;
```

### 6. View Largest Connected Components

```cypher
MATCH path = (n:GoldenRecord)-[:RELATED_TO*1..3]-(m:GoldenRecord)
WHERE n <> m
WITH n, collect(DISTINCT m) AS component
WITH n, component, size(component) AS compSize
ORDER BY compSize DESC
LIMIT 10
RETURN n.gr_id, compSize, component[0..5] AS sample_members;
```

### 7. Find Nodes with Most Connections (Hubs)

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]-()
WITH n, count(r) AS degree
ORDER BY degree DESC
LIMIT 20
RETURN n.gr_id, n.family_id, degree
ORDER BY degree DESC;
```

### 8. Visualize Hub Nodes

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]-(connected:GoldenRecord)
WITH n, count(r) AS degree, collect(connected) AS neighbors
WHERE degree >= 10
RETURN n, neighbors[0..10], degree
LIMIT 5;
```

### 9. View Relationship Types Distribution

```cypher
MATCH ()-[r:RELATED_TO]->()
RETURN r.type AS relationship_type, count(*) AS count
ORDER BY count DESC;
```

### 10. Find Relationship Patterns

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO {type: 'SPOUSE'}]->(m:GoldenRecord)
RETURN n, r, m
LIMIT 20;
```

### 11. View Co-Residence Networks

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO {type: 'CO_RESIDENT'}]->(m:GoldenRecord)
RETURN n, r, m
LIMIT 30;
```

### 12. Explore Specific Cluster from PostgreSQL

If you want to explore a specific cluster from your PostgreSQL results:

```cypher
// First, let's see if cluster_id is stored in Neo4j
MATCH (n:GoldenRecord)
WHERE n.cluster_id IS NOT NULL
RETURN n.cluster_id, count(n) AS size
ORDER BY size DESC
LIMIT 20;
```

If cluster_id isn't in Neo4j yet, you can query by family_id or other properties.

## Advanced Visualizations

### 13. View Full Network of a Specific Node

Replace `'your-gr-id'` with an actual gr_id:

```cypher
MATCH path = (start:GoldenRecord {gr_id: 'your-gr-id'})-[*1..2]-(connected:GoldenRecord)
RETURN path
LIMIT 50;
```

### 14. Find Shortest Path Between Two Nodes

```cypher
MATCH path = shortestPath(
    (n1:GoldenRecord {gr_id: 'gr-id-1'})-[*..5]-(n2:GoldenRecord {gr_id: 'gr-id-2'})
)
RETURN path;
```

### 15. Community Detection Visualization (if GDS installed)

```cypher
// This requires GDS plugin
CALL gds.graph.project('my-graph', 'GoldenRecord', 'RELATED_TO')
YIELD graphName;

CALL gds.louvain.stream('my-graph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).gr_id AS node, communityId
LIMIT 100;
```

## Tips for Neo4j Browser

1. **Graph View**: Click and drag nodes to rearrange
2. **Node Details**: Click on a node to see its properties
3. **Relationship Details**: Click on an edge to see relationship properties
4. **Filter**: Use the filter icon to focus on specific nodes/relationships
5. **Fullscreen**: Click fullscreen icon for better visualization
6. **Export**: Right-click on graph to export as image

## Common Use Cases

### View All Family Members

```cypher
MATCH (head:GoldenRecord {family_id: NULL})-[:RELATED_TO*]-(member:GoldenRecord)
WHERE member.family_id = head.gr_id OR head.gr_id = member.family_id
RETURN head, member;
```

### Find Isolated Nodes (No Relationships)

```cypher
MATCH (n:GoldenRecord)
WHERE NOT (n)-[:RELATED_TO]-()
RETURN n
LIMIT 100;
```

### View Weight Distribution

```cypher
MATCH ()-[r:RELATED_TO]->()
RETURN r.weight AS weight, count(*) AS frequency
ORDER BY weight;
```

---

**Start with query #1 or #4 to get a visual overview of your graph!**

