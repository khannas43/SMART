# Action Plan: Complete Configuration

**Date**: 2024-12-30  
**Status**: In Progress  
**Goal**: Complete all configuration tasks that can be done without department API access

---

## ✅ Completed Actions

1. ✅ **Form Schema Enhancement** - Completed (12 schemas with 20 fields each)
2. ✅ **Configuration Scripts Created** - All scripts ready
3. ✅ **Documentation** - Configuration guides created

---

## 🚀 Execute Now (In WSL Terminal)

### Step 1: Run Field Mappings Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/create_field_mappings_template.py
```

**Expected Output**: Creates ~240 field mappings (20 mappings × 12 schemes)

---

### Step 2: Verify Configuration

```bash
python scripts/check_config.py
```

**Expected**: All checks pass ✅

---

### Step 3: View Configuration Summary

```bash
python scripts/view_mappings_and_schemas.py
```

**Expected**: Shows summary of mappings, schemas, submission modes, and connectors

---

### Or Run All at Once:

```bash
bash scripts/run_all_configurations.sh
```

---

## 📋 Configuration Checklist

After running scripts, verify:

### Field Mappings ✅
- [ ] Mappings created for all 12 active schemes
- [ ] Direct mappings (GR → form fields)
- [ ] Derived mappings (income_band → BPL status)
- [ ] Concatenated mappings (first_name + last_name → full_name)
- [ ] Scheme-specific mappings (NREGA job card, etc.)

**Verify**:
```sql
SELECT scheme_code, COUNT(*) as count
FROM application.scheme_field_mappings
WHERE is_active = true
GROUP BY scheme_code;
```

### Form Schemas ✅
- [ ] All 12 schemas enhanced with standard fields
- [ ] Validation rules added
- [ ] Mandatory fields defined

**Verify**:
```sql
SELECT scheme_code, jsonb_array_length(fields) as field_count
FROM application.scheme_form_schemas
WHERE is_active = true;
```

---

## 🔄 Next Steps (After Scripts Run)

### 1. Review and Customize Field Mappings

**Review mappings for each scheme:**
```sql
SELECT * FROM application.scheme_field_mappings
WHERE scheme_code = 'CHIRANJEEVI'
ORDER BY priority;
```

**Add scheme-specific custom mappings** as needed.

### 2. Customize Submission Modes

**Update per scheme requirements:**
```sql
-- For auto submission schemes
UPDATE application.submission_modes_config
SET default_mode = 'auto',
    allow_auto_submission = true,
    auto_submission_min_score = 0.8
WHERE scheme_code = 'CHIRANJEEVI';

-- For review mode schemes
UPDATE application.submission_modes_config
SET default_mode = 'review',
    require_citizen_review = true
WHERE scheme_code = 'OLD_AGE_PENSION';
```

### 3. Add Scheme-Specific Validation Rules

**Add business rules per scheme:**
```sql
UPDATE application.scheme_form_schemas
SET semantic_rules = jsonb_set(
    COALESCE(semantic_rules, '{}'::jsonb),
    '{age_validation}',
    '{
        "field": "age",
        "rule": "age >= 60",
        "message": "Age must be 60 or above for old age pension"
    }'::jsonb
)
WHERE scheme_code = 'OLD_AGE_PENSION';
```

---

## ⏳ Waiting For (Department API Information)

Once department API information is available:

### 1. Configure Department Connectors

```sql
UPDATE application.department_connectors
SET 
    endpoint_url = 'https://dept-api.rajasthan.gov.in/applications',
    auth_config = '{"api_key": "YOUR_KEY"}'::jsonb,
    payload_template = '{"applicant": "{{full_name}}", ...}'::jsonb
WHERE connector_name = 'YOUR_CONNECTOR';
```

### 2. Test Department Connectors

```bash
python scripts/test_department_connector.py --connector YOUR_CONNECTOR
```

### 3. Create Payload Templates

Use Jinja2 templates to format application data per department requirements.

---

## 📊 Progress Tracking

| Task | Status | Notes |
|------|--------|-------|
| Field Mappings | ⏳ Pending | Script ready, run now |
| Form Schemas | ✅ Complete | 12 schemas with 20 fields |
| Submission Modes | ⏳ Partial | Default modes set, needs customization |
| Validation Rules | ⏳ Partial | Framework ready, needs business rules |
| Department Connectors | ⏳ Waiting | Need API access and credentials |
| Payload Templates | ⏳ Waiting | Need department API formats |

---

## 🎯 Success Criteria

After completing configuration scripts:

- ✅ 12 schemes have field mappings configured
- ✅ 12 schemes have enhanced form schemas
- ✅ Submission modes configured per scheme
- ✅ Validation framework ready for business rules
- ⏳ Department connectors waiting for API access

---

**Last Updated**: 2024-12-30

