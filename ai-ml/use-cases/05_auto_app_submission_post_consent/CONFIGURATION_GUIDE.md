# Configuration Guide: Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05  
**Purpose:** Step-by-step guide for configuring the application submission system

---

## Overview

This guide helps you configure the key components needed to make the application submission system production-ready:

1. **Field Mapping Rules** - Map GR/360° data to form fields
2. **Form Schemas** - Define scheme-specific application forms
3. **Department Connectors** - Configure API endpoints and authentication
4. **Submission Modes** - Configure auto/review/assisted modes per scheme

---

## Step 1: Field Mapping Rules

### What are Field Mappings?

Field mappings define how data from Golden Records (GR) and 360° Profiles gets transformed into application form fields.

### Automated Setup

Run the automated script to create standard mappings:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/create_field_mappings_template.py
```

This will create mappings for:
- **Direct mappings**: `GR.date_of_birth` → `form.date_of_birth`
- **Derived mappings**: `income_band` → `bpl_status` (Yes/No)
- **Concatenated mappings**: `GR.first_name + GR.last_name` → `form.full_name`
- **Relationship mappings**: Select family member for individual-centric schemes

### Manual Configuration

To add custom mappings, insert into `application.scheme_field_mappings`:

```sql
INSERT INTO application.scheme_field_mappings (
    scheme_code, target_field, source_type, source_path,
    mapping_type, transformation_expression, priority, is_active
) VALUES (
    'CHIRANJEEVI',
    'family_size',
    'PROFILE_360',
    'PROFILE_360.household_size',
    'direct',
    NULL,
    1,
    true
);
```

### Mapping Types

1. **direct**: Copy value as-is
2. **derived**: Transform using expression
3. **concatenated**: Combine multiple fields
4. **conditional**: Apply based on conditions
5. **relationship**: Select from family members

---

## Step 2: Form Schemas

### What are Form Schemas?

Form schemas define the structure, validation rules, and mandatory fields for each scheme's application form.

### Automated Enhancement

Run the script to enhance existing schemas with standard fields:

```bash
python scripts/enhance_form_schemas.py
```

This adds:
- Standard fields (name, DOB, address, bank details, etc.)
- Validation rules (patterns, formats, constraints)
- Mandatory/optional field definitions

### Manual Customization

To customize a scheme's form schema:

1. **Update Schema Definition**:
```sql
UPDATE application.scheme_form_schemas
SET schema_definition = '{
    "type": "object",
    "properties": {
        "full_name": {
            "type": "string",
            "minLength": 3,
            "maxLength": 100,
            "required": true
        },
        "age": {
            "type": "integer",
            "minimum": 60,
            "maximum": 120,
            "required": true
        }
    },
    "required": ["full_name", "age"]
}'
WHERE scheme_code = 'OLD_AGE_PENSION';
```

2. **Add Validation Rules**:
```sql
UPDATE application.scheme_form_schemas
SET validation_rules = '{
    "age_validation": {
        "field": "age",
        "rule": "age >= 60",
        "message": "Age must be 60 or above for old age pension"
    }
}'
WHERE scheme_code = 'OLD_AGE_PENSION';
```

---

## Step 3: Department Connectors

### What are Department Connectors?

Department connectors handle API communication with external departmental systems (REST/SOAP/API Setu).

### Configuration Steps

1. **Update Connector Configuration**:

Edit `application.department_connectors` table:

```sql
UPDATE application.department_connectors
SET 
    connector_name = 'CHIRANJEEVI_REST_API',
    endpoint_url = 'https://api.health.rajasthan.gov.in/applications',
    auth_type = 'OAUTH2',
    auth_config = '{
        "token_url": "https://api.health.rajasthan.gov.in/oauth/token",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "scope": "application.submit"
    }',
    payload_template = '{
        "applicant_name": "{{full_name}}",
        "date_of_birth": "{{date_of_birth}}",
        "aadhaar": "{{aadhaar_number}}"
    }'
WHERE connector_id = 1;
```

2. **REST Connector**:
   - **Endpoint URL**: Department API endpoint
   - **Auth Type**: API_KEY, OAUTH2, BASIC
   - **Payload Template**: Jinja2 template for request body

3. **SOAP Connector**:
   - **WSDL URL**: WSDL file location
   - **Service Name**: SOAP service name
   - **Auth Type**: WSS (WS-Security)

4. **API Setu Connector**:
   - **API Setu Gateway URL**: Government API gateway endpoint
   - **Auth Type**: OAUTH2 (API Setu standard)
   - **API Key**: Your API Setu API key

### Testing Connectors

Test connector configuration:

```bash
python scripts/test_department_connector.py --connector CHIRANJEEVI_REST_API
```

---

## Step 4: Submission Modes

### Configure Per-Scheme Submission Mode

Update `application.submission_modes_config`:

```sql
UPDATE application.submission_modes_config
SET 
    submission_mode = 'auto',  -- or 'review', 'assisted'
    auto_submission_min_score = 0.8,
    require_all_documents = true,
    require_all_mandatory_fields = true
WHERE scheme_code = 'CHIRANJEEVI';
```

### Submission Mode Types

1. **auto**: Fully automatic submission
   - Requires: High eligibility score, all documents, validation passed
   - Use for: Low-risk schemes

2. **review**: Citizen review before submission
   - Requires: Validation passed, draft stored
   - Use for: Moderate-risk schemes

3. **assisted**: Route to field workers
   - Requires: Missing data or validation errors
   - Use for: High-risk schemes or incomplete data

### Configuration via YAML

Alternatively, configure in `config/use_case_config.yaml`:

```yaml
schemes:
  CHIRANJEEVI:
    submission_mode: "auto"
    auto_submission:
      min_eligibility_score: 0.8
      require_all_documents: true
      require_all_mandatory_fields: true
```

---

## Step 5: Document Requirements

### Configure Required Documents

Update document requirements in `config/use_case_config.yaml`:

```yaml
documents:
  required_documents:
    HEALTH:
      - "AADHAAR"
      - "PHOTO"
      - "HEALTH_CARD"
    PENSION:
      - "AADHAAR"
      - "PHOTO"
      - "AGE_PROOF"
      - "BANK_PASSBOOK"
```

Or update per-scheme:

```sql
UPDATE application.scheme_form_schemas
SET validation_rules = jsonb_set(
    validation_rules,
    '{required_documents}',
    '["AADHAAR", "PHOTO", "HEALTH_CARD"]'::jsonb
)
WHERE scheme_code = 'CHIRANJEEVI';
```

---

## Step 6: Validation Rules

### Add Scheme-Specific Validation

1. **Semantic Validation Rules**:

```sql
UPDATE application.scheme_form_schemas
SET semantic_rules = '{
    "old_age_pension_age_check": {
        "field": "age",
        "rule": "age >= 60",
        "message": "Applicant must be 60 years or above"
    },
    "widow_pension_status_check": {
        "field": "marital_status",
        "rule": "marital_status == \"WIDOWED\"",
        "message": "Applicant must be widowed"
    }
}'
WHERE scheme_code = 'OLD_AGE_PENSION';
```

2. **Pre-Fraud Checks** (Optional):

Enable in `config/use_case_config.yaml`:

```yaml
validation:
  enable_fraud_checks: true
  fraud_checks:
    duplicate_bank_account: true
    conflicting_income: true
    residence_verification: true
```

---

## Verification

### Check Configuration

Run configuration check:

```bash
python scripts/check_config.py
```

This verifies:
- Database connectivity
- Schema existence
- Configuration files
- Field mappings count
- Form schemas count

### Test Application Creation

```bash
# Create test consent
python scripts/create_test_consent.py

# Test application creation
python scripts/test_application_creation.py

# Test form mapping
python scripts/test_form_mapping.py

# Test validation
python scripts/test_validation.py

# End-to-end test
python scripts/test_end_to_end.py
```

---

## Common Configuration Patterns

### Pattern 1: Health Scheme (Auto Submission)

```sql
-- CHIRANJEEVI: Auto submission for health insurance
UPDATE application.submission_modes_config
SET submission_mode = 'auto',
    auto_submission_min_score = 0.75
WHERE scheme_code = 'CHIRANJEEVI';
```

### Pattern 2: Pension Scheme (Review Mode)

```sql
-- OLD_AGE_PENSION: Citizen review required
UPDATE application.submission_modes_config
SET submission_mode = 'review'
WHERE scheme_code = 'OLD_AGE_PENSION';
```

### Pattern 3: High-Risk Scheme (Assisted Mode)

```sql
-- GRAMIN_AWAS: Assisted channel for housing
UPDATE application.submission_modes_config
SET submission_mode = 'assisted'
WHERE scheme_code = 'GRAMIN_AWAS';
```

---

## Next Steps

After completing configuration:

1. **Test with Real Data**: Use actual consent records and eligibility snapshots
2. **Verify Department APIs**: Test connector endpoints with department systems
3. **Monitor Performance**: Check application creation and submission rates
4. **Refine Mappings**: Adjust field mappings based on data quality
5. **Update Schemas**: Customize form schemas per department requirements

---

## Troubleshooting

### Issue: No mappings created

**Solution**: Check that schemes exist in `public.scheme_master`:
```sql
SELECT scheme_code FROM public.scheme_master WHERE status = 'active';
```

### Issue: Form validation fails

**Solution**: Check schema definition and required fields:
```sql
SELECT schema_definition, mandatory_fields 
FROM application.scheme_form_schemas 
WHERE scheme_code = 'YOUR_SCHEME';
```

### Issue: Department API connection fails

**Solution**: Verify connector configuration:
```sql
SELECT connector_name, endpoint_url, auth_type 
FROM application.department_connectors 
WHERE is_active = true;
```

---

**Last Updated**: 2024-12-30  
**Version**: 1.0

