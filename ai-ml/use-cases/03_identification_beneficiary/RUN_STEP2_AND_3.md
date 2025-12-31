# Run Step 2 & 3: Python Code Updates and Testing

## ✅ Step 1 Completed
You've successfully executed the migration script in pgAdmin4.

---

## Step 2: Python Code Updates

**Status**: ✅ **COMPLETED AUTOMATICALLY**

All Python files have been updated to use `scheme_code` instead of `scheme_id` for eligibility schema queries.

**Files Updated:**
- ✅ `src/evaluator_service.py`
- ✅ `src/rule_engine.py`
- ✅ `src/ml_scorer.py`
- ✅ `src/prioritizer.py`
- ✅ `src/train_eligibility_model.py`
- ✅ `src/rule_manager.py`

---

## Step 3: Run Test Script

### Option 1: Direct Python Command

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/STEP3_TEST_UPDATES.py
```

### Option 2: Use Convenience Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
./scripts/RUN_STEP2_AND_3.sh
```

---

## What the Test Verifies

1. ✅ `scheme_master` table has `is_auto_id_enabled` and `scheme_type` columns
2. ✅ Can query schemes using `scheme_code` from `public.scheme_master`
3. ✅ Eligibility tables (`eligibility` schema) have `scheme_code` column
4. ✅ No duplicate `scheme_master` table (only `public.scheme_master` exists)
5. ✅ Foreign keys properly reference `scheme_master(scheme_code)`

---

## Expected Result

```
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

## If Tests Fail

1. **Check error messages** - The test script will show what failed
2. **Verify migration** - Ensure `extend_scheme_master.sql` ran completely
3. **Check schema** - Ensure `eligibility_schema.sql` was executed
4. **Database connection** - Verify database credentials in `config/db_config.yaml`

---

## Summary

- ✅ **Step 1**: Migration script executed (extended `public.scheme_master`)
- ✅ **Step 2**: Python code updated (using `scheme_code`)
- ⏳ **Step 3**: Run test script to verify everything works

**Next**: Run the test script to complete Step 3!

