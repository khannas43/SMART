# Testing Guide - Auto Approval & Straight-through Processing

**Use Case ID:** AI-PLATFORM-06

## Prerequisites

1. **Virtual Environment**: Activate Python virtual environment
   ```bash
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   ```

2. **Database**: Ensure database schema is set up
   ```bash
   ./scripts/setup_database.sh
   python scripts/init_decision_config.py
   ```

3. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

4. **Test Data**: Ensure you have applications to test
   - Applications should be created via AI-PLATFORM-05
   - Or create test applications manually in `application.applications` table

## Running Tests

### End-to-End Decision Workflow Test

Test the complete decision evaluation workflow:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/06_auto_approval_straight_processing
python scripts/test_decision_workflow.py
```

This test will:
1. Find available applications from `application.applications` table
2. Evaluate each application using DecisionEngine
3. Show decision results (type, risk score, routing)
4. Display rule evaluation results
5. Display risk assessment details
6. Show routing actions taken

**Expected Output:**
```
================================================================================
Testing Decision Workflow - End-to-End
================================================================================

📋 Finding applications to evaluate...
   ✅ Found 5 application(s) to test

================================================================================
Test 1/5: Application ID 1
================================================================================
Family ID: 0009c028-cac7-4458-8b8c-03efdd1f2604
Scheme: CHIRANJEEVI
Status: submitted

✅ Decision Evaluation Complete!
   Decision ID: 1
   Decision Type: AUTO_APPROVE
   Decision Status: approved
   Risk Score: 0.2500
   Risk Band: LOW
   Reason: Low risk, rules passed, auto-approved

📊 Rule Evaluation:
   All Passed: True
   Passed: 6
   Failed: 0

🎯 Risk Assessment:
   Score: 0.2500
   Band: LOW
   Model: rule-based v1.0
   Top Factors:
     - Auto-submitted (verified data)

🚦 Routing:
   Action: payment_triggered
   Status: pending
   Message: Payment trigger created, awaiting processing
```

## Test Scenarios

### Scenario 1: Low Risk Auto-Approval
- **Application**: Low risk score (< 0.3), all rules pass
- **Expected**: AUTO_APPROVE decision, payment trigger created

### Scenario 2: Medium Risk Officer Review
- **Application**: Medium risk score (0.3-0.7), rules pass
- **Expected**: ROUTE_TO_OFFICER decision, added to worklist

### Scenario 3: High Risk Fraud Queue
- **Application**: High risk score (> 0.7), rules pass
- **Expected**: ROUTE_TO_FRAUD decision, added to fraud queue

### Scenario 4: Auto-Reject on Critical Failure
- **Application**: Critical rule failure (e.g., deceased flag, duplicate)
- **Expected**: AUTO_REJECT decision

### Scenario 5: Document Validation Failure
- **Application**: Missing mandatory documents
- **Expected**: ROUTE_TO_OFFICER with document requirement reason

## Manual Testing

### Test Decision Engine Directly

```python
from decision_engine import DecisionEngine

# Initialize
engine = DecisionEngine()
engine.connect()

try:
    # Evaluate application
    result = engine.evaluate_application(application_id=1)
    
    # Check results
    print(f"Success: {result['success']}")
    print(f"Decision: {result['decision']['decision_type']}")
    print(f"Risk Score: {result['risk_results']['risk_score']}")
    
finally:
    engine.disconnect()
```

### Test Rule Engine

```python
from engines.rule_engine import RuleEngine

engine = RuleEngine()
engine.connect()

try:
    result = engine.evaluate_rules(
        application_id=1,
        family_id='0009c028-cac7-4458-8b8c-03efdd1f2604',
        scheme_code='CHIRANJEEVI'
    )
    
    print(f"All Passed: {result['all_passed']}")
    print(f"Critical Failures: {result['critical_failures']}")
    
finally:
    engine.disconnect()
```

### Test Risk Scorer

```python
from models.risk_scorer import RiskScorer

scorer = RiskScorer()
scorer.connect()

try:
    result = scorer.calculate_risk_score(
        application_id=1,
        family_id='0009c028-cac7-4458-8b8c-03efdd1f2604',
        scheme_code='CHIRANJEEVI'
    )
    
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Top Factors: {result['top_factors']}")
    
finally:
    scorer.disconnect()
```

## Database Verification

### Check Decisions Created

```sql
SELECT 
    decision_id, application_id, scheme_code,
    decision_type, decision_status, risk_score, risk_band
FROM decision.decisions
ORDER BY decision_timestamp DESC
LIMIT 10;
```

### Check Rule Evaluations

```sql
SELECT 
    evaluation_id, decision_id, rule_category, rule_name,
    passed, severity, result_message
FROM decision.rule_evaluations
WHERE decision_id = 1
ORDER BY rule_category, rule_name;
```

### Check Risk Scores

```sql
SELECT 
    score_id, decision_id, overall_score, score_band,
    model_type, model_version
FROM decision.risk_scores
WHERE decision_id = 1;
```

### Check Payment Triggers

```sql
SELECT 
    trigger_id, decision_id, payment_status,
    payment_system, triggered_at
FROM decision.payment_triggers
WHERE decision_id = 1;
```

## Troubleshooting

### No Applications Found
- **Issue**: Test script reports "No applications found"
- **Solution**: 
  - Create applications via AI-PLATFORM-05
  - Or manually insert test data into `application.applications` table

### Database Connection Errors
- **Issue**: Connection failures
- **Solution**: 
  - Check database is running
  - Verify `config/db_config.yaml` has correct credentials
  - Run `python scripts/check_config.py` to verify connectivity

### Import Errors
- **Issue**: ModuleNotFoundError
- **Solution**:
  - Ensure virtual environment is activated
  - Install dependencies: `pip install -r requirements.txt`
  - Check Python path includes `src` directory

### Decision Always Routes to Officer
- **Issue**: All decisions go to officer review
- **Solution**:
  - Check risk scores (may all be medium/high)
  - Verify rule evaluation results (some rules may be failing)
  - Check decision configuration thresholds

## Next Steps

1. **Unit Tests**: Create unit tests for individual components
2. **Integration Tests**: Test with real department APIs
3. **Performance Tests**: Load testing with multiple applications
4. **ML Model Tests**: Test with trained risk scoring models

---

**Last Updated**: 2024-12-30

