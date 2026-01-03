# Data Migration Guide: smart_warehouse → smart_citizen

This guide explains how to migrate data from the `smart_warehouse` database to the `smart_citizen` database for testing purposes.

## Overview

The migration script (`V11__migrate_data_from_warehouse.sql`) copies:
- **Citizens** - From `smart_warehouse.citizens` to `smart_citizen.citizens`
- **Schemes** - From `smart_warehouse.schemes` to `smart_citizen.schemes`
- **Applications** - From `smart_warehouse.applications` to `smart_citizen.service_applications`
- **Status History** - Creates application status history entries

## Prerequisites

1. ✅ Both databases exist:
   - `smart_warehouse` (source - must have data)
   - `smart_citizen` (target - tables created via Flyway)

2. ✅ `dblink` extension enabled in `smart_citizen` database:
   ```sql
   -- Connect to smart_citizen database
   \c smart_citizen
   
   -- Enable dblink extension
   CREATE EXTENSION IF NOT EXISTS dblink;
   ```

3. ✅ Warehouse has data populated (check counts):
   ```sql
   -- Connect to smart_warehouse
   \c smart_warehouse
   SELECT COUNT(*) FROM citizens;
   SELECT COUNT(*) FROM schemes;
   SELECT COUNT(*) FROM applications;
   ```

## Migration Methods

### Method 1: Automatic via Flyway (Recommended)

The migration script will run automatically when you start the citizen-service:

```bash
cd portals/citizen/backend/services/citizen-service
mvn clean spring-boot:run
```

Flyway will detect `V11__migrate_data_from_warehouse.sql` and execute it.

### Method 2: Manual Execution via PowerShell

```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
.\scripts\migrate_data_from_warehouse.ps1
```

### Method 3: Manual Execution via Bash/WSL

```bash
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
chmod +x scripts/migrate_data_from_warehouse.sh
./scripts/migrate_data_from_warehouse.sh
```

### Method 4: Direct SQL Execution

```bash
# Connect to smart_citizen database
psql -h localhost -U sameer -d smart_citizen

# Enable dblink if not already enabled
CREATE EXTENSION IF NOT EXISTS dblink;

# Execute migration script
\i src/main/resources/db/migration/V11__migrate_data_from_warehouse.sql
```

Or via pgAdmin4:
1. Connect to `smart_citizen` database
2. Open Query Tool
3. Execute the SQL file: `V11__migrate_data_from_warehouse.sql`

## What Gets Migrated

### Citizens
- All citizens with mobile numbers
- Maps: `citizen_id` (BIGINT) → `id` (UUID)
- Maps: `gender` ('Male'/'Female') → 'MALE'/'FEMALE'
- Maps: `status` ('active'/'inactive') → 'ACTIVE'/'INACTIVE'
- Includes district name lookup

### Schemes
- All schemes from warehouse
- Maps: `scheme_id` (INTEGER) → `id` (UUID)
- Builds `eligibility_criteria` JSON from warehouse fields
- Maps: `status` ('active'/'inactive') → 'ACTIVE'/'INACTIVE'

### Applications
- All applications
- Maps: `application_status` → proper status values:
  - 'pending' → 'SUBMITTED'
  - 'under_review' → 'UNDER_REVIEW'
  - 'approved' → 'APPROVED'
  - 'rejected' → 'REJECTED'
  - 'disbursed' → 'COMPLETED'
  - 'closed' → 'COMPLETED'
- Stores eligibility data in `application_data` JSON field

### Status History
- Creates initial status entry for each application
- Creates status change entry if status was updated

## Data Mapping Details

### ID Conversion
- **Citizens**: `citizen_id` (BIGINT) → `id` (UUID) via temporary mapping table
- **Schemes**: `scheme_id` (INTEGER) → `id` (UUID) via temporary mapping table
- **Applications**: New UUIDs generated, maintains `application_number` uniqueness

### Status Mapping
- **Citizen Status**: 'active' → 'ACTIVE', 'inactive' → 'INACTIVE'
- **Scheme Status**: 'active' → 'ACTIVE', 'inactive'/'suspended' → 'INACTIVE'
- **Application Status**: See mapping above

### Field Mapping
- **Gender**: 'Male' → 'MALE', 'Female' → 'FEMALE', else → 'OTHER'
- **District**: Looked up from `districts` table
- **Eligibility Criteria**: Built as JSONB from warehouse scheme fields

## Verification

After migration, verify the data:

```sql
-- Connect to smart_citizen
\c smart_citizen

-- Check counts
SELECT COUNT(*) as citizens FROM citizens;
SELECT COUNT(*) as schemes FROM schemes;
SELECT COUNT(*) as applications FROM service_applications;
SELECT COUNT(*) as history FROM application_status_history;

-- Sample data
SELECT * FROM citizens LIMIT 5;
SELECT * FROM schemes LIMIT 5;
SELECT * FROM service_applications LIMIT 5;
```

## Troubleshooting

### Error: "dblink extension does not exist"
**Solution**: Enable dblink extension:
```sql
CREATE EXTENSION IF NOT EXISTS dblink;
```

### Error: "relation does not exist"
**Solution**: Ensure Flyway migrations have run to create all tables in `smart_citizen`

### Error: "password authentication failed"
**Solution**: Update connection string in migration script with correct credentials

### Error: "duplicate key value violates unique constraint"
**Solution**: This is handled by `ON CONFLICT DO NOTHING` - duplicates are skipped

### No data migrated
**Check**:
1. Does `smart_warehouse` have data?
2. Are citizens filtered by `mobile_number IS NOT NULL`?
3. Check migration logs for errors

## Rollback

If you need to clear migrated data:

```sql
-- Connect to smart_citizen
\c smart_citizen

-- Delete in reverse order (respecting foreign keys)
DELETE FROM application_status_history;
DELETE FROM service_applications;
DELETE FROM schemes;
DELETE FROM citizens;
```

## Notes

- Migration is **idempotent** - can be run multiple times safely
- Duplicates are skipped using `ON CONFLICT` clauses
- Only citizens with mobile numbers are migrated
- Application numbers must be unique (enforced by UNIQUE constraint)
- Status history is created automatically for migrated applications

