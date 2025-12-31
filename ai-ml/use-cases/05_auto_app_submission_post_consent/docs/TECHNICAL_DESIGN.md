# Technical Design Document: Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05  
**Version:** 1.0  
**Last Updated:** 2024-12-29  
**Status:** In Development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [Component Design](#component-design)
5. [Form Mapping & Transformation](#form-mapping--transformation)
6. [Validation Engine](#validation-engine)
7. [Submission Modes](#submission-modes)
8. [Department Integration](#department-integration)
9. [API Design](#api-design)
10. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
11. [Integration Points](#integration-points)
12. [Performance & Scalability](#performance--scalability)
13. [Security & Governance](#security--governance)
14. [Compliance & Privacy](#compliance--privacy)
15. [Deployment Architecture](#deployment-architecture)
16. [Monitoring & Observability](#monitoring--observability)
17. [Success Metrics](#success-metrics)
18. [Implementation Status](#implementation-status)
19. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose

The Auto Application Submission Post-Consent system automatically creates and submits scheme applications for citizens/families after they have given consent for a scheme. The system leverages Golden Records (AI-PLATFORM-01) and 360° Profiles (AI-PLATFORM-02) to pre-fill application forms with minimal or zero manual input, ensuring applications are complete, consistent, and compliant with each department's application format and legal requirements.

### 1.2 Key Capabilities

1. **Automatic Application Creation**
   - Triggers on consent events (`CONSENT_GIVEN`) from AI-PLATFORM-04
   - Pre-fills forms using Golden Records and 360° Profile data
   - Maps data to scheme-specific form schemas
   - Handles document attachments from document stores (Raj eVault)

2. **Form Mapping & Transformation**
   - Direct field mapping (e.g., `GR.DOB → form.dob`)
   - Derived field mapping (e.g., `income_band → "Below Poverty Line = Yes/No"`)
   - Relationship mapping (auto-select target beneficiary within family)
   - Concatenated fields (e.g., `full_name = first_name + " " + last_name`)

3. **Validation & Completeness**
   - Syntactic validations (type, length, format)
   - Semantic validations (age >= 60, address district matches scheme coverage)
   - Completeness checks for mandatory fields
   - Pre-fraud checks for high-risk schemes

4. **Submission Modes**
   - **Fully Automatic**: Direct submission for low-risk schemes
   - **Auto Prefill with Review**: Citizen reviews and confirms before submission
   - **Assisted Channels**: Route to e-Mitra/field workers for missing data

5. **Department Integration**
   - REST/SOAP/API Setu connectors
   - Scheme-specific payload formatting
   - Response handling and status tracking

6. **Audit & Compliance**
   - Full field-level source tracking (GR, 360°, citizen, system)
   - Immutable audit logs
   - Consent alignment verification
   - Transparency for citizens

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for orchestration, mapping, validation
- **Database**: PostgreSQL 14+ (`smart_warehouse.application` schema)
- **External Integrations**: Department APIs (REST/SOAP/API Setu), Raj eVault (documents)
- **Validation**: JSON Schema for form validation, custom semantic validators
- **Event Streaming**: Event logs for downstream systems

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input Sources                                 │
├─────────────────────────────────────────────────────────────────┤
│  AI-PLATFORM-04  │ AI-PLATFORM-03 │ AI-PLATFORM-01 │ AI-PLATFORM-02│
│  (Consent Events)│ (Eligibility)  │ (Golden Record)│ (360° Profile)│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Application Orchestrator                                │
│  - Trigger on consent events                                     │
│  - Check eligibility state                                       │
│  - Prevent duplicate applications                                │
│  - Coordinate workflow                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Form Mapper Service                                     │
│  - Load Golden Record snapshot                                   │
│  - Load 360° Profile snippet                                     │
│  - Load scheme form schema                                       │
│  - Apply mapping rules                                           │
│  - Attach documents from Raj eVault                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Validation Engine                                       │
│  - Syntactic validation (type, length, format)                  │
│  - Semantic validation (business rules)                          │
│  - Completeness checks                                           │
│  - Pre-fraud checks (optional)                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Submission Handler                                      │
│  - Determine submission mode (auto/review/assisted)             │
│  - Store draft (if review required)                             │
│  - Route to assisted channels (if missing data)                 │
│  - Prepare department payload                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Department Connectors                                   │
│  - REST Connector                                                │
│  - SOAP Connector                                                │
│  - API Setu Connector                                            │
│  - Scheme-specific formatters                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Departmental Systems                                    │
│  - ServicePlus / Custom Portals                                  │
│  - Back-office Systems                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Event Stream & Status Tracking                          │
├─────────────────────────────────────────────────────────────────┤
│  APPLICATION_DRAFT_CREATED │ APPLICATION_SUBMITTED │            │
│  APPLICATION_REJECTED_BY_DEPT_VALIDATION │ etc.                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Output Destinations                                     │
├─────────────────────────────────────────────────────────────────┤
│  Citizen Portal/App │ Department Portal │ Analytics Dashboards │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Application Orchestrator
- **Purpose**: Main orchestrator that coordinates the entire application creation and submission workflow
- **Input**: Consent events, eligibility data
- **Output**: Application records, submission status
- **Features**: Trigger detection, eligibility verification, duplicate prevention, workflow coordination

#### 2.2.2 Form Mapper Service
- **Purpose**: Map data from Golden Records and 360° Profiles to scheme-specific form schemas
- **Input**: GR snapshot, 360° profile, scheme form schema, mapping rules
- **Output**: Pre-filled application form (JSON/dict)
- **Features**: Direct mapping, derived mapping, relationship mapping, concatenation

#### 2.2.3 Validation Engine
- **Purpose**: Validate application forms for completeness, correctness, and compliance
- **Input**: Pre-filled application form
- **Output**: Validation results, errors, warnings
- **Features**: Syntactic validation, semantic validation, completeness checks, fraud checks

#### 2.2.4 Submission Handler
- **Purpose**: Handle application submission based on mode (auto/review/assisted)
- **Input**: Validated application form, submission mode
- **Output**: Submission status, department response
- **Features**: Mode determination, draft storage, citizen notification, assisted routing

#### 2.2.5 Department Connectors
- **Purpose**: Connect to departmental systems and submit applications
- **Input**: Formatted application payload
- **Output**: Department response, application number
- **Features**: REST/SOAP/API Setu support, scheme-specific formatting, retry logic

---

## 3. Data Architecture

### 3.1 Database Schema

#### 3.1.1 Application Schema (`smart_warehouse.application`)

**Database**: `smart_warehouse` (shared with other AI/ML use cases)  
**Schema**: `application`

**Core Tables:**

1. **applications**
   - Main application records
   - Status tracking, submission mode, department reference
   - References: `scheme_code` → `public.scheme_master`, `family_id`, `consent_id`

2. **application_fields**
   - Field-level data for each application
   - Stores actual form field values
   - Source tracking (GR, 360°, citizen, system)

3. **application_documents**
   - Document attachments for applications
   - References to Raj eVault or document store
   - Document type, status, validation

4. **application_validation_results**
   - Validation results and errors
   - Syntactic and semantic validation outcomes
   - Missing field flags

5. **application_submissions**
   - Submission records and department responses
   - Department application number
   - Submission payload, response, status

6. **application_audit_logs**
   - Immutable audit trail
   - Field-level change tracking
   - Source tracking for compliance

7. **scheme_form_schemas**
   - Canonical form schemas per scheme
   - Field definitions, types, validation rules
   - Mandatory/optional flags

8. **scheme_field_mappings**
   - Mapping rules from GR/360° to form fields
   - Mapping type (direct, derived, concatenated)
   - Transformation expressions

9. **submission_modes_config**
   - Per-scheme submission mode configuration
   - Auto submission rules
   - Review requirements

10. **department_connectors**
    - Department API configurations
    - Connector type (REST/SOAP/API Setu)
    - Authentication, endpoints, payload formats

### 3.2 Data Sources

#### 3.2.1 Input Data Sources

1. **AI-PLATFORM-04 (Consent)**
   - `intimation.consent_records` - Consent records with LOA
   - `intimation.intimation_events` - `CONSENT_GIVEN` events
   - Trigger: `CONSENT_GIVEN` event for `(family_id, scheme_code)`

2. **AI-PLATFORM-03 (Eligibility)**
   - `eligibility.eligibility_snapshots` - Eligibility evaluation results
   - Eligibility score, status, rule path, reason codes
   - Used for validation and justification

3. **AI-PLATFORM-01 (Golden Records)**
   - Personal information (name, DOB, gender, etc.)
   - Demographics (caste, category, etc.)
   - Address (full address with district, block, etc.)
   - Identifiers (Jan Aadhaar, Aadhaar where permitted, bank details)
   - Relationships (family structure)
   - Documents (disability certificates, etc.)

4. **AI-PLATFORM-02 (360° Profiles)**
   - Income band
   - Vulnerability tags
   - Household composition
   - Benefit history (for fields like "already receiving X")
   - Employment type

5. **public.scheme_master**
   - Scheme metadata
   - Category, type, descriptions

6. **Raj eVault / Document Store**
   - Documents for attachment (Aadhaar, certificates, etc.)
   - Document metadata and references

#### 3.2.2 Output Data Destinations

1. **Departmental Systems**
   - Application submissions via REST/SOAP/API Setu
   - Application numbers and status updates

2. **Citizen Portal/App**
   - Draft applications for review
   - Application status and tracking

3. **Analytics Dashboards**
   - Application metrics
   - Success rates, error rates, time to submission

4. **Event Stream**
   - `APPLICATION_DRAFT_CREATED`
   - `APPLICATION_SUBMITTED`
   - `APPLICATION_REJECTED_BY_DEPT_VALIDATION`
   - `APPLICATION_ACCEPTED_BY_DEPT`

---

## 4. Component Design

### 4.1 Application Orchestrator

#### 4.1.1 Trigger Conditions

**Trigger Event**: `CONSENT_GIVEN` from AI-PLATFORM-04

**Validation Checks**:
1. Consent exists for `(family_id, scheme_code)`
2. Consent has sufficient LOA (OTP/e-sign for high-risk schemes)
3. Eligibility state is `RULE_ELIGIBLE` or `POSSIBLE_ELIGIBLE`
4. Eligibility score >= configured threshold (per scheme)
5. No active or pending application exists for same `(family_id, scheme_code)`

**Prevention of Duplicates**:
- Check `application.applications` table for existing applications
- Statuses to check: `draft`, `pending_review`, `pending_submission`, `submitted`
- Only allow one active application per `(family_id, scheme_code)` combination

#### 4.1.2 Workflow Coordination

```
1. Receive consent event
   ↓
2. Verify consent record and LOA
   ↓
3. Check eligibility snapshot
   ↓
4. Verify no duplicate application
   ↓
5. Create application record (status: 'creating')
   ↓
6. Call Form Mapper Service
   ↓
7. Call Validation Engine
   ↓
8. Determine submission mode
   ↓
9. If auto: Submit via Department Connector
   If review: Store draft and notify citizen
   If missing data: Route to assisted channel
   ↓
10. Update application status and log events
```

### 4.2 Form Mapper Service

#### 4.2.1 Data Loading

1. **Load Golden Record Snapshot**
   ```sql
   SELECT * FROM golden_records 
   WHERE family_id = :family_id 
   AND status = 'active'
   ORDER BY updated_at DESC LIMIT 1
   ```

2. **Load 360° Profile Snippet**
   ```sql
   SELECT profile_data, income_band, cluster_id, vulnerability_level
   FROM profile_360 
   WHERE gr_id = :gr_id OR family_id = :family_id
   ORDER BY updated_at DESC LIMIT 1
   ```

3. **Load Scheme Form Schema**
   ```sql
   SELECT schema_definition 
   FROM application.scheme_form_schemas 
   WHERE scheme_code = :scheme_code 
   AND is_active = true
   ```

4. **Load Mapping Rules**
   ```sql
   SELECT * FROM application.scheme_field_mappings 
   WHERE scheme_code = :scheme_code 
   AND is_active = true
   ORDER BY priority
   ```

#### 4.2.2 Mapping Types

**1. Direct Mapping**
- Source: `GR.dob` → Target: `form.date_of_birth`
- No transformation, direct copy

**2. Derived Mapping**
- Source: `360_profile.income_band` → Target: `form.bpl_status`
- Transformation: `"BELOW_POVERTY_LINE" → "Yes"`, else `"No"`

**3. Concatenated Mapping**
- Sources: `GR.first_name`, `GR.last_name` → Target: `form.full_name`
- Transformation: `first_name + " " + last_name`

**4. Relationship Mapping**
- Source: Family members from GR → Target: `form.beneficiary_id`
- Logic: For individual-centric schemes (e.g., widow pension), auto-select appropriate family member

**5. Conditional Mapping**
- Based on scheme rules or eligibility data
- Example: If eligibility reason includes "DISABILITY", set `form.disability_certificate_required = true`

#### 4.2.3 Document Attachment

1. **Query Document Store** (Raj eVault or integrated DMS)
   - Get documents for family_id
   - Filter by document type (Aadhaar, disability certificate, etc.)
   - Get document references/URLs

2. **Map to Form Requirements**
   - Check scheme form schema for required documents
   - Match available documents to requirements
   - Attach document references to application

3. **Missing Documents**
   - Flag application with `missing_documents` status
   - List required but missing documents
   - Do not submit until documents are attached

### 4.3 Validation Engine

#### 4.3.1 Syntactic Validation

**Type Validation**:
- Check field types match schema (string, number, date, boolean, etc.)
- Validate date formats (ISO 8601, DD/MM/YYYY, etc.)
- Validate numeric ranges

**Length Validation**:
- Check string length against min/max constraints
- Validate array/list lengths

**Format Validation**:
- Email format
- Phone number format (Indian: 10 digits)
- Aadhaar format (12 digits)
- PIN code format (6 digits)
- Bank account number format

**Example Rules**:
```python
{
  "field": "email",
  "type": "string",
  "format": "email",
  "required": false
},
{
  "field": "mobile_number",
  "type": "string",
  "pattern": "^[0-9]{10}$",
  "required": true
}
```

#### 4.3.2 Semantic Validation

**Business Rule Validation**:
- Age >= 60 for old age pension
- Address district matches scheme coverage area
- Bank account present for schemes with direct benefit transfer
- Caste category matches scheme eligibility (SC/ST/OBC schemes)

**Cross-Field Validation**:
- If `relationship_to_head = "SELF"`, then beneficiary must be head of family
- If `beneficiary_type = "WIDOW"`, then marital_status must be "WIDOWED"
- Income band and BPL status consistency

**Scheme-Specific Rules**:
- Per-scheme validation rules stored in `scheme_form_schemas.validation_rules`
- JSON Schema-based validation
- Custom Python validators for complex rules

#### 4.3.3 Completeness Checks

**Mandatory Field Check**:
- Check all `required: true` fields are present
- Check all mandatory documents are attached
- Report missing fields with user-friendly messages

**Derived Field Check**:
- Ensure derived fields are computed if required
- Check conditional mandatory fields (e.g., disability certificate if disability_status = true)

#### 4.3.4 Pre-Fraud Checks (Optional, High-Risk Schemes)

**Duplicate Account Check**:
- Check for duplicate bank accounts across applications
- Flag if same bank account used by multiple beneficiaries

**Conflicting Income Check**:
- Cross-reference income across schemes
- Flag if income reported inconsistently

**Residence Verification**:
- Cross-check address with other records
- Flag if address mismatch detected

### 4.4 Submission Handler

#### 4.4.1 Submission Mode Determination

**Mode Selection Logic**:
```python
if scheme_config.submission_mode == "auto":
    if validation_passed and all_documents_attached:
        mode = "auto_submit"
    elif missing_data:
        mode = "assisted"
    else:
        mode = "review"
elif scheme_config.submission_mode == "review":
    mode = "review"
else:  # "assisted"
    mode = "assisted"
```

**Scheme Configuration**:
- Per-scheme configuration in `submission_modes_config`
- Low-risk schemes: `auto`
- Moderate-risk schemes: `review`
- High-risk schemes: `review` or `assisted`

#### 4.4.2 Auto Submission Flow

1. Validation passes
2. All documents attached
3. Consent LOA sufficient
4. Directly invoke Department Connector
5. Submit application
6. Update status: `submitted`
7. Log event: `APPLICATION_SUBMITTED`
8. Notify citizen via SMS/app with application number

#### 4.4.3 Review Flow

1. Store draft application in database
2. Set status: `pending_review`
3. Log event: `APPLICATION_DRAFT_CREATED`
4. Notify citizen: "Your application for Scheme X is ready; please review & confirm"
5. Citizen portal/app shows read-only pre-filled data with minimal editable fields
6. On confirmation, invoke Department Connector
7. Submit application
8. Update status: `submitted`

#### 4.4.4 Assisted Channel Flow

1. Identify missing data or validation errors
2. Set status: `pending_citizen_input` or `pending_assisted`
3. Log event: `APPLICATION_REQUIRES_ASSISTANCE`
4. Route to e-Mitra/field worker queue
5. Field worker fills missing data
6. Re-validate application
7. Submit via Department Connector or route back to review

### 4.5 Department Connectors

#### 4.5.1 Connector Types

**1. REST Connector**
- Standard REST API calls
- JSON payloads
- OAuth 2.0 / API key authentication
- HTTP methods: POST, PUT, GET

**2. SOAP Connector**
- SOAP/XML web services
- WSDL-based service definitions
- WS-Security for authentication
- Python library: `zeep`

**3. API Setu Connector**
- India-specific API gateway
- Standardized payload formats
- OAuth-based authentication
- Common response format

#### 4.5.2 Payload Formatting

**Scheme-Specific Formatters**:
- Each scheme may have different payload format
- Formatters convert internal JSON to department-specific format
- Handled by `scheme_field_mappings.payload_format`

**Example REST Payload**:
```json
{
  "application_id": "APP-2024-001234",
  "scheme_code": "CHIRANJEEVI",
  "beneficiary": {
    "name": "Ram Kumar",
    "dob": "1980-01-15",
    "aadhaar": "123456789012",
    ...
  },
  "documents": [
    {
      "type": "AADHAAR",
      "url": "https://evault.rajasthan.gov.in/doc/12345"
    }
  ]
}
```

#### 4.5.3 Response Handling

**Success Response**:
- Extract application number from department
- Update `application_submissions` table
- Update application status: `submitted`
- Log event: `APPLICATION_SUBMITTED`

**Error Response**:
- Parse error messages
- Update application status: `submission_failed`
- Log event: `APPLICATION_REJECTED_BY_DEPT_VALIDATION`
- Store error details for retry or manual intervention

**Retry Logic**:
- Retry transient failures (network errors, timeout)
- Exponential backoff
- Max retries: 3
- After max retries, flag for manual review

---

## 5. Form Mapping & Transformation

### 5.1 Mapping Strategy

The Form Mapper Service transforms data from multiple sources into scheme-specific application forms using a flexible mapping configuration system.

### 5.2 Mapping Configuration

Mappings are stored in `application.scheme_field_mappings` table with the following structure:

- **scheme_code**: Target scheme
- **target_field**: Form field name
- **source_type**: Data source (GR, PROFILE_360, ELIGIBILITY, SYSTEM, CITIZEN)
- **source_path**: JSON path to source data (e.g., `GR.golden_records.first_name`)
- **mapping_type**: direct, derived, concatenated, conditional, relationship
- **transformation_expression**: Python/Jinja2 expression for transformations
- **priority**: Order of application when multiple mappings exist

### 5.3 Transformation Examples

**Direct Mapping:**
```python
# GR.dob → form.date_of_birth
target_field = "date_of_birth"
source_path = "GR.date_of_birth"
mapping_type = "direct"
```

**Derived Mapping:**
```python
# income_band → bpl_status
target_field = "bpl_status"
source_path = "PROFILE_360.income_band"
mapping_type = "derived"
transformation = "Yes" if income_band == "BELOW_POVERTY_LINE" else "No"
```

**Concatenated Mapping:**
```python
# first_name + last_name → full_name
target_field = "full_name"
source_paths = ["GR.first_name", "GR.last_name"]
mapping_type = "concatenated"
transformation = "{{ GR.first_name }} {{ GR.last_name }}"
```

---

## 6. Validation Engine

### 6.1 Validation Levels

The Validation Engine performs multi-level validation:

1. **Syntactic**: Type, length, format validation
2. **Semantic**: Business rule validation
3. **Completeness**: Mandatory field checks
4. **Fraud Prevention**: Optional pre-fraud checks

### 6.2 Validation Configuration

Validation rules are stored in `application.scheme_form_schemas.validation_rules` as JSON Schema.

### 6.3 Validation Results

Validation results are stored in `application.application_validation_results`:
- Overall validation status (passed, failed, warnings)
- Field-level errors
- Missing mandatory fields
- Fraud check flags

---

## 7. Submission Modes

### 7.1 Auto Submission

**Criteria:**
- Scheme configured with `submission_mode = "auto"`
- Validation passed
- All mandatory documents attached
- Consent LOA sufficient (OTP/e-sign for high-risk)

**Process:**
1. Validate application
2. Format payload for department
3. Submit via Department Connector
4. Update status to `submitted`
5. Notify citizen

### 7.2 Review Mode

**Criteria:**
- Scheme configured with `submission_mode = "review"`
- Or missing optional data requiring citizen confirmation

**Process:**
1. Store draft application
2. Set status to `pending_review`
3. Notify citizen via SMS/app
4. Citizen reviews in portal/app
5. Citizen confirms → Submit via Department Connector
6. Citizen edits → Update fields → Re-validate → Submit

### 7.3 Assisted Mode

**Criteria:**
- Missing mandatory data
- Validation errors requiring manual intervention

**Process:**
1. Set status to `pending_assisted`
2. Route to e-Mitra/field worker queue
3. Field worker collects missing data
4. Update application fields
5. Re-validate
6. Submit or route back to review

---

## 8. Department Integration

### 8.1 Connector Architecture

All department connectors implement the `DepartmentConnector` abstract base class:

```python
class DepartmentConnector(ABC):
    def submit_application(self, application_id, payload) -> Dict
    def check_status(self, application_id) -> Dict
    def format_payload(self, application_data) -> Dict
```

### 8.2 Connector Configuration

Connectors are configured in `application.department_connectors`:
- Connector name and type
- Authentication method
- Endpoint URLs
- Payload templates
- Response parsing rules

### 8.3 Authentication

**REST**: API Key, OAuth 2.0, Basic Auth  
**SOAP**: WS-Security, Certificate-based  
**API Setu**: OAuth 2.0 with government credentials

---

## 9. API Design

### 9.1 REST Endpoints

**Base URL**: `/api/v1/application`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start` | POST | Trigger application creation from consent |
| `/draft` | GET | Get draft application for review |
| `/confirm` | POST | Confirm and submit draft |
| `/status` | GET | Get application status |
| `/{id}` | GET | Get application details |
| `/{id}/field` | PUT | Update application field |
| `/{id}/retry` | POST | Retry failed submission |

### 9.2 Request/Response Formats

All endpoints use JSON with standardized request/response DTOs (see `spring_boot/dto/`).

---

## 10. Data Flow & Processing Pipeline

### 10.1 Complete Flow

```
1. Consent Event (AI-PLATFORM-04)
   ↓
2. Application Orchestrator receives event
   ↓
3. Verify consent & eligibility
   ↓
4. Create application record (status: 'creating')
   ↓
5. Form Mapper loads data & applies mappings
   ↓
6. Update status: 'mapped'
   ↓
7. Validation Engine validates form
   ↓
8. Update status: 'validated' or 'validation_failed'
   ↓
9. Submission Handler determines mode
   ↓
10a. Auto: Submit → 'submitted'
10b. Review: Store draft → 'pending_review'
10c. Assisted: Route → 'pending_assisted'
   ↓
11. Department Connector submits (if auto/review)
   ↓
12. Update submission status & notify citizen
```

### 10.2 Error Handling

- **Transient Errors**: Retry with exponential backoff
- **Validation Errors**: Route to assisted or citizen review
- **Department Errors**: Store error details, flag for manual review

---

## 11. Integration Points

### 11.1 Input Integrations

- **AI-PLATFORM-04**: Consent events via `intimation.consent_records`
- **AI-PLATFORM-03**: Eligibility via `eligibility.eligibility_snapshots`
- **AI-PLATFORM-01**: GR data via `golden_records` schema
- **AI-PLATFORM-02**: 360° Profiles via `profile_360` schema

### 11.2 Output Integrations

- **Department Systems**: REST/SOAP/API Setu submissions
- **Citizen Portal**: Draft applications via REST API
- **Event Stream**: Application events for downstream systems
- **Analytics**: Application metrics and status updates

---

## 12. Performance & Scalability

### 12.1 Performance Targets

- **Application Creation**: < 5 seconds end-to-end
- **Form Mapping**: < 2 seconds per application
- **Validation**: < 1 second per application
- **Submission**: < 10 seconds (depends on department API)

### 12.2 Scalability Considerations

- Database indexing on frequently queried fields
- Connection pooling for database access
- Async processing for department submissions
- Batch processing for bulk operations

---

## 13. Security & Governance

### 13.1 Authentication & Authorization

- All REST APIs require authentication
- Role-based access control (RBAC)
- API rate limiting

### 13.2 Data Privacy

- Field-level source tracking for audit
- Encryption at rest for sensitive data
- PII masking in logs

### 13.3 Consent Compliance

- Verify consent before application creation
- Track consent LOA level
- Support consent withdrawal

---

## 14. Compliance & Privacy

### 14.1 Audit Requirements

- Immutable audit logs in `application_audit_logs`
- Field-level change tracking
- Source tracking for every field

### 14.2 Transparency

- Citizens can view all data sources
- Citizens can see which fields came from which source
- Citizens can update/edit fields in review mode

### 14.3 Data Retention

- Applications retained per policy
- Audit logs retained for compliance period
- Archive old applications to cold storage

---

## 15. Deployment Architecture

### 15.1 Service Components

- **Application Orchestrator**: Python service
- **Form Mapper**: Python service
- **Validation Engine**: Python service
- **Submission Handler**: Python service
- **REST APIs**: Spring Boot application
- **Department Connectors**: Python services

### 15.2 Infrastructure

- **Database**: PostgreSQL 14+ (shared `smart_warehouse`)
- **Application Server**: Spring Boot on JVM
- **Python Services**: Deploy as services or Docker containers
- **Message Queue**: For async processing (optional)

---

## 16. Monitoring & Observability

### 16.1 Metrics

- Application creation rate
- Submission success rate
- Average time to submission
- Validation failure rate
- Department API response times

### 16.2 Logging

- Structured logging for all operations
- Error logging with stack traces
- Audit logging for compliance

### 16.3 Alerts

- High error rates
- Department API failures
- Validation failure spikes
- Processing delays

---

## 17. Success Metrics

### 17.1 Adoption Metrics

- Number of applications created via auto submission
- Percentage of consents that result in applications
- Adoption by scheme

### 17.2 Efficiency Metrics

- Reduction in incomplete applications vs manual
- Average time from consent to submission
- Reduction in manual data entry

### 17.3 Quality Metrics

- Application correctness (validation pass rate)
- Department acceptance rate
- Citizen satisfaction scores

---

## 18. Implementation Status

### 18.1 Completed ✅

- Database schema (11 tables)
- Core Python services (Orchestrator, Form Mapper, Validation, Submission)
- Department connectors (REST, SOAP, API Setu)
- Spring Boot REST API controllers
- Configuration system
- Test scripts
- Web viewer for monitoring

### 18.2 In Progress ⏳

- Department API integration (credentials, endpoints)
- Form schema customization per scheme
- Field mapping rules configuration
- Spring Boot service layer implementation

### 18.3 Pending 📋

- Document store integration (Raj eVault)
- End-to-end testing with real department APIs
- Production deployment
- Monitoring and alerting setup
- Performance tuning

---

## 19. Web Interface for Viewing Results

### 19.1 Purpose

A web-based interface for viewing application submission results, status, and statistics in a browser for development and testing purposes.

### 19.2 Implementation

**Location**: Integrated into Eligibility Rules Viewer at `/ai05` endpoint

**File**: `ai-ml/use-cases/03_identification_beneficiary/scripts/view_rules_web.py` (routes for `/ai05`)

**Technology**: Flask web application with Jinja2 templates

### 19.3 Features

#### 19.3.1 Statistics Dashboard

Displays key metrics:
- Total applications created
- Submitted applications count
- Pending applications count
- Error applications count

#### 19.3.2 Application View

Shows recent applications with:
- Application ID
- Family ID (truncated for privacy)
- Scheme code
- Status (creating, mapped, validated, submitted, error, etc.)
- Submission mode (auto, review, assisted)
- Eligibility score (color-coded)
- Fields mapped count
- Creation timestamp

#### 19.3.3 Submission Status View

Displays recent submissions with:
- Submission ID
- Application ID
- Scheme code
- Response status (success, error, validation_error, etc.)
- Department application number
- Submission timestamp

### 19.4 Access

**URL**: `http://127.0.0.1:5001/ai05`

**Server**: Runs on the same Flask server as Eligibility Rules Viewer (port 5001)

**Navigation**: 
- Main Eligibility Rules: `http://127.0.0.1:5001`
- Campaign Results: `http://127.0.0.1:5001/ai04`
- Application Submission: `http://127.0.0.1:5001/ai05`

### 19.5 Usage

1. **Start the Server**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   python scripts/view_rules_web.py
   ```

2. **Access in Browser**:
   - Open `http://127.0.0.1:5001/ai05` in your web browser
   - Click "Refresh Data" button to reload latest data from database

3. **Create Sample Data**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
   python scripts/create_sample_applications.py
   ```

### 19.6 Data Source

- **Database**: `smart_warehouse`
- **Schema**: `application`
- **Tables Queried**:
  - `application.applications`
  - `application.application_submissions`
  - `application.application_fields`

### 19.7 Limitations

- **Read-only**: View-only interface for development/testing
- **Not for Production**: For production use, integrate with portal UI or use REST APIs
- **Limited Pagination**: Shows recent 20 records per table
- **No Filtering**: Basic view without advanced filtering/search

---

## 20. Future Enhancements

### 20.1 Advanced Features

- Machine learning for field mapping optimization
- Predictive validation using historical data
- Auto-correction of common data entry errors
- Multi-language form support

### 20.2 Enhanced Integration

- Real-time status updates via WebSocket
- Push notifications to citizen apps
- Department status polling and sync
- Batch submission capabilities

### 20.3 Analytics & Insights

- Application success rate by scheme
- Time-to-submission analytics
- Validation error patterns
- Department API performance metrics

---

**Document Version**: 1.1  
**Last Updated**: 2024-12-30  
**Next Review**: 2025-01-15

