# ✅ Step 2 & 3: Complete Instructions

## ✅ Step 1 Completed
You've successfully run the migration script in pgAdmin4.

---

## Step 2: Python Code Updates

**Status**: ✅ **AUTOMATICALLY COMPLETED**

I've updated all Python files to use `scheme_code` instead of `scheme_id`:

- ✅ `src/evaluator_service.py`
- ✅ `src/rule_engine.py`
- ✅ `src/ml_scorer.py`
- ✅ `src/prioritizer.py`
- ✅ `src/train_eligibility_model.py`
- ✅ `src/rule_manager.py`

**Also updated:**
- ✅ `database/eligibility_schema.sql`
- ✅ `database/eligibility_schema_versioning.sql`

---

## Step 3: Run Test Script

### Command to Run:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/STEP3_TEST_UPDATES.py
```

### Or Use Convenience Script:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
chmod +x scripts/RUN_STEP2_AND_3.sh
./scripts/RUN_STEP2_AND_3.sh
```

---

## What the Test Checks:

1. ✅ **scheme_master columns** - Verifies `is_auto_id_enabled` and `scheme_type` exist
2. ✅ **scheme_code queries** - Tests querying schemes using `scheme_code`
3. ✅ **eligibility tables** - Verifies tables have `scheme_code` column
4. ✅ **No duplicate tables** - Ensures only `public.scheme_master` exists
5. ✅ **Foreign keys** - Verifies foreign keys use `scheme_code`

---

## Expected Output:

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
✅ Found X schemes with auto-identification enabled:
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
✅ Found X foreign keys to scheme_master:
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

## Next Steps:

1. ✅ Run the test script (Step 3)
2. ⏳ If tests pass, you're ready to use the updated code
3. ⏳ If tests fail, review error messages and fix any remaining issues

---

**Status**: Step 2 complete ✅. Ready for Step 3 testing!

