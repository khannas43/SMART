# MLflow Models Guide: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03

---

## Overview

MLflow is used to track experiments and register models for eligibility scoring. Models are trained per scheme using XGBoost.

---

## MLflow Configuration

### Experiment Name
```
smart/identification_beneficiary
```

### Model Naming Convention
```
EligibilityScorer_{SCHEME_ID}
```

Example: `EligibilityScorer_SCHEME_001`

### Tracking URI
```
http://127.0.0.1:5000
```

---

## Viewing Models in MLflow UI

### 1. Start MLflow UI

```bash
# From WSL
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --port 5000

# Or if already running in background, check status
curl http://127.0.0.1:5000
```

### 2. Access MLflow UI

Open in browser:
```
http://127.0.0.1:5000
```

### 3. Find Experiments

1. Navigate to **Experiments** tab
2. Look for experiment: `smart/identification_beneficiary`
3. Click on experiment to see all training runs

### 4. View Model Details

In each run, you'll see:
- **Parameters**: Hyperparameters, scheme_id, model_type
- **Metrics**: Accuracy, precision, recall, F1, ROC-AUC, PR-AUC
- **Artifacts**: 
  - Model files (XGBoost model)
  - Feature importance (`feature_importance.json`)
  - SHAP plots (`shap_summary.png`)
  - Model description (`model_description.txt`)
- **Tags**: use_case, model_name, scheme_id

### 5. View Registered Models

1. Navigate to **Models** tab
2. Look for models with prefix: `EligibilityScorer_`
3. Click on model to see:
   - All versions
   - Current stage (Staging/Production/Archived)
   - Model metadata
   - Model description

---

## Check Models Programmatically

### Using Python Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_mlflow_models.py
```

This script will:
- ✅ List all experiments related to identification/eligibility
- ✅ Show registered models
- ✅ Display latest runs
- ✅ Check MLflow UI status

---

## Training a Model

### Prerequisites

1. **Database Setup**: Ensure eligibility schema is created
2. **Training Data**: Historical application/benefit data available
3. **Scheme Rules**: At least one scheme configured with rules

### Train Model for a Scheme

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Train model for a specific scheme
python src/train_eligibility_model.py --scheme_id SCHEME_001
```

### What Happens During Training

1. **Load Training Data**: 
   - Queries `smart_warehouse` database
   - Gets historical applications and benefits
   - Minimum 100 samples required

2. **Feature Engineering**:
   - Demographics (age, gender, caste)
   - Household composition
   - Income band (from 360° Profile)
   - Benefit history
   - Socio-economic facts

3. **Model Training**:
   - XGBoost classifier
   - Cross-validation (5 folds)
   - Early stopping
   - Hyperparameter tuning

4. **Evaluation**:
   - Test set metrics
   - Feature importance
   - SHAP explainability

5. **MLflow Logging**:
   - Parameters logged
   - Metrics logged
   - Model artifact saved
   - Model registered in registry

6. **Database Registration**:
   - Model metadata saved to `eligibility.ml_model_registry`
   - MLflow run ID stored
   - Feature list recorded

---

## Model Information Stored

### In MLflow

- **Experiment**: `smart/identification_beneficiary`
- **Run Name**: `{SCHEME_ID}_{TIMESTAMP}`
- **Registered Model**: `EligibilityScorer_{SCHEME_ID}`
- **Artifacts**: 
  - `model/` - XGBoost model files
  - `feature_importance.json` - Feature importance scores
  - `shap_summary.png` - SHAP summary plot
  - `model_description.txt` - Model description

### In Database (`eligibility.ml_model_registry`)

- `scheme_id` - Scheme this model is for
- `model_version` - Model version (auto-incremented)
- `model_path` - Path to model (MLflow URI: `models:/EligibilityScorer_SCHEME_001/1`)
- `mlflow_run_id` - MLflow run ID
- `training_samples_count` - Number of training samples
- `training_metrics` - JSON with accuracy, precision, recall, etc.
- `feature_list` - Array of feature names
- `feature_importance` - JSON with feature importance scores
- `is_active` - Whether model is active
- `is_production` - Whether model is in production

---

## Viewing Model Metrics

### In MLflow UI

1. Go to experiment: `smart/identification_beneficiary`
2. Click on a run
3. View **Metrics** tab:
   - `accuracy`
   - `precision`
   - `recall`
   - `f1_score`
   - `roc_auc`
   - `pr_auc`
   - `test_accuracy`
   - `test_precision`
   - etc.

### In Database

```sql
SELECT 
    scheme_id,
    model_version,
    mlflow_run_id,
    training_samples_count,
    training_metrics,
    feature_list,
    is_active,
    is_production,
    created_at
FROM eligibility.ml_model_registry
WHERE scheme_id = 'SCHEME_001'
ORDER BY created_at DESC;
```

---

## Loading Models for Inference

Models are automatically loaded by `ml_scorer.py`:

```python
from src.ml_scorer import MLEligibilityScorer

scorer = MLEligibilityScorer()
scorer.load_model('SCHEME_001')  # Loads from MLflow Model Registry
```

The scorer will:
1. Query `eligibility.ml_model_registry` for latest active model
2. Load model from MLflow using `models:/EligibilityScorer_SCHEME_001/1`
3. Cache model in memory for performance
4. Initialize SHAP explainer for explainability

---

## Current Status

### To Check if Models Exist

Run the check script:
```bash
python scripts/check_mlflow_models.py
```

### If No Models Found

Models need to be trained first. Steps:

1. **Ensure data exists**: Check `smart_warehouse` database has application/benefit data
2. **Configure schemes**: Ensure schemes are set up in `eligibility.scheme_master`
3. **Train model**: Run training script for each scheme
4. **Verify**: Check MLflow UI and database

---

## Example Workflow

### Step 1: Train Model

```bash
python src/train_eligibility_model.py --scheme_id SCHEME_001
```

### Step 2: Check MLflow UI

Open: http://127.0.0.1:5000
- Navigate to `smart/identification_beneficiary` experiment
- Find latest run for `SCHEME_001`
- View metrics and artifacts

### Step 3: Verify Model Registration

```sql
SELECT * FROM eligibility.ml_model_registry 
WHERE scheme_id = 'SCHEME_001';
```

### Step 4: Use Model for Inference

Models are automatically used by the evaluation service when available.

---

## Troubleshooting

### MLflow UI Not Accessible

```bash
# Start MLflow UI
mlflow ui --port 5000

# Check if running
curl http://127.0.0.1:5000
```

### No Models in MLflow

1. Check if training has been run
2. Verify experiment name matches: `smart/identification_beneficiary`
3. Check training script output for errors
4. Verify MLflow tracking URI: `http://127.0.0.1:5000`

### Model Not Loading

1. Check `eligibility.ml_model_registry` table
2. Verify model_path format: `models:/EligibilityScorer_SCHEME_001/1`
3. Check MLflow model registry for registered model
4. Verify model version exists in MLflow

---

**Last Updated**: 2024-12-27

