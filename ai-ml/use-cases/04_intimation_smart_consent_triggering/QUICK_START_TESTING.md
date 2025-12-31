# Quick Start: Database Setup & Testing

**Use Case ID:** AI-PLATFORM-04

## 🚀 Quick Start (5 Steps)

### Step 1: Setup Database Schema

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering

# Option A: Using script (recommended)
./scripts/setup_database.sh

# Option B: Manual (PgAdmin)
# Open PgAdmin → Execute SQL from: database/intimation_schema.sql
```

**Verify:**
```bash
python scripts/verify_database_setup.py
```

### Step 2: Initialize Data

```bash
# Initialize message templates
python scripts/init_message_templates.py

# Initialize scheme configurations
python scripts/init_scheme_config.py
```

### Step 3: Validate Configuration

```bash
python scripts/check_config.py
```

### Step 4: Test Intake Process

```bash
python scripts/test_intake.py
```

**Expected:** Campaign created with eligible candidates

### Step 5: Test End-to-End

```bash
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

**Expected:** Complete flow from intake → message → consent

---

## 📋 Database Setup Checklist

### Prerequisites Check

```sql
-- Run in PgAdmin or psql
-- 1. Check required schemas exist
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name IN ('eligibility', 'golden_record');

-- 2. Check scheme_master exists
SELECT COUNT(*) FROM public.scheme_master;

-- 3. Check eligible candidates exist
SELECT COUNT(*) FROM eligibility.eligibility_snapshots 
WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED';
```

### Setup Commands

```bash
# 1. Create schema
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/intimation_schema.sql

# 2. Initialize templates
python scripts/init_message_templates.py

# 3. Initialize scheme config
python scripts/init_scheme_config.py

# 4. Verify setup
python scripts/verify_database_setup.py
```

---

## 🧪 Testing Commands

### Basic Tests

```bash
# 1. Configuration validation
python scripts/check_config.py

# 2. Database verification
python scripts/verify_database_setup.py

# 3. Test intake
python scripts/test_intake.py

# 4. Test consent
python scripts/test_consent.py

# 5. Test message personalization
python scripts/test_message_personalization.py

# 6. End-to-end test
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 10
```

### Test with Specific Scheme

```bash
# Test for specific scheme
python scripts/test_intake.py  # Modify script to use different scheme_code
python scripts/test_end_to_end.py --scheme-code OLD_AGE_PENSION --limit 5
```

---

## 📊 Verify Database Setup

### Quick Verification

```sql
-- Check schema and tables
SELECT 
    'Schema' as type, 
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.schemata 
        WHERE schema_name = 'intimation'
    ) THEN '✅ EXISTS' ELSE '❌ MISSING' END as status

UNION ALL

SELECT 
    'Tables',
    COUNT(*)::text || ' tables'
FROM information_schema.tables 
WHERE table_schema = 'intimation'

UNION ALL

SELECT 
    'Templates',
    COUNT(*)::text || ' templates'
FROM intimation.message_templates

UNION ALL

SELECT 
    'Scheme Configs',
    COUNT(*)::text || ' configs'
FROM intimation.scheme_intimation_config;
```

### Detailed Verification

```bash
python scripts/verify_database_setup.py
```

---

## 🐛 Troubleshooting

### Issue: Schema Not Created

**Solution:**
```sql
-- Run as postgres user
psql -h 172.17.16.1 -p 5432 -U postgres -d smart_warehouse

GRANT USAGE ON SCHEMA intimation TO sameer;
GRANT CREATE ON SCHEMA intimation TO sameer;
ALTER SCHEMA intimation OWNER TO sameer;
```

### Issue: No Eligible Candidates

**Solution:**
```sql
-- Check if eligibility data exists
SELECT COUNT(*) FROM eligibility.eligibility_snapshots 
WHERE evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED';

-- If 0, run AI-PLATFORM-03 evaluation first
```

### Issue: Templates Not Found

**Solution:**
```bash
# Re-initialize templates
python scripts/init_message_templates.py

# Verify
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "
SELECT template_code, channel, language 
FROM intimation.message_templates;
"
```

---

## 📚 Detailed Documentation

- **Database Setup**: See [DATABASE_SETUP.md](DATABASE_SETUP.md)
- **Testing Guide**: See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Setup Guide**: See [SETUP.md](SETUP.md)
- **Technical Design**: See [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)

---

**Quick Reference Last Updated**: 2024-12-29

