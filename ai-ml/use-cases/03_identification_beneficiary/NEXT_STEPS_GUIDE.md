# Next Steps Guide: Auto Identification of Beneficiaries
## Use Case: AI-PLATFORM-03

This guide walks you through the next steps for:
1. ✅ Training ML models for schemes
2. ✅ Creating eligibility rules via the rule management interface
3. ✅ Running batch evaluations
4. ✅ Testing the full evaluation pipeline

---

## Prerequisites

Before starting, ensure you have:

1. ✅ Database setup complete (`eligibility` schema in `smart_warehouse`)
2. ✅ Schemes loaded in `public.scheme_master` with `is_auto_id_enabled = true`
3. ✅ Training data available (Golden Records + 360° Profiles from AI-PLATFORM-01 and AI-PLATFORM-02)
4. ✅ MLflow UI running at `http://127.0.0.1:5000`
5. ✅ Python venv activated: `source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate`

---

## Step 1: Load Sample Eligibility Rules

Create eligibility rules for your schemes:

```bash
cd ai-ml/use-cases/03_identification_beneficiary
python scripts/load_sample_rules.py
```

This will create rules for:
- `CHIRANJEEVI` (Health Insurance)
- `OLD_AGE_PENSION`
- `DISABILITY_PENSION`
- `GRAMIN_AWAS` (Housing)
- `SC_ST_SCHOLARSHIP`
- `KISAN_CREDIT`

**Verify rules loaded:**
```bash
# In pgAdmin4 or psql:
SELECT scheme_code, rule_name, rule_type, rule_operator, rule_value
FROM eligibility.scheme_eligibility_rules
WHERE effective_to IS NULL
ORDER BY scheme_code, priority DESC;
```

---

## Step 2: Train ML Models

### 2.1 Check Available Schemes and Data

```bash
python scripts/test_train_models.py --check-only
```

This checks:
- MLflow connectivity
- Available schemes
- Training data availability for each scheme

### 2.2 Train Model for a Specific Scheme

```bash
# Train for CHIRANJEEVI scheme
python scripts/test_train_models.py --scheme-code CHIRANJEEVI

# Train for all available schemes
python scripts/test_train_models.py --all
```

**What happens:**
1. Loads training data from `smart_warehouse.golden_records`, `profile_360`, `benefit_events`, `application_events`
2. Prepares features (demographics, income, education, etc.)
3. Trains XGBoost classifier
4. Logs metrics to MLflow
5. Saves model to MLflow Model Registry
6. Records model metadata in `eligibility.ml_model_registry`

**View trained models in MLflow UI:**
- Open: `http://127.0.0.1:5000`
- Experiment: `smart/identification_beneficiary`
- Registered Models: `EligibilityScorer_<SCHEME_CODE>`

**Verify model registration:**
```bash
# Check in database
SELECT scheme_code, model_version, mlflow_run_id, training_samples_count, 
       training_metrics->>'roc_auc' as roc_auc
FROM eligibility.ml_model_registry
WHERE is_active = true
ORDER BY deployed_at DESC;
```

---

## Step 3: Test Rule Management

Test CRUD operations for eligibility rules:

```bash
# Test all operations (create, update, delete, snapshot)
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test all

# Test only rule creation
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test create

# Test only snapshot creation
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test snapshot
```

**Create rules programmatically:**
```python
from src.rule_manager import RuleManager

manager = RuleManager()

# Create a rule
rule = manager.create_rule(
    scheme_code='CHIRANJEEVI',
    rule_name='Age Requirement',
    rule_type='AGE',
    rule_expression='age >= 0',
    rule_operator='>=',
    rule_value='0',
    is_mandatory=True,
    priority=10,
    created_by='admin'
)

# Update rule (creates new version)
updated = manager.update_rule(
    rule_id=rule['rule_id'],
    rule_value='18',
    updated_by='admin'
)

# Create snapshot
snapshot_id = manager.create_rule_set_snapshot(
    scheme_code='CHIRANJEEVI',
    snapshot_version='v2.0',
    snapshot_name='Production Rules',
    created_by='admin'
)

manager.close()
```

---

## Step 4: Run Batch Evaluation

### 4.1 Test Single Family Evaluation

```bash
python scripts/test_batch_evaluation.py --test single-family
```

### 4.2 Test Batch Evaluation (All Schemes)

```bash
# Evaluate 10 families for all schemes
python scripts/test_batch_evaluation.py --test batch-all --limit 10

# Evaluate 50 families for specific scheme
python scripts/test_batch_evaluation.py --test batch-scheme --scheme-code CHIRANJEEVI --limit 50
```

### 4.3 Generate Departmental Worklist

```bash
python scripts/test_batch_evaluation.py --test worklist --scheme-code CHIRANJEEVI
```

**What happens:**
1. Loads family data from Golden Records and 360° Profiles
2. Evaluates eligibility using Rule Engine + ML Scorer
3. Creates eligibility snapshots in `eligibility.eligibility_snapshots`
4. Generates candidate lists with priority ranking
5. Saves worklists in `eligibility.candidate_lists`

**Verify results:**
```sql
-- Check eligibility snapshots
SELECT scheme_code, evaluation_status, COUNT(*) as count,
       AVG(final_eligibility_score) as avg_score
FROM eligibility.eligibility_snapshots
WHERE snapshot_date >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY scheme_code, evaluation_status
ORDER BY scheme_code;

-- Check candidate lists
SELECT scheme_code, list_type, COUNT(*) as candidate_count
FROM eligibility.candidate_lists
WHERE is_active = true
    AND generated_at >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY scheme_code, list_type
ORDER BY scheme_code;
```

---

## Step 5: End-to-End Pipeline Test

Run the complete pipeline test:

```bash
# Full pipeline test (checks, loads rules, evaluates, verifies)
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50

# Skip rule loading (if rules already exist)
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50 --skip-rules

# Skip evaluation (just check prerequisites and verify existing results)
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --skip-eval
```

**This test:**
1. ✅ Checks prerequisites (schemes, rules, models, data)
2. ✅ Verifies/loads eligibility rules
3. ✅ Runs batch evaluation
4. ✅ Generates candidate lists
5. ✅ Verifies results in database

---

## Quick Reference: Common Commands

### Load Rules
```bash
python scripts/load_sample_rules.py
```

### Train Models
```bash
# Check data availability
python scripts/test_train_models.py --check-only

# Train single scheme
python scripts/test_train_models.py --scheme-code CHIRANJEEVI

# Train all schemes
python scripts/test_train_models.py --all
```

### Test Rule Management
```bash
python scripts/test_rule_management.py --scheme-code CHIRANJEEVI --test all
```

### Run Evaluation
```bash
# Batch evaluation
python scripts/test_batch_evaluation.py --test batch-all --limit 50

# Generate worklist
python scripts/test_batch_evaluation.py --test worklist --scheme-code CHIRANJEEVI
```

### Full Pipeline
```bash
python scripts/test_end_to_end.py --scheme-code CHIRANJEEVI --limit 50
```

---

## Troubleshooting

### Issue: "No training data available"

**Solution:**
- Ensure AI-PLATFORM-01 (Golden Records) and AI-PLATFORM-02 (360° Profiles) are complete
- Check if `smart_warehouse.golden_records` has data
- Check if `smart_warehouse.benefit_events` or `smart_warehouse.application_events` have records for the scheme

```sql
-- Check data availability
SELECT COUNT(*) as families
FROM smart_warehouse.golden_records
WHERE status = 'active' AND family_id IS NOT NULL;

-- Check scheme-specific data
SELECT COUNT(DISTINCT be.gr_id) as beneficiaries
FROM smart_warehouse.benefit_events be
INNER JOIN public.scheme_master sm ON be.scheme_id = sm.scheme_id
WHERE sm.scheme_code = 'CHIRANJEEVI';
```

### Issue: "MLflow connection failed"

**Solution:**
- Start MLflow UI: `mlflow ui --port 5000`
- Verify MLflow is accessible: `curl http://127.0.0.1:5000`

### Issue: "No rules found for scheme"

**Solution:**
- Load rules: `python scripts/load_sample_rules.py`
- Or create rules manually using `rule_manager.py`

### Issue: "Insufficient training data: X samples (minimum: 100)"

**Solution:**
- Use `--min-samples` to lower threshold: `python scripts/test_train_models.py --scheme-code CHIRANJEEVI --min-samples 50`
- Or generate more synthetic data (see AI-PLATFORM-02 setup)

---

## Next Steps After Testing

Once all tests pass:

1. **Production Deployment:**
   - Set up scheduled batch evaluations (weekly/monthly)
   - Configure event-driven evaluation triggers
   - Set up monitoring for evaluation jobs

2. **Model Management:**
   - Promote models to production in MLflow: `is_production = true`
   - Set up model retraining pipeline
   - Monitor model performance and drift

3. **Rule Management UI:**
   - Implement frontend for rule CRUD operations (see `docs/RULE_MANAGEMENT_FRONTEND.md`)
   - Set up approval workflow for rule changes
   - Configure rule versioning and rollback

4. **API Integration:**
   - Deploy Spring Boot REST APIs (see `spring_boot/` directory)
   - Integrate with frontend portals
   - Set up API authentication and authorization

---

## Summary Checklist

- [ ] Load sample eligibility rules
- [ ] Train ML models for schemes
- [ ] Test rule management (create/update/delete)
- [ ] Run batch evaluation
- [ ] Generate candidate lists
- [ ] Verify results in database
- [ ] Run end-to-end pipeline test
- [ ] Review MLflow experiments and models
- [ ] Verify data quality and coverage

---

## Support

For issues or questions:
1. Check logs in terminal output
2. Verify database connectivity
3. Check MLflow UI for training issues
4. Review `TECHNICAL_DESIGN.md` for architecture details
5. Check `FIX_PERMISSIONS.md` for database permission issues

---

**Good luck! 🚀**

