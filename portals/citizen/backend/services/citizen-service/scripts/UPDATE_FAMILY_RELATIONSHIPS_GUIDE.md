# Guide: Updating Family Relationships

This guide explains how to update family relationships for citizens, specifically for seed Aadhaar `387193279353` (Sulekha Rajput).

## Two Approaches

### Approach 1: Direct SQL Update (Quick & Direct)

Use this for immediate database updates without going through the API.

#### Option A: Run SQL Script in pgAdmin

1. Open pgAdmin
2. Connect to `smart_citizen` database
3. Open Query Tool
4. Copy and paste the contents of `update_family_relationships_simple.sql`
5. Execute the query

#### Option B: Run PowerShell Script

```powershell
cd portals/citizen/backend/services/citizen-service/scripts
.\update_family_relationships.ps1
```

**What it does:**
- Deletes existing relationships for seed Aadhaar `387193279353`
- Inserts 8 new relationships:
  - **Spouse**: Shyam Rajput (859689643743) - 85% confidence
  - **Children**: Bali Rajput, Babita Rajput, Jugnu Rajput, Bholaram Gujjar - 80% confidence
  - **Family Members**: Choteram Gujjar, Savita Gujjar, Chiku Rajput - 75-80% confidence
- Marks all relationships as `is_verified = true` and `source = 'MANUAL'`
- Shows verification query results

---

### Approach 2: Backend API Endpoint (For Frontend Updates)

Use this when you want to update relationships from the frontend application.

#### API Endpoint

```
PUT /api/v1/citizens/{citizenId}/family/relationships
```

#### Request Body

```json
{
  "relationships": [
    {
      "relatedCitizenAadhaar": "859689643743",
      "relationshipType": "SPOUSE",
      "relationshipLabel": "Spouse",
      "confidence": 85
    },
    {
      "relatedCitizenAadhaar": "859689643991",
      "relationshipType": "CHILD",
      "relationshipLabel": "Child",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "237694608901",
      "relationshipType": "CHILD",
      "relationshipLabel": "Child",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "875205246823",
      "relationshipType": "CHILD",
      "relationshipLabel": "Child",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "411886224383",
      "relationshipType": "FAMILY_MEMBER",
      "relationshipLabel": "Family Member",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "888205246823",
      "relationshipType": "FAMILY_MEMBER",
      "relationshipLabel": "Family Member",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "859548833425",
      "relationshipType": "CHILD",
      "relationshipLabel": "Child",
      "confidence": 80
    },
    {
      "relatedCitizenAadhaar": "876205246823",
      "relationshipType": "FAMILY_MEMBER",
      "relationshipLabel": "Family Member",
      "confidence": 75
    }
  ]
}
```

#### Example using cURL

```bash
curl -X PUT "http://localhost:8081/citizen/api/v1/citizens/{citizen-uuid}/family/relationships" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your-jwt-token}" \
  -d @request.json
```

#### Response

```json
{
  "success": true,
  "message": "8 family relationship(s) updated successfully",
  "data": 8
}
```

---

## Relationship Types

Valid relationship types:
- `SPOUSE` - Spouse/Partner
- `CHILD` - Child
- `PARENT` - Parent
- `SIBLING` - Sibling
- `FAMILY_MEMBER` - Other family member

## Notes

1. **Replacement Behavior**: The API endpoint replaces ALL existing relationships for the citizen with the new ones provided. If you want to add relationships without deleting existing ones, you'll need to include all relationships in the request.

2. **Verification**: All relationships updated via the API are marked as:
   - `is_verified = true`
   - `source = 'MANUAL'`
   - `expires_at = NULL` (never expires)

3. **Validation**: 
   - Related citizens must exist in the database
   - Self-relationships are automatically skipped
   - Confidence must be between 0-100

4. **Database Table**: Relationships are stored in `family_relationships_cache` table with a unique constraint on `(citizen_id, related_citizen_id, relationship_type)`.

---

## Files Created

1. **SQL Scripts**:
   - `update_family_relationships_387193279353.sql` - Complex version with CTEs
   - `update_family_relationships_simple.sql` - Simple version (recommended)

2. **PowerShell Script**:
   - `update_family_relationships.ps1` - Automated script runner

3. **Backend Code**:
   - `UpdateFamilyRelationshipRequest.java` - DTO for single relationship
   - `BulkUpdateFamilyRelationshipsRequest.java` - DTO for bulk updates
   - `CitizenService.updateFamilyRelationships()` - Service method
   - `CitizenController.updateFamilyRelationships()` - REST endpoint

---

## Next Steps

To use the API from the frontend:

1. Create a React component/form to collect relationship data
2. Call the API endpoint with the citizen's UUID
3. Handle success/error responses
4. Refresh the family graph to show updated relationships

