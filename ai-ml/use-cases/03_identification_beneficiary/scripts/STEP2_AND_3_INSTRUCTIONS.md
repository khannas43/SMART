# Step 2 & 3: Update Python Code and Test

## ✅ Step 1 Completed
You've successfully run the migration script to extend `public.scheme_master` with eligibility fields.

---

## Step 2: Update Python Code

### Automated Updates

I've updated the following files automatically:

1. ✅ `src/evaluator_service.py` - Updated to use `scheme_code`
2. ✅ `src/rule_engine.py` - Updated to use `scheme_code`  
3. ✅ `src/ml_scorer.py` - Updated to use `scheme_code`

### Changes Made:

**Key Changes:**
- Changed queries from `eligibility.scheme_master` to `public.scheme_master`
- Changed `WHERE scheme_id = %s` to `WHERE scheme_code = %s`
- Changed `SELECT scheme_id` to `SELECT scheme_code`
- Updated INSERT queries to use `scheme_code` column
- Updated column references in result processing

**Files Updated:**
- `src/evaluator_service.py`:
  - `_get_active_schemes()` - Now queries `scheme_master` (public) and returns `scheme_code`
  - `_get_schemes_for_event()` - Updated to use `scheme_code` and `category` (not `scheme_category`)
  - `get_precomputed_results()` - Updated to use `scheme_code`
  - `generate_departmental_worklist()` - Updated to use `scheme_code`
  - `_save_evaluation_snapshot()` - Updated INSERT to use `scheme_code`

- `src/rule_engine.py`:
  - `load_scheme_rules()` - Changed to `WHERE scheme_code = %s`

- `src/ml_scorer.py`:
  - `load_model()` - Changed to `WHERE scheme_code = %s`

---

## Step 3: Test Updates

### Run Test Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/STEP3_TEST_UPDATES.py
```

### What the Test Checks:

1. ✅ **scheme_master columns** - Verifies `is_auto_id_enabled` and `scheme_type` exist
2. ✅ **scheme_code queries** - Tests querying schemes using `scheme_code`
3. ✅ **eligibility tables** - Verifies tables have `scheme_code` column
4. ✅ **No duplicate tables** - Ensures only `public.scheme_master` exists
5. ✅ **Foreign keys** - Verifies foreign keys use `scheme_code`

### Expected Output:

```
============================================================
STEP 3: Testing Python Code Updates
============================================================

============================================================
Test 1: Verify scheme_master has eligibility columns
============================================================
✅ Both columns exist:
   - is_auto_id_enabled: boolean (default: true)
   - scheme_type: character varying (default: None)

============================================================
Test 2: Query schemes using scheme_code
============================================================
✅ Found 5 schemes with auto-identification enabled:
   - OLD_AGE_PENSION: Old Age Pension (SOCIAL_SECURITY)
   ...

============================================================
Test 3: Verify eligibility tables use scheme_code
============================================================
✅ Found scheme_code in 4 tables:
   - candidate_lists
   - eligibility_snapshots
   - ml_model_registry
   - scheme_eligibility_rules

============================================================
Test 4: Verify no duplicate scheme_master
============================================================
✅ Only one scheme_master table exists: public.scheme_master

============================================================
Test 5: Verify foreign key constraints
============================================================
✅ Found 4 foreign keys to scheme_master:
   - eligibility.candidate_lists.scheme_code → public.scheme_master.scheme_code
   ...

============================================================
TEST SUMMARY
============================================================
✅ PASS: scheme_master columns
✅ PASS: scheme_code queries
✅ PASS: eligibility tables
✅ PASS: no duplicate tables
✅ PASS: foreign keys

Total: 5/5 tests passed

✅ All tests passed! Python code updates are working correctly.
```

---

## Manual Verification (Optional)

### Check in pgAdmin4:

```sql
-- 1. Verify scheme_master has new columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'scheme_master'
AND column_name IN ('is_auto_id_enabled', 'scheme_type');

-- 2. Check schemes with auto-identification enabled
SELECT scheme_code, scheme_name, category, is_auto_id_enabled, scheme_type
FROM scheme_master
WHERE status = 'active' AND is_auto_id_enabled = true
LIMIT 10;

-- 3. Verify eligibility tables use scheme_code
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'eligibility' 
AND column_name = 'scheme_code'
ORDER BY table_name;

-- 4. Check foreign keys
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
    AND ccu.table_name = 'scheme_master'
    AND tc.table_schema = 'eligibility';
```

---

## Next Steps After Testing

If all tests pass:

1. ✅ **Python code is updated** and ready to use
2. ✅ **Database schema is consolidated** 
3. ⏳ **Ready for testing** with actual data

If tests fail:

1. Review error messages
2. Check if migration script ran completely
3. Verify eligibility_schema.sql was executed
4. Check for any remaining `scheme_id` references in code

---

## Summary

- ✅ **Step 1**: Migration script executed (extended scheme_master)
- ✅ **Step 2**: Python code updated (using scheme_code)
- ✅ **Step 3**: Run test script to verify

**Status**: Ready to test!

