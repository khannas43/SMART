# Neo4j Browser Visualization Legend & Tips

## Relationship Arrow Types Explained

### Single Arrow (→)
- **Directed relationship**: One-way connection
- Example: `(Parent)-[:CHILD]->(Child)` means "Parent has Child"
- Direction matters!

### Double Arrow (↔)
- **Bidirectional relationship**: Connection works both ways
- Example: `(Person1)-[:SPOUSE]-(Person2)` means they are spouses of each other
- Less common in our graph (we use directed)

### How Neo4j Browser Shows Relationships

1. **Solid Arrow**: Default relationship
2. **Dashed Arrow**: Optional/weak relationship (not used in our graph)
3. **Thickness**: Can represent relationship weight/strength
4. **Color**: Can be customized by relationship type

## Configuring Relationship Display

### Step 1: In Neo4j Browser Settings

1. Click **Settings** (⚙️) icon (top right)
2. Go to **Relationship** section

### Step 2: Set Relationship Caption

Set **Caption** to: `${r.type}` or `${r.relationship_type}`

This will display the relationship type (SPOUSE, CHILD, etc.) on the arrow.

### Step 3: Customize Colors

Set **Color** to show different colors for different relationship types:
```javascript
CASE r.type
  WHEN 'SPOUSE' THEN '#FF6B6B'      // Red for spouses
  WHEN 'CHILD' THEN '#4ECDC4'       // Teal for children
  WHEN 'PARENT' THEN '#95E1D3'      // Light green for parents
  WHEN 'SIBLING' THEN '#F38181'     // Pink for siblings
  WHEN 'CO_RESIDENT' THEN '#AA96DA' // Purple for co-residents
  ELSE '#68BDF6'                    // Blue for others
END
```

### Step 4: Set Relationship Width

Use weight to show relationship strength:
```javascript
r.weight * 5  // Multiplies weight by 5 for visibility
```

## Node Display Configuration

### Show Names Instead of IDs

1. Go to **Settings** → **Node** section
2. Set **Caption** to: `${n.full_name}`

Or combine with other info:
- `${n.full_name} (${n.age})` - Name and age
- `${n.full_name}\nID: ${n.gr_id}` - Name with ID below

### Node Size by Age

```javascript
CASE 
  WHEN n.age < 18 THEN 30  // Small for children
  WHEN n.age < 65 THEN 40  // Medium for adults
  ELSE 50                  // Large for seniors
END
```

### Node Color by Gender

```javascript
CASE n.gender
  WHEN 'MALE' THEN '#68BDF6'   // Blue
  WHEN 'FEMALE' THEN '#FF6B9D' // Pink
  ELSE '#95A5A6'               // Gray for unknown
END
```

## Complete Browser Settings Example

### Node Configuration
```
Caption: ${n.full_name}
Size: 40
Color: ${n.gender === 'FEMALE' ? '#FF6B9D' : '#68BDF6'}
```

### Relationship Configuration
```
Caption: ${r.type}
Width: ${r.weight || 1} * 3
Color: #68BDF6
```

## Quick Setup Guide

1. **Enhance nodes** (run `enhance_neo4j_nodes.py`)
2. **Open Browser Settings** (⚙️ icon)
3. **Set Node Caption** to `${n.full_name}`
4. **Set Relationship Caption** to `${r.type}`
5. **Save settings**
6. **Run query** from `NEO4J_ENHANCED_QUERIES.md`

## Relationship Type Reference

| Type | Arrow Direction | Description |
|------|----------------|-------------|
| **SPOUSE** | → or ↔ | Married partners |
| **CHILD** | Parent → Child | Parent has child |
| **PARENT** | Child → Parent | Child belongs to parent |
| **SIBLING** | → | Sibling relationship |
| **CO_RESIDENT** | → | Same address |
| **CO_BENEFIT** | → | Same benefits |
| **EMPLOYEE_OF** | Employee → Employer | Employment |
| **BUSINESS_PARTNER** | ↔ | Business relationship |

## Visual Example Query

Run this to see all relationship types:

```cypher
MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
WHERE n.full_name IS NOT NULL
WITH r.type AS rel_type, count(*) AS count
ORDER BY count DESC
RETURN 
  rel_type AS "Relationship Type",
  count AS "Count",
  CASE rel_type
    WHEN 'SPOUSE' THEN '👫'
    WHEN 'CHILD' THEN '👨‍👩‍👧‍👦'
    WHEN 'PARENT' THEN '👨‍👩‍👧‍👦'
    WHEN 'SIBLING' THEN '👨‍👩‍👧‍👦'
    WHEN 'CO_RESIDENT' THEN '🏠'
    WHEN 'CO_BENEFIT' THEN '💰'
    WHEN 'EMPLOYEE_OF' THEN '💼'
    ELSE '🔗'
  END AS "Icon"
```

---

**Configure Browser Settings once, then all queries will use your custom formatting!**

