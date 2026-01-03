# How to Run Data Migration (Option 1: Automatic via Flyway)

This guide explains how to start the citizen-service so Flyway automatically runs the data migration.

## Prerequisites

1. ✅ **Enable dblink extension** in smart_citizen database (REQUIRED):
   ```sql
   -- Connect to smart_citizen database
   psql -h localhost -U sameer -d smart_citizen
   
   -- Enable dblink extension
   CREATE EXTENSION IF NOT EXISTS dblink;
   
   -- Verify it's enabled
   \dx dblink
   ```

2. ✅ **Ensure smart_warehouse has data**:
   ```sql
   -- Connect to smart_warehouse
   psql -h localhost -U sameer -d smart_warehouse
   
   -- Check data counts
   SELECT COUNT(*) FROM citizens;
   SELECT COUNT(*) FROM schemes;
   SELECT COUNT(*) FROM applications;
   ```

3. ✅ **Ensure PostgreSQL is running**:
   ```powershell
   # Windows PowerShell
   Get-Service -Name "*postgresql*"
   ```

## Step-by-Step Instructions

### Step 1: Navigate to Service Directory

**Windows PowerShell:**
```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
```

**WSL/Linux:**
```bash
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service
```

### Step 2: Enable dblink Extension (One-time setup)

**Option A: Via psql command line**
```powershell
# Windows PowerShell
$env:PGPASSWORD='anjali143'
psql -h localhost -U sameer -d smart_citizen -c "CREATE EXTENSION IF NOT EXISTS dblink;"
```

**Option B: Via pgAdmin4**
1. Open pgAdmin4
2. Connect to PostgreSQL server
3. Expand `smart_citizen` database
4. Right-click on "Extensions" → "Create" → "Extension"
5. Select `dblink` from the dropdown
6. Click "Save"

**Option C: Via SQL file**
```sql
-- Create file: enable_dblink.sql
CREATE EXTENSION IF NOT EXISTS dblink;

-- Execute
psql -h localhost -U sameer -d smart_citizen -f enable_dblink.sql
```

### Step 3: Start the Citizen Service

**Windows PowerShell:**
```powershell
# Navigate to service directory
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service

# Start the service (Flyway will run migrations automatically)
mvn clean spring-boot:run
```

**WSL/Linux:**
```bash
# Navigate to service directory
cd /mnt/c/Projects/SMART/portals/citizen/backend/services/citizen-service

# Start the service
mvn clean spring-boot:run
```

### Step 4: Watch for Migration Execution

When the service starts, you'll see Flyway migration logs:

```
2025-01-01 10:00:00 - Flyway Community Edition 9.22.3 by Redgate
2025-01-01 10:00:00 - Database: jdbc:postgresql://localhost:5432/smart_citizen
2025-01-01 10:00:00 - Successfully validated 11 migrations
2025-01-01 10:00:00 - Current version of schema "public": 10
2025-01-01 10:00:01 - Migrating schema "public" to version "11 - migrate data from warehouse"
2025-01-01 10:00:05 - Successfully applied 1 migration to schema "public"
```

### Step 5: Verify Migration Success

After the service starts, check the logs for:
- ✅ "Successfully applied 1 migration"
- ✅ Migration summary showing data counts

Or verify manually:
```sql
-- Connect to smart_citizen
psql -h localhost -U sameer -d smart_citizen

-- Check counts
SELECT COUNT(*) as citizens FROM citizens;
SELECT COUNT(*) as schemes FROM schemes;
SELECT COUNT(*) as applications FROM service_applications;
SELECT COUNT(*) as history FROM application_status_history;
```

## What Happens During Startup

1. **Spring Boot starts** → Connects to `smart_citizen` database
2. **Flyway initializes** → Checks migration version
3. **Detects V11 migration** → Executes `V11__migrate_data_from_warehouse.sql`
4. **Migration runs** → Copies data from `smart_warehouse` to `smart_citizen`
5. **Service continues** → Application starts normally

## Troubleshooting

### Error: "extension dblink does not exist"
**Solution**: Enable dblink extension (see Step 2)

### Error: "password authentication failed for user sameer"
**Solution**: Update connection string in migration script or use environment variables

### Error: "relation smart_warehouse.citizens does not exist"
**Solution**: 
- Check if `smart_warehouse` database exists
- Verify database name in dblink connection string
- Ensure you're connecting to the correct PostgreSQL instance

### Migration runs but no data appears
**Check**:
1. Does `smart_warehouse` have data? (see Prerequisites)
2. Are citizens filtered out? (only those with mobile numbers are migrated)
3. Check application logs for errors

### Service fails to start after migration
**Solution**: 
- Check PostgreSQL logs
- Verify all tables exist in `smart_citizen`
- Check Flyway migration history: `SELECT * FROM flyway_schema_history;`

## Alternative: Run Migration Manually First

If you prefer to run the migration separately before starting the service:

```powershell
# Enable dblink
$env:PGPASSWORD='anjali143'
psql -h localhost -U sameer -d smart_citizen -c "CREATE EXTENSION IF NOT EXISTS dblink;"

# Run migration script manually
psql -h localhost -U sameer -d smart_citizen -f src/main/resources/db/migration/V11__migrate_data_from_warehouse.sql

# Then start service (Flyway will skip V11 as it's already applied)
mvn clean spring-boot:run
```

## Quick Start Command

**All-in-one PowerShell command:**
```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
$env:PGPASSWORD='anjali143'
psql -h localhost -U sameer -d smart_citizen -c "CREATE EXTENSION IF NOT EXISTS dblink;"
mvn clean spring-boot:run
```

## Expected Output

When migration runs successfully, you should see:

```
NOTICE: ========================================
NOTICE: Migration Summary
NOTICE: ========================================
NOTICE: Citizens migrated: 100000
NOTICE: Schemes migrated: 12
NOTICE: Applications migrated: 50000
NOTICE: Status history entries: 50000
NOTICE: ========================================
```

Then the service will continue starting normally.

