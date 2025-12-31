# MLflow Guide for Golden Record Deduplication

## Understanding MLflow Runs

### What is MLflow?

MLflow is an **experiment tracking and model management** tool. It helps us:
- Track different training runs
- Compare model performance
- Log parameters, metrics, and artifacts
- Reproduce experiments
- Deploy models

### Key Concepts

1. **Experiment**: A collection of related runs (e.g., "Golden Record Deduplication")
2. **Run**: A single execution of your training script
3. **Parameters**: Input settings (e.g., learning rate, batch size)
4. **Metrics**: Output measurements (e.g., accuracy, precision, recall)
5. **Artifacts**: Files (e.g., models, plots, data samples)

---

## Accessing MLflow UI

### Start MLflow UI

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

Then open browser: **http://127.0.0.1:5000**

---

## Understanding the Failed Run

### Run Name: `deduplication_training_20251226_181502`

**Status: Failed** ❌

### Why It Failed

The run failed because:
- ❌ The `citizens` table didn't exist in `smart_warehouse` database
- ❌ Training script couldn't load data
- ❌ Error: `relation "citizens" does not exist`

### What Was Fixed

✅ Created `citizens` table in `smart_warehouse`  
✅ Loaded 100,000 synthetic citizens  
✅ Data is now ready for training

---

## Checking MLflow Runs

### 1. View All Runs

**In MLflow UI:**
1. Go to: http://127.0.0.1:5000
2. Click on experiment: `smart/golden_record/baseline_v1`
3. See all runs listed with status (Running/Failed/Finished)

### 2. View Failed Run Details

**Click on the failed run** (`deduplication_training_20251226_181502`):

**Information you'll see:**
- **Status**: Failed ❌
- **Start Time**: When training started
- **Duration**: How long it ran before failing
- **Parameters**: Model configuration used
- **Metrics**: Any metrics logged before failure
- **Tags**: Metadata (run name, model type, etc.)
- **Artifacts**: Any files saved

### 3. Check Error Messages

**In the run details page:**
- Scroll down to see error traceback
- Look for the specific error message
- In this case: `relation "citizens" does not exist`

### 4. Compare Runs

**MLflow UI allows you to:**
- Select multiple runs (checkboxes)
- Compare parameters and metrics side-by-side
- See which configuration performed best

---

## Playing Around with MLflow

### Scenario 1: Start a New Training Run

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python src/train.py
```

**What to watch:**
- New run appears in MLflow UI (may take a few seconds)
- Status changes: `Running` → `Finished` (or `Failed`)
- Metrics update in real-time (refresh the page)

### Scenario 2: Modify Parameters and Retrain

**Edit:** `config/model_config.yaml`

```yaml
model:
  type: fellegi_sunter
  params:
    match_threshold: 0.95  # Try changing to 0.90 or 0.98
    blocking_fields: ["jan_aadhaar", "full_name"]
```

**Run training again:**
```bash
python src/train.py
```

**Compare in MLflow:**
- Two runs with different thresholds
- See which threshold gives better precision/recall
- Identify optimal configuration

### Scenario 3: Check Metrics Over Time

**In MLflow UI:**
1. Click on a successful run
2. Go to "Metrics" tab
3. See logged metrics:
   - `precision`: How many matches are correct
   - `recall`: How many duplicates were found
   - `f1_score`: Balanced measure
   - `training_pairs`: Number of pairs created
   - `match_pairs`: Number of true matches

### Scenario 4: Download Model Artifacts

**For successful runs:**
1. Click on run
2. Go to "Artifacts" tab
3. Download:
   - `model/`: Saved model files
   - `training_samples.csv`: Sample data used
   - `evaluation_report.json`: Performance report

### Scenario 5: View Training Visualizations

**If logged, you can see:**
- Confusion matrix plots
- ROC curves
- Training loss curves
- Feature importance charts

---

## Explaining to Others

### Quick 2-Minute Explanation

> **"MLflow is like a lab notebook for machine learning."**
> 
> When we train a model, MLflow automatically records:
> - **What we tried**: Parameters (learning rate, thresholds, etc.)
> - **How well it worked**: Metrics (accuracy, precision, recall)
> - **What we created**: Models and reports
> 
> This lets us:
> - Compare different approaches
> - Reproduce successful experiments
> - Track progress over time

### For Technical Team Members

**MLflow Components:**

1. **Tracking Server** (UI at http://127.0.0.1:5000)
   - Stores all run data
   - Provides web interface
   - Handles versioning

2. **Experiments**
   - Organize related runs
   - Example: `smart/golden_record/baseline_v1`
   - Can have multiple experiments for different use cases

3. **Runs**
   - One execution = one run
   - Each run has unique ID
   - Can be tagged for organization

4. **Model Registry** (Advanced)
   - Promote models through stages (Staging → Production)
   - Version control for production models
   - A/B testing capabilities

### For Business/Non-Technical Stakeholders

**Simple Analogy:**

> **"Think of MLflow like a fitness tracker for our AI models."**
> 
> Just like a fitness tracker records:
> - Steps walked (metrics)
> - Workout type (parameters)
> - Progress photos (artifacts)
> 
> MLflow records:
> - Model performance (metrics)
> - Training settings (parameters)
> - Model files (artifacts)

**Why It Matters:**

- **Transparency**: See exactly what we tried and what worked
- **Accountability**: Track model performance over time
- **Collaboration**: Team can see progress and contribute
- **Quality**: Catch issues early (like the failed run we just fixed)

### For Project Managers

**Key Metrics to Monitor:**

1. **Run Success Rate**: How many runs succeed vs. fail?
2. **Model Performance**: Are precision/recall improving?
3. **Training Time**: Is it getting faster with optimizations?
4. **Experiment Frequency**: Are we iterating quickly?

**Example Dashboard View:**
```
Experiment: Golden Record Deduplication
Total Runs: 5
Successful: 4 ✅
Failed: 1 ❌ (data issue - now fixed)
Best Model: Run #4 (Precision: 96%, Recall: 94%)
```

---

## Common Tasks

### Task 1: Delete Failed Run

**In MLflow UI:**
1. Find the run
2. Click checkbox to select
3. Click "Delete" button
4. Confirm deletion

**Or via API:**
```python
import mlflow
mlflow.delete_run(run_id="40489f80bfce4ec2911839b39cbc205e")
```

### Task 2: Rename a Run

**In MLflow UI:**
1. Click on run
2. Click "Edit" next to run name
3. Enter new name
4. Save

### Task 3: Tag Runs for Organization

**In MLflow UI:**
1. Click on run
2. Go to "Tags" section
3. Add tags like:
   - `model_version`: v1.0
   - `data_source`: synthetic
   - `status`: baseline

### Task 4: Export Run Data

**Download as CSV:**
1. Select runs (checkboxes)
2. Click "Compare"
3. Export to CSV

---

## Troubleshooting

### Issue: MLflow UI Not Loading

**Check:**
```bash
# Is MLflow running?
pgrep -f "mlflow ui"

# Check logs
tail -f /mnt/c/Projects/SMART/ai-ml/mlflow.log
```

**Restart:**
```bash
pkill -f "mlflow ui"
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000 &
```

### Issue: Run Shows as "Running" Forever

**Check if process is actually running:**
```bash
ps aux | grep train.py
```

**Kill stuck process:**
```bash
pkill -f train.py
```

**Manually mark run as failed in MLflow UI** (or it will timeout)

### Issue: Can't See Latest Run

**Refresh browser** (Ctrl+F5 for hard refresh)

**Check if experiment name matches:**
```python
import mlflow
print(mlflow.get_experiment_by_name("smart/golden_record/baseline_v1"))
```

---

## Next Steps

1. **Run Successful Training:**
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
   source ../../.venv/bin/activate
   python src/train.py
   ```

2. **Monitor in MLflow:**
   - Watch status change from Running → Finished
   - Check metrics when complete
   - Download model artifacts

3. **Experiment:**
   - Try different thresholds
   - Modify feature configurations
   - Compare results

4. **Share:**
   - Send MLflow UI link to team
   - Export reports
   - Document best configurations

---

## Quick Reference

| What | How |
|------|-----|
| **Start MLflow** | `mlflow ui --host 0.0.0.0 --port 5000` |
| **View UI** | http://127.0.0.1:5000 |
| **Run Training** | `python src/train.py` |
| **Check Run** | Click on run in MLflow UI |
| **Compare Runs** | Select multiple runs, click "Compare" |
| **Download Model** | Run → Artifacts → Download |

