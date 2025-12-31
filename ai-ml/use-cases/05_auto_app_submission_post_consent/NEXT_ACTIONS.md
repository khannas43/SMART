# Next Actions: Configuration & Integration

**Status**: Core Implementation Complete ✅  
**Focus**: Configuration and Department Integration

---

## ✅ Completed

1. **Core Services**: All Python services implemented and tested
2. **Database Schema**: All 11 tables created and initialized
3. **Web Viewer**: Available at http://localhost:5001/ai05
4. **Helper Scripts**: Sample data creation, configuration scripts
5. **Documentation**: Complete technical design and guides

---

## 🎯 Immediate Next Steps

### Step 1: Field Mapping Configuration ✅ Script Ready

**Status**: Script created - ready to run

**Action**:
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/create_field_mappings_template.py
```

**What it does**:
- Creates field mappings for all active schemes
- Maps GR fields (name, DOB, address, etc.) to form fields
- Maps 360° Profile fields (income, BPL status, etc.)
- Sets up derived, concatenated, and relationship mappings

**After running**: Review and customize mappings as needed per scheme requirements

---

### Step 2: Form Schema Enhancement ✅ Script Ready

**Status**: Script created - ready to run

**Action**:
```bash
python scripts/enhance_form_schemas.py
```

**What it does**:
- Enhances existing form schemas with standard field definitions
- Adds validation rules (patterns, formats, constraints)
- Defines mandatory/optional fields
- Adds JSON Schema validation structure

**After running**: Customize scheme-specific validation rules in database

---

### Step 3: Department Connector Configuration ⏳ Manual

**Status**: Framework ready, needs department API details

**Actions Required**:

1. **Collect Department API Information**:
   - [ ] API endpoints for each scheme/department
   - [ ] Authentication credentials (API keys, OAuth tokens)
   - [ ] Request/response formats
   - [ ] Required payload structure

2. **Update Connector Configurations**:
```sql
UPDATE application.department_connectors
SET 
    endpoint_url = 'https://dept-api.rajasthan.gov.in/applications',
    auth_config = '{"api_key": "YOUR_KEY"}',
    payload_template = '{"applicant": "{{full_name}}", ...}'
WHERE connector_name = 'YOUR_CONNECTOR';
```

3. **Test Connectors**:
```bash
python scripts/test_department_connector.py --connector YOUR_CONNECTOR
```

**Blockers**: Requires actual department API access and credentials

---

### Step 4: Customize Submission Modes ⏳ Partially Done

**Status**: Default modes set, needs scheme-specific customization

**Actions Required**:

1. **Review Submission Mode Requirements**:
   - Determine auto vs review vs assisted per scheme
   - Set eligibility score thresholds
   - Configure document requirements

2. **Update Configuration**:
```sql
-- For auto submission (low-risk schemes)
UPDATE application.submission_modes_config
SET submission_mode = 'auto',
    auto_submission_min_score = 0.8
WHERE scheme_code = 'CHIRANJEEVI';

-- For review mode (moderate-risk schemes)
UPDATE application.submission_modes_config
SET submission_mode = 'review'
WHERE scheme_code = 'OLD_AGE_PENSION';

-- For assisted mode (high-risk schemes)
UPDATE application.submission_modes_config
SET submission_mode = 'assisted'
WHERE scheme_code = 'GRAMIN_AWAS';
```

**Available Now**: Configuration can be updated immediately

---

### Step 5: Scheme-Specific Validation Rules ⏳ Manual

**Status**: Framework ready, needs business rules

**Actions Required**:

1. **Define Business Rules** per scheme:
   - Age requirements (e.g., >= 60 for old age pension)
   - Income thresholds
   - Caste category requirements
   - Relationship validations

2. **Add to Form Schemas**:
```sql
UPDATE application.scheme_form_schemas
SET semantic_rules = '{
    "age_check": {
        "field": "age",
        "rule": "age >= 60",
        "message": "Age must be 60 or above"
    }
}'
WHERE scheme_code = 'OLD_AGE_PENSION';
```

**Available Now**: Can be configured as business rules are defined

---

## 📋 Configuration Checklist

Use this checklist to track progress:

### Field Mappings
- [ ] Run `create_field_mappings_template.py`
- [ ] Review mappings for each scheme
- [ ] Add scheme-specific custom mappings
- [ ] Test mappings with sample data

### Form Schemas
- [ ] Run `enhance_form_schemas.py`
- [ ] Customize field definitions per scheme
- [ ] Add validation rules per scheme
- [ ] Define mandatory fields per scheme

### Department Connectors
- [ ] Collect API endpoints and credentials
- [ ] Configure REST connectors
- [ ] Configure SOAP connectors (if needed)
- [ ] Configure API Setu connectors (if needed)
- [ ] Test all connectors

### Submission Modes
- [ ] Determine mode per scheme (auto/review/assisted)
- [ ] Update submission_modes_config table
- [ ] Set eligibility score thresholds
- [ ] Configure document requirements

### Validation Rules
- [ ] Define business rules per scheme
- [ ] Add semantic validation rules
- [ ] Configure pre-fraud checks (if needed)
- [ ] Test validation with sample data

---

## 🔄 Integration Dependencies

### Ready for Integration
- ✅ Application Orchestrator (triggered by consent events)
- ✅ Form Mapper (can map from GR/360°)
- ✅ Validation Engine (can validate forms)
- ✅ Submission Handler (can submit via connectors)

### Waiting For
- ⏳ Department API access and credentials
- ⏳ Document store integration (Raj eVault)
- ⏳ Spring Boot service layer (if using Java services)
- ⏳ Event streaming setup (if using Kafka/RabbitMQ)

---

## 📝 Recommended Order

1. **Run configuration scripts** (Steps 1-2) - Can do immediately
2. **Configure submission modes** (Step 4) - Can do with business knowledge
3. **Add validation rules** (Step 5) - Can do with business knowledge
4. **Department connectors** (Step 3) - Requires API access
5. **Integration testing** - After all configurations complete

---

## 🚀 Quick Start Commands

```bash
# 1. Activate environment
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# 2. Create field mappings
python scripts/create_field_mappings_template.py

# 3. Enhance form schemas
python scripts/enhance_form_schemas.py

# 4. Verify configuration
python scripts/check_config.py

# 5. View mappings and schemas
# Check application.scheme_field_mappings
# Check application.scheme_form_schemas
```

---

## 📚 Reference

- **Configuration Guide**: [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)
- **Technical Design**: [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)
- **Testing Guide**: [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

**Last Updated**: 2024-12-30  
**Status**: Ready for Configuration Phase

