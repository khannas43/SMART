# Intake Process Fix

## Issue
The intake process was not finding any eligible candidates even though batch evaluations had been run.

## Root Cause
**Status Value Mismatch**: The intake query was looking for `evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'`, but the batch evaluation creates snapshots with statuses:
- `RULE_ELIGIBLE`
- `POSSIBLE_ELIGIBLE`

## Fix Applied
Updated the intake query in `campaign_manager.py` to use the correct status values:

**Before:**
```python
WHERE es.evaluation_status = 'POTENTIALLY_ELIGIBLE_IDENTIFIED'
```

**After:**
```python
WHERE es.evaluation_status IN ('RULE_ELIGIBLE', 'POSSIBLE_ELIGIBLE')
```

## Testing
After running batch evaluation, the intake process should now correctly identify eligible candidates.

### Test Steps:
1. Run batch evaluation (if not already done):
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   python scripts/test_batch_evaluation.py --test batch-all --limit 10
   ```

2. Run intake process:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/04_intimation_smart_consent_triggering
   python scripts/test_intake.py
   ```

3. Verify campaigns are created with eligible candidates.

## Note
If snapshots still don't appear, check:
- Whether snapshots were actually saved (batch evaluation showed 0 snapshots created)
- Whether the evaluation_status values match in the database
- Whether the evaluation_timestamp is within the last 7 days (intake query filters for recent evaluations)

