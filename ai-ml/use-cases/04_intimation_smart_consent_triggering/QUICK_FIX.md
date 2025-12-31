# Quick Fix Guide

## Issue 1: Database Schema Errors

If you see errors during schema creation:
```
ERROR: cannot determine type of empty array
ERROR: relation "intimation.user_preferences" does not exist
```

### Fix:

```bash
# Run the fix script
./scripts/fix_schema_errors.sh

# OR manually
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/fix_schema_errors.sql
```

Then verify:
```bash
python scripts/verify_database_setup.py
```

## Issue 2: Import Errors

If you see:
```
ModuleNotFoundError: No module named 'db_connector'
```

### Fix:

All scripts have been updated with correct import paths. If you still see this error:

1. Verify you're in the correct directory:
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
```

2. Verify virtual environment is activated:
```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

3. Verify shared utils exist:
```bash
ls -la ../../shared/utils/db_connector.py
```

4. Try running scripts again:
```bash
python scripts/verify_database_setup.py
```

## Complete Setup After Fixes

```bash
# 1. Fix schema errors (if any)
./scripts/fix_schema_errors.sh

# 2. Verify database setup
python scripts/verify_database_setup.py

# 3. Initialize templates
python scripts/init_message_templates.py

# 4. Initialize scheme config
python scripts/init_scheme_config.py

# 5. Test
python scripts/test_intake.py
```

