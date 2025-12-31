# Step 2: Update Python Code to Use scheme_code

**After running migration script (Step 1)**, update Python code to use `scheme_code` instead of `scheme_id` in database queries.

---

## Files to Update

The following files need updates:

1. `src/evaluator_service.py`
2. `src/rule_engine.py`
3. `src/ml_scorer.py`
4. `src/rule_manager.py`
5. `src/train_eligibility_model.py`
6. `src/prioritizer.py` (if needed)

---

## Changes Summary

### Key Changes:

1. **Query `public.scheme_master` instead of `eligibility.scheme_master`**
2. **Use `scheme_code` column instead of `scheme_id` in WHERE clauses**
3. **Return `scheme_code` instead of `scheme_id` from queries**
4. **Update INSERT queries to use `scheme_code` column**

### Note:
- Function parameters can still be called `scheme_id` (that's fine for variable names)
- Database columns must use `scheme_code` (not `scheme_id`)

---

## Manual Updates Required

Since this involves multiple files with different contexts, manual updates are recommended. See detailed changes below.

