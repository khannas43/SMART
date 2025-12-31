# Technical Design Document: AI-driven Eligibility Checker & Recommendations

**Use Case ID:** AI-PLATFORM-08  
**Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** Core Implementation Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [Component Design](#component-design)
5. [Eligibility Checking Logic](#eligibility-checking-logic)
6. [Scheme Ranking & Recommendations](#scheme-ranking--recommendations)
7. [Explanation Generation](#explanation-generation)
8. [Questionnaire Handling](#questionnaire-handling)
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
19. [Web Interface](#web-interface)
20. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose

The AI-driven Eligibility Checker & Recommendations system provides an interactive tool (web/app/chatbot) where citizens can quickly see which schemes they are eligible for, might be eligible for, or are ineligible for, with clear explanations and next steps. The system uses ML and rule logic from Auto Identification (AI-PLATFORM-03) plus 360° profiles (AI-PLATFORM-02) to rank "best fit" schemes and personalize recommendations, not just list everything.

### 1.2 Key Capabilities

1. **Eligibility Checking**
   - **Logged-in Users**: Direct eligibility evaluation using Golden Record + 360° Profile
   - **Guest Users**: Questionnaire-based eligibility checking with approximate results
   - **Anonymous Mode**: Basic eligibility checks with limited accuracy

2. **Scheme Ranking & Recommendations**
   - Priority scoring based on eligibility, impact, under-coverage, and time sensitivity
   - Top recommendations (short list) and other potentially relevant schemes
   - Filters by domain, department, family member, time effort

3. **Explanation Generation**
   - Human-readable explanations in simple language
   - Available in multiple languages (English, Hindi, etc.)
   - Shows why eligible/not eligible with next steps

4. **Questionnaire System**
   - Guest user questionnaires for approximate eligibility
   - Multi-language questionnaire templates
   - Privacy-conscious data collection

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for eligibility checking, ranking, explanation generation
- **ML Integration**: Uses AI-PLATFORM-03 eligibility engine and ML models
- **Database**: PostgreSQL 14+ (`smart_warehouse.eligibility_checker` schema)
- **Integration**: Golden Records, 360° Profiles, Eligibility Engine, Scheme Master
- **Frontend**: Web viewer, portal/app integration ready

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input Sources                                 │
├─────────────────────────────────────────────────────────────────┤
│  LOGGED_IN USER      │  GUEST USER       │  ANONYMOUS USER     │
│  (Family ID)         │  (Questionnaire)  │  (Questionnaire)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Eligibility Checker & Recommendations              │
├─────────────────────────────────────────────────────────────────┤
│  EligibilityChecker  │  SchemeRanker    │  ExplanationGenerator│
│  (Main Service)      │  (Priority Score)│  (NLG Templates)     │
│                      │                   │                      │
│  QuestionnaireHandler│  EligibilityOrchestrator                 │
│  (Guest Support)     │  (End-to-End Workflow)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Output                                        │
├─────────────────────────────────────────────────────────────────┤
│  Recommendations     │  Explanations     │  Eligibility Status │
│  (Ranked Schemes)    │  (Human-Readable) │  (Per Scheme)       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Flow

```
AI-PLATFORM-03 (Eligibility Engine)
         ↓
EligibilityChecker (AI-PLATFORM-08)
    ├── Uses rule-based evaluation
    ├── Uses ML-based scoring
    └── Formats results for recommendations
         ↓
SchemeRanker (AI-PLATFORM-08)
    ├── Combines eligibility scores
    ├── Adds impact/urgency scores
    ├── Adds under-coverage boost (AI-PLATFORM-02)
    └── Ranks schemes
         ↓
ExplanationGenerator (AI-PLATFORM-08)
    ├── Uses NLG templates
    ├── Multi-language support
    └── Generates human-readable explanations
         ↓
Recommendations (Ranked, Explained)
```

---

## 3. Data Architecture

### 3.1 Database Schema (`eligibility_checker`)

**8 Tables:**

1. **eligibility_checks**: Main check records
   - check_id, session_id, user_type, family_id, beneficiary_id
   - check_timestamp, completed_timestamp, status
   - total_schemes_checked, eligible_count, possible_eligible_count, not_eligible_count
   - processing_time_ms, language

2. **scheme_eligibility_results**: Individual scheme results
   - check_id, scheme_code, eligibility_status, eligibility_score, confidence_score
   - is_approximate, rule_paths, ml_features, ml_prediction, ml_probability
   - language, family_id, beneficiary_id

3. **recommendation_sets**: Generated recommendation sets
   - recommendation_id, check_id, family_id, beneficiary_id
   - recommendation_timestamp, language

4. **recommendation_items**: Individual schemes in recommendations
   - recommendation_id, scheme_code, scheme_name, eligibility_status
   - eligibility_score, confidence_score, priority_score
   - explanation, is_top_recommendation

5. **questionnaire_templates**: Questionnaire templates
   - template_name, description, language, template_content (JSON)
   - is_active, created_at

6. **explanation_templates**: NLG templates for explanations
   - template_name, language, template_content (Jinja2)
   - is_active, created_at

7. **eligibility_check_analytics**: Aggregated analytics
   - analytics_date, user_type, total_checks, eligible_count, etc.

8. **eligibility_checker_audit_logs**: Audit logs
   - audit_id, event_type, event_timestamp, actor_type, actor_id
   - check_id, event_description, event_data

### 3.2 External Data Sources

- **Golden Records** (AI-PLATFORM-01): Identity, demographics, family data
- **360° Profiles** (AI-PLATFORM-02): Vulnerability, under-coverage indicators
- **Eligibility Engine** (AI-PLATFORM-03): Eligibility evaluation service
- **Scheme Master**: Scheme metadata, benefit values, criticality scores

---

## 4. Component Design

### 4.1 EligibilityChecker

**Location:** `src/services/eligibility_checker.py` (500+ lines)

**Responsibilities:**
- Perform eligibility checks for logged-in, guest, and anonymous users
- Integrate with AI-PLATFORM-03 eligibility engine
- Handle questionnaire-based evaluation for guests
- Record check results and analytics

**Key Methods:**
- `check_eligibility(user_type, family_id, questionnaire_answers, scheme_codes, session_id, language)` - Main check method
- `_check_logged_in_user(family_id, scheme_codes)` - Uses AI-PLATFORM-03 engine
- `_check_guest_user(questionnaire_responses, scheme_codes)` - Questionnaire-based evaluation
- `_simulate_family_data_from_questionnaire(answers)` - Convert questionnaire to family data
- `_format_ai03_result(eval_result, ...)` - Format AI-PLATFORM-03 results
- `_log_eligibility_check_start/end()` - Audit logging

### 4.2 SchemeRanker

**Location:** `src/models/scheme_ranker.py` (250+ lines)

**Responsibilities:**
- Rank schemes based on multiple factors
- Calculate priority scores
- Separate top recommendations from other schemes

**Key Methods:**
- `rank_schemes(eligibility_results, family_id, beneficiary_id, language)` - Main ranking method
- `_get_scheme_metadata(scheme_codes)` - Fetch scheme metadata
- `_get_under_coverage_boost(family_id, scheme_code)` - Get under-coverage boost (AI-PLATFORM-02)

**Ranking Weights (Configurable):**
- eligibility_score: 0.5
- impact_score: 0.3
- urgency_score: 0.1
- under_coverage_boost: 0.1

### 4.3 ExplanationGenerator

**Location:** `src/generators/explanation_generator.py` (250+ lines)

**Responsibilities:**
- Generate human-readable explanations using NLG templates
- Support multiple languages
- Provide fallback explanations

**Key Methods:**
- `generate_explanation(scheme_code, eligibility_status, rule_paths, ml_features, language, is_approximate)` - Main explanation generation
- `_load_explanation_templates()` - Load templates from database
- `_generate_fallback_explanation(...)` - Fallback when template missing

**Template Structure:**
- Uses Jinja2 templates
- Context: scheme_code, eligibility_status, met_rules, unmet_rules, ml_features
- Language-specific templates

### 4.4 QuestionnaireHandler

**Location:** `src/services/questionnaire_handler.py` (100+ lines)

**Responsibilities:**
- Manage questionnaire templates
- Retrieve templates by language
- List available templates

**Key Methods:**
- `get_questionnaire_template(template_name, language)` - Get template
- `list_questionnaire_templates()` - List all templates

### 4.5 EligibilityOrchestrator

**Location:** `src/services/eligibility_orchestrator.py` (350+ lines)

**Responsibilities:**
- Coordinate end-to-end workflow
- Orchestrate EligibilityChecker, SchemeRanker, ExplanationGenerator
- Save recommendation sets
- Provide history and recommendations retrieval

**Key Methods:**
- `perform_eligibility_check(user_type, family_id, questionnaire_answers, ...)` - Main orchestration
- `get_recommendations(family_id, beneficiary_id, limit, language)` - Get saved recommendations
- `get_questionnaire(template_name, language)` - Get questionnaire template
- `get_eligibility_history(family_id, session_id, limit)` - Get check history
- `_save_recommendation_set(...)` - Persist recommendations

---

## 5. Eligibility Checking Logic

### 5.1 Logged-in User Flow

```
1. User provides family_id
   ↓
2. EligibilityChecker calls AI-PLATFORM-03 EligibilityEvaluationService
   ↓
3. AI-PLATFORM-03 returns:
   - Per-scheme eligibility status (ELIGIBLE, POSSIBLE_ELIGIBLE, NOT_ELIGIBLE)
   - Eligibility scores and confidence
   - Rule paths (met/unmet rules)
   - ML predictions and probabilities
   ↓
4. EligibilityChecker formats results
   ↓
5. Results stored in eligibility_checks and scheme_eligibility_results tables
```

### 5.2 Guest User Flow

```
1. User provides questionnaire answers
   ↓
2. QuestionnaireHandler validates answers
   ↓
3. EligibilityChecker converts questionnaire to simulated family data
   ↓
4. EligibilityChecker calls AI-PLATFORM-03 with simulated data
   ↓
5. Results marked as "approximate" (is_approximate = true)
   ↓
6. User prompted to log in for accurate results
   ↓
7. Results stored (with approximate flag)
```

### 5.3 Anonymous User Flow

Similar to guest, but:
- No session tracking
- Results are even more approximate
- Stronger prompts to log in for accuracy

### 5.4 Eligibility Status Values

- **ELIGIBLE**: Meets all mandatory rules, high confidence
- **POSSIBLE_ELIGIBLE**: Meets most rules, may need verification
- **NOT_ELIGIBLE**: Does not meet eligibility criteria

---

## 6. Scheme Ranking & Recommendations

### 6.1 Priority Score Calculation

**Formula:**
```
priority_score = (
    eligibility_score * 0.5 +
    impact_score * 0.3 +
    urgency_score * 0.1 +
    under_coverage_boost * 0.1
)
```

**Components:**

1. **Eligibility Score** (0-1): From AI-PLATFORM-03
   - Normalized eligibility score
   - Higher = more eligible

2. **Impact Score** (0-1): Based on scheme benefit value and criticality
   - benefit_value * criticality_score (normalized)
   - Higher = more impactful

3. **Urgency Score** (0-1): Time sensitivity
   - Health/food schemes: 0.8
   - Education schemes: 0.5
   - Other: 0.0

4. **Under-Coverage Boost** (0-1): From AI-PLATFORM-02
   - Indicates household is under-covered
   - Higher = more need

### 6.2 Recommendation Structure

**Top Recommendations:**
- Highest priority_score schemes
- Default: Top 5 (configurable)
- Displayed prominently

**Other Schemes:**
- Remaining eligible/possible eligible schemes
- Lower priority but still relevant

### 6.3 Filters (Future Enhancement)

- Domain (health, education, pension, etc.)
- Department
- Family member (head, children, elderly)
- Time effort required

---

## 7. Explanation Generation

### 7.1 NLG Template System

**Template Categories:**
- `eligible_explanation` - For ELIGIBLE status
- `possible_eligible_explanation` - For POSSIBLE_ELIGIBLE status
- `not_eligible_explanation` - For NOT_ELIGIBLE status

**Template Variables:**
- `scheme_code` - Scheme identifier
- `eligibility_status` - Current status
- `is_approximate` - Whether result is approximate
- `met_rules` - List of rules met
- `unmet_rules` - List of rules not met
- `possible_rules` - List of rules possibly met
- `ml_features` - ML feature values (for technical details)

### 7.2 Example Explanations

**ELIGIBLE:**
> "For [SCHEME_NAME], your eligibility status is eligible. You meet criteria such as: age requirement, income threshold, geographic location. You can proceed with application."

**POSSIBLE_ELIGIBLE:**
> "For [SCHEME_NAME], your eligibility status is possibly eligible. Further verification might be needed. Please check the application details or contact the department."

**NOT_ELIGIBLE:**
> "For [SCHEME_NAME], your eligibility status is not eligible. You do not meet criteria such as: income threshold, age requirement. Please review your details or contact the department for more information."

### 7.3 Multi-Language Support

- Templates stored per language
- Fallback to English if language not available
- Supports: English, Hindi (extensible)

---

## 8. Questionnaire Handling

### 8.1 Questionnaire Structure

**Default Questionnaire Fields:**
- Age
- Gender
- District/State
- Annual Income
- Income Group (BPL, APL, etc.)
- Family Size
- Disability Status
- Occupation
- Has Ration Card

### 8.2 Questionnaire to Family Data Mapping

**Mapping Logic:**
- Age → date_of_birth (approximate)
- Gender → gender
- District → address_district
- Annual Income → family_income_annual
- Income Group → is_bpl
- Family Size → family_size
- Disability Status → disability_status

### 8.3 Guest User Limitations

- Results marked as approximate
- Limited to questionnaire fields
- No access to full Golden Record
- Prompts to log in for accurate results

---

## 9. API Design

### 9.1 Spring Boot REST APIs

**Base URL:** `/eligibility`

#### 9.1.1 POST /eligibility/check

**Purpose:** Perform eligibility check for logged-in, guest, or anonymous user

**Request Body:**
```json
{
  "userType": "LOGGED_IN" | "GUEST" | "ANONYMOUS",
  "familyId": "uuid",
  "beneficiaryId": "string",
  "questionnaireAnswers": {
    "age": 35,
    "gender": "FEMALE",
    "district": "Jaipur",
    ...
  },
  "schemeCodes": ["SCHEME_001", "SCHEME_002"],
  "sessionId": "string",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "checkId": 123,
  "userType": "LOGGED_IN",
  "isApproximate": false,
  "totalSchemesChecked": 5,
  "eligibleCount": 2,
  "possibleEligibleCount": 2,
  "notEligibleCount": 1,
  "processingTimeMs": 450,
  "topRecommendations": [...],
  "otherSchemes": [...],
  "allEvaluations": [...]
}
```

#### 9.1.2 GET /eligibility/recommendations

**Purpose:** Get saved recommendations for logged-in user

**Query Parameters:**
- `family_id` (required)
- `beneficiary_id` (optional)
- `limit` (default: 5)
- `language` (default: "en")

**Response:**
```json
{
  "success": true,
  "familyId": "uuid",
  "recommendations": [
    {
      "schemeCode": "SCHEME_001",
      "schemeName": "Scheme Name",
      "eligibilityStatus": "ELIGIBLE",
      "priorityScore": 0.85,
      "explanation": "..."
    }
  ]
}
```

#### 9.1.3 GET /eligibility/questionnaire

**Purpose:** Get questionnaire template

**Query Parameters:**
- `template_name` (default: "default")
- `language` (default: "en")

**Response:**
```json
{
  "success": true,
  "templateName": "default",
  "description": "Default eligibility questionnaire",
  "language": "en",
  "questions": [
    {
      "id": "age",
      "text": "What is your age?",
      "type": "number",
      "required": true
    }
  ]
}
```

#### 9.1.4 GET /eligibility/schemes/{schemeCode}

**Purpose:** Get eligibility for specific scheme

**Query Parameters:**
- `family_id` (optional)
- `beneficiary_id` (optional)
- `session_id` (optional)
- `questionnaire` (optional, JSON string)
- `language` (default: "en")

#### 9.1.5 GET /eligibility/history

**Purpose:** Get eligibility check history

**Query Parameters:**
- `family_id` (optional)
- `session_id` (optional)
- `limit` (default: 10)

---

## 10. Data Flow & Processing Pipeline

### 10.1 End-to-End Flow

```
1. User Request (Logged-in/Guest/Anonymous)
   ↓
2. EligibilityOrchestrator.perform_eligibility_check()
   ↓
3. EligibilityChecker.check_eligibility()
   ├── Log check start
   ├── If LOGGED_IN: Call AI-PLATFORM-03 with family_id
   ├── If GUEST/ANONYMOUS: Convert questionnaire → Call AI-PLATFORM-03
   └── Format results
   ↓
4. For each scheme result:
   ├── ExplanationGenerator.generate_explanation()
   └── Add explanation to result
   ↓
5. SchemeRanker.rank_schemes()
   ├── Calculate priority scores
   ├── Separate top recommendations
   └── Return ranked list
   ↓
6. EligibilityOrchestrator saves:
   ├── eligibility_checks record
   ├── scheme_eligibility_results records
   └── recommendation_sets + recommendation_items (if logged-in)
   ↓
7. Return response with:
   ├── Top recommendations
   ├── Other schemes
   ├── All evaluations
   └── Explanations
```

### 10.2 Caching Strategy (Future)

- Cache scheme metadata (scheme names, benefit values)
- Cache eligibility results for logged-in users (TTL: 24 hours)
- Cache explanation templates in memory

---

## 11. Integration Points

### 11.1 Input Integrations

**AI-PLATFORM-03 (Eligibility Engine):**
- `EligibilityEvaluationService.evaluate_family()`
- Provides: eligibility status, scores, rule paths, ML predictions

**AI-PLATFORM-02 (360° Profile):**
- Under-coverage indicators (future: direct API call)
- Vulnerability flags (indirect via eligibility engine)

**AI-PLATFORM-01 (Golden Record):**
- Family and beneficiary data (indirect via eligibility engine)

**Scheme Master:**
- Scheme metadata (benefit_value, criticality_score)
- Scheme names and descriptions

### 11.2 Output Integrations

**Citizen Portal/App:**
- Displays recommendations with explanations
- Shows eligibility status per scheme
- Prompts to log in for accurate results (for guests)

**Chatbot:**
- Natural language responses using explanations
- Questionnaire collection

**eMitra/Assisted Channels:**
- Field worker access to recommendations
- Questionnaire assistance

---

## 12. Performance & Scalability

### 12.1 Performance Targets

- **Response Time**: < 2 seconds for logged-in users
- **Response Time**: < 3 seconds for guest users (questionnaire processing)
- **Concurrent Users**: Support 100+ concurrent checks
- **Database Queries**: Optimized with indexes

### 12.2 Scalability Considerations

- **Horizontal Scaling**: Stateless services, can scale horizontally
- **Database**: Read replicas for query scaling
- **Caching**: Redis for scheme metadata and templates (future)
- **Async Processing**: Queue-based processing for batch checks (future)

### 12.3 Database Optimization

**Indexes:**
- `eligibility_checks(family_id, check_timestamp)`
- `scheme_eligibility_results(check_id, scheme_code)`
- `recommendation_sets(family_id, recommendation_timestamp)`

---

## 13. Security & Governance

### 13.1 Data Privacy

- **Logged-in Users**: Full data access (with consent)
- **Guest Users**: Limited data collection (questionnaire only)
- **Anonymous Users**: No personal data storage
- **Session Management**: Session IDs for guest tracking

### 13.2 Access Control

- **Authentication**: Required for logged-in users
- **Authorization**: Family data access restricted to family members
- **Rate Limiting**: Per user/IP rate limiting (future)

### 13.3 Data Protection

- **PII Masking**: Family IDs truncated in logs
- **Audit Logging**: All checks logged with timestamps
- **Data Retention**: Configurable retention policies

---

## 14. Compliance & Privacy

### 14.1 Disclaimer for Advisory Results

- Clear disclaimers that results are advisory
- Not a guarantee of eligibility
- Final eligibility determined by departments

### 14.2 Consent for Data Usage

- Guest users: Informed about approximate results
- Anonymous users: Informed about limited accuracy
- Logged-in users: Full consent via portal terms

### 14.3 Periodic Evaluation for Bias

- Monitor recommendation rates across demographics
- Track eligibility check outcomes by segments
- Fairness audits (future)

---

## 15. Deployment Architecture

### 15.1 Components

```
┌─────────────────────────────────────────────────────────┐
│              Spring Boot Application                     │
│  (REST Controllers, Service Layer, Python Client)      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Python Services (WSL/Container)            │
│  EligibilityChecker, SchemeRanker, ExplanationGenerator│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database                         │
│  eligibility_checker schema                             │
└─────────────────────────────────────────────────────────┘
```

### 15.2 Deployment Options

- **Development**: Local Python services, local PostgreSQL
- **Staging**: Docker containers, shared PostgreSQL
- **Production**: Kubernetes pods, managed PostgreSQL, load balancer

---

## 16. Monitoring & Observability

### 16.1 Metrics

- **Check Volume**: Total checks per day/hour
- **User Types**: Distribution of logged-in/guest/anonymous
- **Response Times**: P50, P95, P99 latencies
- **Error Rates**: Failed checks, exceptions
- **Recommendation Rates**: Conversion from check to application

### 16.2 Logging

- **Application Logs**: Eligibility check logs
- **Audit Logs**: All checks with user types, timestamps
- **Error Logs**: Exceptions, failures
- **Performance Logs**: Processing times

### 16.3 Dashboards

- **Eligibility Check Dashboard**: Volume, types, outcomes
- **Recommendation Dashboard**: Top recommended schemes, conversion rates
- **User Dashboard**: Logged-in vs guest usage

---

## 17. Success Metrics

### 17.1 Citizen Usage

- **Total Checks**: Number of eligibility checks performed
- **Unique Users**: Number of unique families/users checking
- **Return Users**: Users checking multiple times
- **Guest vs Logged-in**: Distribution of user types

### 17.2 Accuracy

- **Conversion Rate**: Percentage of recommended schemes leading to applications
- **Accuracy Rate**: Percentage of recommendations confirmed as eligible
- **User Satisfaction**: Feedback scores (future)

### 17.3 Inclusion

- **Awareness**: Increase in scheme awareness
- **Applications from Underserved**: Increase in applications from marginalized groups
- **Geographic Coverage**: Checks from remote areas

---

## 18. Implementation Status

### 18.1 Completed ✅

- ✅ Database schema (8 tables)
- ✅ Configuration files (db_config.yaml, use_case_config.yaml)
- ✅ Core Python services (EligibilityChecker, SchemeRanker, ExplanationGenerator, QuestionnaireHandler, EligibilityOrchestrator)
- ✅ Spring Boot REST APIs (5 endpoints, 3 DTOs)
- ✅ Spring Boot Service Layer (PythonEligibilityClient + EligibilityService)
- ✅ Database setup and initialization
- ✅ Test scripts (check_config.py, test_eligibility_checker.py)
- ✅ Web viewer (http://localhost:5001/ai08)
- ✅ Documentation (README, STATUS_SUMMARY, TESTING_GUIDE, IMPLEMENTATION_SUMMARY)

### 18.2 Pending / Future Enhancements

- ⏳ Technical Design Document completion (this document)
- ⏳ Under-coverage calculation implementation (needs graph store integration)
- ⏳ More explanation templates (multi-language expansion)
- ⏳ Performance optimization (caching, indexing)
- ⏳ Unit tests (incremental testing)

---

## 19. Web Interface

### 19.1 Web Viewer

**URL:** http://localhost:5001/ai08

**Features:**
- Statistics dashboard (total checks, user types, recommendations)
- Recent eligibility checks table
- Top recommendations view
- Scheme eligibility results view

**Technology:** Flask web application integrated into Eligibility Rules Viewer

### 19.2 Portal Integration (Future)

- React components for recommendations display
- Eligibility check widget
- Questionnaire form component
- Explanation display component

---

## 20. Future Enhancements

### 20.1 Advanced Recommendations

- **Collaborative Filtering**: Recommend based on similar users
- **Contextual Recommendations**: Time/season-based recommendations
- **Personalization**: Learn from user behavior

### 20.2 Enhanced Explanations

- **Interactive Explanations**: Click-through to detailed rule paths
- **Visual Explanations**: Charts/graphs for eligibility factors
- **Multi-modal**: Voice explanations, video guides

### 20.3 Advanced Analytics

- **Recommendation Effectiveness**: A/B testing
- **User Journey Analytics**: Track from check to application
- **Demographic Analytics**: Usage patterns by segments

### 20.4 Integration Enhancements

- **Real-time Updates**: WebSocket for live eligibility changes
- **Batch Processing**: Bulk eligibility checks
- **API Gateway**: Centralized API management

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-30  
**Status:** Core Implementation Complete

