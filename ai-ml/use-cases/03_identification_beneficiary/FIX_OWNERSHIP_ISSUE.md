# Fix Table Ownership Issue

## Problem

Some tables exist but are owned by a different user (likely `postgres`), causing:
- `must be owner of table` errors
- Permission denied errors when trying to ALTER tables

---

## Solution: Clean Recreate (Recommended)

### Option 1: Using Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
./scripts/fix_ownership_and_recreate.sh
```

**Note**: This script requires `postgres` user password. Edit the script to set your postgres password, or use Option 2.

### Option 2: Manual in pgAdmin4 (Easiest)

**Run as `postgres` user:**

```sql
-- 1. Drop and recreate schema (clean slate)
DROP SCHEMA IF EXISTS eligibility CASCADE;
CREATE SCHEMA eligibility;
ALTER SCHEMA eligibility OWNER TO sameer;
GRANT ALL ON SCHEMA eligibility TO sameer;

-- 2. Run eligibility_schema.sql (as sameer user)
-- Switch to sameer user connection, then execute:
-- database/eligibility_schema.sql

-- 3. Run eligibility_schema_versioning.sql (as sameer user)
-- database/eligibility_schema_versioning.sql
```

### Option 3: Transfer Ownership Only (Keep Existing Tables)

If you want to keep existing data, just transfer ownership:

**Run as `postgres` user in pgAdmin4:**

```sql
-- Transfer schema ownership
ALTER SCHEMA eligibility OWNER TO sameer;

-- Transfer all tables (run for each table)
ALTER TABLE eligibility.scheme_eligibility_rules OWNER TO sameer;
ALTER TABLE eligibility.scheme_exclusion_rules OWNER TO sameer;
ALTER TABLE eligibility.eligibility_snapshots OWNER TO sameer;
ALTER TABLE eligibility.candidate_lists OWNER TO sameer;
ALTER TABLE eligibility.ml_model_registry OWNER TO sameer;
ALTER TABLE eligibility.evaluation_audit_log OWNER TO sameer;
ALTER TABLE eligibility.rule_change_history OWNER TO sameer;
ALTER TABLE eligibility.batch_evaluation_jobs OWNER TO sameer;
ALTER TABLE eligibility.consent_status OWNER TO sameer;
ALTER TABLE eligibility.data_quality_indicators OWNER TO sameer;
ALTER TABLE eligibility.rule_set_snapshots OWNER TO sameer;
ALTER TABLE eligibility.dataset_versions OWNER TO sameer;
ALTER TABLE eligibility.rule_change_detail OWNER TO sameer;

-- Grant all privileges
GRANT ALL ON ALL TABLES IN SCHEMA eligibility TO sameer;
GRANT ALL ON ALL SEQUENCES IN SCHEMA eligibility TO sameer;
```

Then run `create_eligibility_schema.sh` again.

---

## Quick Fix (pgAdmin4)

**1. Connect as `postgres` user to `smart_warehouse`**

**2. Run this to drop and recreate (clean slate):**

```sql
DROP SCHEMA IF EXISTS eligibility CASCADE;
CREATE SCHEMA eligibility;
ALTER SCHEMA eligibility OWNER TO sameer;
GRANT ALL ON SCHEMA eligibility TO sameer;
```

**3. Switch to `sameer` user connection**

**4. Execute `database/eligibility_schema.sql`**

**5. Execute `database/eligibility_schema_versioning.sql`**

---

## After Fixing

Run the test script:

```bash
python scripts/STEP3_TEST_UPDATES.py
```

All tests should pass!

