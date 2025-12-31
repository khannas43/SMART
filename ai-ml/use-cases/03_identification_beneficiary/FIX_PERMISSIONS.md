# Fix Schema Permissions

## Issue

**Error**: `permission denied for schema eligibility`

The `eligibility` schema exists but user `sameer` doesn't have CREATE permissions on it.

---

## Solution

### Option 1: Grant Permissions via pgAdmin4 (Recommended)

**Run this SQL in pgAdmin4** (as `postgres` superuser or schema owner):

```sql
-- Connect to smart_warehouse database as postgres user
-- Then run:

-- Grant usage and create on schema
GRANT USAGE ON SCHEMA eligibility TO sameer;
GRANT CREATE ON SCHEMA eligibility TO sameer;

-- Grant all privileges on all tables (existing and future)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON TABLES TO sameer;

-- Grant all privileges on all sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON SEQUENCES TO sameer;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT EXECUTE ON FUNCTIONS TO sameer;

-- Make sameer the owner (optional, but ensures full control)
ALTER SCHEMA eligibility OWNER TO sameer;
```

### Option 2: Using Script (Requires postgres password)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# Edit the script to set postgres password
# Then run:
./scripts/fix_schema_permissions.sh
```

### Option 3: Manual psql (as postgres user)

```bash
export PGPASSWORD='postgres'  # Your postgres password
psql -h 172.17.16.1 -p 5432 -U postgres -d smart_warehouse -f scripts/grant_schema_permissions.sql
unset PGPASSWORD
```

---

## After Fixing Permissions

Run the schema creation script again:

```bash
./scripts/create_eligibility_schema.sh
```

---

## Quick Fix (One Command in pgAdmin4)

**Copy and paste this entire block in pgAdmin4** (connected as `postgres` user to `smart_warehouse`):

```sql
GRANT USAGE ON SCHEMA eligibility TO sameer;
GRANT CREATE ON SCHEMA eligibility TO sameer;
ALTER SCHEMA eligibility OWNER TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON TABLES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON SEQUENCES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT EXECUTE ON FUNCTIONS TO sameer;
```

Then run `create_eligibility_schema.sh` again.

