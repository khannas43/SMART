# Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05  
**Version:** 1.0  
**Status:** In Development

## Overview

The Auto Application Submission Post-Consent system automatically creates and submits scheme applications for citizens/families after they have given consent. The system uses Golden Records and 360° Profile data to pre-fill application forms with minimal or zero manual input, ensuring applications are complete, consistent, and compliant with each department's requirements.

## Key Capabilities

1. **Automatic Application Creation**
   - Triggers on consent events (`CONSENT_GIVEN`)
   - Pre-fills forms using Golden Records and 360° Profile data
   - Maps data to scheme-specific form schemas
   - Handles document attachments from document stores

2. **Form Mapping & Validation**
   - Direct field mapping (e.g., DOB → form.dob)
   - Derived field mapping (e.g., income_band → BPL status)
   - Relationship mapping (auto-select beneficiary within family)
   - Comprehensive validation (syntactic and semantic)

3. **Submission Modes**
   - **Fully Automatic**: Direct submission for low-risk schemes
   - **Auto Prefill with Review**: Citizen reviews and confirms before submission
   - **Assisted Channels**: Route to e-Mitra/field workers for missing data

4. **Department Integration**
   - REST/SOAP/API Setu connectors
   - Scheme-specific payload formatting
   - Response handling and status tracking

5. **Audit & Compliance**
   - Full field-level source tracking (GR, 360°, citizen, system)
   - Immutable audit logs
   - Consent alignment verification
   - Transparency for citizens

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Navigate to use case directory
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

```bash
# Create database schema
./scripts/setup_database.sh

# Or manually:
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/application_schema.sql
```

### 4. Configure

Edit configuration files:
- `config/db_config.yaml` - Database connections
- `config/use_case_config.yaml` - Application mapping rules, validation rules, submission policies

### 5. Initialize Data

```bash
# Initialize scheme form schemas and mapping rules
python scripts/init_scheme_form_configs.py
```

### 6. Test

```bash
# Test application creation from consent
python scripts/test_application_creation.py

# Test form mapping
python scripts/test_form_mapping.py

# Test validation
python scripts/test_validation.py

# End-to-end test
python scripts/test_end_to_end.py
```

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** ⭐ **NEW** - Configuration guide for field mappings, form schemas, and connectors
- **[NEXT_ACTIONS.md](NEXT_ACTIONS.md)** ⭐ **NEW** - Detailed next actions and checklist
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures
- **[docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)** - Comprehensive technical design
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Implementation status and completion tracking

## Architecture

```
┌─────────────────────────────────────────┐
│      Consent Events (AI-PLATFORM-04)   │
│         CONSENT_GIVEN events            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Application Orchestrator            │
│  - Trigger on consent                   │
│  - Check eligibility                    │
│  - Prevent duplicates                   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│        Form Mapper Service              │
│  - Load Golden Record                   │
│  - Load 360° Profile                    │
│  - Map to scheme form schema            │
│  - Attach documents                     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│        Validation Engine                │
│  - Syntactic validation                 │
│  - Semantic validation                  │
│  - Completeness checks                  │
│  - Pre-fraud checks (optional)          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Submission Handler                 │
│  - Auto submit (low-risk)               │
│  - Store draft (citizen review)         │
│  - Route to assisted channels           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Department Connectors                │
│  - REST/SOAP/API Setu                   │
│  - Scheme-specific formatting           │
│  - Response handling                    │
└─────────────────────────────────────────┘
```

## Integration Points

### Input Dependencies
- **AI-PLATFORM-03**: Eligibility snapshots and candidate lists
- **AI-PLATFORM-04**: Consent records and events
- **AI-PLATFORM-01**: Golden Records (personal, demographic, address, identifiers)
- **AI-PLATFORM-02**: 360° Profiles (income, vulnerability, household composition)

### Output Destinations
- **Departmental Systems**: Application submissions
- **Citizen Portal/App**: Draft applications for review
- **Analytics Dashboards**: Application metrics and events
- **Event Stream**: APPLICATION_DRAFT_CREATED, APPLICATION_SUBMITTED events

## Key Features

- ✅ Automatic trigger on consent events
- ✅ Multi-source data aggregation (GR + 360°)
- ✅ Schema-aware form mapping
- ✅ Comprehensive validation
- ✅ Multiple submission modes
- ✅ Department integration abstraction
- ✅ Full audit trails
- ✅ Source tracking for every field

## Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for orchestration, mapping, validation
- **Database**: PostgreSQL 14+ (`smart_warehouse.application` schema)
- **External Integrations**: Department APIs (REST/SOAP/API Setu)
- **Document Store**: Raj eVault / integrated DMS
- **Event Streaming**: Event logs for downstream systems

## Status

**Current Status**: ✅ **Core Implementation Complete** - Ready for Configuration

- ✅ Project structure created
- ✅ Technical design document (complete)
- ✅ Database schema design (11 tables)
- ✅ Core service implementation (all services)
- ✅ Form mapping engine
- ✅ Validation engine
- ✅ Department connectors (framework ready)
- ✅ Spring Boot APIs (controllers ready)
- ✅ Testing scripts
- ✅ Web viewer (http://localhost:5001/ai05)
- ✅ Configuration scripts and guides

## Next Steps

1. **Run Configuration Scripts** (Ready Now):
   - Field mapping rules: `python scripts/create_field_mappings_template.py`
   - Form schema enhancement: `python scripts/enhance_form_schemas.py`

2. **Configure Department Connectors** (Requires API Access):
   - Add department API endpoints and credentials
   - Configure authentication
   - Test connectors

3. **Customize Per Scheme**:
   - Submission modes per scheme
   - Validation rules per scheme
   - Field mapping customizations

4. **Integration Testing**:
   - Test with real department APIs
   - Test end-to-end workflow
   - Performance testing

See [NEXT_ACTIONS.md](NEXT_ACTIONS.md) and [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) for detailed next steps.

---

**Last Updated**: 2024-12-29  
**Use Case Owner**: SMART Platform Team

