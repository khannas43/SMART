# Citizen Portal Integration: Neo4j Graph Visualization

## Overview

This guide explains how to integrate Neo4j relationship graph visualization into the Citizen Portal React frontend, showing relationship types (SPOUSE, CHILD, PARENT, etc.) with colors and labels.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Citizen Portal (React Frontend)            │
│  ┌───────────────────────────────────────────────────┐  │
│  │   RelationshipGraph Component (react-force-graph) │  │
│  └──────────────────────┬────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ HTTP REST API
┌─────────────────────────┴───────────────────────────────┐
│          Spring Boot Backend (Profile360 API)           │
│  ┌───────────────────────────────────────────────────┐  │
│  │   ProfileGraphController.java                     │  │
│  │   ProfileGraphService.java                        │  │
│  └──────────────────────┬────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ Bolt Protocol
┌─────────────────────────┴───────────────────────────────┐
│                   Neo4j Database                         │
│  - Nodes: GoldenRecord (people)                         │
│  - Edges: RELATED_TO (relationships with types)         │
└─────────────────────────────────────────────────────────┘
```

## Step 1: Backend API Setup

### 1.1 Add Neo4j Driver Dependency

In your Spring Boot `pom.xml`:

```xml
<dependency>
    <groupId>org.neo4j.driver</groupId>
    <artifactId>neo4j-java-driver</artifactId>
    <version>5.14.0</version>
</dependency>
```

### 1.2 Add Configuration

In `application.yml`:

```yaml
neo4j:
  uri: bolt://172.17.16.1:7687
  user: neo4j
  password: anjali143
  database: smartgraphdb
```

### 1.3 Deploy Controllers & Services

Copy the following files to your Spring Boot project:
- `ProfileGraphController.java`
- `ProfileGraphService.java`

Location: `portals/citizen/backend/services/citizen-service/src/main/java/com/smart/platform/aiml/profile360/`

### 1.4 Test API Endpoints

```bash
# Get relationship types
curl http://localhost:8080/api/v1/profiles/graph/relationship-types

# Get family network
curl http://localhost:8080/api/v1/profiles/graph/family-network/{grId}?depth=2
```

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd portals/citizen/frontend
npm install react-force-graph-2d
npm install @mui/material @mui/icons-material
```

### 2.2 Copy Component

Copy `RelationshipGraph.tsx` to:
```
portals/citizen/frontend/src/components/features/profile/RelationshipGraph.tsx
```

### 2.3 Create API Service

Create `src/services/profile.service.ts`:

```typescript
import axios from 'axios';

const API_BASE = '/api/v1/profiles/graph';

export interface GraphData {
  nodes: Node[];
  links: Link[];
}

export const profileService = {
  async getFamilyNetwork(grId: string, depth = 2): Promise<GraphData> {
    const response = await axios.get(`${API_BASE}/family-network/${grId}`, {
      params: { depth }
    });
    return response.data;
  },

  async getRelationshipTypes(): Promise<Record<string, RelationshipType>> {
    const response = await axios.get(`${API_BASE}/relationship-types`);
    return response.data;
  },
};
```

### 2.4 Integrate in Profile Page

Update your profile page component:

```tsx
import { RelationshipGraph } from '@/components/features/profile/RelationshipGraph';

export function CitizenProfilePage() {
  const { grId } = useParams();
  
  return (
    <Container>
      <ProfileHeader />
      <RelationshipGraph grId={grId!} depth={2} height={600} />
      <ProfileDetails />
    </Container>
  );
}
```

## Step 3: Relationship Type Display

### Visual Legend

The component automatically displays a legend showing:
- 👫 SPOUSE (Red)
- 👨‍👩‍👧‍👦 CHILD (Teal)
- 👨‍👩‍👧‍👦 PARENT (Light Green)
- 👨‍👩‍👧‍👦 SIBLING (Pink)
- 🏠 CO_RESIDENT (Purple)
- 💰 CO_BENEFIT (Yellow)
- 💼 EMPLOYEE_OF (Blue)
- 🤝 BUSINESS_PARTNER (Green)
- 👥 SHG_MEMBER (Dark Purple)

### On Graph Edges

Relationship types are displayed:
- **As labels** on the edges (arrows)
- **With colors** matching the legend
- **With icons** (optional, via label)

## Step 4: Customization

### Change Colors

Edit `RelationshipGraph.tsx`:

```tsx
const getRelationshipColor = (type: string): string => {
  const colors: Record<string, string> = {
    SPOUSE: '#FF0000',      // Custom red
    CHILD: '#00FF00',       // Custom green
    // ... add more
  };
  return colors[type] || '#68BDF6';
};
```

### Change Node Appearance

```tsx
nodeVal={(node) => {
  // Larger nodes for family heads
  return node.family_id === node.gr_id ? 10 : 5;
}}
```

### Add Click Actions

```tsx
onNodeClick={(node) => {
  // Navigate to person's profile
  navigate(`/profile/${node.gr_id}`);
}}
```

## Step 5: Testing

### Test Backend

```bash
# Start Spring Boot application
cd portals/citizen/backend/services/citizen-service
mvn spring-boot:run

# Test endpoints
curl http://localhost:8080/api/v1/profiles/graph/relationship-types
```

### Test Frontend

```bash
cd portals/citizen/frontend
npm start

# Open browser to profile page with grId parameter
# http://localhost:3000/profile/{grId}
```

## Step 6: Production Considerations

### Performance

1. **Cache relationship types** (rarely changes)
2. **Limit graph depth** (max 2-3 levels)
3. **Paginate large networks** (>100 nodes)
4. **Lazy load** graph data

### Security

1. **Authenticate requests** (JWT tokens)
2. **Validate grId** (check user permissions)
3. **Rate limit** graph queries
4. **Sanitize** Neo4j query inputs

### Error Handling

```tsx
try {
  const graphData = await profileService.getFamilyNetwork(grId);
  setGraphData(graphData);
} catch (error) {
  if (error.response?.status === 404) {
    setError('Profile not found');
  } else {
    setError('Failed to load relationship network');
  }
}
```

## Alternative Visualization Libraries

### Option 1: vis-network

```bash
npm install vis-network
```

Better for:
- Large networks (1000+ nodes)
- Static layouts
- Custom styling

### Option 2: cytoscape.js

```bash
npm install cytoscape react-cytoscapejs
```

Better for:
- Complex layouts (hierarchical, circular)
- Edge routing
- Advanced filtering

### Option 3: D3.js

```bash
npm install d3 @types/d3
```

Better for:
- Full customization
- Custom interactions
- Performance optimization

## Troubleshooting

### Graph Not Loading

1. **Check Neo4j connection** in backend logs
2. **Verify API endpoints** are accessible
3. **Check CORS** configuration
4. **Inspect network** tab in browser DevTools

### Relationship Types Not Showing

1. **Run enhancement script**: `enhance_neo4j_nodes.py`
2. **Check Neo4j data**: Verify `r.type` property exists
3. **Check API response**: Verify relationship types are in response

### Performance Issues

1. **Reduce depth**: Use `depth=1` instead of `depth=3`
2. **Filter relationships**: Only show family relationships
3. **Limit nodes**: Show max 50-100 nodes at once
4. **Use pagination**: Load graph in chunks

## Complete Example

See `portals/citizen/frontend/src/components/features/profile/RelationshipGraph.tsx` for complete implementation.

## Next Steps

1. ✅ Backend API endpoints created
2. ✅ Frontend component created
3. ⏳ Integrate in profile page
4. ⏳ Add authentication/authorization
5. ⏳ Add error handling
6. ⏳ Add loading states
7. ⏳ Add unit tests
8. ⏳ Deploy to staging

---

**The relationship graph will show names, relationship types, and colors just like in Neo4j Browser!**

