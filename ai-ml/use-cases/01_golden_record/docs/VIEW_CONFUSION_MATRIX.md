# How to View Confusion Matrix Metrics

## Overview

The confusion matrix metrics (True Positives, True Negatives, False Positives, False Negatives) are logged to MLflow during model training. Here are multiple ways to view them.

---

## Method 1: Using MLflow UI (Easiest)

### Step 1: Open MLflow UI
```
http://127.0.0.1:5000
```

### Step 2: Navigate to Experiment
1. Click on experiment: `smart/golden_record/baseline_v1`
2. Or direct link: http://127.0.0.1:5000/#/experiments/2

### Step 3: View Metrics
1. Click on any **successful** run (status: ✅ FINISHED)
2. Go to **Metrics** tab
3. Scroll down to find:
   - `true_positives`
   - `false_positives`
   - `true_negatives`
   - `false_negatives`
   - `precision`
   - `recall`
   - `f1_score`

### Step 4: View Confusion Matrix (if logged)
1. Go to **Artifacts** tab
2. Look for confusion matrix plots or CSV files
3. Download if available

---

## Method 2: Using Command-Line Script (Recommended)

### Install Dependencies
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
```

### View Latest Run
```bash
python scripts/view_confusion_matrix.py --latest
```

**Output:**
```
📊 Run: deduplication_training_20251226_181502
   Run ID: abc123...
   
   Confusion Matrix:
   ----------------------------------------------------------------------------
                    | Predicted: Match      | Predicted: Non-Match
   ----------------------------------------------------------------------------
   Actual: Match    | TP =   950           | FN =    50
   Actual: Non-Match| FP =    25           | TN =  4975
   ----------------------------------------------------------------------------

   Totals:
   - Actual Positives (matches):     1000
   - Actual Negatives (non-matches): 5000
   - Predicted Positives (merged):   975
   - Predicted Negatives (rejected): 5025
   - Total Predictions:              6000

   Performance Metrics:
   - Precision: 0.9744 (97.44%)
   - Recall:    0.9500 (95.00%)
   - F1 Score:  0.9621

   Interpretation:
   ✅ True Positives (950): Correctly identified duplicate pairs
   ❌ False Positives (25): Incorrectly merged different people (Type I error)
   ✅ True Negatives (4,975): Correctly identified non-duplicate pairs
   ❌ False Negatives (50): Missed duplicate pairs (Type II error)
```

### View All Runs
```bash
python scripts/view_confusion_matrix.py --all
```

### Compare Multiple Runs
```bash
python scripts/view_confusion_matrix.py --all --compare
```

**Output:**
```
COMPARISON OF RUNS
================================================================================

Run Name                          TP      FP      TN      FN     Precision  Recall  F1
-----------------------------------------------------------------------
deduplication_training_20251226   950     25    4975     50      0.9744   0.9500  0.9621
deduplication_training_20251227   945     30    4970     55      0.9692   0.9450  0.9570

📈 Best Performers:
   Highest Precision: deduplication_training_20251226 (0.9744)
   Highest Recall: deduplication_training_20251226 (0.9500)
   Best F1 Score: deduplication_training_20251226 (0.9621)

⚠️  Error Analysis:
   Lowest False Positives: deduplication_training_20251226 (25)
   Lowest False Negatives: deduplication_training_20251226 (50)
```

### Export to CSV
```bash
python scripts/view_confusion_matrix.py --all --export confusion_metrics.csv
```

### View Specific Run
```bash
python scripts/view_confusion_matrix.py --run-id <RUN_ID>
```

---

## Method 3: Using Python Directly

### Quick Script

Create a file `check_metrics.py`:

```python
import mlflow

mlflow.set_tracking_uri('http://127.0.0.1:5000')
experiment = mlflow.get_experiment_by_name('smart/golden_record/baseline_v1')

# Get latest run
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="status = 'FINISHED'",
    order_by=["start_time DESC"],
    max_results=1
)

if not runs.empty:
    run = mlflow.get_run(runs.iloc[0]['run_id'])
    metrics = run.data.metrics
    
    print("Confusion Matrix Metrics:")
    print(f"  True Positives:  {metrics.get('true_positives', 'N/A')}")
    print(f"  False Positives: {metrics.get('false_positives', 'N/A')}")
    print(f"  True Negatives:  {metrics.get('true_negatives', 'N/A')}")
    print(f"  False Negatives: {metrics.get('false_negatives', 'N/A')}")
    print(f"\nPerformance:")
    print(f"  Precision: {metrics.get('precision', 'N/A')}")
    print(f"  Recall:    {metrics.get('recall', 'N/A')}")
    print(f"  F1 Score:  {metrics.get('f1_score', 'N/A')}")
else:
    print("No successful runs found")
```

Run:
```bash
python check_metrics.py
```

---

## Method 4: From Training Script Output

When you run training, the confusion matrix metrics are printed:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python src/train.py
```

**Look for this section in the output:**
```
EVALUATION RESULTS
============================================================
precision: 0.9744
recall: 0.9500
f1_score: 0.9621
true_positives: 950
false_positives: 25
true_negatives: 4975
false_negatives: 50
```

---

## Understanding the Metrics

### Confusion Matrix Layout

```
                    Predicted
                 Match    Non-Match
Actual Match     TP       FN
Actual Non-Match FP       TN
```

### What Each Metric Means

1. **True Positives (TP)**
   - ✅ Correctly identified duplicate pairs
   - Records that should be merged AND were merged
   - **Good!** This is what we want

2. **False Positives (FP)**
   - ❌ Incorrectly merged different people
   - Records that should NOT be merged but were merged
   - **Bad!** Type I error - merging different people
   - **Impact**: Could cause eligibility errors

3. **True Negatives (TN)**
   - ✅ Correctly identified non-duplicate pairs
   - Records that are different AND were correctly kept separate
   - **Good!** This is what we want

4. **False Negatives (FN)**
   - ❌ Missed duplicate pairs
   - Records that SHOULD be merged but were not
   - **Bad!** Type II error - missing duplicates
   - **Impact**: Duplicate records remain in system

### Derived Metrics

**Precision** = TP / (TP + FP)
- What % of merged pairs are correct?
- Higher = fewer false merges

**Recall** = TP / (TP + FN)
- What % of duplicates were found?
- Higher = fewer missed duplicates

**F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
- Balanced measure
- Best single metric to optimize

---

## Example Interpretation

### Example Run Results:
```
TP = 950  (95% of duplicates found and correctly merged)
FP = 25   (2.5% false merges - 25 different people incorrectly merged)
TN = 4975 (99.5% of non-duplicates correctly kept separate)
FN = 50   (5% of duplicates missed)
```

**What this means:**
- ✅ Model found 95% of duplicates (good recall)
- ✅ Only 2.5% false merges (good precision)
- ⚠️ 5% duplicates still missed (could improve recall)
- ✅ 99.5% correctly rejected non-duplicates (very good)

**Is this good?**
- Yes! Meeting our targets:
  - Precision: 97.44% > 95% target ✅
  - Recall: 95.00% = 95% target ✅
- Could improve:
  - Reduce FN (find more duplicates)
  - Reduce FP (fewer false merges)

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| View latest run | `python scripts/view_confusion_matrix.py --latest` |
| View all runs | `python scripts/view_confusion_matrix.py --all` |
| Compare runs | `python scripts/view_confusion_matrix.py --all --compare` |
| Export to CSV | `python scripts/view_confusion_matrix.py --all --export metrics.csv` |
| View specific run | `python scripts/view_confusion_matrix.py --run-id <ID>` |
| View in MLflow UI | Open http://127.0.0.1:5000 |

---

## Troubleshooting

### Issue: "No results found"

**Check:**
1. Is MLflow UI running? http://127.0.0.1:5000
2. Do you have any successful runs? (status = FINISHED)
3. Did training complete successfully?
4. Check experiment name: `smart/golden_record/baseline_v1`

**Solution:**
```bash
# Check if runs exist
python scripts/manage_mlflow_runs.py --list
```

### Issue: Metrics show "None" or "N/A"

**Possible causes:**
1. Run failed before evaluation
2. Metrics not logged (older runs)
3. Error in evaluation step

**Solution:**
- Check run status in MLflow UI
- Re-run training to generate new metrics
- Check training script logs for errors

### Issue: Script can't connect to MLflow

**Error:** `Connection refused` or `Failed to connect`

**Solution:**
```bash
# Start MLflow UI
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000 &

# Wait a few seconds, then retry
python scripts/view_confusion_matrix.py --latest
```

---

## Next Steps

1. **View Latest Metrics:**
   ```bash
   python scripts/view_confusion_matrix.py --latest
   ```

2. **Compare Different Runs:**
   ```bash
   python scripts/view_confusion_matrix.py --all --compare
   ```

3. **Export for Analysis:**
   ```bash
   python scripts/view_confusion_matrix.py --all --export metrics.csv
   ```

4. **Analyze Trends:**
   - Export multiple runs
   - Track TP, FP, FN over time
   - Identify best configurations

---

## Related Documentation

- **MLflow Guide**: `docs/MLFLOW_GUIDE.md`
- **Training Script**: `src/train.py`
- **Run Management**: `scripts/manage_mlflow_runs.py`

