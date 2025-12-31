# Enhanced Neo4j Browser Queries with Names & Relationship Types

## First: Enhance Your Nodes

Run this script to add names to Neo4j nodes:
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/enhance_neo4j_nodes.py
```

## Browser Visualization Settings

### 1. Configure Node Labels to Show Names

In Neo4j Browser, go to **Settings** (⚙️ icon) → **Node Styles**:

1. **Node Caption**: Set to `${n.full_name}` or `${n.full_name}\n${n.gr_id}`
2. **Node Size**: Use `${n.age}` or fixed size
3. **Node Color**: Use `${n.gender}` or `${n.family_id}`

Or use this query with custom properties:

```cypher
// Query that returns formatted node labels
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
RETURN 
  n,
  n.full_name AS n_name,
  r,
  r.type AS rel_type,
  m,
  m.full_name AS m_name
LIMIT 50
```

### 2. Configure Relationship Labels

In Browser **Settings** → **Relationship Styles**:

1. **Relationship Caption**: Set to `${r.type}` or `${r.relationship_type}`
2. **Relationship Width**: Use `${r.weight}` for thickness

## Enhanced Queries

### Query 1: Visualize with Names and Relationship Types

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
WHERE n.full_name IS NOT NULL AND m.full_name IS NOT NULL
RETURN 
  n.full_name AS from_name,
  r.type AS relationship_type,
  m.full_name AS to_name,
  n,
  r,
  m
LIMIT 100
```

**In Browser**: After running, click on nodes to see full properties. Relationship types will show on arrows.

### Query 2: Family Network with Names

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]-(m:GoldenRecord)
WHERE n.family_id IS NOT NULL 
  AND n.family_id = m.family_id
  AND r.type IN ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING']
RETURN 
  n.full_name AS person1,
  r.type AS relationship,
  m.full_name AS person2,
  n,
  r,
  m
LIMIT 50
```

### Query 3: Formatted Family Tree

```cypher
MATCH path = (head:GoldenRecord {family_id: NULL})-[r1:RELATED_TO*1..3]-(member:GoldenRecord)
WHERE member.family_id = head.gr_id
WITH head, member, relationships(path) AS rels
UNWIND rels AS rel
RETURN 
  head.full_name AS family_head,
  rel.type AS relationship,
  member.full_name AS member_name,
  member.age AS age,
  member.gender AS gender,
  head,
  rel,
  member
LIMIT 30
```

### Query 4: Specific Relationship Types

```cypher
// View SPOUSE relationships
MATCH (n:GoldenRecord)-[r:RELATED_TO {type: 'SPOUSE'}]->(m:GoldenRecord)
WHERE n.full_name IS NOT NULL
RETURN 
  n.full_name AS spouse1,
  '👫 SPOUSE' AS relationship,
  m.full_name AS spouse2,
  n,
  r,
  m
LIMIT 30
```

```cypher
// View PARENT-CHILD relationships
MATCH (parent:GoldenRecord)-[r:RELATED_TO {type: 'CHILD'}]->(child:GoldenRecord)
WHERE parent.full_name IS NOT NULL AND child.full_name IS NOT NULL
RETURN 
  parent.full_name AS parent_name,
  '👨‍👩‍👧‍👦 CHILD' AS relationship,
  child.full_name AS child_name,
  child.age AS child_age,
  parent,
  r,
  child
LIMIT 30
```

### Query 5: Co-Residence Networks

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO {type: 'CO_RESIDENT'}]->(m:GoldenRecord)
WHERE n.full_name IS NOT NULL
RETURN 
  n.full_name AS person1,
  n.city_village AS location,
  '🏠 CO_RESIDENT' AS relationship,
  m.full_name AS person2,
  n,
  r,
  m
LIMIT 30
```

## Custom Browser Configuration

### Save as Browser Favorite

1. Run a query
2. Click the **star icon** (⭐) to save as favorite
3. Name it (e.g., "Family Networks with Names")

### Create Custom Style Sheet

Create a file `~/.neo4j/browser-styles.css` (on Windows: `%USERPROFILE%\.neo4j\browser-styles.css`):

```css
.node {
  border-color: #68BDF6;
  border-width: 2px;
  color: #FFFFFF;
  font-size: 10px;
  font-weight: bold;
  height: 50px;
  width: 50px;
}

.relationship {
  font-size: 10px;
  padding: 3px;
  text-color: #68BDF6;
  text-rotation: autorotate;
  text-margin-x: 10px;
}

.node.selected {
  border-color: #FF6B6B;
}
```

## Relationship Type Legend

Here's what each relationship type means:

| Relationship Type | Symbol | Description |
|------------------|--------|-------------|
| **SPOUSE** | 👫 | Married partners |
| **CHILD** | 👨‍👩‍👧‍👦 | Parent → Child relationship |
| **PARENT** | 👨‍👩‍👧‍👦 | Child → Parent relationship |
| **SIBLING** | 👨‍👩‍👧‍👦 | Brothers/Sisters |
| **CO_RESIDENT** | 🏠 | Living at same address |
| **EMPLOYEE_OF** | 💼 | Employee → Employer |
| **CO_BENEFIT** | 💰 | Receiving same benefits |
| **BUSINESS_PARTNER** | 🤝 | Business partners |
| **SHG_MEMBER** | 👥 | Self-Help Group members |

## Pro Tips

### 1. Use Node Caption Property

In Browser Settings, set **Node Caption** to:
- `${n.full_name}` - Shows only name
- `${n.full_name} (${n.age})` - Shows name and age
- `${n.full_name}\n${n.gr_id}` - Shows name and ID on separate lines

### 2. Color Nodes by Property

- **By Gender**: Use `${n.gender}` in Node Color
- **By Family**: Use `${n.family_id}` in Node Color
- **By Age Group**: Use a CASE statement in a computed property

### 3. Filter in Browser

After running a query:
- **Click on a node** to see all properties
- **Right-click** to expand connections
- **Use filter icon** to focus on specific nodes/relationships

### 4. Export Visualizations

- **Right-click** on graph → **Export as PNG**
- Or use **Screenshot** button in Browser

## Quick Reference Query Template

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
WHERE n.full_name IS NOT NULL 
  AND m.full_name IS NOT NULL
  AND r.type = 'YOUR_RELATIONSHIP_TYPE'  // Optional: filter by type
RETURN 
  n.full_name AS from_person,
  r.type AS relationship_type,
  m.full_name AS to_person,
  n, r, m
LIMIT 50
```

---

**Run `enhance_neo4j_nodes.py` first, then use these enhanced queries!**

