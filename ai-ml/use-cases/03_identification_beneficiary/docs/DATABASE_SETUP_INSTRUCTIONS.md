# Database Setup Instructions: smart_warehouse

**Use Case ID:** AI-PLATFORM-03  
**Database**: `smart_warehouse` (shared with AI-PLATFORM-02)  
**Schema**: `eligibility`

---

## ✅ Consolidated Architecture

All AI/ML use cases use the **same `smart_warehouse` database** with different schemas:

- **Database**: `smart_warehouse`
- **Schema `public`**: AI-PLATFORM-02 (360° Profiles) tables
- **Schema `eligibility`**: AI-PLATFORM-03 (Auto Identification) tables

---

## Setup Steps

### Step 1: Verify/Create Database

The `smart_warehouse` database should already exist from AI-PLATFORM-02 setup.

**Check in pgAdmin4**:
```sql
-- Connect to postgres database
SELECT datname FROM pg_database WHERE datname = 'smart_warehouse';
```

**If doesn't exist, create it**:
```sql
CREATE DATABASE smart_warehouse;
```

### Step 2: Create Eligibility Schema

**In pgAdmin4** (connected to `smart_warehouse` database):

1. Open file: `database/eligibility_schema.sql`
2. Execute the entire file
3. This creates the `eligibility` schema with all tables

### Step 3: Create Versioning Extensions (Optional)

**In pgAdmin4** (connected to `smart_warehouse` database):

1. Open file: `database/eligibility_schema_versioning.sql`
2. Execute the entire file
3. This adds versioning tables and functions

### Step 4: Load Initial Schemes

**In pgAdmin4** (connected to `smart_warehouse` database):

1. Open file: `scripts/load_initial_schemes.sql`
2. Execute to load sample scheme data

---

## Verification

### Check Schema Exists

```sql
-- Connect to smart_warehouse database
SELECT schema_name 
FROM information_schema.schemata 
WHERE catalog_name = 'smart_warehouse'
ORDER BY schema_name;

-- Should show:
-- - public (or smart_warehouse) - for 360° Profiles
-- - eligibility - for Auto Identification
```

### Check Tables

```sql
-- Check eligibility tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'eligibility' 
ORDER BY table_name;

-- Should show:
-- - scheme_master
-- - scheme_eligibility_rules
-- - eligibility_snapshots
-- - candidate_lists
-- - ml_model_registry
-- - etc.
```

### Check Schemes Loaded

```sql
SELECT * FROM eligibility.scheme_master;
```

---

## Command Line Setup (Alternative)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
export PGPASSWORD='anjali143'

# Create schema in smart_warehouse
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql

# Create versioning extensions
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema_versioning.sql

# Load initial schemes
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/load_initial_schemes.sql

unset PGPASSWORD
```

---

## Database Structure

```
smart_warehouse (database)
│
├── public schema (or smart_warehouse schema)
│   └── AI-PLATFORM-02 tables:
│       ├── golden_records
│       ├── gr_relationships
│       ├── profile_360
│       ├── benefit_events
│       ├── application_events
│       └── ...
│
└── eligibility schema
    └── AI-PLATFORM-03 tables:
        ├── scheme_master
        ├── scheme_eligibility_rules
        ├── eligibility_snapshots
        ├── candidate_lists
        ├── ml_model_registry
        └── ...
```

---

## Benefits of Consolidation

1. ✅ **Single Database**: One database to backup, monitor, manage
2. ✅ **Shared Connections**: Reuse database connections
3. ✅ **Data Co-location**: Related data in one place
4. ✅ **Cross-Schema Queries**: Can join across schemas when needed
5. ✅ **Consistent Configuration**: Single database configuration

---

## Configuration

**`config/db_config.yaml`**:
```yaml
database:
  host: 172.17.16.1
  port: 5432
  name: smart_warehouse  # Consolidated database
  user: sameer
  password: anjali143
  schema: eligibility  # Schema within smart_warehouse
```

---

**Status**: ✅ All setup instructions updated for `smart_warehouse` database.

