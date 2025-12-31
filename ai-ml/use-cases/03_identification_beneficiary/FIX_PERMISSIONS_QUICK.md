# Quick Fix: Schema Permissions

## Problem
`permission denied for schema eligibility` - User `sameer` can't create tables in the schema.

## Quick Solution (pgAdmin4)

**1. Connect to `smart_warehouse` database as `postgres` user**

**2. Run this SQL:**

```sql
-- Grant all permissions to sameer on eligibility schema
GRANT USAGE ON SCHEMA eligibility TO sameer;
GRANT CREATE ON SCHEMA eligibility TO sameer;
ALTER SCHEMA eligibility OWNER TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON TABLES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON SEQUENCES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT EXECUTE ON FUNCTIONS TO sameer;
```

**3. Then run the schema creation script again:**

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
./scripts/create_eligibility_schema.sh
```

---

## Alternative: Drop and Recreate Schema

If you prefer to start fresh:

```sql
-- As postgres user in pgAdmin4:
DROP SCHEMA IF EXISTS eligibility CASCADE;
CREATE SCHEMA eligibility;
ALTER SCHEMA eligibility OWNER TO sameer;
GRANT ALL ON SCHEMA eligibility TO sameer;
```

Then run `create_eligibility_schema.sh` again.

