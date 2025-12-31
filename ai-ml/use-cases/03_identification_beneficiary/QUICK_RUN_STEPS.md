# Quick Run: Step 2 & 3

## ✅ Step 1 Completed
You've already run the migration script in pgAdmin4.

---

## Step 2: Python Code Updates

**Status**: ✅ **Already Done!**

I've automatically updated all Python files to use `scheme_code`:

- ✅ `src/evaluator_service.py` - Updated queries
- ✅ `src/rule_engine.py` - Updated to use `scheme_code`
- ✅ `src/ml_scorer.py` - Updated to use `scheme_code`
- ✅ `src/prioritizer.py` - Updated INSERT queries
- ✅ `src/train_eligibility_model.py` - Updated INSERT queries

---

## Step 3: Test Updates

### Run Test Script:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/STEP3_TEST_UPDATES.py
```

### Or Use Convenience Script:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
./scripts/RUN_STEP2_AND_3.sh
```

---

## What Tests Check:

1. ✅ `scheme_master` has `is_auto_id_enabled` and `scheme_type` columns
2. ✅ Can query schemes using `scheme_code`
3. ✅ Eligibility tables have `scheme_code` column
4. ✅ No duplicate `scheme_master` tables
5. ✅ Foreign keys use `scheme_code`

---

## Expected Result:

```
✅ All tests passed! Python code updates are working correctly.
```

---

## If Tests Fail:

1. Check error messages
2. Verify migration script completed
3. Ensure `eligibility_schema.sql` was executed
4. Check database connection

---

**Status**: Step 2 complete. Run Step 3 test script now!

