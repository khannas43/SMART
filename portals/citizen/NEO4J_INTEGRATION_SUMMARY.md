# Neo4j Integration for Family Tree Visualization

## Overview

The Citizen Portal family tree visualization has been migrated from PostgreSQL-based address matching to **Neo4j graph database** for better performance and more accurate relationship detection. This follows the AI/ML use case design (AI-PLATFORM-02: 360° Profiles).

## What Was Implemented

### 1. Backend Changes

#### Neo4j Dependency Added
- **File**: `pom.xml`
- **Dependency**: `org.neo4j.driver:neo4j-java-driver:5.14.0`

#### Neo4j Configuration
- **File**: `application.yml`
- **Configuration**:
  ```yaml
  neo4j:
    uri: bolt://172.17.16.1:7687
    user: neo4j
    password: anjali143
    database: smartgraphdb
  ```

#### New Service: ProfileGraphService
- **File**: `src/main/java/com/smart/citizen/service/ProfileGraphService.java`
- **Purpose**: Queries Neo4j for family relationship graphs
- **Features**:
  - Supports querying by `gr_id` (UUID) or `jan_aadhaar` (Aadhaar number)
  - Returns graph data in format compatible with `react-force-graph-2d`
  - Handles relationship types: SPOUSE, CHILD, PARENT, SIBLING, CO_RESIDENT, etc.
  - Returns relationship type legend with colors and icons

#### New Controller: ProfileGraphController
- **File**: `src/main/java/com/smart/citizen/controller/ProfileGraphController.java`
- **Endpoints**:
  - `GET /profiles/graph/family-network/{identifier}?depth=2` - Get family network graph
  - `GET /profiles/graph/relationship-types` - Get relationship type legend

#### Updated Service: CitizenServiceImpl
- **File**: `src/main/java/com/smart/citizen/service/impl/CitizenServiceImpl.java`
- **Method**: `getFamilyRelationships(UUID citizenId, int depth)`
- **Behavior**:
  1. **Primary**: Queries Neo4j first (by citizen ID or Aadhaar number)
  2. **Fallback**: If Neo4j fails or returns no data, falls back to PostgreSQL address matching
  3. **Conversion**: Converts Neo4j graph format (nodes/links) to `FamilyGraphResponse` DTO format

### 2. Frontend Changes

**No changes required!** The frontend already uses:
- Endpoint: `/citizens/{id}/family/relationships`
- Library: `react-force-graph-2d` (already installed)
- The backend now serves Neo4j data through the existing endpoint

## How It Works

### Data Flow

```
Frontend Request
    ↓
GET /citizens/{citizenId}/family/relationships?depth=2
    ↓
CitizenServiceImpl.getFamilyRelationships()
    ↓
ProfileGraphService.getFamilyNetwork()
    ↓
Neo4j Query (Cypher)
    ↓
Convert to FamilyGraphResponse
    ↓
Return to Frontend
```

### Neo4j Query Strategy

1. **Try by Aadhaar Number** (if available):
   ```cypher
   MATCH path = (start:GoldenRecord {jan_aadhaar: $identifier})-[r:RELATED_TO*1..2]-(connected:GoldenRecord)
   ```

2. **Try by gr_id (UUID)** (if Aadhaar not available):
   ```cypher
   MATCH path = (start:GoldenRecord {gr_id: $identifier})-[r:RELATED_TO*1..2]-(connected:GoldenRecord)
   ```

3. **Filter Relationships**:
   - Family relationships: SPOUSE, CHILD, PARENT, SIBLING
   - Or same `family_id` (co-residents)

### Fallback Strategy

If Neo4j:
- Returns no data
- Connection fails
- Query times out

Then the system automatically falls back to PostgreSQL address matching (existing logic).

## Relationship Types

| Type | Icon | Color | Description |
|------|------|-------|-------------|
| SPOUSE | 👫 | #FF6B6B | Married partner |
| CHILD | 👨‍👩‍👧‍👦 | #4ECDC4 | Parent → Child |
| PARENT | 👨‍👩‍👧‍👦 | #95E1D3 | Child → Parent |
| SIBLING | 👨‍👩‍👧‍👦 | #F38181 | Brother/Sister |
| CO_RESIDENT | 🏠 | #AA96DA | Same address |
| CO_BENEFIT | 💰 | #FECA57 | Same benefits |
| EMPLOYEE_OF | 💼 | #48DBFB | Employee → Employer |
| BUSINESS_PARTNER | 🤝 | #10AC84 | Business partnership |
| SHG_MEMBER | 👥 | #5F27CD | Self-Help Group member |

## API Endpoints

### Existing Endpoint (Updated)
```
GET /citizens/{citizenId}/family/relationships?depth=2
```
- **Uses Neo4j** (with PostgreSQL fallback)
- **Returns**: `FamilyGraphResponse` with `members` and `relationships`

### New Direct Neo4j Endpoints
```
GET /profiles/graph/family-network/{identifier}?depth=2
GET /profiles/graph/relationship-types
```
- **Direct Neo4j access** (for advanced use cases)
- **Returns**: Raw graph format (nodes/links)

## Configuration

### Neo4j Connection
Update `application.yml` if your Neo4j instance is different:
```yaml
neo4j:
  uri: bolt://your-neo4j-host:7687
  user: your-username
  password: your-password
  database: your-database-name
```

### Default Values
- **URI**: `bolt://172.17.16.1:7687`
- **User**: `neo4j`
- **Password**: `anjali143`
- **Database**: `smartgraphdb`

## Testing

### 1. Verify Neo4j Connection
```bash
# Check if Neo4j is running
curl http://172.17.16.1:7474

# Or use Neo4j Browser
# http://172.17.16.1:7474
```

### 2. Test Backend Endpoints
```bash
# Get family network (requires authentication)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8081/citizen/api/v1/citizens/{citizenId}/family/relationships?depth=2

# Get relationship types
curl http://localhost:8081/citizen/api/v1/profiles/graph/relationship-types
```

### 3. Test Frontend
1. Navigate to Profile Dashboard
2. Click "360° View" tab
3. Family tree should load from Neo4j (if data exists)

## Troubleshooting

### No Family Members Showing

1. **Check Neo4j Data**:
   ```cypher
   MATCH (n:GoldenRecord)
   RETURN n LIMIT 10
   ```

2. **Check Relationships**:
   ```cypher
   MATCH (n:GoldenRecord)-[r:RELATED_TO]->(m:GoldenRecord)
   RETURN n, r, m LIMIT 10
   ```

3. **Verify Citizen Mapping**:
   - Check if `citizen.aadhaar_number` matches `golden_records.jan_aadhaar` in Neo4j
   - Or if `citizen.id` matches `golden_records.gr_id` in Neo4j

### Connection Errors

1. **Check Neo4j is Running**:
   ```bash
   # Windows
   netstat -an | findstr 7687
   
   # Linux/WSL
   netstat -an | grep 7687
   ```

2. **Verify Credentials** in `application.yml`

3. **Check Firewall** allows connection to Neo4j port

### Fallback to PostgreSQL

If Neo4j fails, the system automatically falls back to PostgreSQL address matching. Check logs:
```
Neo4j query failed, falling back to PostgreSQL: <error message>
```

## Benefits of Neo4j

1. **Performance**: Native graph queries are faster than SQL joins
2. **Accuracy**: Relationships are explicitly stored, not inferred
3. **Scalability**: Handles large relationship networks efficiently
4. **Flexibility**: Easy to add new relationship types
5. **Graph Algorithms**: Can use Neo4j GDS for community detection, centrality, etc.

## Next Steps

1. ✅ Neo4j integration complete
2. ⏳ Populate Neo4j with relationship data (if not already done)
3. ⏳ Map `citizen.id` to `gr_id` for better matching
4. ⏳ Add relationship confidence scores
5. ⏳ Implement relationship verification workflow
6. ⏳ Add graph analytics (community detection, centrality)

## References

- **AI/ML Use Case**: `ai-ml/use-cases/02_eligibility_scoring_360_profile/`
- **Integration Guide**: `ai-ml/use-cases/02_eligibility_scoring_360_profile/docs/CITIZEN_PORTAL_INTEGRATION.md`
- **Neo4j Setup**: `ai-ml/use-cases/02_eligibility_scoring_360_profile/docs/NEO4J_SETUP.md`

---

**Status**: ✅ **Implementation Complete**

The family tree visualization now uses Neo4j for relationship queries, with automatic fallback to PostgreSQL if Neo4j is unavailable.

