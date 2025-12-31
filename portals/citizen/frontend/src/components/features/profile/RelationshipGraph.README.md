# Relationship Graph Component

## Overview

This React component visualizes citizen relationship networks using Neo4j graph data. It displays:
- **Nodes**: People (citizens) with names and properties
- **Edges**: Relationships with types (SPOUSE, CHILD, PARENT, etc.)
- **Colors**: Different colors for different relationship types
- **Labels**: Relationship types displayed on edges

## Installation

### Install Required Packages

```bash
cd portals/citizen/frontend
npm install react-force-graph-2d
# or for 3D version:
npm install react-force-graph-3d
```

### Package.json Dependency

```json
{
  "dependencies": {
    "react-force-graph-2d": "^1.25.3",
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0"
  }
}
```

## Usage

### Basic Usage

```tsx
import { RelationshipGraph } from '@/components/features/profile/RelationshipGraph';

function ProfilePage() {
  const grId = "your-golden-record-id";
  
  return (
    <RelationshipGraph 
      grId={grId}
      depth={2}
      height={600}
    />
  );
}
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `grId` | `string` | required | Golden Record ID to visualize |
| `depth` | `number` | `2` | Depth of relationships to fetch (1-3 recommended) |
| `height` | `number` | `600` | Graph visualization height in pixels |

## Features

### 1. Relationship Type Colors

- **SPOUSE**: Red (#FF6B6B) 👫
- **CHILD**: Teal (#4ECDC4) 👨‍👩‍👧‍👦
- **PARENT**: Light Green (#95E1D3) 👨‍👩‍👧‍👦
- **SIBLING**: Pink (#F38181) 👨‍👩‍👧‍👦
- **CO_RESIDENT**: Purple (#AA96DA) 🏠
- **CO_BENEFIT**: Yellow (#FECA57) 💰
- **EMPLOYEE_OF**: Blue (#48DBFB) 💼
- **BUSINESS_PARTNER**: Green (#10AC84) 🤝
- **SHG_MEMBER**: Dark Purple (#5F27CD) 👥

### 2. Node Colors

- **Male**: Blue (#68BDF6)
- **Female**: Pink (#FF6B9D)
- **Unknown**: Gray (#95A5A6)

### 3. Interactive Features

- **Hover**: Pause animation and show node details
- **Click**: Trigger actions (e.g., open profile modal)
- **Drag**: Nodes can be repositioned
- **Zoom**: Mouse wheel zoom
- **Pan**: Click and drag background

## API Endpoints

The component expects these backend endpoints:

### 1. Get Relationship Types

```
GET /api/v1/profiles/graph/relationship-types
```

Response:
```json
{
  "SPOUSE": {
    "label": "Spouse",
    "icon": "👫",
    "color": "#FF6B6B",
    "description": "Married partner"
  },
  ...
}
```

### 2. Get Family Network

```
GET /api/v1/profiles/graph/family-network/{grId}?depth=2
```

Response:
```json
{
  "nodes": [
    {
      "id": 1,
      "gr_id": "uuid",
      "label": "John Doe",
      "name": "John Doe",
      "age": 35,
      "gender": "MALE"
    }
  ],
  "links": [
    {
      "source": 1,
      "target": 2,
      "relationship_type": "SPOUSE",
      "label": "SPOUSE",
      "type": "SPOUSE",
      "weight": 1.0
    }
  ]
}
```

## Customization

### Custom Colors

Modify the `getRelationshipColor` function:

```tsx
const getRelationshipColor = (type: string): string => {
  const customColors: Record<string, string> = {
    SPOUSE: '#FF0000',
    CHILD: '#00FF00',
    // ... add more
  };
  return customColors[type] || '#68BDF6';
};
```

### Custom Node Rendering

You can customize node appearance:

```tsx
<ForceGraph2D
  nodeCanvasObject={(node, ctx, globalScale) => {
    // Custom node rendering
    ctx.fillStyle = getNodeColor(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
    ctx.fill();
  }}
/>
```

### Add Tooltips

```tsx
<ForceGraph2D
  onNodeHover={(node) => {
    if (node) {
      // Show tooltip
      setTooltip(node);
    } else {
      setTooltip(null);
    }
  }}
/>
```

## Integration with Profile 360 Page

```tsx
import { RelationshipGraph } from '@/components/features/profile/RelationshipGraph';
import { useProfile } from '@/hooks/useProfile';

export function Profile360Page() {
  const { profile, loading } = useProfile();
  
  if (loading) return <Loading />;
  
  return (
    <Box>
      <ProfileHeader profile={profile} />
      <RelationshipGraph grId={profile.gr_id} depth={2} />
      <ProfileDetails profile={profile} />
    </Box>
  );
}
```

## Alternative Libraries

If `react-force-graph-2d` doesn't fit your needs:

### Option 1: vis-network

```bash
npm install vis-network
```

### Option 2: cytoscape.js

```bash
npm install cytoscape react-cytoscapejs
```

### Option 3: D3.js directly

```bash
npm install d3 @types/d3
```

## Performance Tips

1. **Limit depth**: Keep `depth` ≤ 3 for large networks
2. **Limit nodes**: Show max 100-200 nodes at once
3. **Lazy load**: Load graph data on-demand
4. **Cache**: Cache relationship types legend
5. **Virtual scrolling**: For very large graphs

## Troubleshooting

### Graph not showing

- Check API endpoint URLs
- Verify CORS settings
- Check browser console for errors
- Ensure Neo4j is accessible from backend

### Performance issues

- Reduce `depth` parameter
- Limit number of nodes displayed
- Use pagination or filtering
- Optimize Neo4j queries

---

**See `docs/CITIZEN_PORTAL_INTEGRATION.md` for full integration guide.**

