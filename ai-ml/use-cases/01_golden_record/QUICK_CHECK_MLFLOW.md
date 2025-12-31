# Quick Guide: Checking MLflow Runs

## 🚀 Quick Start (30 seconds)

1. **Start MLflow UI** (if not running):
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml
   source .venv/bin/activate
   mlflow ui --host 0.0.0.0 --port 5000
   ```

2. **Open Browser:**
   ```
   http://127.0.0.1:5000
   ```

3. **Navigate to Experiment:**
   - Click: "smart/golden_record/baseline_v1"
   - Or use direct link: http://127.0.0.1:5000/#/experiments/2

---

## ✅ Checking Your Failed Run

### Step 1: Find the Run

**In MLflow UI:**
1. Open experiment: `smart/golden_record/baseline_v1`
2. Look for run: `deduplication_training_20251226_181502`
3. Status badge shows: ❌ **Failed**

### Step 2: View Error Details

**Click on the run**, then:

1. **Overview Tab:**
   - See status: Failed
   - Start time and duration
   - Run ID

2. **Parameters Tab:**
   - What config was used
   - Model type, thresholds

3. **Metrics Tab:**
   - Any metrics logged before failure
   - (May be empty if it failed early)

4. **Error Information:**
   - Scroll down to see error message
   - Look for: `relation "citizens" does not exist`
   - This is the issue we fixed!

---

## 🔧 Fixing the Failed Run

### Option 1: Delete It (Clean Up)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python scripts/manage_mlflow_runs.py --delete-failed --confirm
```

### Option 2: Keep It (Learning)

- Leave it as a reference
- Shows the error we encountered
- Demonstrates problem-solving process

### Option 3: Run New Training

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python src/train.py
```

This will create a **new successful run** with:
- ✅ All data loaded
- ✅ Training completed
- ✅ Metrics logged

---

## 📊 Playing Around with MLflow

### Experiment 1: Compare Runs

1. **In MLflow UI:**
   - Select 2-3 runs (checkboxes)
   - Click "Compare" button
   - See side-by-side comparison

2. **What to Compare:**
   - Parameters: Different thresholds?
   - Metrics: Which performed better?
   - Timing: Which was faster?

### Experiment 2: Modify and Retrain

1. **Edit Config:**
   ```bash
   # Edit: config/model_config.yaml
   # Change: auto_merge: 0.95 → 0.90
   ```

2. **Run Training:**
   ```bash
   python src/train.py
   ```

3. **Compare in MLflow:**
   - New run appears
   - Compare with previous runs
   - See how threshold affects metrics

### Experiment 3: Export Run Data

```bash
python scripts/manage_mlflow_runs.py --export runs_export.csv
```

Opens CSV with all run data for analysis in Excel/Python.

---

## 🎯 Understanding Run Status

| Status | Meaning | What to Do |
|--------|---------|------------|
| ✅ **FINISHED** | Training completed successfully | ✅ Good! Check metrics |
| ❌ **FAILED** | Error occurred during training | Check error message, fix issue, retry |
| 🏃 **RUNNING** | Currently training | Wait for completion |

---

## 📈 Key Metrics to Watch

### For Successful Runs:

1. **Precision** (Target: >95%)
   - % of merged records that are correct
   - Higher = fewer false merges

2. **Recall** (Target: >95%)
   - % of duplicates found
   - Higher = finding more duplicates

3. **F1 Score** (Target: >95%)
   - Balanced measure
   - Best single metric to optimize

4. **Training Pairs**
   - Number of record pairs used for training
   - More = better (usually)

---

## 🛠️ Management Commands

### List All Runs

```bash
python scripts/manage_mlflow_runs.py --list
```

### List Only Failed Runs

```bash
python scripts/manage_mlflow_runs.py --list --status FAILED
```

### Compare Successful Runs

```bash
python scripts/manage_mlflow_runs.py --compare
```

### Delete Failed Runs

```bash
# Preview (safe)
python scripts/manage_mlflow_runs.py --delete-failed

# Actually delete
python scripts/manage_mlflow_runs.py --delete-failed --confirm
```

---

## 💡 Tips for Exploration

1. **Use Filters:**
   - In MLflow UI, filter by status
   - Filter by date range
   - Search by run name

2. **Tag Runs:**
   - Click on run → Add tags
   - Example: `baseline`, `experiment_v2`, `production`
   - Makes filtering easier

3. **Bookmark Best Run:**
   - Add tag: `best_model`
   - Easy to find later
   - Use for deployment decisions

4. **Download Artifacts:**
   - Click run → Artifacts tab
   - Download model files
   - Download evaluation reports

---

## ❓ Troubleshooting

### MLflow UI Not Loading?

**Check if running:**
```bash
pgrep -f "mlflow ui"
```

**Restart:**
```bash
pkill -f "mlflow ui"
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000 &
```

### Can't See Latest Run?

1. **Refresh browser** (Ctrl+F5)
2. **Check experiment name** matches
3. **Wait a few seconds** (takes time to appear)

### Run Stuck in "Running" Status?

**Check if process is actually running:**
```bash
ps aux | grep train.py
```

**Kill stuck process:**
```bash
pkill -f train.py
```

**Manually mark as failed in MLflow UI** (or wait for timeout)

---

## 🎓 Learning Path

### Beginner:
1. ✅ View failed run (this one)
2. ✅ Run new training
3. ✅ View successful run
4. ✅ Compare two runs

### Intermediate:
1. Modify parameters and retrain
2. Export run data
3. Analyze metrics trends
4. Tag and organize runs

### Advanced:
1. Use MLflow API programmatically
2. Set up model registry
3. Integrate with CI/CD
4. A/B testing workflows

---

## 📚 Further Reading

- **Detailed Guide**: `docs/MLFLOW_GUIDE.md`
- **Explaining to Others**: `docs/EXPLAIN_TO_OTHERS.md`
- **Use Case Spec**: `docs/USE_CASE_SPEC.md`

---

**Quick Links:**
- MLflow UI: http://127.0.0.1:5000
- Experiment: http://127.0.0.1:5000/#/experiments/2
- Failed Run: http://127.0.0.1:5000/#/experiments/2/runs/[RUN_ID]

