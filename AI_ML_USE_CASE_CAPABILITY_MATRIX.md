# AI/ML Use Case Capability Matrix for Citizen Portal Integration

**Purpose:** Reference document for mapping Citizen Portal screens to AI/ML use cases  
**Created:** 2024-12-30  
**For:** Citizen Portal Development Team  
**Version:** 1.0

---

## Quick Reference Table

| Use Case ID | Name | Primary Purpose | Key Portal Use Cases | Status |
|-------------|------|-----------------|---------------------|--------|
| AI-PLATFORM-01 | Golden Records | Deduplication & Master Data | Profile management, identity verification | ✅ Complete |
| AI-PLATFORM-02 | 360° Profiles | Comprehensive citizen profiles | Profile dashboard, relationship view | ✅ Complete |
| AI-PLATFORM-03 | Eligibility Identification | Auto-identify eligible schemes | Eligibility hints, scheme discovery | ✅ Complete |
| AI-PLATFORM-04 | Auto Intimation & Consent | Automated notifications & consent | Notifications, consent management | ✅ Complete |
| AI-PLATFORM-05 | Auto Application Submission | Auto-create & submit applications | Application submission, form prefill | ⏳ Partial |
| AI-PLATFORM-06 | Auto Approval & STP | Automatic application approval | Application status, approval notifications | ✅ Complete |
| AI-PLATFORM-07 | Beneficiary Detection | Detect ineligible/mistargeted cases | Case alerts, verification requests | ✅ Complete |
| AI-PLATFORM-08 | Eligibility Checker | Real-time eligibility checking | Eligibility checker widget, recommendations | ✅ Complete |
| AI-PLATFORM-09 | Proactive Inclusion | Identify inclusion gaps | Outreach notifications, priority alerts | ✅ Complete |
| AI-PLATFORM-10 | Benefit Forecast | Future benefit predictions | Financial planning, benefit projections | ✅ Complete |
| AI-PLATFORM-11 | Personalized Nudging | Optimized reminders & messages | Inbox, notifications, reminders | ✅ Complete |

---

## Detailed Use Case Capabilities

### AI-PLATFORM-01: Golden Records ✅

**Purpose:** Maintain deduplicated master citizen identities with conflict reconciliation

**Key Capabilities:**
- Deduplicate citizen records across multiple sources
- Maintain single source of truth for citizen identity
- Resolve conflicts between duplicate records
- Track data lineage and sources

**REST APIs:**
```
GET  /api/v1/golden-records/{citizen_id} - Get golden record
POST /api/v1/golden-records/search - Search golden records
GET  /api/v1/golden-records/{citizen_id}/sources - Get source records
POST /api/v1/golden-records/merge - Merge duplicate records
```

**Request/Response Examples:**
```json
// GET /api/v1/golden-records/{citizen_id}
Response: {
  "citizen_id": "uuid",
  "name": "string",
  "dob": "date",
  "aadhaar": "string",
  "demographics": {...},
  "sources": [...]
}
```

**Data Output:**
- Demographics (name, DOB, gender, address)
- Identity documents (Aadhaar, mobile, email)
- Family relationships
- Source tracking

**Integration Points:**
- Input: Multiple departmental databases
- Output: Used by all other use cases as master data source

**Portal Screen Mapping Potential:**
- Citizen profile screens (identity verification)
- Registration/onboarding (duplicate check)
- Profile editing (conflict resolution)

---

### AI-PLATFORM-02: 360° Profiles ✅

**Purpose:** Build comprehensive citizen profiles with income inference, eligibility scoring, graph relationships, and anomaly detection

**Key Capabilities:**
- Income band inference (ML model)
- Eligibility scoring per scheme
- Family relationship graphs (Neo4j)
- Anomaly detection (fraud indicators)
- Vulnerability categorization
- Under-coverage identification

**REST APIs:**
```
GET  /api/v1/profiles/{family_id} - Get complete profile
GET  /api/v1/profiles/{family_id}/income - Get income inference
GET  /api/v1/profiles/{family_id}/eligibility-scores - Get eligibility scores
GET  /api/v1/profiles/{family_id}/relationships - Get relationship graph
GET  /api/v1/profiles/{family_id}/anomalies - Get anomaly indicators
GET  /api/v1/profiles/{family_id}/vulnerability - Get vulnerability category
```

**Request/Response Examples:**
```json
// GET /api/v1/profiles/{family_id}
Response: {
  "family_id": "uuid",
  "income_band": "5000-10000",
  "vulnerability_category": "HIGH",
  "eligibility_scores": {
    "scheme_code": {
      "score": 0.85,
      "confidence": 0.9
    }
  },
  "relationships": [...],
  "anomalies": []
}
```

**Data Output:**
- Income band (inferred)
- Eligibility scores (per scheme)
- Relationship graph data
- Vulnerability indicators
- Anomaly flags
- Under-coverage status

**Integration Points:**
- Input: Golden Records, benefit history, scheme enrollment data
- Output: Used by Eligibility Engine, Approval Engine, Forecast

**Portal Screen Mapping Potential:**
- Profile dashboard (complete profile view)
- Income details screen
- Family relationships screen
- Scheme eligibility cards
- Anomaly alerts

---

### AI-PLATFORM-03: Eligibility Identification ✅

**Purpose:** Automatically identify citizens/families potentially eligible for 157+ welfare schemes

**Key Capabilities:**
- Rule-based eligibility evaluation (8 rule types)
- ML-based eligibility scoring (XGBoost)
- Hybrid evaluation (rules + ML)
- Prioritization and ranking
- Explainable results (rule paths, SHAP values)
- Batch, event-driven, and on-demand evaluation

**REST APIs:**
```
POST /api/v1/eligibility/evaluate?family_id={id}&scheme_ids={list} - On-demand evaluation
GET  /api/v1/eligibility/precomputed?family_id={id} - Get precomputed results
GET  /api/v1/eligibility/citizen-hints?family_id={id}&limit={n} - Top N schemes for citizen
GET  /api/v1/eligibility/candidate-list?scheme_id={id}&district={name}&score>={x} - Department worklist
POST /api/v1/eligibility/candidate-list/batch - Trigger batch evaluation
GET  /api/v1/eligibility/config/scheme/{scheme_id} - Get scheme configuration
```

**Request/Response Examples:**
```json
// POST /api/v1/eligibility/evaluate
Request: {
  "family_id": "uuid",
  "scheme_ids": ["SCHEME1", "SCHEME2"],  // optional
  "use_ml": true
}

Response: {
  "family_id": "uuid",
  "evaluated_at": "2024-12-30T12:00:00Z",
  "schemes": [
    {
      "scheme_id": "uuid",
      "scheme_code": "OAP001",
      "scheme_name": "Old Age Pension",
      "status": "ELIGIBLE",
      "eligibility_score": 0.92,
      "rule_result": "RULE_ELIGIBLE",
      "ml_score": 0.88,
      "confidence": 0.95,
      "explanations": {
        "rule_path": [...],
        "shap_values": {...}
      }
    }
  ]
}

// GET /api/v1/eligibility/citizen-hints
Response: {
  "family_id": "uuid",
  "top_schemes": [
    {
      "scheme_code": "OAP001",
      "scheme_name": "Old Age Pension",
      "eligibility_score": 0.92,
      "priority": "HIGH",
      "reason": "Age threshold met"
    }
  ]
}
```

**Data Output:**
- Eligibility status (ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE)
- Eligibility scores (0-1)
- Explanations (rule paths, SHAP values)
- Priority rankings
- Confidence levels

**Integration Points:**
- Input: Golden Records, 360° Profiles, scheme rules, ML models
- Output: Triggers Auto Intimation (AI-PLATFORM-04)

**Portal Screen Mapping Potential:**
- Eligibility discovery/hints widget
- Scheme recommendation cards
- "You may be eligible for" sections
- Detailed eligibility view
- Scheme search with eligibility filter

---

### AI-PLATFORM-04: Auto Intimation & Consent ✅

**Purpose:** Automatically notify eligible citizens and capture consent for scheme enrollment

**Key Capabilities:**
- Automated intimation scheduling
- Multi-channel notifications (SMS, App Push, Web Inbox)
- Consent capture (Yes/No/More Info)
- Consent lifecycle management
- Campaign management
- Fatigue management
- Response rate tracking

**REST APIs:**
```
POST /api/v1/intimation/schedule - Register eligible candidates for auto intimation
GET  /api/v1/intimation/status?family_id={id} - Get pending/completed intimations
POST /api/v1/intimation/retry?campaign_id={id} - Trigger retry for pending intimations
GET  /api/v1/intimation/campaigns - List active campaigns with metrics

POST /api/v1/consent/capture - Record citizen response (Yes/No/More info)
GET  /api/v1/consent/status?family_id={id}&scheme_id={id} - Get consent status
POST /api/v1/consent/revoke - Revoke existing consent
GET  /api/v1/consent/history?family_id={id} - Get consent history
```

**Request/Response Examples:**
```json
// POST /api/v1/consent/capture
Request: {
  "family_id": "uuid",
  "scheme_id": "uuid",
  "response": "YES",  // YES, NO, MORE_INFO
  "captured_via": "WEB_PORTAL",
  "ip_address": "string",
  "user_agent": "string"
}

Response: {
  "success": true,
  "consent_id": "uuid",
  "consent_status": "GIVEN",
  "consent_date": "2024-12-30T12:00:00Z",
  "expiry_date": "2025-12-30T12:00:00Z"
}

// GET /api/v1/intimation/status
Response: {
  "family_id": "uuid",
  "pending_intimations": [
    {
      "intimation_id": "uuid",
      "scheme_code": "OAP001",
      "scheme_name": "Old Age Pension",
      "sent_at": "2024-12-30T09:00:00Z",
      "channel": "SMS",
      "status": "DELIVERED"
    }
  ],
  "consent_pending": [...]
}
```

**Data Output:**
- Intimation records (sent, delivered, opened)
- Consent status (GIVEN, REJECTED, REVOKED, EXPIRED)
- Consent history
- Campaign metrics

**Integration Points:**
- Input: Eligibility results (AI-PLATFORM-03)
- Output: Triggers Auto Application Submission (AI-PLATFORM-05) on CONSENT_GIVEN

**Portal Screen Mapping Potential:**
- Notifications/inbox screen
- Consent requests/approvals
- Notification preferences
- Consent history
- Campaign notifications

---

### AI-PLATFORM-05: Auto Application Submission ⏳

**Purpose:** Automatically create and submit scheme applications post-consent with minimal manual input

**Key Capabilities:**
- Automatic application creation on consent
- Form pre-filling from Golden Records & 360° Profiles
- Field mapping (direct, derived, relationship-based)
- Data validation (syntactic, semantic, completeness)
- Multiple submission modes (auto, review, assisted)
- Department connector integration (REST/SOAP/API Setu)
- Audit trail and source tracking

**REST APIs:**
```
POST /api/v1/applications/create - Create application from consent
GET  /api/v1/applications/{application_id} - Get application details
POST /api/v1/applications/{application_id}/submit - Submit application
GET  /api/v1/applications?family_id={id} - List applications for family
GET  /api/v1/applications/{application_id}/status - Get submission status
POST /api/v1/applications/{application_id}/review - Submit after citizen review
```

**Request/Response Examples:**
```json
// POST /api/v1/applications/create
Request: {
  "consent_id": "uuid",
  "family_id": "uuid",
  "scheme_code": "OAP001",
  "submission_mode": "AUTO"  // AUTO, REVIEW, ASSISTED
}

Response: {
  "success": true,
  "application_id": "uuid",
  "status": "CREATED",
  "mapped_fields": 25,
  "missing_fields": 2,
  "validation_errors": [],
  "prefilled_data": {...},
  "requires_review": false
}

// GET /api/v1/applications/{application_id}
Response: {
  "application_id": "uuid",
  "family_id": "uuid",
  "scheme_code": "OAP001",
  "status": "SUBMITTED",
  "submission_mode": "AUTO",
  "mapped_fields_count": 25,
  "field_sources": {
    "dob": "GOLDEN_RECORD",
    "income_band": "360_PROFILE"
  },
  "submitted_at": "2024-12-30T12:00:00Z",
  "department_application_number": "APP123456"
}
```

**Data Output:**
- Application records
- Field-level source tracking
- Validation results
- Submission status
- Department responses

**Integration Points:**
- Input: Consent events (AI-PLATFORM-04), Golden Records, 360° Profiles
- Output: Applications sent to departments, triggers Auto Approval (AI-PLATFORM-06)

**Portal Screen Mapping Potential:**
- Application submission screen
- Form prefill/preview
- Application status tracking
- Draft applications
- Application history
- Document upload (for missing fields)

**Status:** ⚠️ Configuration complete, needs external department API integration

---

### AI-PLATFORM-06: Auto Approval & Straight-through Processing ✅

**Purpose:** Automatically approve low-risk applications and route others appropriately

**Key Capabilities:**
- Rule-based evaluation (eligibility, authenticity, documents)
- Risk scoring (ML-based with rule fallback)
- Decision routing (AUTO_APPROVE, ROUTE_TO_OFFICER, ROUTE_TO_FRAUD, AUTO_REJECT)
- Explainable decisions
- Payment triggers for auto-approved cases
- Officer worklist routing

**REST APIs:**
```
POST /api/v1/decision/evaluateApplication - Evaluate an application
GET  /api/v1/decision/history?applicationId={id} - Get decision history
GET  /api/v1/decision/{decisionId} - Get decision details
POST /api/v1/decision/override - Override a decision (officer)
GET  /api/v1/decision/family/{familyId} - Get decisions by family
GET  /api/v1/decision/scheme/{schemeCode} - Get decisions by scheme
GET  /api/v1/decision/metrics/stp - Get STP performance metrics
```

**Request/Response Examples:**
```json
// POST /api/v1/decision/evaluateApplication
Request: {
  "application_id": "uuid",
  "scheme_code": "OAP001",
  "family_id": "uuid"
}

Response: {
  "success": true,
  "decision_id": "uuid",
  "application_id": "uuid",
  "decision": "AUTO_APPROVED",  // AUTO_APPROVED, ROUTE_TO_OFFICER, ROUTE_TO_FRAUD, AUTO_REJECTED
  "risk_score": 0.15,
  "confidence": 0.95,
  "reasons": [
    "All eligibility rules passed",
    "Low risk score (0.15)",
    "All documents verified"
  ],
  "rule_evaluations": [...],
  "payment_triggered": true,
  "officer_routing": null
}
```

**Data Output:**
- Decision status
- Risk scores
- Decision explanations
- Rule evaluation details
- Payment trigger status
- Routing information

**Integration Points:**
- Input: Applications (AI-PLATFORM-05)
- Output: Payment triggers, officer worklists

**Portal Screen Mapping Potential:**
- Application status/decision screen
- Approval notifications
- Decision explanations
- Payment status
- Review requests

---

### AI-PLATFORM-07: Ineligible/Mistargeted Beneficiary Detection ✅

**Purpose:** Detect beneficiaries who may be ineligible or mistargeted after enrollment

**Key Capabilities:**
- Rule-based detection (eligibility, income, geography)
- ML anomaly detection (Isolation Forest)
- Case classification and prioritization
- Officer worklist assignment
- Verification workflow
- Leakage analytics

**REST APIs:**
```
POST /api/v1/detection/run - Start a detection run
GET  /api/v1/detection/run/{runId} - Get detection run details
GET  /api/v1/detection/runs - List detection runs
GET  /api/v1/detection/case/{caseId} - Get detected case details
GET  /api/v1/detection/cases - List detected cases (with filters)
POST /api/v1/detection/case/{caseId}/verify - Verify a detected case
GET  /api/v1/detection/worklist - Get worklist for officer
POST /api/v1/detection/worklist/assign - Assign case to officer
GET  /api/v1/detection/analytics - Get leakage analytics
POST /api/v1/detection/detect - Detect single beneficiary (on-demand)
```

**Request/Response Examples:**
```json
// GET /api/v1/detection/cases
Query Params: schemeCode, caseType, status, priority, limit

Response: {
  "cases": [
    {
      "case_id": "uuid",
      "family_id": "uuid",
      "scheme_code": "OAP001",
      "case_type": "INELIGIBLE_INCOME",
      "status": "PENDING_VERIFICATION",
      "priority": "HIGH",
      "detection_reasons": [
        "Income exceeds threshold",
        "Anomaly score: 0.85"
      ],
      "detected_at": "2024-12-30T12:00:00Z"
    }
  ],
  "total": 150
}
```

**Data Output:**
- Detected cases
- Case classifications
- Priority rankings
- Detection reasons
- Verification results

**Integration Points:**
- Input: Current beneficiaries, scheme rules, 360° Profiles
- Output: Officer worklists, case verification

**Portal Screen Mapping Potential:**
- Case alerts/notifications
- Verification requests
- Case details view
- Citizen response to cases

---

### AI-PLATFORM-08: Eligibility Checker & Recommendations ✅

**Purpose:** Real-time eligibility checking with personalized recommendations and explanations

**Key Capabilities:**
- Real-time eligibility checking (logged-in, guest, anonymous)
- Questionnaire-based eligibility for guests
- Scheme ranking and prioritization
- Human-readable explanations (NLG)
- Personalized recommendations
- Multi-language support

**REST APIs:**
```
POST /api/v1/eligibility/check - Perform eligibility check
GET  /api/v1/eligibility/recommendations?family_id={id} - Get recommendations
GET  /api/v1/eligibility/questionnaire?template_name={name} - Get questionnaire
GET  /api/v1/eligibility/schemes/{schemeCode} - Check specific scheme
GET  /api/v1/eligibility/history?family_id={id} - Get check history
```

**Request/Response Examples:**
```json
// POST /api/v1/eligibility/check
Request: {
  "familyId": "uuid",  // optional for logged-in users
  "beneficiaryId": "string",  // optional
  "sessionId": "string",  // for guest/anonymous
  "checkType": "FULL_CHECK",
  "checkMode": "WEB",
  "schemeCodes": ["SCHEME1"],  // optional
  "questionnaireResponses": {  // for guest users
    "age": 65,
    "income_band": "Below 5000",
    "district": "Jaipur"
  },
  "language": "en"
}

Response: {
  "success": true,
  "checkId": 123,
  "userType": "LOGGED_IN",
  "totalSchemesChecked": 10,
  "eligibleCount": 3,
  "topRecommendations": [
    {
      "schemeCode": "OAP001",
      "schemeName": "Old Age Pension",
      "eligibilityStatus": "ELIGIBLE",
      "score": 0.92,
      "explanation": "You are eligible because...",
      "priority": "HIGH"
    }
  ],
  "otherSchemes": [...]
}
```

**Data Output:**
- Eligibility results per scheme
- Recommendations (ranked)
- Explanations (human-readable)
- Questionnaire templates
- Check history

**Integration Points:**
- Input: Golden Records, 360° Profiles, Eligibility Engine (AI-PLATFORM-03)
- Output: Recommendations for citizen portal

**Portal Screen Mapping Potential:**
- Eligibility checker widget
- Recommendations dashboard
- Scheme search with eligibility
- Guest eligibility checker
- Eligibility explanations

---

### AI-PLATFORM-09: Proactive Inclusion & Exception Handling ✅

**Purpose:** Identify citizens missing from schemes and generate proactive inclusion nudges

**Key Capabilities:**
- Inclusion gap scoring (who should be enrolled but isn't)
- Exception pattern detection (ML-based)
- Priority household identification
- Nudge generation for outreach
- Exception review workflows

**REST APIs:**
```
POST /api/v1/inclusion/calculate-gaps - Calculate inclusion gaps
GET  /api/v1/inclusion/households?priority={level} - Get priority households
GET  /api/v1/inclusion/exceptions?type={type} - Get detected exceptions
POST /api/v1/inclusion/generate-nudges - Generate outreach nudges
GET  /api/v1/inclusion/analytics - Get inclusion analytics
```

**Request/Response Examples:**
```json
// GET /api/v1/inclusion/households
Response: {
  "households": [
    {
      "family_id": "uuid",
      "inclusion_score": 0.85,
      "priority": "HIGH",
      "missing_schemes": ["OAP001", "PDS001"],
      "exception_flags": ["LOW_INCOME", "ELDERLY"],
      "recommended_actions": [
        "Outreach via field worker",
        "Priority enrollment"
      ]
    }
  ]
}
```

**Data Output:**
- Inclusion gap scores
- Priority household lists
- Exception patterns
- Nudge recommendations
- Inclusion analytics

**Integration Points:**
- Input: 360° Profiles, current enrollments, scheme rules
- Output: Nudges (AI-PLATFORM-11), outreach worklists

**Portal Screen Mapping Potential:**
- Inclusion alerts
- Missing scheme notifications
- Priority enrollment offers
- Outreach invitations

---

### AI-PLATFORM-10: Entitlement & Benefit Forecast ✅

**Purpose:** Predict future entitlements and benefit amounts for financial planning

**Key Capabilities:**
- Baseline forecasting (current schemes projected forward)
- Scenario-aware forecasting (status quo, recommendations, policy changes)
- Time-series forecasting (ARIMA for aggregate)
- ML probability estimation
- Life stage event integration
- Aggregate forecasting (district/state level)

**REST APIs:**
```
GET  /api/v1/forecast/benefits?family_id={id}&horizon={months} - Get benefit forecast
GET  /api/v1/forecast/scenarios?family_id={id}&scenario={name} - Get scenario forecast
GET  /api/v1/forecast/aggregate?level={block|district|state} - Get aggregate forecasts
POST /api/v1/forecast/refresh?family_id={id} - Trigger forecast refresh
GET  /api/v1/forecast/probabilities?family_id={id} - Get ML probability estimates
```

**Request/Response Examples:**
```json
// GET /api/v1/forecast/benefits
Response: {
  "forecast_id": "uuid",
  "family_id": "uuid",
  "horizon_months": 12,
  "forecast_type": "BASELINE",
  "total_annual_value": 72000,
  "total_forecast_value": 72000,
  "scheme_count": 3,
  "uncertainty_level": "LOW",
  "projections": [
    {
      "scheme_code": "OAP001",
      "scheme_name": "Old Age Pension",
      "period_start": "2024-01-01",
      "period_end": "2024-12-31",
      "benefit_amount": 6000,
      "benefit_frequency": "MONTHLY",
      "probability": 0.95
    }
  ]
}
```

**Data Output:**
- Forecast records
- Projections (monthly/quarterly/annual)
- Scenario comparisons
- Probability estimates
- Uncertainty levels

**Integration Points:**
- Input: 360° Profiles, Eligibility Engine, Eligibility Checker
- Output: Financial planning views for citizens

**Portal Screen Mapping Potential:**
- Financial planning dashboard
- Benefit forecast cards
- Scenario comparison
- Future benefits timeline
- Planning tools

---

### AI-PLATFORM-11: Personalized Communication & Nudging ✅

**Purpose:** Optimize reminders and informational messages with ML-based channel, timing, and content selection

**Key Capabilities:**
- ML-based channel optimization (SMS, App Push, Web Inbox, WhatsApp, IVR, Assisted Visit)
- Send time optimization (morning/afternoon/evening)
- Content personalization (bandit algorithms, A/B testing)
- Fatigue management (frequency limits, vulnerability adjustments)
- Multi-channel support
- Feedback loop for continuous learning

**REST APIs:**
```
POST /api/v1/nudges/schedule - Schedule a nudge
GET  /api/v1/nudges/history?family_id={id} - Get nudge history
POST /api/v1/nudges/{nudge_id}/feedback - Record feedback event
GET  /api/v1/nudges/active?family_id={id} - Get active nudges
GET  /api/v1/nudges/preferences?family_id={id} - Get/update preferences
```

**Request/Response Examples:**
```json
// POST /api/v1/nudges/schedule
Request: {
  "action_type": "renewal",  // renewal, missing_doc, consent, deadline, informational
  "family_id": "uuid",
  "urgency": "HIGH",  // CRITICAL, HIGH, MEDIUM, LOW
  "expiry_date": "2024-01-15T23:59:59Z",
  "action_context": {
    "scheme_name": "Old Age Pension",
    "scheme_code": "OAP001",
    "deadline": "2024-01-15"
  }
}

Response: {
  "success": true,
  "nudge_id": "uuid",
  "scheduled_channel": "SMS",
  "scheduled_time": "2024-01-10T09:00:00Z",
  "template_id": "uuid",
  "personalized_content": "Dear Citizen, your Old Age Pension renewal is due..."
}

// GET /api/v1/nudges/history
Response: {
  "nudges": [
    {
      "nudge_id": "uuid",
      "action_type": "renewal",
      "channel": "SMS",
      "status": "DELIVERED",
      "scheduled_time": "2024-01-10T09:00:00Z",
      "sent_at": "2024-01-10T09:00:15Z",
      "delivered_at": "2024-01-10T09:00:30Z",
      "opened_at": null,
      "responded_at": null
    }
  ]
}
```

**Data Output:**
- Nudge records
- Channel preferences
- Send time preferences
- Template effectiveness
- Feedback events (delivered, opened, clicked, responded)

**Integration Points:**
- Input: Application events, deadlines, consent events
- Output: Multi-channel notifications

**Portal Screen Mapping Potential:**
- Inbox/notifications screen
- Nudge preferences
- Reminder management
- Notification history
- Channel preferences

---

## Integration Patterns

### Common Data Flow Patterns

1. **Eligibility Discovery Flow:**
   ```
   Profile Screen → AI-PLATFORM-03 (Eligibility Identification) 
   → Display eligibility hints → AI-PLATFORM-04 (Intimation)
   → Consent screen → AI-PLATFORM-05 (Application)
   ```

2. **Application Processing Flow:**
   ```
   Application Submission → AI-PLATFORM-05 (Auto Submission)
   → AI-PLATFORM-06 (Auto Approval) → Status screen
   → Payment notification
   ```

3. **Proactive Outreach Flow:**
   ```
   AI-PLATFORM-09 (Inclusion Detection) → AI-PLATFORM-11 (Nudging)
   → Inbox/Notification → Eligibility Checker (AI-PLATFORM-08)
   ```

4. **Profile Enhancement Flow:**
   ```
   Profile Screen → AI-PLATFORM-02 (360° Profile)
   → Income inference, eligibility scores → Display on profile
   ```

---

## Data Requirements Summary

### Required Inputs for Portal Integration

1. **Family/Citizen ID** - Primary identifier (UUID or string)
2. **Session ID** - For guest/anonymous users
3. **Language Code** - For multi-language support (en, hi, ta, etc.)
4. **Scheme Codes** - Optional filters for scheme-specific queries

### Common Response Structures

- **Eligibility Results:** Status, score, confidence, explanations
- **Recommendations:** Ranked list with priorities
- **Forecasts:** Projections with amounts, periods, probabilities
- **Nudges:** Channel, content, timing, status
- **Applications:** Status, decisions, field sources

---

## Authentication & Authorization

**Current Status:** All APIs support authentication (to be integrated with portal auth)

**Recommended Approach:**
- Use portal's existing authentication tokens
- Pass as Bearer token in Authorization header
- Session-based auth for guest users (session_id)

---

## Error Handling

**Standard Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {...}
}
```

**Common Error Codes:**
- `FAMILY_NOT_FOUND`
- `SCHEME_NOT_FOUND`
- `INVALID_REQUEST`
- `SERVICE_UNAVAILABLE`
- `RATE_LIMIT_EXCEEDED`

---

## Performance Considerations

### Response Time Targets
- Eligibility checks: < 200ms
- Profile retrieval: < 300ms
- Forecast generation: < 2 seconds
- Nudge scheduling: < 500ms

### Caching Recommendations
- Precomputed eligibility results (7-day cache)
- Profile data (1-hour cache)
- Forecast data (24-hour cache)
- Scheme configurations (static cache)

---

## Next Steps for Portal Agent

1. **Review this matrix** - Understand capabilities of each use case
2. **Review Citizen Portal SRS** - Identify screen requirements
3. **Create Mapping Document** - Map screens to use cases (see template below)
4. **Identify Integration Points** - Where to call which APIs
5. **Define Data Flow** - Sequence of API calls per screen
6. **Create Integration Plan** - Phased integration approach

---

## Portal Screen Mapping Template

Use this template when creating the mapping document:

```markdown
### Screen [N]: [Screen Name]

**Screen ID:** [e.g., CIT-PROF-01]  
**Purpose:** [Brief description]

**AI/ML Use Cases Used:**
- AI-PLATFORM-XX: [How it's used]
- AI-PLATFORM-YY: [How it's used]

**API Calls:**
1. `GET /api/v1/...` - [Purpose]
2. `POST /api/v1/...` - [Purpose]

**Data Flow:**
1. [Step 1]
2. [Step 2]

**UI Components:**
- [Component 1] - Shows [data from use case X]
- [Component 2] - Shows [data from use case Y]

**User Actions:**
- [Action 1] → Triggers [API call]
- [Action 2] → Triggers [API call]
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Maintained By:** AI/ML Platform Team  
**Next Review:** After Portal Agent creates mapping document

