# Testing Guide - AI-PLATFORM-08

**Use Case ID:** AI-PLATFORM-08  
**Name:** Eligibility Checker & Recommendations

## 1. Database Verification

### Check Database Setup
```bash
cd ai-ml/use-cases/08_eligibility_checker_recommendation
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_config.py
```

**Expected Output:**
- ✅ Schema 'eligibility_checker' exists
- ✅ Found 8 tables
- ✅ All external database connections working

### Verify Sample Data
```bash
python scripts/create_sample_data.py
```

**Creates:**
- 15 eligibility checks
- Multiple scheme eligibility results
- 5 recommendation sets

## 2. Workflow Testing

### Test Complete Workflow
```bash
python scripts/test_eligibility_checker.py
```

**Tests:**
1. Questionnaire retrieval
2. Guest user eligibility check
3. Logged-in user eligibility check
4. Recommendations retrieval

**Expected Output:**
- ✅ Questionnaire retrieved with questions
- ✅ Guest check complete with results
- ✅ Logged-in check complete (if family_id available)
- ✅ Recommendations retrieved

## 3. Frontend Viewer Testing

### Start Web Viewer
```bash
cd ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

### Access Eligibility Checker Viewer
Open browser: **http://localhost:5001/ai08**

**What to Check:**
- ✅ Statistics cards display correctly
- ✅ Recent eligibility checks table shows data
- ✅ Top recommendations display with scores
- ✅ Scheme eligibility results show details
- ✅ Status badges are color-coded correctly
- ✅ Refresh button works

## 4. API Testing (Manual)

### Test Eligibility Check API
```bash
# Guest user check
curl -X POST http://localhost:8080/eligibility/check \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_session_001",
    "checkType": "FULL_CHECK",
    "checkMode": "WEB",
    "questionnaireResponses": {
      "age": 65,
      "gender": "Male",
      "district": "Jaipur",
      "income_band": "Below 5000",
      "category": "General"
    },
    "language": "en"
  }'
```

### Test Recommendations API
```bash
curl "http://localhost:8080/eligibility/recommendations?family_id=<uuid>&refresh=false&language=en"
```

### Test Questionnaire API
```bash
curl "http://localhost:8080/eligibility/questionnaire?template_name=default_guest_questionnaire"
```

## 5. Database Query Testing

### Check Recent Checks
```sql
SELECT check_id, user_type, check_type, total_schemes_checked, 
       eligible_count, possible_eligible_count, not_eligible_count,
       check_timestamp
FROM eligibility_checker.eligibility_checks
ORDER BY check_timestamp DESC
LIMIT 10;
```

### Check Top Recommendations
```sql
SELECT ser.scheme_code, ser.scheme_name, ser.eligibility_status,
       ser.eligibility_score, ser.priority_score, ser.recommendation_rank
FROM eligibility_checker.scheme_eligibility_results ser
WHERE ser.recommendation_rank IS NOT NULL
  AND ser.recommendation_rank <= 5
ORDER BY ser.recommendation_rank
LIMIT 20;
```

### Check Recommendation Sets
```sql
SELECT recommendation_id, family_id, total_schemes, top_recommendations_count,
       generated_at, expires_at, is_active
FROM eligibility_checker.recommendation_sets
WHERE is_active = TRUE
ORDER BY generated_at DESC;
```

## 6. Integration Testing

### Test with Real Family ID
1. Get a family_id from golden_records:
```sql
SELECT DISTINCT family_id FROM golden_records.beneficiaries LIMIT 1;
```

2. Test logged-in user check:
```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))
from services.eligibility_orchestrator import EligibilityOrchestrator
orchestrator = EligibilityOrchestrator()
orchestrator.connect()
result = orchestrator.check_and_recommend(family_id='<family_id>')
print(result)
orchestrator.disconnect()
"
```

## 7. Expected Results

### Guest User Check
- User type: GUEST
- Is approximate: TRUE
- Results based on questionnaire responses
- Lower confidence levels

### Logged-in User Check
- User type: LOGGED_IN
- Is approximate: FALSE
- Results from eligibility engine (AI-PLATFORM-03)
- Higher confidence levels
- Recommendations generated

### Recommendations
- Top 5 schemes ranked by priority score
- Includes eligibility status, scores, explanations
- Next steps provided
- Cached for 30 days

## Troubleshooting

### Issue: No schemes found
**Solution:** Verify scheme_master has active schemes

### Issue: Eligibility engine not working
**Solution:** Check AI-PLATFORM-03 is properly set up

### Issue: Sample data not showing
**Solution:** Run `create_sample_data.py` again

### Issue: Viewer not accessible
**Solution:** Check web viewer is running on port 5001

---

**Last Updated:** 2024-12-30

