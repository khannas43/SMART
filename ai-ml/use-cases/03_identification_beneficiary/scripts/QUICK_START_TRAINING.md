# Quick Start: NLP Model Training

**Purpose:** Quick guide to start training the NLP criteria extraction model  
**Status:** ✅ Ready to Train

---

## Prerequisites Check

Run the setup check:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_training_setup.py
```

**Expected:** All checks should pass ✓

---

## Step 1: Start MLflow UI (Optional but Recommended)

```bash
# In a separate terminal
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

**Access MLflow:** http://localhost:5000

---

## Step 2: Start Training

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/train_nlp_model.py
```

---

## Training Details

### Configuration

- **Base Model:** `roberta-base`
- **Training Epochs:** 10
- **Batch Size:** 16
- **Learning Rate:** 2e-5
- **Training Data:** 202 schemes
- **Validation Data:** 43 schemes
- **Test Data:** 44 schemes

### Expected Training Time

- **CPU:** 2-4 hours
- **GPU (if available):** 30-60 minutes

### Expected Output

```
============================================================
NLP Criteria Extraction Model Training
============================================================
Base Model: roberta-base
Training Epochs: 10
Batch Size: 16
Learning Rate: 2e-5
============================================================

[1/5] Loading tokenizer...
✓ Tokenizer loaded: roberta-base

[2/5] Preparing datasets...
✓ Train: 202 examples
✓ Val: 43 examples
✓ Test: 44 examples

[3/5] Initializing model...
✓ Model initialized

[4/5] Setting up training arguments...
✓ Training arguments configured

[5/5] Creating trainer...
✓ Trainer created

============================================================
Starting Training...
============================================================
```

---

## Monitoring Training

### MLflow UI

1. Open http://localhost:5000
2. Select experiment: `nlp_criteria_extraction`
3. View metrics, logs, and model artifacts

### Training Logs

Watch for:
- Loss decreasing over epochs
- Rule type accuracy increasing
- Operator accuracy increasing
- F1 score improving

---

## After Training

### Model Location

```
models/nlp_criteria_extractor/best_model/
```

### Next Steps

1. **Evaluate Model:** Check test set metrics
2. **Register Model:** Model automatically registered in MLflow
3. **Integration:** Proceed to API development (see `NLP_CRITERIA_EXTRACTION_IMPLEMENTATION_PLAN.md`)

---

## Troubleshooting

### Issue: Out of Memory

**Solution:** Reduce batch size in `config/nlp_model_config.yaml`:
```yaml
training:
  batch_size: 8  # Reduce from 16
```

### Issue: Training Too Slow

**Solution:** 
- Use GPU if available
- Reduce number of epochs
- Reduce max_length

### Issue: Low Accuracy

**Solution:**
- Check training data quality
- Increase training epochs
- Adjust learning rate

---

**Last Updated:** 2024-12-30

