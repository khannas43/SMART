# Technical Design Document: Auto Approval & Straight-through Processing

**Use Case ID:** AI-PLATFORM-06  
**Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** Core Implementation Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [Component Design](#component-design)
5. [Decision Engine](#decision-engine)
6. [Rule Engine](#rule-engine)
7. [Risk Scoring Model](#risk-scoring-model)
8. [Decision Router](#decision-router)
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

The Auto Approval & Straight-through Processing system evaluates incoming scheme applications (especially those created via AI-PLATFORM-05) using rules and risk models to automatically approve low-risk, fully compliant cases, enabling true straight-through processing (STP). Medium/high-risk or ambiguous cases are routed to departmental officers, cutting workload and delays while ensuring fairness and compliance with India's emerging AI governance guidelines.

### 1.2 Key Capabilities

1. **Rule-Based Evaluation**
   - Eligibility and authenticity verification
   - Document validation checks
   - Duplicate detection
   - Cross-scheme conflict checks
   - Deceased flag verification

2. **Risk Scoring**
   - ML-based risk assessment (XGBoost, Logistic Regression)
   - Feature engineering from Golden Records, 360° Profiles, and application behavior
   - Rule-based fallback when ML models unavailable
   - Explainable AI with top contributing factors

3. **Decision Logic & Routing**
   - **AUTO_APPROVE**: Low-risk, fully compliant cases → Payment trigger
   - **ROUTE_TO_OFFICER**: Medium-risk or minor data issues → Officer worklist
   - **ROUTE_TO_FRAUD**: High-risk or strong red flags → Fraud investigation queue
   - **AUTO_REJECT**: Mandatory rule failures → Rejection

4. **Governance & Compliance**
   - Explainable decisions with human-readable reasons
   - Full audit trails and compliance logging
   - Fairness checks and bias monitoring
   - Officer override mechanisms with mandatory justification

5. **Integration**
   - Applications from AI-PLATFORM-05
   - Payment/DBT systems (Jan Aadhaar enabled)
   - Departmental worklists and notifications

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for decision logic, rule evaluation, risk scoring
- **ML Models**: XGBoost, scikit-learn, SHAP (explainability)
- **Database**: PostgreSQL 14+ (`smart_warehouse.decision` schema)
- **Integration**: Payment systems, DBT, departmental worklists
- **Monitoring**: MLflow for model tracking, audit logs for compliance

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input Sources                                 │
├─────────────────────────────────────────────────────────────────┤
│  AI-PLATFORM-05  │ AI-PLATFORM-01 │ AI-PLATFORM-02 │ AI-PLATFORM-03│
│  (Applications)  │ (Golden Record)│ (360° Profile) │ (Eligibility) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Engine                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Rule Engine  │  │ Risk Scorer  │  │ Decision     │          │
│  │              │  │              │  │ Router       │          │
│  │ - Eligibility│  │ - ML Models  │  │              │          │
│  │ - Authenticity│ │ - Features   │  │ - Payment    │          │
│  │ - Documents  │  │ - Scoring    │  │ - Worklist   │          │
│  │ - Duplicates │  │ - Explain    │  │ - Fraud Q    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Output                               │
├─────────────────────────────────────────────────────────────────┤
│  AUTO_APPROVE → Payment/DBT │ ROUTE_TO_OFFICER → Worklist       │
│  ROUTE_TO_FRAUD → Fraud Q   │ AUTO_REJECT → Rejection          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction

```
Application (AI-PLATFORM-05)
    ↓
Decision Engine
    ├──→ Rule Engine
    │       ├── Eligibility Check
    │       ├── Authenticity Check
    │       ├── Document Validation
    │       ├── Duplicate Check
    │       └── Cross-Scheme Check
    │
    ├──→ Risk Scorer
    │       ├── Feature Extraction
    │       ├── ML Model Inference
    │       └── Risk Band Calculation
    │
    └──→ Decision Router
            ├── Payment Trigger (AUTO_APPROVE)
            ├── Worklist Routing (ROUTE_TO_OFFICER)
            ├── Fraud Queue (ROUTE_TO_FRAUD)
            └── Rejection Handling (AUTO_REJECT)
```

---

## 3. Data Architecture

### 3.1 Database Schema

**Schema:** `decision` (in `smart_warehouse` database)

**Key Tables:**

1. **`decisions`** - Main decision records
   - `decision_id`, `application_id`, `family_id`, `scheme_code`
   - `decision_type`, `decision_status`, `risk_score`, `risk_band`
   - `rules_passed`, `critical_rules_failed`, `routing_reason`
   - `model_version`, `model_type`, `thresholds_used`

2. **`rule_evaluations`** - Detailed rule check results
   - `evaluation_id`, `decision_id`, `rule_category`, `rule_name`
   - `passed`, `severity`, `result_message`, `result_details`

3. **`risk_scores`** - ML risk assessment results
   - `score_id`, `decision_id`, `overall_score`, `score_band`
   - `feature_contributions`, `top_risk_factors`, `model_version`

4. **`decision_history`** - Immutable audit trail
   - `history_id`, `decision_id`, `from_status`, `to_status`
   - `change_reason`, `changed_by`, `changed_at`

5. **`decision_overrides`** - Officer overrides
   - `override_id`, `decision_id`, `original_decision_type`
   - `override_decision_type`, `override_reason`, `officer_id`

6. **`risk_models`** - ML model metadata
   - `model_id`, `model_name`, `model_type`, `model_version`
   - `model_path`, `model_artifact_uri`, `performance_metrics`
   - `is_active`, `is_production`, `deployed_at`

7. **`decision_config`** - Per-scheme configuration
   - `config_id`, `scheme_code`, `low_risk_max`, `medium_risk_max`
   - `enable_auto_approval`, `require_human_review_medium`

8. **`payment_triggers`** - Payment integration records
   - `trigger_id`, `decision_id`, `payment_status`, `payment_system`
   - `triggered_at`, `processed_at`

9. **`external_verifications`** - External check results
   - `verification_id`, `decision_id`, `verification_type`
   - `verification_status`, `verification_result`

10. **`decision_audit_logs`** - Compliance logs
    - `audit_id`, `decision_id`, `event_type`, `event_data`
    - `input_snapshot_hash`, `actor_type`, `actor_id`

11. **`fairness_metrics`** - Bias monitoring
    - `metric_id`, `scheme_code`, `demographic_category`
    - `auto_approval_rate`, `avg_risk_score`

### 3.2 Data Sources

**Upstream Services:**
- `application.applications` - Applications from AI-PLATFORM-05
- `golden_records.*` - Identity and demographic data
- `profile_360.*` - Benefit history and vulnerability tags
- `eligibility.eligibility_snapshots` - Eligibility scores and status

**External Data:**
- Aadhaar/Jan Aadhaar verification services
- Bank account validation services
- Document verification services
- Fraud watchlists

---

## 4. Component Design

### 4.1 Decision Engine

**Location:** `src/decision_engine.py`

**Responsibilities:**
- Orchestrate complete decision evaluation workflow
- Coordinate Rule Engine, Risk Scorer, and Decision Router
- Load decision configuration per scheme
- Make final decision based on rules and risk
- Persist decision results to database

**Key Methods:**
- `evaluate_application(application_id, family_id, scheme_code)` - Main entry point
- `_fetch_application()` - Get application details
- `_load_decision_config()` - Load scheme-specific thresholds
- `_evaluate_rules()` - Call Rule Engine
- `_calculate_risk_score()` - Call Risk Scorer
- `_make_decision()` - Decision logic
- `_save_decision()` - Persist to database

### 4.2 Rule Engine

**Location:** `src/engines/rule_engine.py`

**Responsibilities:**
- Evaluate eligibility rules
- Verify authenticity (consent-based)
- Validate documents (mandatory checks)
- Detect duplicates
- Check cross-scheme conflicts
- Verify deceased flags

**Rule Categories:**
1. **ELIGIBILITY** - Eligibility status and score checks
2. **AUTHENTICITY** - Identity verification checks
3. **DOCUMENT** - Mandatory document validation
4. **DUPLICATE** - Existing application checks
5. **CROSS_SCHEME** - Scheme conflict checks
6. **FRAUD** - Deceased flag, watchlist checks

**Key Methods:**
- `evaluate_rules(application_id, family_id, scheme_code)` - Main evaluation
- `_evaluate_eligibility()` - Eligibility checks
- `_evaluate_authenticity()` - Authenticity verification
- `_evaluate_documents()` - Document validation
- `_evaluate_duplicates()` - Duplicate detection
- `_evaluate_cross_scheme()` - Cross-scheme checks
- `_check_deceased_flag()` - Deceased verification
- `save_rule_evaluations()` - Persist results

### 4.3 Risk Scorer

**Location:** `src/models/risk_scorer.py`

**Responsibilities:**
- Extract features from multiple data sources
- Calculate risk scores using ML models or rule-based fallback
- Determine risk bands (LOW/MEDIUM/HIGH)
- Provide explainability (top contributing factors)

**Feature Categories:**
1. **Profile Features** - Age, gender, family size, demographics
2. **Benefit History** - Number of schemes, total benefits, overlap
3. **Application Behavior** - Submission mode, past rejections, timing
4. **Eligibility Features** - Eligibility score, status

**Key Methods:**
- `calculate_risk_score(application_id, family_id, scheme_code)` - Main scoring
- `_extract_features()` - Feature engineering
- `_get_profile_features()` - From Golden Records
- `_get_benefit_history()` - From 360° Profiles
- `_get_application_features()` - From application data
- `_load_model()` - Load ML model for scheme
- `_score_with_model()` - ML model inference
- `_score_with_rules()` - Rule-based fallback
- `_determine_risk_band()` - Risk band calculation

### 4.4 Decision Router

**Location:** `src/engines/decision_router.py`

**Responsibilities:**
- Route decisions to appropriate channels
- Trigger payment for auto-approved applications
- Add to officer worklist for review cases
- Route to fraud queue for high-risk cases
- Handle rejection cases

**Key Methods:**
- `route_decision(decision_id, decision, application_id)` - Main routing
- `_route_auto_approve()` - Payment trigger
- `_route_to_officer()` - Worklist routing
- `_route_to_fraud()` - Fraud queue routing
- `_route_auto_reject()` - Rejection handling

---

## 5. Decision Engine

### 5.1 Workflow

```
1. Receive Application
   ↓
2. Fetch Application Details
   ↓
3. Load Decision Configuration (scheme-specific thresholds)
   ↓
4. Evaluate Rules (Rule Engine)
   ├── Eligibility Check
   ├── Authenticity Check
   ├── Document Validation
   ├── Duplicate Check
   ├── Cross-Scheme Check
   └── Deceased Flag Check
   ↓
5. Calculate Risk Score (Risk Scorer)
   ├── Extract Features
   ├── Load ML Model (or use rule-based)
   └── Calculate Score & Band
   ↓
6. Make Decision
   ├── Check Critical Rule Failures → AUTO_REJECT
   ├── Check Risk Band + Rules
   │   ├── LOW + Rules Pass → AUTO_APPROVE
   │   ├── MEDIUM + Rules Pass → ROUTE_TO_OFFICER
   │   └── HIGH + Rules Pass → ROUTE_TO_FRAUD
   └── Rules Fail → ROUTE_TO_OFFICER
   ↓
7. Save Decision to Database
   ↓
8. Save Rule Evaluations
   ↓
9. Route Decision (Decision Router)
   ├── AUTO_APPROVE → Payment Trigger
   ├── ROUTE_TO_OFFICER → Worklist
   ├── ROUTE_TO_FRAUD → Fraud Queue
   └── AUTO_REJECT → Rejection
```

### 5.2 Decision Logic

**Decision Matrix:**

| Rules Pass | Risk Band | Decision Type | Action |
|------------|-----------|---------------|--------|
| ❌ (Critical Failure) | Any | AUTO_REJECT | Reject immediately |
| ❌ (Non-Critical) | Any | ROUTE_TO_OFFICER | Officer review |
| ✅ | LOW | AUTO_APPROVE | Payment trigger |
| ✅ | MEDIUM | ROUTE_TO_OFFICER | Officer review (if configured) |
| ✅ | HIGH | ROUTE_TO_FRAUD | Fraud investigation |

**Configuration Overrides:**
- Per-scheme risk thresholds
- Per-scheme auto-approval enablement
- Per-scheme human review requirements

---

## 6. Rule Engine

### 6.1 Rule Categories

#### 6.1.1 Eligibility Rules
- **Rule:** `ELIGIBILITY_CHECK`
- **Check:** Eligibility status is `RULE_ELIGIBLE` or `POSSIBLE_ELIGIBLE`
- **Threshold:** Eligibility score >= 0.5
- **Severity:** CRITICAL
- **Source:** `eligibility.eligibility_snapshots`

#### 6.1.2 Authenticity Rules
- **Rule:** `AUTHENTICITY_CHECK`
- **Check:** Application has valid consent record
- **Verification:** Consent ID present, submission mode = 'auto'
- **Severity:** HIGH
- **Source:** `application.applications`, `intimation.consent_records`

#### 6.1.3 Document Rules
- **Rule:** `DOCUMENT_VALIDATION`
- **Check:** All mandatory documents verified
- **Verification:** Count of mandatory documents = Count of verified mandatory documents
- **Severity:** CRITICAL
- **Source:** `application.application_documents`

#### 6.1.4 Duplicate Rules
- **Rule:** `DUPLICATE_CHECK`
- **Check:** No existing active/pending application for same family+scheme
- **Verification:** Count of existing applications = 0
- **Severity:** CRITICAL
- **Source:** `application.applications`

#### 6.1.5 Cross-Scheme Rules
- **Rule:** `CROSS_SCHEME_CHECK`
- **Check:** No conflicting schemes (exclusive schemes)
- **Verification:** Check scheme category for conflicts
- **Severity:** HIGH
- **Source:** `public.scheme_master`, `application.applications`

#### 6.1.6 Fraud Rules
- **Rule:** `DECEASED_FLAG_CHECK`
- **Check:** No deceased flag in Golden Record
- **Verification:** Deceased flag = false
- **Severity:** CRITICAL
- **Source:** `golden_records.family_members`

### 6.2 Rule Evaluation Flow

```
For each rule category:
  1. Execute rule check
  2. Determine pass/fail
  3. Assign severity (CRITICAL, HIGH, MEDIUM, LOW)
  4. Generate result message
  5. Store evaluation result
  6. If CRITICAL failure → Add to critical_failures list
```

---

## 7. Risk Scoring Model

### 7.1 Feature Engineering

**Profile Features:**
- `family_size` - Number of family members
- `avg_age` - Average age of family members
- `demographics` - Caste, category, etc.

**Benefit History Features:**
- `total_benefits` - Total number of benefits received
- `unique_schemes` - Number of different schemes
- `benefit_overlap` - Overlap with similar schemes

**Application Behavior Features:**
- `is_auto_submission` - Auto vs manual submission
- `eligibility_score` - Eligibility score from AI-PLATFORM-03
- `past_rejections` - Number of past rejections

**Eligibility Features:**
- `eligibility_score` - Score value
- `eligibility_status_rule` - RULE_ELIGIBLE flag
- `eligibility_status_possible` - POSSIBLE_ELIGIBLE flag

### 7.2 Model Types

**Primary Models:**
- **XGBoost** - Gradient boosting for risk classification
- **Logistic Regression** - Linear model for interpretability
- **Random Forest** - Ensemble model for robustness

**Model Selection:**
- Per-scheme models (trained on scheme-specific data)
- General models (trained on all schemes)
- Fallback to rule-based scoring if model unavailable

### 7.3 Risk Scoring Flow

```
1. Extract Features
   ├── Profile Features (Golden Records)
   ├── Benefit History (360° Profiles)
   ├── Application Behavior (Application data)
   └── Eligibility Features (Eligibility snapshots)
   ↓
2. Load Model
   ├── Check for scheme-specific model
   ├── Check for general model
   └── Fallback to rule-based if no model
   ↓
3. Calculate Risk Score
   ├── ML Model Inference (if available)
   └── Rule-Based Scoring (fallback)
   ↓
4. Determine Risk Band
   ├── LOW: score <= low_risk_max
   ├── MEDIUM: low_risk_max < score <= medium_risk_max
   └── HIGH: score > medium_risk_max
   ↓
5. Generate Explainability
   ├── Top contributing factors (SHAP/LIME)
   └── Feature contributions
```

### 7.4 Rule-Based Fallback

When ML models are unavailable, use rule-based scoring:

```python
risk_score = 0.0

# Factor 1: Past rejections (higher risk)
if past_rejections > 0:
    risk_score += min(0.3, past_rejections * 0.1)

# Factor 2: Low eligibility score (higher risk)
if eligibility_score < 0.6:
    risk_score += 0.2

# Factor 3: Multiple benefits (lower risk - established beneficiary)
if unique_schemes > 3:
    risk_score -= 0.1

# Factor 4: Auto submission (lower risk - verified data)
if is_auto_submission:
    risk_score -= 0.15

# Normalize to 0-1 range
risk_score = max(0.0, min(1.0, risk_score))
```

---

## 8. Decision Router

### 8.1 Routing Logic

**AUTO_APPROVE:**
- Create payment trigger record
- Set status to 'pending'
- Trigger payment API (when available)
- Notify citizen (when notification service available)

**ROUTE_TO_OFFICER:**
- Update decision with routing info
- Add to officer worklist (when worklist system available)
- Set status to 'under_review'
- Notify officer (when notification service available)

**ROUTE_TO_FRAUD:**
- Update decision with routing info
- Add to fraud investigation queue (when fraud system available)
- Set status to 'under_review'
- Auto-hold payment

**AUTO_REJECT:**
- Update application status to 'rejected'
- Set decision status to 'rejected'
- Log rejection reason

### 8.2 Payment Integration

**Payment Trigger Record:**
- `trigger_id` - Unique identifier
- `decision_id` - Link to decision
- `payment_status` - pending, triggered, processing, completed, failed
- `payment_system` - JAN_AADHAAR_DBT, etc.
- `payment_reference_id` - Department reference
- `triggered_at`, `processed_at`, `completed_at`

**Payment Flow:**
```
1. Decision: AUTO_APPROVE
   ↓
2. Create payment_trigger record (status: pending)
   ↓
3. Validate payment requirements
   ├── Bank account validation
   ├── Name match verification
   └── Jan Aadhaar validation
   ↓
4. Trigger payment API
   ↓
5. Update payment_trigger (status: triggered/processing)
   ↓
6. Receive payment confirmation
   ↓
7. Update payment_trigger (status: completed)
```

---

## 9. API Design

### 9.1 REST API Endpoints

**Base URL:** `/decision`

#### 9.1.1 Evaluate Application
- **Endpoint:** `POST /decision/evaluateApplication`
- **Request:**
  ```json
  {
    "applicationId": 123,
    "familyId": "uuid-optional",
    "schemeCode": "CHIRANJEEVI-optional"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "decisionId": 456,
    "decision": {
      "decisionType": "AUTO_APPROVE",
      "decisionStatus": "approved",
      "riskScore": 0.25,
      "riskBand": "LOW",
      "reason": "Low risk, rules passed, auto-approved"
    },
    "ruleResults": {
      "allPassed": true,
      "passedCount": 6,
      "failedCount": 0,
      "criticalFailures": []
    },
    "riskResults": {
      "riskScore": 0.25,
      "riskBand": "LOW",
      "modelVersion": "1.0",
      "modelType": "rule-based",
      "topFactors": ["Auto-submitted (verified data)"]
    },
    "routing": {
      "action": "payment_triggered",
      "status": "pending",
      "triggerId": 789
    }
  }
  ```

#### 9.1.2 Get Decision History
- **Endpoint:** `GET /decision/history?applicationId=123`
- **Response:**
  ```json
  {
    "success": true,
    "applicationId": 123,
    "history": [
      {
        "historyId": 1,
        "fromStatus": null,
        "toStatus": "approved",
        "fromDecisionType": null,
        "toDecisionType": "AUTO_APPROVE",
        "changeReason": "Initial decision created",
        "changedBy": "decision_engine",
        "changedAt": "2024-12-30T10:00:00Z"
      }
    ]
  }
  ```

#### 9.1.3 Get Decision Details
- **Endpoint:** `GET /decision/{decisionId}`
- **Response:** Complete decision details with rule evaluations and risk scores

#### 9.1.4 Override Decision
- **Endpoint:** `POST /decision/override`
- **Request:**
  ```json
  {
    "decisionId": 456,
    "overrideDecisionType": "OFFICER_APPROVED",
    "overrideReason": "Manual review confirms eligibility",
    "officerId": "officer_123",
    "officerName": "John Doe"
  }
  ```

#### 9.1.5 Get Decisions by Family
- **Endpoint:** `GET /decision/family/{familyId}`
- **Response:** List of all decisions for a family

#### 9.1.6 Get Decisions by Scheme
- **Endpoint:** `GET /decision/scheme/{schemeCode}`
- **Response:** List of all decisions for a scheme

#### 9.1.7 Get STP Metrics
- **Endpoint:** `GET /decision/metrics/stp?schemeCode=CHIRANJEEVI&startDate=2024-01-01&endDate=2024-12-31`
- **Response:** STP performance metrics

---

## 10. Data Flow & Processing Pipeline

### 10.1 Application Evaluation Flow

```
Application Submitted (AI-PLATFORM-05)
    ↓
Decision Engine Triggered
    ↓
┌─────────────────────────────────────┐
│ Parallel Processing                 │
├─────────────────────────────────────┤
│ Rule Engine                         │
│   ├── Eligibility Check             │
│   ├── Authenticity Check            │
│   ├── Document Validation           │
│   ├── Duplicate Check               │
│   ├── Cross-Scheme Check            │
│   └── Deceased Flag Check           │
│                                     │
│ Risk Scorer                         │
│   ├── Extract Features              │
│   ├── Load Model                    │
│   ├── Calculate Score               │
│   └── Determine Band                │
└─────────────────────────────────────┘
    ↓
Decision Logic
    ├── Critical Failure? → AUTO_REJECT
    ├── LOW Risk + Rules Pass? → AUTO_APPROVE
    ├── MEDIUM Risk? → ROUTE_TO_OFFICER
    └── HIGH Risk? → ROUTE_TO_FRAUD
    ↓
Save Decision
    ├── decisions table
    ├── rule_evaluations table
    ├── risk_scores table
    └── decision_history table
    ↓
Route Decision
    ├── AUTO_APPROVE → payment_triggers
    ├── ROUTE_TO_OFFICER → worklist
    ├── ROUTE_TO_FRAUD → fraud_queue
    └── AUTO_REJECT → rejection
```

### 10.2 Event Flow

```
CONSENT_GIVEN (AI-PLATFORM-04)
    ↓
APPLICATION_CREATED (AI-PLATFORM-05)
    ↓
APPLICATION_SUBMITTED (AI-PLATFORM-05)
    ↓
DECISION_EVALUATION_STARTED (AI-PLATFORM-06)
    ↓
DECISION_CREATED (AI-PLATFORM-06)
    ├── APPLICATION_AUTO_APPROVED
    ├── APPLICATION_ROUTED_TO_OFFICER
    ├── APPLICATION_ROUTED_TO_FRAUD
    └── APPLICATION_AUTO_REJECTED
    ↓
PAYMENT_TRIGGERED (if AUTO_APPROVE)
    ↓
CITIZEN_NOTIFIED
```

---

## 11. Integration Points

### 11.1 Upstream Services

**AI-PLATFORM-05 (Applications):**
- Read: `application.applications`
- Read: `application.application_fields`
- Read: `application.application_documents`
- Read: `application.application_submissions`

**AI-PLATFORM-01 (Golden Records):**
- Read: `golden_records.family_members`
- Read: `golden_records.families`
- Read: Identity and demographic data

**AI-PLATFORM-02 (360° Profiles):**
- Read: `profile_360.benefit_history`
- Read: `profile_360.household_composition`
- Read: Vulnerability tags, income bands

**AI-PLATFORM-03 (Eligibility):**
- Read: `eligibility.eligibility_snapshots`
- Read: Eligibility scores and status

**AI-PLATFORM-04 (Intimation):**
- Read: `intimation.consent_records`
- Read: Consent verification data

### 11.2 Downstream Services

**Payment/DBT Systems:**
- Write: Payment trigger records
- Integration: Jan Aadhaar DBT API
- Status: Payment confirmation

**Officer Worklist:**
- Write: Worklist assignments
- Integration: Department worklist system
- Status: Review status updates

**Fraud Investigation:**
- Write: Fraud queue assignments
- Integration: Fraud investigation system
- Status: Investigation results

**Notification Services:**
- Write: Notification requests
- Integration: SMS, app push, email services
- Status: Delivery confirmations

### 11.3 External Services

**Aadhaar/Jan Aadhaar:**
- API: e-KYC verification
- Purpose: Identity authentication
- Status: Verification results

**Bank Validation:**
- API: Account validation
- Purpose: Payment account verification
- Status: Validation results

**Document Verification:**
- API: Document authenticity check
- Purpose: Document validation
- Status: Verification results

---

## 12. Performance & Scalability

### 12.1 Performance Targets

- **Decision Evaluation:** < 5 seconds per application
- **Rule Evaluation:** < 2 seconds
- **Risk Scoring:** < 3 seconds (with ML model)
- **Database Queries:** < 500ms per query
- **API Response Time:** < 1 second (excluding evaluation)

### 12.2 Scalability Considerations

**Horizontal Scaling:**
- Decision Engine: Stateless, can run multiple instances
- Rule Engine: Stateless, parallel rule evaluation
- Risk Scorer: Stateless, can use model serving (MLflow)

**Database Optimization:**
- Indexes on `decisions(application_id, scheme_code)`
- Indexes on `rule_evaluations(decision_id)`
- Indexes on `risk_scores(decision_id)`
- Partitioning by date for large tables

**Caching:**
- Decision configuration (per scheme)
- ML models (in-memory cache)
- Feature extraction results

**Async Processing:**
- Payment triggers (async queue)
- Notification sending (async queue)
- Worklist updates (async queue)

---

## 13. Security & Governance

### 13.1 Security Measures

**Authentication:**
- API authentication (JWT tokens)
- Officer authentication for overrides
- Audit logging of all actions

**Authorization:**
- Role-based access control
- Officer override permissions
- Admin configuration access

**Data Protection:**
- Sensitive data hashing (Aadhaar, bank accounts)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)

### 13.2 AI Governance

**Transparency:**
- Explainable decisions (top factors)
- Human-readable reasons
- Model version tracking

**Fairness:**
- Bias monitoring (fairness_metrics table)
- Demographic breakdown analysis
- Override pattern analysis

**Human Oversight:**
- Medium/high risk → Officer review
- Override requirements (mandatory justification)
- Supervisor approval for high-risk overrides

**Auditability:**
- Immutable audit logs
- Input snapshot hashing
- Model version tracking
- Full decision history

---

## 14. Compliance & Privacy

### 14.1 Data Privacy

**Personal Data:**
- Aadhaar numbers: Hashed in audit logs
- Bank accounts: Hashed in payment triggers
- Family IDs: Used for linking, not exposed

**Data Retention:**
- Decisions: Retained per policy
- Audit logs: Immutable, long-term retention
- Risk scores: Retained for model retraining

### 14.2 Regulatory Compliance

**India AI Governance:**
- Risk-based approach for automated decisions
- Human oversight for medium/high risk
- Transparency and explainability
- Recourse mechanisms (override, appeal)

**Data Protection:**
- Consent alignment verification
- Data minimization (only necessary data)
- Purpose limitation (decision evaluation only)

---

## 15. Deployment Architecture

### 15.1 Component Deployment

**Python Services:**
- Decision Engine: Python service (Flask/FastAPI)
- Rule Engine: Python module
- Risk Scorer: Python module with ML models
- Decision Router: Python module

**Spring Boot Services:**
- REST API Controllers: Spring Boot application
- Service Layer: Java service (calls Python)
- DTOs: Java classes

**Database:**
- PostgreSQL: `smart_warehouse.decision` schema
- Connection pooling
- Read replicas for reporting

**ML Models:**
- MLflow: Model registry and serving
- Model storage: S3 or local filesystem
- Model versioning: MLflow tracking

### 15.2 Deployment Options

**Option 1: Monolithic**
- All Python services in one process
- Spring Boot as separate service
- Direct database connections

**Option 2: Microservices**
- Decision Engine as separate service
- Rule Engine as separate service
- Risk Scorer as separate service
- API Gateway for routing

**Option 3: Serverless**
- Decision evaluation as serverless function
- ML model inference as serverless function
- Event-driven architecture

---

## 16. Monitoring & Observability

### 16.1 Metrics

**Decision Metrics:**
- Total decisions per day
- Auto-approval rate (STP rate)
- Officer review rate
- Fraud queue rate
- Rejection rate

**Performance Metrics:**
- Average evaluation time
- Rule evaluation time
- Risk scoring time
- API response time

**Quality Metrics:**
- Override rate
- Post-facto error rate
- Fraud detection rate
- Appeal rate

### 16.2 Logging

**Application Logs:**
- Decision evaluation logs
- Rule evaluation logs
- Risk scoring logs
- Routing logs
- Error logs

**Audit Logs:**
- All decision changes
- All overrides
- All configuration changes
- All API calls

### 16.3 Alerting

**Critical Alerts:**
- High rejection rate (> threshold)
- High fraud queue rate (> threshold)
- Model inference failures
- Database connection failures

**Warning Alerts:**
- Low STP rate (< threshold)
- High override rate (> threshold)
- Slow evaluation times
- High error rate

---

## 17. Success Metrics

### 17.1 STP Effectiveness

- **Auto-Approval Rate:** % of applications auto-approved
- **Target:** > 60% for low-risk schemes
- **Measurement:** `COUNT(AUTO_APPROVE) / COUNT(total_decisions)`

### 17.2 Quality & Risk Control

- **Post-Facto Error Rate:** % of auto-approved with errors
- **Target:** < 1%
- **Measurement:** Errors found in audits / auto-approved count

- **Override Rate:** % of decisions overridden
- **Target:** 5-15% (balanced)
- **Measurement:** `COUNT(overrides) / COUNT(total_decisions)`

### 17.3 Efficiency

- **Average Processing Time:** Time from application to decision
- **Target:** < 5 minutes for auto-approval
- **Measurement:** `AVG(decision_timestamp - application_created_at)`

- **Officer Workload Reduction:** % reduction in manual reviews
- **Target:** > 50% reduction
- **Measurement:** Manual reviews before / after

### 17.4 Citizen Experience

- **Same-Day Approvals:** % of approvals on same day
- **Target:** > 80% for low-risk
- **Measurement:** `COUNT(same_day_approvals) / COUNT(approvals)`

- **Complaint Rate:** % of decisions with complaints
- **Target:** < 2%
- **Measurement:** Complaints / total_decisions

---

## 18. Implementation Status

### 18.1 Completed ✅

- Database schema (11 tables)
- Configuration files
- Decision Engine (complete workflow)
- Rule Engine (6 rule categories)
- Risk Scorer (feature engineering + rule-based fallback)
- Decision Router (routing logic)
- Spring Boot REST APIs (controllers + DTOs)
- End-to-end test script (tested successfully)
- Web viewer (http://localhost:5001/ai06)
- Documentation (README, QUICK_START, TESTING_GUIDE)

### 18.2 In Progress 🚧

- Spring Boot service layer (connecting to Python)
- Unit tests
- ML model training scripts

### 18.3 Pending ⏳

- ML model integration (requires trained models)
- Payment/DBT integration (requires department APIs)
- Officer worklist integration (requires worklist system)
- Notification service integration
- External verification services
- Fairness monitoring dashboard

---

## 19. Future Enhancements

### 19.1 Short-Term (3-6 months)

1. **ML Model Training**
   - Train XGBoost models per scheme
   - Model evaluation and validation
   - MLflow integration

2. **Enhanced Explainability**
   - SHAP values for feature importance
   - LIME for local explanations
   - Citizen-facing explanations

3. **Real-Time Monitoring**
   - Live dashboard for STP rates
   - Real-time alerts
   - Performance monitoring

### 19.2 Medium-Term (6-12 months)

1. **Advanced Risk Models**
   - Graph-based risk analysis
   - Anomaly detection
   - Fraud pattern recognition

2. **Fairness Monitoring**
   - Automated bias detection
   - Demographic analysis
   - Fairness dashboard

3. **A/B Testing**
   - Model version comparison
   - Threshold optimization
   - Decision policy testing

### 19.3 Long-Term (12+ months)

1. **Continuous Learning**
   - Online model updates
   - Feedback loop integration
   - Auto-retraining pipeline

2. **Multi-Model Ensemble**
   - Combine multiple models
   - Model selection logic
   - Confidence scoring

3. **Advanced Analytics**
   - Predictive analytics
   - Trend analysis
   - Policy impact analysis

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Next Review:** 2025-01-30

