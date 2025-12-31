# Database Setup Guide: Auto Intimation & Smart Consent Triggering

**Use Case ID:** AI-PLATFORM-04

## Overview

This guide provides step-by-step instructions for setting up the database schema for Auto Intimation & Smart Consent Triggering.

## Prerequisites

### 1. Database Access

- **Database**: `smart_warehouse`
- **Host**: `172.17.16.1` (or `localhost`)
- **Port**: `5432`
- **User**: `sameer` (with appropriate permissions)
- **Schema**: `intimation` (will be created)

### 2. Required Dependencies

- PostgreSQL 14+ installed and running
- User `sameer` has permissions to:
  - CREATE SCHEMA
  - CREATE TABLE
  - INSERT, UPDATE, DELETE data
  - CREATE INDEX, TRIGGER, FUNCTION

### 3. External Dependencies

The intimation schema depends on:
- ✅ `public.scheme_master` table (from AI-PLATFORM-02)
- ✅ `eligibility` schema (from AI-PLATFORM-03)
- ✅ `golden_record` schema (from AI-PLATFORM-01)

Ensure these exist before proceeding.

## Setup Steps

### Step 1: Verify Prerequisites

```sql
-- Connect to database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse

-- Check if required tables/schemas exist
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('eligibility', 'golden_record');

SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'scheme_master';
```

**Expected Output:**
```
 schema_name
-------------
 eligibility
 golden_record

 table_name
-------------
 scheme_master
```

### Step 2: Create Schema

**Option A: Using Setup Script (Recommended)**

```bash
# From WSL/Ubuntu terminal
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

**Option B: Manual Setup (PgAdmin or psql)**

```bash
# Using psql command line
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/intimation_schema.sql
```

**Option C: Manual Setup (SQL Script)**

```sql
-- Run in PgAdmin or psql
\i database/intimation_schema.sql
```

### Step 3: Verify Schema Creation

```sql
-- Check schema exists
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name = 'intimation';

-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'intimation'
ORDER BY table_name;

-- Expected: 10 tables
```

**Expected Tables:**
1. `campaigns`
2. `campaign_candidates`
3. `consent_records`
4. `consent_history`
5. `intimation_events`
6. `message_fatigue`
7. `message_logs`
8. `message_templates`
9. `scheme_intimation_config`
10. `user_preferences`

### Step 4: Verify Foreign Key Constraints

```sql
-- Check foreign keys to scheme_master
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'intimation'
  AND ccu.table_name = 'scheme_master';
```

**Expected:** Foreign keys from:
- `campaigns.scheme_code` → `scheme_master.scheme_code`
- `campaign_candidates.scheme_code` → `scheme_master.scheme_code`
- `consent_records.scheme_code` → `scheme_master.scheme_code`
- `scheme_intimation_config.scheme_code` → `scheme_master.scheme_code`

### Step 5: Verify Triggers

```sql
-- Check triggers
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'intimation'
ORDER BY event_object_table, trigger_name;
```

**Expected Triggers:**
- `update_campaigns_updated_at`
- `update_candidates_updated_at`
- `update_consent_updated_at`
- `update_preferences_updated_at`
- `log_consent_history_trigger`

### Step 6: Verify Functions

```sql
-- Check functions
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'intimation'
ORDER BY routine_name;
```

**Expected Functions:**
- `update_updated_at_column()`
- `log_consent_history()`

### Step 7: Initialize Data

```bash
# Initialize message templates
python scripts/init_message_templates.py

# Initialize scheme configuration
python scripts/init_scheme_config.py
```

### Step 8: Verify Initialization

```sql
-- Check message templates
SELECT template_code, channel, language, status
FROM intimation.message_templates
ORDER BY template_code;

-- Check scheme configuration
SELECT scheme_code, consent_type_required, auto_intimation_enabled
FROM intimation.scheme_intimation_config
ORDER BY scheme_code;
```

## Common Issues & Solutions

### Issue 1: Permission Denied

**Error:**
```
ERROR: permission denied for schema intimation
ERROR: must be owner of schema intimation
```

**Solution:**
```sql
-- Run as postgres superuser
psql -h 172.17.16.1 -p 5432 -U postgres -d smart_warehouse

-- Grant permissions
GRANT USAGE ON SCHEMA intimation TO sameer;
GRANT CREATE ON SCHEMA intimation TO sameer;
GRANT ALL PRIVILEGES ON SCHEMA intimation TO sameer;
ALTER SCHEMA intimation OWNER TO sameer;

-- Grant table permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA intimation TO sameer;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA intimation TO sameer;
```

### Issue 2: Schema Already Exists

**Error:**
```
NOTICE: schema "intimation" already exists, skipping
```

**Solution:**
This is fine - the schema already exists. The script will skip schema creation but create missing tables.

To start fresh (⚠️ **WARNING: Deletes all data**):
```sql
-- Drop schema (as postgres user)
DROP SCHEMA intimation CASCADE;

-- Re-run schema script
\i database/intimation_schema.sql
```

### Issue 3: Foreign Key Constraint Violations

**Error:**
```
ERROR: insert or update on table "campaigns" violates foreign key constraint
DETAIL: Key (scheme_code)=(CHIRANJEEVI) is not present in table "scheme_master".
```

**Solution:**
Ensure `public.scheme_master` has the required schemes:
```sql
-- Check schemes
SELECT scheme_code, scheme_name, status
FROM public.scheme_master
WHERE status = 'active';

-- Insert missing scheme if needed
INSERT INTO public.scheme_master (scheme_code, scheme_name, category, status)
VALUES ('CHIRANJEEVI', 'Mukhyamantri Chiranjeevi Yojana', 'HEALTH', 'active')
ON CONFLICT (scheme_code) DO UPDATE SET status = 'active';
```

### Issue 4: Missing Eligibility Schema

**Error:**
```
ERROR: relation "eligibility.eligibility_snapshots" does not exist
```

**Solution:**
Ensure AI-PLATFORM-03 schema is set up:
```bash
cd ../03_identification_beneficiary
./scripts/create_eligibility_schema.sh
```

## Verification Checklist

After setup, verify:

- [ ] Schema `intimation` exists
- [ ] All 10 tables created
- [ ] Foreign keys to `scheme_master` exist
- [ ] Triggers created (5 triggers)
- [ ] Functions created (2 functions)
- [ ] Message templates initialized (4+ templates)
- [ ] Scheme configuration initialized (12+ schemes)
- [ ] User `sameer` has all permissions
- [ ] Indexes created (check with `\d+ table_name`)

## Quick Verification Query

```sql
-- Comprehensive verification
SELECT 
    'Schema' as type, 
    COUNT(*) as count 
FROM information_schema.schemata 
WHERE schema_name = 'intimation'

UNION ALL

SELECT 
    'Tables', 
    COUNT(*) 
FROM information_schema.tables 
WHERE table_schema = 'intimation'

UNION ALL

SELECT 
    'Foreign Keys', 
    COUNT(*) 
FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' 
  AND table_schema = 'intimation'

UNION ALL

SELECT 
    'Triggers', 
    COUNT(*) 
FROM information_schema.triggers 
WHERE trigger_schema = 'intimation'

UNION ALL

SELECT 
    'Functions', 
    COUNT(*) 
FROM information_schema.routines 
WHERE routine_schema = 'intimation'

UNION ALL

SELECT 
    'Templates', 
    COUNT(*) 
FROM intimation.message_templates

UNION ALL

SELECT 
    'Scheme Configs', 
    COUNT(*) 
FROM intimation.scheme_intimation_config;
```

**Expected Output:**
```
   type    | count
-----------+-------
 Schema    |     1
 Tables    |    10
 Foreign Keys |   8+
 Triggers  |     5
 Functions |     2
 Templates |     4+
 Scheme Configs | 12+
```

## Next Steps

After database setup is complete:

1. ✅ Run configuration validation: `python scripts/check_config.py`
2. ✅ Test intake process: `python scripts/test_intake.py`
3. ✅ Test consent management: `python scripts/test_consent.py`
4. ✅ Run end-to-end test: `python scripts/test_end_to_end.py`

---

**Last Updated**: 2024-12-29  
**Status**: Ready for Setup

