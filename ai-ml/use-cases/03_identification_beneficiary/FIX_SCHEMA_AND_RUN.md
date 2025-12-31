# Quick Fix: Database Schema & Code Issues

## Issue
The `rule_change_history` table in the database still has `scheme_id` column instead of `scheme_code`.

## Quick Fix (Choose One Method)

### Method 1: Run SQL Script in pgAdmin4 (Recommended)

1. Open pgAdmin4
2. Connect to `smart_warehouse` database
3. Open Query Tool
4. Copy and paste the contents of `scripts/fix_rule_change_history.sql`
5. Execute the query

### Method 2: Run Fix Script from Terminal

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
./scripts/fix_database_schema.sh
```

### Method 3: Manual SQL Fix (If methods above don't work)

```sql
-- Connect to smart_warehouse database as sameer user
-- Then run:

ALTER TABLE eligibility.rule_change_history 
DROP COLUMN IF EXISTS scheme_id CASCADE;

ALTER TABLE eligibility.rule_change_history 
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

ALTER TABLE eligibility.rule_change_history
ADD CONSTRAINT rule_change_history_scheme_code_fkey
FOREIGN KEY (scheme_code) REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_rule_change_history_scheme_code 
ON eligibility.rule_change_history(scheme_code);
```

## After Fixing Schema

1. **Load rules:**
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   python scripts/load_sample_rules.py
   ```

2. **Verify rules loaded:**
   ```sql
   SELECT scheme_code, rule_name, rule_type, rule_operator, rule_value
   FROM eligibility.scheme_eligibility_rules
   WHERE effective_to IS NULL
   ORDER BY scheme_code, priority DESC;
   ```

## What Was Fixed

1. ✅ Fixed `rule_change_history` table schema (added migration script)
2. ✅ Fixed all `.close()` calls to use `.disconnect()` for DBConnector objects
3. ✅ Created fix script for easy execution

## Files Modified

- `src/rule_manager.py` - Fixed `.close()` to `.disconnect()`
- `src/train_eligibility_model.py` - Fixed `.close()` to `.disconnect()`
- `src/prioritizer.py` - Fixed `.close()` to `.disconnect()`
- `src/ml_scorer.py` - Fixed `.close()` to `.disconnect()`
- `src/rule_engine.py` - Fixed `.close()` to `.disconnect()`
- `src/evaluator_service.py` - Fixed `.close()` to `.disconnect()`

## New Files Created

- `scripts/fix_rule_change_history.sql` - SQL migration script
- `scripts/fix_database_schema.sh` - Bash script to run the fix

---

**After running the fix, try loading rules again!**

