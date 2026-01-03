# Database Cleanup Instructions

## Problem

The database already contains tables (like `schemes`) that conflict with Flyway migrations. Flyway expects to manage all schema changes, so existing tables cause conflicts.

## Solution: Clean the Database

You have two options:

### Option 1: Complete Cleanup (Recommended for Development)

Drop and recreate the entire public schema:

```sql
-- Connect to PostgreSQL
psql -U sameer -d smart_citizen

-- Or using Windows command line:
psql -U sameer -d smart_citizen

-- Then run:
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO sameer;
GRANT ALL ON SCHEMA public TO public;
```

### Option 2: Drop Only Conflicting Tables

If you want to keep some data, drop only the conflicting tables:

```sql
-- Connect to PostgreSQL
psql -U sameer -d smart_citizen

-- List existing tables
\dt

-- Drop conflicting tables (adjust list based on what exists)
DROP TABLE IF EXISTS schemes CASCADE;
DROP TABLE IF EXISTS citizens CASCADE;
DROP TABLE IF EXISTS service_applications CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS application_status_history CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;

-- Also drop Flyway's schema history if it exists
DROP TABLE IF EXISTS flyway_schema_history CASCADE;
```

### Option 3: Quick Script (Windows PowerShell)

Run this from the service directory:

```powershell
# Connect and clean database
$env:PGPASSWORD='anjali143'
psql -U sameer -d smart_citizen -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sameer; GRANT ALL ON SCHEMA public TO public;"
```

## After Cleanup

Once the database is cleaned:

1. Run the Spring Boot application:
   ```bash
   mvn spring-boot:run
   ```

2. Flyway will automatically:
   - Create all tables from migrations
   - Create the `flyway_schema_history` table
   - Track all applied migrations

3. The service should start successfully!

## Prevention

In the future, always let Flyway manage schema changes. Don't create tables manually in the database that Flyway migrations will create.

