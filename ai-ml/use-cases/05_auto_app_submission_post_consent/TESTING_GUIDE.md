# Testing Guide: Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05

## Prerequisites

1. **Install Python Dependencies**
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   pip install -r requirements.txt
   ```
   
   **Or use the full path to venv pip:**
   ```bash
   /mnt/c/Projects/SMART/ai-ml/.venv/bin/pip install -r requirements.txt
   ```

2. **Database Setup Complete**
   - Application schema created
   - Form schemas initialized
   - Submission modes configured

3. **Upstream Data Available**
   - Consent records from AI-PLATFORM-04
   - Eligibility snapshots from AI-PLATFORM-03
   - Golden Records from AI-PLATFORM-01
   - 360° Profiles from AI-PLATFORM-02

## Test Scripts

### 0. Activate Virtual Environment

**Important:** Make sure the virtual environment is activated before running any tests:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
```

### 1. Create Test Consent Records (If Needed)

If you don't have consent records, create test ones:

```bash
python scripts/create_test_consent.py
```

This script will:
- Find eligible families from AI-PLATFORM-03
- Create consent records for them
- Skip if consent already exists

### 2. Test Application Creation

Tests the orchestrator triggering on consent events:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/test_application_creation.py
```

**What it tests:**
- Consent verification
- Eligibility checking
- Duplicate prevention
- Application record creation

**Expected output:**
- Application created with status 'creating'
- Application ID returned

### 3. Test Form Mapping

Tests the form mapper service:

```bash
python scripts/test_form_mapping.py
```

**What it tests:**
- Loading Golden Record data
- Loading 360° Profile data
- Applying field mappings
- Storing mapped fields with source tracking

**Expected output:**
- Fields mapped from GR/360° sources
- Source tracking for each field
- Form data structure created

### 4. Test Validation

Tests the validation engine:

```bash
python scripts/test_validation.py
```

**What it tests:**
- Syntactic validation (type, length, format)
- Semantic validation (business rules)
- Completeness checks
- Pre-fraud checks (if enabled)

**Expected output:**
- Validation results (errors, warnings)
- Application status updated based on validation

### 5. End-to-End Test

Tests the complete workflow:

```bash
python scripts/test_end_to_end.py
```

**What it tests:**
- Complete workflow from consent to submission
- All services working together
- Submission mode handling

**Expected output:**
- Application created
- Fields mapped
- Validation performed
- Submission handled (auto/review/assisted)

## Test Scenarios

### Scenario 1: Auto Submission (Low-Risk Scheme)

1. Ensure consent exists for CHIRANJEEVI scheme
2. Run `test_end_to_end.py`
3. Application should be auto-submitted if validation passes

### Scenario 2: Review Mode (Default)

1. Ensure consent exists for any scheme (except CHIRANJEEVI)
2. Run `test_end_to_end.py`
3. Application should be stored as 'pending_review'

### Scenario 3: Missing Data

1. Create application with incomplete data
2. Run validation
3. Should flag missing mandatory fields

## Troubleshooting

### No Consent Records Found

**Error**: "No consent records found"

**Solution**: Run AI-PLATFORM-04 intake and consent tests first:
```bash
cd ../04_intimation_smart_consent_triggering
python scripts/test_intake.py
python scripts/test_consent.py
```

### No Eligibility Snapshots

**Error**: "No eligibility snapshot found"

**Solution**: Run AI-PLATFORM-03 batch evaluation:
```bash
cd ../03_identification_beneficiary
python scripts/test_batch_evaluation.py --test batch-all --limit 50
```

### Mapping Errors

**Error**: "Error mapping field"

**Solution**: 
- Check if Golden Records exist for family
- Check if 360° Profiles exist
- Verify field mappings are configured in database

### Validation Errors

**Error**: Multiple validation errors

**Solution**:
- Check if required fields are present in GR/360°
- Verify form schema matches data structure
- Check validation rules configuration

---

**For detailed component testing, run individual test scripts in order.**

