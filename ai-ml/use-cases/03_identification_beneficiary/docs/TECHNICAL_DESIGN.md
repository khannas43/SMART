# Technical Design Document: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03  
**Version:** 1.0  
**Last Updated:** 2024-12-27  
**Status:** Implementation Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [ML Model Design](#ml-model-design)
5. [Rule Engine Design](#rule-engine-design)
6. [Hybrid Evaluation Design](#hybrid-evaluation-design)
7. [Prioritization & Ranking Design](#prioritization--ranking-design)
8. [API Design](#api-design)
9. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
10. [Integration Points](#integration-points)
11. [Performance & Scalability](#performance--scalability)
12. [Security & Governance](#security--governance)
13. [Deployment Architecture](#deployment-architecture)
14. [Monitoring & Observability](#monitoring--observability)
15. [Success Metrics](#success-metrics)
16. [Rule Version Control & Historical Tracking](#16-rule-version-control--historical-tracking)
17. [Implementation Status & Completion Checklist](#17-implementation-status--completion-checklist)
18. [Future Enhancements & TODO List](#18-future-enhancements--todo-list)
   - [18.8 Portal Integration & Deployment (Critical for Production)](#188-portal-integration--deployment-critical-for-production)

---

## 1. Executive Summary

### 1.1 Purpose

The Auto Identification of Beneficiaries system automatically identifies citizens/families who are potentially eligible for one or more welfare schemes and services using Jan Aadhaar Resident Data Repository (JRDR) plus seeded departmental databases.

### 1.2 Key Capabilities

1. **Auto Identification Engine**
   - Rule-based eligibility evaluation (deterministic)
   - ML-powered eligibility scoring (probabilistic)
   - Hybrid evaluation combining both approaches
   - Support for 157+ schemes (cash and non-cash)

2. **Prioritization & Ranking**
   - Multi-factor priority scoring
   - Vulnerability-based ranking
   - Under-coverage identification
   - Geographic clustering

3. **Output Generation**
   - Citizen-facing eligibility hints (top 3-5 schemes)
   - Departmental worklists (ranked candidate queues)
   - Eligibility snapshots with explainability

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **ML/Data Science**: Python 3.12+, XGBoost, scikit-learn, SHAP
- **Database**: PostgreSQL 14+ (eligibility, Golden Records, 360° Profiles)
- **MLflow**: Model registry and experiment tracking
- **APIs**: RESTful APIs for evaluation and candidate lists

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources                                  │
├─────────────────────────────────────────────────────────────────┤
│  JRDR │ Golden Records │ 360° Profiles │ Departmental Systems   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Auto Identification Engine                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐                        │
│  │ Rule Engine  │      │  ML Scorer   │                        │
│  │(Deterministic)│      │ (XGBoost)   │                        │
│  └──────┬───────┘      └──────┬───────┘                        │
│         │                     │                                 │
│         └──────────┬──────────┘                                 │
│                    ↓                                             │
│            Hybrid Evaluator                                      │
│         (Rule + ML Combination)                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Prioritization & Ranking                            │
│  (Vulnerability │ Under-Coverage │ Geographic Clustering)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Output Generation                           │
├─────────────────────────────────────────────────────────────────┤
│  • Citizen Hints      • Departmental Worklists                  │
│  • Eligibility Snaps  • Candidate Lists                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Consumer Applications                        │
├─────────────────────────────────────────────────────────────────┤
│  Citizen Portal │ Department Portal │ Auto Intimation Service   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Rule Engine
- **Purpose**: Deterministic eligibility evaluation based on scheme rules
- **Input**: Golden Records + 360° Profile data
- **Output**: RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE
- **Rules Types**: Age, Income, Gender, Geography, Disability, Category, Prior Participation

#### 2.2.2 ML Scorer
- **Purpose**: Probabilistic eligibility scoring using XGBoost
- **Input**: Family/member features
- **Output**: Eligibility probability (0-1) with confidence
- **Features**: Demographics, household composition, income band, assets, geography, historical participation

#### 2.2.3 Hybrid Evaluator
- **Purpose**: Combine rule engine + ML scorer results
- **Method**: Weighted combination (60% rule, 40% ML default)
- **Conflict Resolution**: Conservative approach (rules take precedence for safety)
- **Output**: Final eligibility status with explanations

#### 2.2.4 Prioritizer
- **Purpose**: Rank eligible candidates
- **Factors**: Eligibility score, vulnerability, under-coverage, geographic clustering
- **Output**: Ranked candidate lists, citizen hints, worklists

#### 2.2.5 Evaluation Service
- **Purpose**: Orchestrate evaluation workflows
- **Modes**: Batch (weekly), Event-driven (on changes), On-demand (API)
- **Features**: Progress tracking, error handling, result storage

---

## 3. Data Architecture

### 3.1 Database Schema

#### 3.1.1 Eligibility Schema (`smart_warehouse.eligibility`)

**Database**: `smart_warehouse` (shared with AI-PLATFORM-02: 360° Profiles)  
**Schema**: `eligibility`

**Note**: All AI/ML use cases use the same `smart_warehouse` database with different schemas:
- `smart_warehouse` schema: 360° Profiles tables (AI-PLATFORM-02)
- `eligibility` schema: Eligibility tables (AI-PLATFORM-03)

**Core Tables:**

1. **scheme_master**
   - Scheme metadata (ID, name, category, type)
   - Auto-identification enable flag

2. **scheme_eligibility_rules**
   - Machine-readable eligibility rules
   - Rule types: AGE, INCOME, GENDER, GEOGRAPHY, DISABILITY, CATEGORY, etc.
   - Rule expressions and operators

3. **scheme_exclusion_rules**
   - Exclusion conditions (who is NOT eligible)
   - Examples: already enrolled, income exceeded

4. **eligibility_snapshots**
   - Main table storing evaluation results
   - Per family/scheme evaluations with scores, status, explanations
   - Versioning and audit trail

5. **candidate_lists**
   - Pre-computed worklists
   - Citizen hints, departmental worklists, auto-intimation lists
   - Ranking and prioritization metadata

6. **ml_model_registry**
   - ML model metadata per scheme
   - Model versioning, training metrics, feature lists
   - MLflow run IDs

7. **batch_evaluation_jobs**
   - Batch job tracking
   - Progress monitoring, error tracking

8. **evaluation_audit_log**
   - Audit trail for evaluations
   - Rule changes, model updates, threshold changes

9. **rule_change_history**
   - History of rule modifications
   - Change tracking for governance

10. **consent_status**
    - Consent flags per family/member
    - Eligibility processing consent, proxy data consent

11. **data_quality_indicators**
    - Data quality scores
    - Completeness, accuracy, timeliness indicators

### 3.2 External Data Sources

#### 3.2.1 Golden Records (AI-PLATFORM-01)
- **Database**: `smart` (schema: `golden_record`)
- **Data**: Demographics, family structure, relationships
- **Usage**: Primary identity and household data

#### 3.2.2 360° Profiles (AI-PLATFORM-02)
- **Database**: `smart_warehouse` (schema: `smart_warehouse`)
- **Data**: Income band, vulnerability level, under-coverage indicators, cluster IDs
- **Usage**: Enriched profile data for prioritization

#### 3.2.3 JRDR (Jan Aadhaar)
- **Database**: `smart` (schema: `jrdr`)
- **Data**: Master household and member data
- **Usage**: Authoritative source for family relationships

#### 3.2.4 Departmental Systems
- **Data**: Scheme rules, current beneficiaries, historical disbursements
- **Usage**: Training data, scheme configuration

### 3.3 Data Flow

```
JRDR + Departmental DBs
    ↓
Golden Records (Deduplication)
    ↓
360° Profiles (Enrichment)
    ↓
Auto Identification Engine
    ├── Rule Engine (Deterministic)
    └── ML Scorer (Probabilistic)
    ↓
Hybrid Evaluation Results
    ↓
Prioritization & Ranking
    ↓
Eligibility Snapshots (Database)
    ↓
Candidate Lists / Hints / Worklists
```

---

## 4. ML Model Design

### 4.1 Model Architecture

**Model Type**: XGBoost Classifier (Binary Classification)  
**Output**: Eligibility Probability (0-1)  
**Training**: Per scheme or scheme family

### 4.2 Feature Engineering

#### 4.2.1 Demographic Features
- Age, gender, marital status
- District, block, village
- Urban/rural classification
- Caste/category

#### 4.2.2 Household Features
- Family size
- Household type (nuclear, joint)
- Number of children, elderly
- Number of disabled members
- Head of family attributes

#### 4.2.3 Income & Assets
- Income band (from 360° Profile)
- Inferred income range
- Land holding category
- House type
- Electricity connection
- Bank account

#### 4.2.4 Education & Employment
- Education level
- Employment status
- Employment type
- Skill training

#### 4.2.5 Health & Disability
- Disability status
- Disability type
- Chronic illness
- Health insurance coverage

#### 4.2.6 Prior Participation
- Number of schemes enrolled
- List of enrolled schemes
- Benefits received (1Y, 3Y windows)
- Application rejection count

#### 4.2.7 Proxy Indicators (Optional, with consent)
- Land records value
- Electricity bill amount
- Transaction frequency
- Transport registrations

### 4.3 Model Training

#### 4.3.1 Training Data
- **Source**: Historical application data (approved/rejected)
- **Features**: All features listed above
- **Target**: Binary (eligible=1, not eligible=0)
- **Minimum Samples**: 100 per scheme

#### 4.3.2 Hyperparameters
```yaml
n_estimators: 200
max_depth: 6
learning_rate: 0.1
subsample: 0.8
colsample_bytree: 0.8
min_child_weight: 3
gamma: 0.1
reg_alpha: 0.1
reg_lambda: 1.0
```

#### 4.3.3 Evaluation Metrics
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- PR-AUC (Precision-Recall AUC)

#### 4.3.4 Model Registry
- **Storage**: MLflow Model Registry
- **Versioning**: Automatic version tracking
- **Metadata**: Stored in `ml_model_registry` table
- **Deployment**: Model paths referenced in registry

### 4.4 Explainability

#### 4.4.1 SHAP Values
- Feature importance per prediction
- Top contributing features
- Feature impact direction (positive/negative)

#### 4.4.2 Model Artifacts
- SHAP summary plots
- Feature importance rankings
- Model descriptions

---

## 5. Rule Engine Design

### 5.1 Rule Storage (Not Hard-Coded)

**Rules are database-driven**, not hard-coded in application code:

- **Storage**: `eligibility.scheme_eligibility_rules` table in PostgreSQL
- **Loading**: Rules loaded dynamically from database at runtime
- **Caching**: Rules cached in memory for 24 hours (configurable via `use_case_config.yaml`)
- **Dynamic Updates**: Rules can be added/modified/deleted without code changes
- **Versioning**: Each rule has a version number and effective dates

#### 5.1.1 Rule Table Structure

```sql
CREATE TABLE eligibility.scheme_eligibility_rules (
    rule_id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50), -- AGE, INCOME, GENDER, etc.
    rule_expression TEXT NOT NULL,
    rule_operator VARCHAR(20),
    rule_value TEXT,
    is_mandatory BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.2 Rule Loading Mechanism

```python
# Rules loaded from database (not hard-coded)
rules = rule_engine.load_scheme_rules(scheme_id, force_reload=False)

# Caching strategy:
# - Cache TTL: 24 hours (configurable)
# - Cache key: scheme_id
# - Force reload: Available for immediate rule updates
```

### 5.2 Rule Types

#### 5.2.1 Age-Based Rules
- **Operators**: >=, <=, =
- **Example**: `age >= 60` (pension eligibility)
- **Data Source**: Golden Records (date_of_birth → age)

#### 5.2.2 Income-Based Rules
- **Operators**: IN, NOT_IN
- **Example**: `income_band IN ('VERY_LOW', 'LOW')`
- **Data Source**: 360° Profile (inferred income band)

#### 5.2.3 Gender-Based Rules
- **Operators**: IN, NOT_IN
- **Example**: `gender IN ('Female')` (widow pension)
- **Data Source**: Golden Records

#### 5.2.4 Geography-Based Rules
- **Operators**: DISTRICT_IN, BLOCK_IN
- **Example**: `district_id IN (101, 102, 103)`
- **Data Source**: Golden Records

#### 5.2.5 Category/Caste Rules
- **Operators**: IN, NOT_IN
- **Example**: `caste_id IN (3, 4)` (SC/ST schemes)
- **Data Source**: Golden Records

#### 5.2.6 Disability Rules
- **Operators**: =
- **Example**: `disability_status = TRUE`
- **Data Source**: Golden Records / 360° Profile

#### 5.2.7 Household Composition Rules
- **Operators**: >=, <=
- **Example**: `family_size >= 4`
- **Data Source**: Golden Records (family aggregation)

#### 5.2.8 Prior Participation Rules
- **Operators**: NOT_IN
- **Example**: `schemes_enrolled_list NOT_IN ('SCHEME_001')`
- **Data Source**: Benefit Events

### 5.3 Rule Evaluation Flow

```
1. Load rules for scheme
   ↓
2. Check exclusion rules first
   ↓
3. Evaluate eligibility rules
   ├── Mandatory rules (must pass)
   └── Optional rules (weighted)
   ↓
4. Generate rule path
   ├── Rules passed
   └── Rules failed (with reasons)
   ↓
5. Determine status
   ├── RULE_ELIGIBLE (all mandatory + some optional passed)
   ├── POSSIBLE_ELIGIBLE (some rules passed)
   └── NOT_ELIGIBLE (mandatory rule failed)
```

### 5.4 Rule Caching

- Rules cached in memory for performance
- Cache TTL: 24 hours (configurable)
- Force reload option available

### 5.5 Rule Management Interface

#### 5.5.1 Frontend Rule Management

**Location**: Admin Portal → Scheme Configuration → Rule Management

**UI Components**:

1. **Rule Management Dashboard**
   - List all schemes
   - View rules per scheme (active/inactive)
   - Add/Edit/Delete rules
   - Enable/Disable rules
   - Rule validation and testing

2. **Rule Editor Modal**
   - Scheme selector
   - Rule name input
   - Rule type dropdown (AGE, INCOME, GENDER, etc.)
   - Operator dropdown (>=, <=, =, IN, NOT_IN, etc.)
   - Rule value input
   - Rule expression preview
   - Mandatory flag checkbox
   - Priority input
   - Effective dates (from/to)
   - Test rule button (with sample data)

3. **Rule Version History View**
   - View all versions of a rule
   - Compare versions side-by-side
   - Rollback to previous version
   - See who changed what and when

#### 5.5.2 Rule Management APIs

**Controller**: `RuleManagementController.java`

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/admin/rules/schemes` | List all schemes |
| GET | `/api/v1/admin/rules/scheme/{scheme_id}` | Get rules for scheme |
| GET | `/api/v1/admin/rules/{rule_id}` | Get specific rule |
| POST | `/api/v1/admin/rules` | Create new rule |
| PUT | `/api/v1/admin/rules/{rule_id}` | Update rule |
| DELETE | `/api/v1/admin/rules/{rule_id}` | Delete rule (soft delete) |
| POST | `/api/v1/admin/rules/{rule_id}/clone` | Clone rule |
| GET | `/api/v1/admin/rules/{rule_id}/versions` | Get version history |
| POST | `/api/v1/admin/rules/{rule_id}/rollback` | Rollback to version |
| POST | `/api/v1/admin/rules/test` | Test rule expression |
| POST | `/api/v1/admin/rules/validate` | Validate rule syntax |
| POST | `/api/v1/admin/rules/scheme/{scheme_id}/snapshot` | Create rule set snapshot |
| GET | `/api/v1/admin/rules/scheme/{scheme_id}/snapshots` | Get rule set snapshots |
| GET | `/api/v1/admin/rules/comparison` | Compare evaluations across versions |

**Example Request/Response**:

```json
// POST /api/v1/admin/rules
{
  "scheme_id": "SCHEME_001",
  "rule_name": "Age Requirement",
  "rule_type": "AGE",
  "rule_expression": "age >= 60",
  "rule_operator": ">=",
  "rule_value": "60",
  "is_mandatory": true,
  "priority": 10,
  "effective_from": "2024-01-01",
  "effective_to": null
}

// Response
{
  "rule_id": 123,
  "scheme_id": "SCHEME_001",
  "rule_name": "Age Requirement",
  "version": 1,
  "created_at": "2024-12-27T10:00:00Z"
}
```

#### 5.5.3 Python Rule Management Service

**File**: `src/rule_manager.py`

**Key Methods**:
- `create_rule()` - Create new rule with version tracking
- `update_rule()` - Update rule (creates new version automatically)
- `delete_rule()` - Soft delete (sets effective_to date)
- `create_rule_set_snapshot()` - Create snapshot of current rule set
- `get_rule_set_snapshots()` - Get all snapshots for a scheme
- `compare_evaluations()` - Compare evaluations across rule versions

---

## 6. Hybrid Evaluation Design

### 6.1 Evaluation Strategy

#### 6.1.1 Rule Engine Evaluation
- Runs first (deterministic, fast)
- Returns: eligible (bool), status, rule path, confidence (0.5-1.0)

#### 6.1.2 ML Scorer Evaluation
- Runs if model available (probabilistic, slower)
- Returns: probability (0-1), confidence (0-1), top features

#### 6.1.3 Hybrid Combination
- **Rule Weight**: 0.6 (default)
- **ML Weight**: 0.4 (default)
- **Combined Score**: Weighted average of rule score and ML probability
- **Confidence**: Weighted combination of rule and ML confidence

### 6.2 Conflict Resolution

#### 6.2.1 Conflict Scenarios

**Scenario 1: Rules Pass + ML Low**
- **Resolution**: Use rules (rules take precedence for safety)
- **Reason**: Conservative approach to prevent leakage
- **Status**: RULE_ELIGIBLE (flagged for review if ML very low)

**Scenario 2: Rules Fail + ML High**
- **Resolution**: Require review (never auto-identify)
- **Reason**: Prevent false positives from ML
- **Status**: NOT_ELIGIBLE or POSSIBLE_ELIGIBLE (requires manual review)

**Scenario 3: Agreement**
- **Resolution**: Use combined score with high confidence
- **Status**: RULE_ELIGIBLE or NOT_ELIGIBLE

**Scenario 4: Mixed Signals**
- **Resolution**: Mark as POSSIBLE_ELIGIBLE for review
- **Status**: POSSIBLE_ELIGIBLE

### 6.3 Final Status Determination

```python
if eligibility_score >= confidence_threshold (0.7):
    if rule_status == 'RULE_ELIGIBLE':
        return 'RULE_ELIGIBLE'
    else:
        return 'POSSIBLE_ELIGIBLE'
elif eligibility_score >= 0.5:
    return 'POSSIBLE_ELIGIBLE'
else:
    return 'NOT_ELIGIBLE'
```

---

## 7. Prioritization & Ranking Design

### 7.1 Priority Score Calculation

```python
priority_score = (
    (eligibility_score * confidence_score) * vulnerability_multiplier +
    under_coverage_boost
) * scheme_priority_weight
```

#### 7.1.1 Components

**Base Score**:
- `eligibility_score * confidence_score`
- Core eligibility assessment

**Vulnerability Multiplier**:
- VERY_HIGH: 1.5x
- HIGH: 1.3x
- MEDIUM: 1.0x
- LOW: 0.8x
- VERY_LOW: 0.6x

**Under-Coverage Boost**:
- +0.15 if under-covered
- Encourages identification of underserved families

**Scheme Priority Weight**:
- Scheme-specific multiplier
- Default: 1.0

### 7.2 Ranking Factors

1. **Eligibility Score** (primary)
2. **Vulnerability Level** (from 360° Profile)
3. **Under-Coverage Indicator** (from 360° Profile)
4. **Geographic Clustering** (optional boost for batch processing)

### 7.3 Output Types

#### 7.3.1 Citizen Hints
- **Count**: Top 3-5 schemes per family
- **Criteria**: Highest priority eligible schemes
- **Use Case**: Citizen portal eligibility widget

#### 7.3.2 Departmental Worklists
- **Count**: Configurable (default: 100 per scheme)
- **Criteria**: Ranked by priority score
- **Filters**: District, minimum score threshold
- **Use Case**: Departmental outreach queues

#### 7.3.3 Auto-Intimation Lists
- **Count**: All eligible candidates
- **Criteria**: High confidence (>= 0.7)
- **Use Case**: Automated notification service

---

## 8. API Design

### 8.1 Spring Boot REST Controllers

The Auto Identification system exposes REST APIs through Spring Boot controllers. All controllers are implemented and ready for integration with the Departmental Portal and Citizen Portal.

**Base URL**: `/api/v1`

**Authentication**: All endpoints require authentication (to be integrated with portal authentication)

**Cross-Origin**: CORS enabled for portal integration (`@CrossOrigin(origins = "*")`)

### 8.2 Eligibility Evaluation Controller

**Controller**: `EligibilityEvaluationController`  
**Base Path**: `/api/v1/eligibility`

#### 8.2.1 Evaluate Family (On-Demand)

**Endpoint**: `POST /api/v1/eligibility/evaluate`

**Purpose**: Evaluate eligibility for a family on-demand (for real-time checks)

**Request Parameters**:
- `family_id` (required, String): Family UUID
- `scheme_ids` (optional, List<String>): List of specific scheme IDs to evaluate. If not provided, evaluates all active schemes.
- `use_ml` (optional, boolean, default: `true`): Whether to use ML scorer if available

**Response**: `EvaluationResponse`
```json
{
  "family_id": "uuid-string",
  "evaluated_at": "2024-12-29T12:00:00Z",
  "schemes_evaluated": 5,
  "evaluations": [
    {
      "scheme_id": "CHIRANJEEVI",
      "evaluation_status": "RULE_ELIGIBLE",
      "eligibility_score": 0.85,
      "confidence_score": 0.90,
      "rule_path": "Universal Coverage",
      "explanation": "Rules and ML both indicate eligibility",
      "ml_probability": 0.82,
      "top_features": [...]
    }
  ],
  "error": null
}
```

**Example Request**:
```bash
POST /api/v1/eligibility/evaluate?family_id=123e4567-e89b-12d3-a456-426614174000&use_ml=true
```

**Latency Target**: <200ms

#### 8.2.2 Get Precomputed Results

**Endpoint**: `GET /api/v1/eligibility/precomputed`

**Purpose**: Retrieve precomputed eligibility results from database (faster than on-demand evaluation)

**Request Parameters**:
- `family_id` (required, String): Family UUID
- `scheme_ids` (optional, List<String>): Filter by specific schemes

**Response**: `PrecomputedResultsResponse`
```json
{
  "family_id": "uuid-string",
  "results": [
    {
      "scheme_id": "CHIRANJEEVI",
      "status": "RULE_ELIGIBLE",
      "eligibility_score": 0.85,
      "confidence": 0.90,
      "rule_path": "Universal Coverage",
      "explanation": "Precomputed eligibility result",
      "evaluated_at": "2024-12-28T10:00:00Z"
    }
  ],
  "count": 1
}
```

**Example Request**:
```bash
GET /api/v1/eligibility/precomputed?family_id=123e4567-e89b-12d3-a456-426614174000
```

**Latency Target**: <50ms

#### 8.2.3 Get Citizen Hints

**Endpoint**: `GET /api/v1/eligibility/citizen-hints`

**Purpose**: Get top eligible schemes for a citizen (for Citizen Portal display)

**Request Parameters**:
- `family_id` (required, String): Family UUID

**Response**: `CitizenHintsResponse`
```json
{
  "family_id": "uuid-string",
  "hints": [
    {
      "scheme_id": "CHIRANJEEVI",
      "scheme_name": "Mukhyamantri Chiranjeevi Yojana",
      "eligibility_status": "RULE_ELIGIBLE",
      "eligibility_score": 0.90,
      "confidence": 0.95,
      "explanation": "You meet all eligibility criteria for this health scheme",
      "rank": 1
    },
    {
      "scheme_id": "OLD_AGE_PENSION",
      "scheme_name": "Old Age Pension",
      "eligibility_status": "RULE_ELIGIBLE",
      "eligibility_score": 0.85,
      "confidence": 0.88,
      "explanation": "You are eligible for old age pension",
      "rank": 2
    }
  ]
}
```

**Example Request**:
```bash
GET /api/v1/eligibility/citizen-hints?family_id=123e4567-e89b-12d3-a456-426614174000
```

**Latency Target**: <100ms

#### 8.2.4 Get Scheme Configuration

**Endpoint**: `GET /api/v1/eligibility/config/scheme/{scheme_id}`

**Purpose**: Get scheme configuration, rules, and ML model information

**Path Parameters**:
- `scheme_id` (required, String): Scheme code

**Response**: `SchemeConfigResponse`
```json
{
  "scheme_id": "CHIRANJEEVI",
  "scheme_name": "Mukhyamantri Chiranjeevi Yojana",
  "scheme_type": "HEALTH",
  "rules": [...],
  "ml_model": {
    "available": true,
    "version": "EligibilityScorer_CHIRANJEEVI",
    "model_type": "xgboost"
  },
  "active": true
}
```

**Example Request**:
```bash
GET /api/v1/eligibility/config/scheme/CHIRANJEEVI
```

**Latency Target**: <50ms

### 8.3 Candidate List Controller

**Controller**: `CandidateListController`  
**Base Path**: `/api/v1/eligibility/candidate-list`

#### 8.3.1 Get Candidate List (Departmental Worklist)

**Endpoint**: `GET /api/v1/eligibility/candidate-list`

**Purpose**: Get ranked candidate list for a scheme (departmental worklist)

**Request Parameters**:
- `scheme_id` (required, String): Scheme code
- `district` (optional, Integer): District ID filter
- `score` (optional, double, default: `0.5`): Minimum eligibility score threshold
- `limit` (optional, int, default: `100`): Maximum number of candidates to return

**Response**: `CandidateListResponse`
```json
{
  "scheme_id": "CHIRANJEEVI",
  "candidates": [
    {
      "family_id": "uuid-1",
      "rank": 1,
      "priority_score": 0.92,
      "eligibility_score": 0.90,
      "confidence": 0.95,
      "status": "RULE_ELIGIBLE",
      "vulnerability_level": "VERY_HIGH",
      "under_coverage": true,
      "district_id": 101,
      "explanation": "High priority candidate with universal coverage eligibility"
    }
  ],
  "total": 150,
  "generated_at": "2024-12-29T12:00:00Z"
}
```

**Example Request**:
```bash
GET /api/v1/eligibility/candidate-list?scheme_id=CHIRANJEEVI&district=101&score=0.7&limit=50
```

**Latency Target**: <500ms

#### 8.3.2 Trigger Batch Evaluation

**Endpoint**: `POST /api/v1/eligibility/candidate-list/batch`

**Purpose**: Trigger batch evaluation job (async processing)

**Request Body**: `BatchEvaluationRequest` (optional)
```json
{
  "scheme_ids": ["CHIRANJEEVI", "OLD_AGE_PENSION"],
  "district_ids": [101, 102],
  "max_families": 1000
}
```

**Response**: `BatchEvaluationResponse`
```json
{
  "batch_id": "BATCH_20241229_120000_abc123",
  "job_id": 12345,
  "status": "RUNNING",
  "created_at": "2024-12-29T12:00:00Z",
  "estimated_completion": "2024-12-29T14:00:00Z"
}
```

**Example Request**:
```bash
POST /api/v1/eligibility/candidate-list/batch
Content-Type: application/json

{
  "scheme_ids": ["CHIRANJEEVI"],
  "max_families": 500
}
```

**Latency Target**: Immediate (async processing)

#### 8.3.3 Get Batch Evaluation Status

**Endpoint**: `GET /api/v1/eligibility/candidate-list/batch/{batch_id}`

**Purpose**: Get status and progress of a batch evaluation job

**Path Parameters**:
- `batch_id` (required, String): Batch job ID

**Response**: `BatchStatusResponse`
```json
{
  "batch_id": "BATCH_20241229_120000_abc123",
  "job_id": 12345,
  "status": "RUNNING",
  "progress_percentage": 45,
  "families_processed": 450,
  "total_families": 1000,
  "evaluations_created": 4500,
  "errors": 2,
  "started_at": "2024-12-29T12:00:00Z",
  "estimated_completion": "2024-12-29T14:00:00Z"
}
```

**Example Request**:
```bash
GET /api/v1/eligibility/candidate-list/batch/BATCH_20241229_120000_abc123
```

**Latency Target**: <50ms

### 8.4 Rule Management Controller

**Controller**: `RuleManagementController`  
**Base Path**: `/api/v1/admin/rules`

**Note**: These endpoints are for administrative use and will be integrated with the Departmental Portal for rule management UI.

#### 8.4.1 List All Schemes

**Endpoint**: `GET /api/v1/admin/rules/schemes`

**Purpose**: Get list of all schemes for rule management

**Response**: `List<SchemeDto>`
```json
[
  {
    "scheme_id": "CHIRANJEEVI",
    "scheme_name": "Mukhyamantri Chiranjeevi Yojana",
    "scheme_type": "HEALTH",
    "is_auto_id_enabled": true,
    "active": true
  }
]
```

#### 8.4.2 Get Scheme Rules

**Endpoint**: `GET /api/v1/admin/rules/scheme/{scheme_id}`

**Purpose**: Get all rules for a scheme

**Path Parameters**:
- `scheme_id` (required, String): Scheme code

**Request Parameters**:
- `include_inactive` (optional, boolean, default: `false`): Include inactive rules

**Response**: `SchemeRulesResponse`
```json
{
  "scheme_id": "CHIRANJEEVI",
  "scheme_name": "Mukhyamantri Chiranjeevi Yojana",
  "eligibility_rules": [
    {
      "rule_id": 1,
      "rule_name": "Universal Coverage",
      "rule_type": "MANDATORY",
      "rule_expression": "true",
      "is_active": true,
      "priority": 1
    }
  ],
  "exclusion_rules": []
}
```

#### 8.4.3 Get Specific Rule

**Endpoint**: `GET /api/v1/admin/rules/{rule_id}`

**Purpose**: Get details of a specific rule

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID

**Response**: `RuleDto`

#### 8.4.4 Create Rule

**Endpoint**: `POST /api/v1/admin/rules`

**Purpose**: Create a new eligibility rule

**Request Body**: `CreateRuleRequest`
```json
{
  "scheme_id": "CHIRANJEEVI",
  "rule_name": "Age Requirement",
  "rule_type": "MANDATORY",
  "rule_expression": "age >= 60",
  "description": "Citizen must be 60 years or older",
  "priority": 1,
  "is_active": true
}
```

**Response**: `RuleDto` (created rule)

#### 8.4.5 Update Rule

**Endpoint**: `PUT /api/v1/admin/rules/{rule_id}`

**Purpose**: Update an existing rule

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID

**Request Body**: `UpdateRuleRequest`
```json
{
  "rule_name": "Age Requirement",
  "rule_expression": "age >= 65",
  "description": "Updated age requirement to 65",
  "is_active": true
}
```

**Response**: `RuleDto` (updated rule)

#### 8.4.6 Delete Rule

**Endpoint**: `DELETE /api/v1/admin/rules/{rule_id}`

**Purpose**: Delete a rule (soft delete - sets is_active=false)

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID

**Response**: `204 No Content` on success

#### 8.4.7 Clone Rule

**Endpoint**: `POST /api/v1/admin/rules/{rule_id}/clone`

**Purpose**: Clone an existing rule (create a copy)

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID to clone

**Response**: `RuleDto` (new cloned rule)

#### 8.4.8 Get Rule Version History

**Endpoint**: `GET /api/v1/admin/rules/{rule_id}/versions`

**Purpose**: Get version history of a rule

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID

**Response**: `List<RuleVersionDto>`

#### 8.4.9 Rollback Rule

**Endpoint**: `POST /api/v1/admin/rules/{rule_id}/rollback`

**Purpose**: Rollback rule to a previous version

**Path Parameters**:
- `rule_id` (required, Integer): Rule ID

**Request Body**: `RollbackRequest`
```json
{
  "version_id": 5
}
```

**Response**: `RuleDto` (rolled back rule)

#### 8.4.10 Test Rule Expression

**Endpoint**: `POST /api/v1/admin/rules/test`

**Purpose**: Test a rule expression with sample data

**Request Body**: `RuleTestRequest`
```json
{
  "rule_expression": "age >= 60",
  "test_data": {
    "age": 65,
    "gender": "Male"
  }
}
```

**Response**: `RuleTestResponse`
```json
{
  "passed": true,
  "result": true,
  "explanation": "Rule passed: age (65) >= 60"
}
```

#### 8.4.11 Validate Rule Syntax

**Endpoint**: `POST /api/v1/admin/rules/validate`

**Purpose**: Validate rule syntax without saving

**Request Body**: `RuleDto` (rule to validate)

**Response**: `RuleValidationResponse`
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

#### 8.4.12 Create Rule Set Snapshot

**Endpoint**: `POST /api/v1/admin/rules/scheme/{scheme_id}/snapshot`

**Purpose**: Create a snapshot of current rule set for version tracking

**Path Parameters**:
- `scheme_id` (required, String): Scheme code

**Request Body**: `CreateSnapshotRequest`
```json
{
  "snapshot_version": "v2.0",
  "snapshot_name": "Rule Set v2.0 - Dec 2024",
  "description": "Updated age requirement from 60 to 65",
  "created_by": "admin_user"
}
```

**Response**: `RuleSetSnapshotDto`

#### 8.4.13 Get Rule Set Snapshots

**Endpoint**: `GET /api/v1/admin/rules/scheme/{scheme_id}/snapshots`

**Purpose**: Get all rule set snapshots for a scheme

**Path Parameters**:
- `scheme_id` (required, String): Scheme code

**Response**: `List<RuleSetSnapshotDto>`

#### 8.4.14 Compare Rule Versions

**Endpoint**: `GET /api/v1/admin/rules/comparison`

**Purpose**: Compare evaluation results across rule versions

**Request Parameters**:
- `scheme_id` (required, String): Scheme code
- `rule_set_version_old` (required, String): Old rule set version
- `rule_set_version_new` (required, String): New rule set version
- `family_id` (optional, UUID): Specific family to compare

**Response**: `EvaluationComparisonResponse`
```json
{
  "scheme_id": "CHIRANJEEVI",
  "rule_set_version_old": "v1.0",
  "rule_set_version_new": "v2.0",
  "comparison": [
    {
      "family_id": "uuid-1",
      "old_status": "RULE_ELIGIBLE",
      "new_status": "NOT_ELIGIBLE",
      "old_score": 0.95,
      "new_score": 0.45,
      "score_delta": -0.50,
      "status_changed": true
    }
  ],
  "summary": {
    "total_families": 150,
    "status_changed": 25,
    "newly_eligible": 5,
    "no_longer_eligible": 20
  }
}
```

**Example Request**:
```bash
GET /api/v1/admin/rules/comparison?scheme_id=CHIRANJEEVI&rule_set_version_old=v1.0&rule_set_version_new=v2.0
```

### 8.5 Error Responses

All endpoints return standard error responses:

**400 Bad Request**:
```json
{
  "error": "Invalid request parameters",
  "details": "..."
}
```

**404 Not Found**:
```json
{
  "error": "Resource not found",
  "details": "..."
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "details": "..."
}
```

### 8.6 Response Formats

See sections 8.2-8.4 for detailed response formats for each endpoint.

### 8.7 Integration Notes for Portal Development

1. **Base URL Configuration**: Configure API base URL in portal environment settings
2. **Authentication**: Integrate with portal authentication (JWT tokens, session management)
3. **Error Handling**: Implement error handling for all API responses
4. **Loading States**: Show loading indicators for async operations (batch evaluation)
5. **Pagination**: Implement pagination for candidate lists (large result sets)
6. **Caching**: Consider caching precomputed results on client side
7. **Polling**: For batch jobs, implement polling mechanism to check status

### 8.8 Web Interface for Viewing Rules

**Purpose**: A simple web-based interface for viewing all eligibility rules in a browser without needing portal access.

**Implementation**: Flask-based web application (`scripts/view_rules_web.py`)

**Features**:
- **Statistics Dashboard**: Displays total schemes, total rules, and active rules
- **Scheme-wise Organization**: All schemes with auto-identification enabled
- **Expandable Sections**: Click on scheme headers to expand/collapse rules
- **Detailed Rule Information**: 
  - Rule ID, Name, Type
  - Rule Expression (actual rule logic)
  - Mandatory Status
  - Priority
  - Effective Dates
- **Color-coded Display**: Visual indicators for rule types and mandatory status
- **Responsive Design**: Works on desktop and mobile browsers
- **Real-time Data**: Reads directly from database

**Usage**:

1. **Start the Web Server**:
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   python scripts/view_rules_web.py
   ```

2. **Access in Browser**:
   - Open: `http://localhost:5001`
   - View all rules organized by scheme
   - Click scheme headers to expand/collapse rules

3. **Stop the Server**:
   - Press `Ctrl+C` in the terminal

**Requirements**:
- Flask >= 3.0.0 (added to `requirements.txt`)
- Database connection (via DBConnector)
- Access to `public.scheme_master` and `eligibility.scheme_eligibility_rules` tables

**Note**: This is a read-only viewer for development/testing purposes. For production rule management, use the REST APIs documented in section 8.4 (Rule Management Controller) or the future portal UI.

---
### 8.2 Response Formats

#### 8.2.1 Evaluation Response
```json
{
  "family_id": "uuid",
  "evaluated_at": "2024-12-27T10:00:00Z",
  "schemes_evaluated": 5,
  "evaluations": [
    {
      "scheme_id": "SCHEME_001",
      "evaluation_status": "RULE_ELIGIBLE",
      "eligibility_score": 0.85,
      "confidence_score": 0.90,
      "rule_path": "Age >= 60, Income Band LOW",
      "explanation": "Rules and ML both indicate eligibility",
      "ml_probability": 0.82,
      "top_features": [...]
    }
  ]
}
```

#### 8.2.2 Citizen Hints Response
```json
{
  "family_id": "uuid",
  "hints": [
    {
      "scheme_id": "SCHEME_001",
      "scheme_name": "Old Age Pension",
      "eligibility_status": "RULE_ELIGIBLE",
      "eligibility_score": 0.90,
      "confidence": 0.95,
      "explanation": "You meet all eligibility criteria",
      "rank": 1
    }
  ]
}
```

#### 8.2.3 Candidate List Response
```json
{
  "scheme_id": "SCHEME_001",
  "candidates": [
    {
      "family_id": "uuid",
      "rank": 1,
      "priority_score": 0.92,
      "eligibility_score": 0.90,
      "confidence": 0.95,
      "status": "RULE_ELIGIBLE",
      "vulnerability_level": "VERY_HIGH",
      "under_coverage": true,
      "explanation": "..."
    }
  ],
  "total": 150,
  "generated_at": "2024-12-27T10:00:00Z"
}
```

---

## 9. Data Flow & Processing Pipeline

### 9.1 Batch Evaluation Flow

```
1. Batch Trigger (Weekly, 2 AM)
   ↓
2. Load Families (from Golden Records)
   ├── Filter by district (optional)
   ├── Filter by scheme (optional)
   └── Limit to max families
   ↓
3. For Each Family:
   ├── Load Family Data (Golden Records + 360° Profile)
   ├── For Each Active Scheme:
   │   ├── Evaluate (Rule Engine + ML Scorer)
   │   ├── Calculate Priority Score
   │   └── Save Snapshot
   └── Generate Candidate Lists
   ↓
4. Update Batch Job Status
   ├── Progress tracking
   └── Error reporting
   ↓
5. Complete (Generate Summary)
```

### 9.2 Event-Driven Evaluation Flow

```
1. Event Trigger
   ├── age_threshold_crossed
   ├── new_child_added
   ├── disability_registered
   ├── calamity_tagged
   ├── income_band_changed
   └── household_composition_changed
   ↓
2. Identify Affected Schemes
   ├── Map event type to scheme categories
   └── Get active schemes for categories
   ↓
3. Re-evaluate Family
   ├── Load updated family data
   ├── Evaluate for affected schemes
   └── Save snapshots
   ↓
4. Update Candidate Lists
   └── Regenerate affected worklists
```

### 9.3 On-Demand Evaluation Flow

```
1. API Request
   ↓
2. Check Precomputed Results
   ├── If recent (< 30 days): Return cached
   └── If stale/missing: Continue
   ↓
3. Evaluate Family
   ├── Load family data
   ├── Evaluate requested schemes
   └── Save snapshots
   ↓
4. Return Results
   └── Include explanations and scores
```

---

## 10. Integration Points

### 10.1 Dependencies

#### 10.1.1 AI-PLATFORM-01 (Golden Records)
- **Purpose**: Primary identity and family data
- **Database**: `smart.golden_records`
- **Data**: Demographics, relationships, family structure
- **Usage**: Rule evaluation, feature engineering

#### 10.1.2 AI-PLATFORM-02 (360° Profiles)
- **Purpose**: Enriched profile data
- **Database**: `smart_warehouse.profile_360`
- **Data**: Income band, vulnerability, under-coverage, cluster IDs
- **Usage**: Prioritization, ML features

#### 10.1.3 JRDR (Jan Aadhaar)
- **Purpose**: Master household data
- **Database**: `smart.jrdr`
- **Data**: Family relationships, member data
- **Usage**: Family validation

### 10.2 Outputs To

#### 10.2.1 Citizen Portal
- **Endpoints**: `/eligibility/citizen-hints`
- **Data**: Top N eligible schemes per family
- **Screens**: CIT-PROF-04, CIT-SCHEME-10, CIT-SCHEME-12

#### 10.2.2 Departmental Portal
- **Endpoints**: `/eligibility/candidate-list`
- **Data**: Ranked candidate worklists
- **Screens**: Beneficiary discovery queues

#### 10.2.3 Auto-Intimation Service
- **Events**: `POTENTIALLY_ELIGIBLE_IDENTIFIED`
- **Data**: Eligible candidates for notification
- **Use Case**: Automated SMS/email notifications

#### 10.2.4 AI/ML Insights Portal
- **Endpoints**: Configuration and monitoring APIs
- **Data**: Model performance, recall/precision metrics
- **Screens**: Configuration, monitoring dashboards

---

## 11. Performance & Scalability

### 11.1 Performance Targets

#### 11.1.1 API Latency
- On-demand evaluation: <200ms
- Precomputed results: <50ms
- Citizen hints: <100ms
- Candidate lists: <500ms

#### 11.1.2 Batch Processing
- Full JRDR scan: <6 hours (overnight window)
- Incremental batch: <1 hour
- Progress tracking: Real-time updates

#### 11.1.3 Throughput
- On-demand API: 100+ requests/second
- Batch processing: 1000+ families/minute

### 11.2 Scalability Considerations

#### 11.2.1 Database Optimization
- Indexes on family_id, scheme_id, district_id
- Partitioning eligibility_snapshots by evaluation_timestamp
- Materialized views for candidate lists

#### 11.2.2 Caching Strategy
- Rule caching (24-hour TTL)
- Model caching (in-memory)
- Precomputed results (30-day retention)

#### 11.2.3 Horizontal Scaling
- Stateless API services (can scale horizontally)
- Batch processing: Distributed across workers
- Database connection pooling

### 11.3 Resource Requirements

#### 11.3.1 Compute
- API services: 2-4 CPU cores, 4-8 GB RAM per instance
- Batch processing: 4-8 CPU cores, 16-32 GB RAM
- ML inference: GPU optional (CPU sufficient for XGBoost)

#### 11.3.2 Storage
- Database: 100GB+ for eligibility snapshots (grows with evaluations)
- Model storage: 1-2GB per scheme model
- MLflow artifacts: 10-20GB

---

## 12. Security & Governance

### 12.1 Data Privacy

#### 12.1.1 Consent Management
- **Consent Required**: Eligibility processing consent
- **Proxy Data**: Additional consent for proxy datasets
- **Storage**: Consent flags in `consent_status` table
- **Enforcement**: Check consent before evaluation

#### 12.1.2 Data Minimization
- Only use data necessary for eligibility evaluation
- Sensitive attributes can be excluded from ML models
- Configurable feature lists per scheme

#### 12.1.3 Data Retention
- Eligibility snapshots: 1 year (configurable)
- Candidate lists: 90 days (configurable)
- Audit logs: 7 years (legal requirement)

### 12.2 Fairness & Non-Discrimination

#### 12.2.1 Bias Monitoring
- Regular bias checks by demographic breakdowns
- Metrics: Eligibility rates by district, gender, social group
- Frequency: Monthly

#### 12.2.2 Threshold Management
- Configurable thresholds per scheme
- Policy team review of thresholds
- Ability to exclude sensitive attributes

#### 12.2.3 Explainability
- Every evaluation stores rule path
- ML predictions include top features
- Human-readable explanations

### 12.3 Audit & Compliance

#### 12.3.1 Audit Logging
- All evaluations logged with timestamp, user/system
- Rule changes tracked in `rule_change_history`
- Model updates tracked in `ml_model_registry`
- Threshold changes logged in audit log

#### 12.3.2 Version Control
- Evaluation snapshots include version numbers
- Rule versions tracked
- Model versions tracked
- Complete lineage for reproducibility

#### 12.3.3 Legal Basis
- Uses Jan Aadhaar Act provisions for beneficiary identification
- Departmental notifications and consents
- Proxy datasets flagged in explanations
- Policy compliance documented

---

## 13. Deployment Architecture

### 13.1 Component Deployment

#### 13.1.1 Python Services
- **Location**: WSL/Linux environment
- **Process**: Python processes or microservices
- **Communication**: REST API or process execution
- **Scaling**: Horizontal scaling via load balancer

#### 13.1.2 Spring Boot APIs
- **Location**: Application servers
- **Framework**: Spring Boot 3.x
- **Deployment**: JAR files or containers (Docker)
- **Scaling**: Horizontal scaling, load balanced

#### 13.1.3 Database
- **Location**: PostgreSQL cluster
- **Replication**: Master-slave for read scaling
- **Backup**: Daily backups, 7-day retention

#### 13.1.4 MLflow
- **Location**: MLflow Tracking Server
- **Deployment**: Standalone or containerized
- **Storage**: File system or S3-compatible storage

### 13.2 Scheduled Jobs

#### 13.2.1 Batch Evaluation
- **Schedule**: Weekly (Sunday 2 AM)
- **Implementation**: Kubernetes CronJob or Linux cron
- **Notification**: Email on completion/failure

#### 13.2.2 Model Retraining
- **Schedule**: Monthly (first Sunday)
- **Implementation**: Kubernetes CronJob
- **Process**: Train models for all active schemes

### 13.3 Model Retraining Workflows

#### 13.3.1 Overview

Model retraining is essential to maintain ML model accuracy as new data becomes available and eligibility patterns change over time. The system provides both automated and manual retraining workflows.

#### 13.3.2 Automated Retraining Workflow

**Trigger**: Scheduled monthly retraining (configurable)

**Process Flow**:

```
1. Scheduled Trigger (Monthly, First Sunday 2 AM)
   ↓
2. Check Training Data Availability
   ├── Verify minimum sample size (e.g., 1000+ families)
   ├── Check data quality (missing values, outliers)
   └── Verify class balance (eligible vs. not eligible)
   ↓
3. For Each Active Scheme:
   ├── Load Training Data
   │   ├── Query eligibility_snapshots (last 90 days)
   │   ├── Extract features from Golden Records + 360° Profiles
   │   └── Include both eligible and non-eligible examples
   ├── Split Data (Train/Test: 80/20)
   ├── Train New Model
   │   ├── Use XGBoost with configured hyperparameters
   │   ├── Cross-validation (5-fold)
   │   ├── Early stopping (if supported)
   │   └── Compute SHAP values for explainability
   ├── Evaluate Model Performance
   │   ├── Accuracy, Precision, Recall, F1
   │   ├── ROC-AUC, PR-AUC
   │   └── Confusion matrix
   ├── Compare with Current Production Model
   │   ├── Load current production model metrics
   │   ├── Compare test set performance
   │   └── Determine if new model is better
   ├── Model Promotion Decision
   │   ├── If new model is better (by threshold):
   │   │   ├── Register new model in MLflow
   │   │   ├── Update ml_model_registry (set old model inactive)
   │   │   ├── Set new model as active
   │   │   └── Log model deployment
   │   └── If new model is worse:
   │       ├── Keep current production model
   │       ├── Log performance degradation alert
   │       └── Archive new model for analysis
   └── Generate Training Report
       ├── Model performance metrics
       ├── Feature importance changes
       └── Training statistics
   ↓
4. Send Notification
   ├── Training completion status
   ├── Models updated count
   └── Performance summary
```

**Implementation**: 
- Script: `src/train_eligibility_model.py`
- Command: `python src/train_eligibility_model.py --scheme-code <SCHEME_CODE>`
- Batch script: `python scripts/test_train_models.py --all`

#### 13.3.3 Manual Retraining Workflow

**Triggers**:
- Significant data drift detected
- Model performance degradation
- Rule changes affecting eligibility patterns
- New feature availability
- Periodic review request

**Process Steps**:

1. **Initiate Retraining**
   ```bash
   # Train specific scheme
   python src/train_eligibility_model.py --scheme-code CHIRANJEEVI
   
   # Train all schemes
   python scripts/test_train_models.py --all
   ```

2. **Review Model Performance**
   - Access MLflow UI: `http://127.0.0.1:5000`
   - Compare training runs
   - Review metrics and SHAP plots
   - Check feature importance changes

3. **Promote Model to Production** (if performance improved)
   - Model is automatically set as active if better than current
   - Manual override available via MLflow Model Registry UI

4. **Validate Model in Production**
   - Monitor evaluation metrics
   - Compare pre/post deployment performance
   - Check for any anomalies

#### 13.3.4 Model Performance Thresholds

**Promotion Criteria**:
- **Accuracy**: New model accuracy ≥ current model accuracy
- **Precision**: New model precision ≥ current model precision (or within 2%)
- **Recall**: New model recall ≥ current model recall (or within 2%)
- **ROC-AUC**: New model ROC-AUC ≥ current model ROC-AUC
- **Minimum Thresholds**: All models must maintain:
  - Accuracy ≥ 80%
  - Precision ≥ 20% (due to class imbalance)
  - ROC-AUC ≥ 0.60

**Degradation Alerts**:
- If new model performs significantly worse (>5% drop in any metric)
- Alert sent to ML team for investigation
- Current production model retained

#### 13.3.5 Data Requirements for Retraining

**Minimum Sample Size**:
- **Per Scheme**: 1000+ evaluation records
- **Class Balance**: At least 5% positive examples (eligible)
- **Time Range**: Last 90 days of evaluation snapshots

**Feature Availability**:
- All required features must be available in source data
- Missing features handled with imputation or defaults

**Data Quality Checks**:
- Check for outliers
- Verify feature distributions
- Check for data drift (compare with previous training data)

#### 13.3.6 Model Versioning and Rollback

**Versioning**:
- Each training run creates a new model version in MLflow
- Model versions tracked in `eligibility.ml_model_registry`
- Version format: `EligibilityScorer_{SCHEME_CODE}` with auto-incrementing version numbers

**Rollback Process**:
- Previous model versions retained in MLflow
- Can rollback to previous version if new model fails in production
- Rollback via MLflow UI or database update:
  ```sql
  UPDATE eligibility.ml_model_registry
  SET is_active = false
  WHERE scheme_code = 'CHIRANJEEVI' AND model_version = 'EligibilityScorer_CHIRANJEEVI';
  
  UPDATE eligibility.ml_model_registry
  SET is_active = true
  WHERE scheme_code = 'CHIRANJEEVI' AND model_version = 'EligibilityScorer_CHIRANJEEVI_previous';
  ```

#### 13.3.7 Monitoring and Alerting

**Training Monitoring**:
- Track training job status
- Monitor training duration
- Alert on training failures

**Model Performance Monitoring**:
- Track prediction accuracy over time
- Monitor feature importance drift
- Alert on performance degradation

**Production Monitoring**:
- Track model usage (predictions per day)
- Monitor evaluation metrics (eligibility scores)
- Compare actual eligibility vs. predicted eligibility

#### 13.3.8 Best Practices

1. **Regular Retraining**: Retrain monthly or when significant data changes occur
2. **A/B Testing**: Test new models on sample data before full deployment
3. **Performance Baselines**: Maintain baseline metrics for comparison
4. **Feature Monitoring**: Track feature importance changes to detect data drift
5. **Model Documentation**: Document model changes, hyperparameters, and training data
6. **Staged Rollout**: Consider gradual rollout for critical schemes

### 13.4 High Availability

#### 13.3.1 API Services
- **Redundancy**: 2+ instances behind load balancer
- **Health Checks**: HTTP health check endpoints
- **Failover**: Automatic failover on instance failure

#### 13.3.2 Database
- **Redundancy**: Master-slave replication
- **Failover**: Automatic promotion of slave
- **Backup**: Continuous backups with point-in-time recovery

---

## 14. Monitoring & Observability

### 14.1 Metrics

#### 14.1.1 Evaluation Metrics
- Evaluations per second
- Average evaluation latency
- Evaluation success/failure rates
- Cache hit rates

#### 14.1.2 Model Metrics
- Model prediction latency
- Model accuracy/precision/recall (per scheme)
- Feature importance trends
- SHAP value distributions

#### 14.1.3 Business Metrics
- Total eligible candidates identified
- Coverage (recall): % of eligible identified
- Precision: % of identified confirmed eligible
- False positive rate
- Under-coverage rate

#### 14.1.4 System Metrics
- CPU, memory, disk usage
- Database connection pool usage
- API request rates
- Error rates

### 14.2 Logging

#### 14.2.1 Structured Logging
- JSON format logs
- Correlation IDs for request tracking
- Log levels: DEBUG, INFO, WARN, ERROR

#### 14.2.2 Log Aggregation
- Centralized logging system (ELK stack or similar)
- Log retention: 30 days
- Search and analytics capabilities

### 14.3 Alerting

#### 14.3.1 Critical Alerts
- Batch evaluation failures
- API error rate > 5%
- Database connection failures
- Model loading failures

#### 14.3.2 Warning Alerts
- Evaluation latency > 500ms
- Batch processing > 8 hours
- Cache hit rate < 70%
- Model performance degradation

### 14.4 Dashboards

#### 14.4.1 Operational Dashboard
- Real-time API metrics
- Batch job status
- System health
- Error rates

#### 14.4.2 Business Dashboard
- Eligible candidates by scheme
- Coverage and precision metrics
- Geographic distribution
- Vulnerability breakdown

#### 14.4.3 ML Dashboard
- Model performance trends
- Feature importance changes
- SHAP value distributions
- Training metrics

---

## 15. Success Metrics

### 15.1 Coverage & Recall
- **Target**: 85% of actually eligible non-enrolled beneficiaries identified
- **Measurement**: Compare identified vs. manually verified eligible
- **Frequency**: Monthly review

### 15.2 Precision / Leakage Control
- **Target**: 90% of identified candidates confirmed eligible
- **Measurement**: Departmental verification of candidates
- **Frequency**: Monthly review
- **Threshold**: <1% false positive rate

### 15.3 Operational Metrics
- **Batch Completion**: <6 hours for full JRDR scan
- **API Latency**: <200ms for on-demand evaluation
- **Uptime**: 99.9% availability
- **Error Rate**: <1% of evaluations

### 15.4 Adoption Metrics
- **Citizen Portal**: Usage of eligibility hints widget
- **Departmental Portal**: Usage of worklist queues
- **Auto-Intimation**: Notification delivery rate

---

## 16. Rule Version Control & Historical Tracking

### 16.1 Version Control Architecture

#### 16.1.1 Rule Set Snapshots

**Purpose**: Store complete rule sets at specific points in time for historical tracking

**Table**: `eligibility.rule_set_snapshots`

```sql
CREATE TABLE eligibility.rule_set_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(50) NOT NULL,
    snapshot_name VARCHAR(200), -- e.g., "Rule Set v2.0 - Dec 2024"
    snapshot_version VARCHAR(50) NOT NULL, -- e.g., "v2.0"
    snapshot_date DATE NOT NULL,
    rule_data JSONB, -- Complete rule definitions (denormalized)
    exclusion_rule_data JSONB,
    description TEXT,
    change_summary TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Function**: `eligibility.create_rule_set_snapshot()`
- Creates a snapshot of current rule set for a scheme
- Stores all active rules and exclusion rules
- Automatically generates snapshot version

**Usage**:
```sql
-- Before making rule changes
SELECT eligibility.create_rule_set_snapshot(
    'SCHEME_001', 
    'v2.0', 
    'Rule Set v2.0 - Dec 2024',
    'Updated age requirement from 60 to 65',
    'admin'
);
```

#### 16.1.2 Dataset Versioning

**Purpose**: Track versions of source datasets used for evaluation

**Table**: `eligibility.dataset_versions`

```sql
CREATE TABLE eligibility.dataset_versions (
    dataset_version_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL, -- 'golden_records', 'profile_360', 'jrdr'
    version VARCHAR(50) NOT NULL, -- e.g., "v2.1", "2024-12-27"
    version_date DATE NOT NULL,
    description TEXT,
    metadata JSONB, -- Record counts, schema changes, data quality metrics
    schema_hash VARCHAR(64),
    source_system VARCHAR(100),
    extraction_date TIMESTAMP,
    total_records BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dataset_name, version)
);
```

**Usage**:
```sql
-- Register dataset version
INSERT INTO eligibility.dataset_versions (
    dataset_name, version, version_date, description, metadata, total_records
) VALUES (
    'golden_records', 'v2.2', '2024-12-27', 
    'Updated with new family linkages',
    '{"record_count": 500000, "schema_version": "2.0"}',
    500000
);
```

#### 16.1.3 Evaluation Version Tracking

**Enhanced Table**: `eligibility.eligibility_snapshots`

**Additional Columns**:
```sql
ALTER TABLE eligibility.eligibility_snapshots
ADD COLUMN rule_set_version VARCHAR(50),
ADD COLUMN rule_set_snapshot_id INTEGER REFERENCES eligibility.rule_set_snapshots(snapshot_id),
ADD COLUMN dataset_version_golden_records VARCHAR(50),
ADD COLUMN dataset_version_profile_360 VARCHAR(50),
ADD COLUMN dataset_version_jrdr VARCHAR(50);
```

**Automatic Version Recording**:
- When evaluation is performed, versions are automatically recorded:
  - `rule_set_version` - Current rule set version for the scheme
  - `dataset_version_golden_records` - Version of Golden Records used
  - `dataset_version_profile_360` - Version of 360° Profile used
  - `dataset_version_jrdr` - Version of JRDR used

**Implementation**:
```python
# In evaluator_service.py
eval_result['rule_set_version'] = self._get_current_rule_set_version(scheme_id)
eval_result['dataset_version_golden_records'] = self._get_current_dataset_version('golden_records')
eval_result['dataset_version_profile_360'] = self._get_current_dataset_version('profile_360')
```

### 16.2 Historical Query Examples

#### 16.2.1 Query Evaluations Before Rule Change

```sql
-- Get all evaluations before December 1, 2024 (when rule v2.0 was introduced)
SELECT 
    family_id,
    scheme_id,
    evaluation_status,
    eligibility_score,
    rule_path,
    evaluation_timestamp
FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v1.0'
  AND evaluation_timestamp < '2024-12-01'
  AND dataset_version_golden_records = 'v2.1'
  AND dataset_version_profile_360 = 'v2.0'
ORDER BY evaluation_timestamp DESC;
```

#### 16.2.2 Query Evaluations After Rule Change

```sql
-- Get all evaluations after December 1, 2024 (with rule v2.0)
SELECT 
    family_id,
    scheme_id,
    evaluation_status,
    eligibility_score,
    rule_path,
    evaluation_timestamp
FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v2.0'
  AND evaluation_timestamp >= '2024-12-01'
  AND dataset_version_golden_records = 'v2.2'
  AND dataset_version_profile_360 = 'v2.1'
ORDER BY evaluation_timestamp DESC;
```

#### 16.2.3 Compare Before/After Rule Changes

```sql
-- Compare evaluation results for a specific family
SELECT 
    rule_set_version,
    evaluation_status,
    eligibility_score,
    confidence_score,
    rule_path,
    evaluation_timestamp
FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND family_id = 'uuid-here'
  AND rule_set_version IN ('v1.0', 'v2.0')
ORDER BY rule_set_version, evaluation_timestamp DESC;
```

#### 16.2.4 Impact Analysis Query

```sql
-- Analyze impact of rule change on eligible families
SELECT 
    rule_set_version,
    evaluation_status,
    COUNT(*) as family_count,
    AVG(eligibility_score) as avg_score,
    AVG(confidence_score) as avg_confidence
FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version IN ('v1.0', 'v2.0')
  AND evaluation_timestamp >= '2024-12-01'
GROUP BY rule_set_version, evaluation_status
ORDER BY rule_set_version, evaluation_status;
```

### 16.3 Evaluation Comparison Table

**Purpose**: Track and compare evaluations across rule versions

**Table**: `eligibility.evaluation_comparison`

```sql
CREATE TABLE eligibility.evaluation_comparison (
    comparison_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    scheme_id VARCHAR(50) NOT NULL,
    rule_set_version_old VARCHAR(50),
    rule_set_version_new VARCHAR(50),
    evaluation_old_snapshot_id INTEGER REFERENCES eligibility.eligibility_snapshots(snapshot_id),
    evaluation_new_snapshot_id INTEGER REFERENCES eligibility.eligibility_snapshots(snapshot_id),
    status_changed BOOLEAN,
    score_delta DECIMAL(5,4), -- Change in eligibility score
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compared_by VARCHAR(100)
);
```

**Usage**: Automatically populated when comparing rule versions or manually triggered

### 16.4 Rule Change Workflow

#### 16.4.1 Complete Workflow for Rule Changes

```
1. Create Rule Set Snapshot (Before Change)
   ↓
   SELECT eligibility.create_rule_set_snapshot(
       'SCHEME_001', 'v1.0', 'Snapshot before rule update', 
       'Pre-change snapshot', 'admin'
   );
   ↓
2. Record Current Dataset Versions
   ↓
   - Get current versions from dataset_versions table
   - Document which datasets will be used
   ↓
3. Update/Add/Delete Rules
   ↓
   - Via Frontend UI or API
   - Changes create new rule versions automatically
   - Rule change history logged in rule_change_history table
   ↓
4. Create New Rule Set Snapshot (After Change)
   ↓
   SELECT eligibility.create_rule_set_snapshot(
       'SCHEME_001', 'v2.0', 'Rule Set v2.0 - Dec 2024',
       'Updated age requirement from 60 to 65', 'admin'
   );
   ↓
5. Run Evaluation (Automatic Version Recording)
   ↓
   - Evaluator service automatically records:
     * rule_set_version
     * dataset_version_golden_records
     * dataset_version_profile_360
   ↓
6. Compare Results (Before/After Analysis)
   ↓
   - Use evaluation_comparison table
   - Identify families affected by rule changes
   - Calculate impact metrics
```

#### 16.4.2 API for Comparison

**Endpoint**: `GET /api/v1/admin/rules/comparison`

**Parameters**:
- `scheme_id` (required)
- `rule_set_version_old` (required)
- `rule_set_version_new` (required)
- `family_id` (optional)

**Response**:
```json
{
  "scheme_id": "SCHEME_001",
  "rule_set_version_old": "v1.0",
  "rule_set_version_new": "v2.0",
  "comparison": [
    {
      "family_id": "uuid-1",
      "old_status": "RULE_ELIGIBLE",
      "new_status": "NOT_ELIGIBLE",
      "old_score": 0.95,
      "new_score": 0.45,
      "score_delta": -0.50,
      "status_changed": true
    }
  ],
  "summary": {
    "total_families": 150,
    "status_changed": 25,
    "newly_eligible": 5,
    "no_longer_eligible": 20
  }
}
```

### 16.5 Rule Change History & Audit

#### 16.5.1 Rule Change Tracking

**Table**: `eligibility.rule_change_history`

Already exists in base schema, enhanced with:
- Change type (CREATED, UPDATED, DELETED, ACTIVATED, DEACTIVATED)
- Old and new values
- Changed by user
- Timestamp

#### 16.5.2 Audit Logging

All rule changes are automatically logged:
- Who made the change
- When the change was made
- What changed (field-level tracking)
- Version numbers

**Example**:
```sql
SELECT 
    change_id,
    rule_id,
    scheme_id,
    change_type,
    changed_by,
    changed_at,
    new_value
FROM eligibility.rule_change_history
WHERE scheme_id = 'SCHEME_001'
ORDER BY changed_at DESC;
```

### 16.6 Implementation Checklist

#### 16.6.1 Database Setup

- [ ] Run `eligibility_schema_versioning.sql` to create versioning tables
- [ ] Add version columns to `eligibility_snapshots` table
- [ ] Create helper functions (`create_rule_set_snapshot`, etc.)
- [ ] Set up indexes on version columns for performance

#### 16.6.2 Backend Implementation

- [ ] Implement `RuleManagementService.java` (or Python service)
- [ ] Update `evaluator_service.py` to record versions
- [ ] Implement version retrieval methods (`_get_current_rule_set_version`, etc.)
- [ ] Add comparison API endpoints
- [ ] Implement rule change audit logging

#### 16.6.3 Frontend Implementation

- [ ] Create `RuleManagement.tsx` component
- [ ] Create `RuleVersionHistory.tsx` component
- [ ] Create `RuleSetSnapshot.tsx` component
- [ ] Create `EvaluationComparison.tsx` component
- [ ] Create `DatasetVersionSelector.tsx` component
- [ ] Integrate with backend APIs

#### 16.6.4 Testing

- [ ] Test rule CRUD operations
- [ ] Test version tracking in evaluations
- [ ] Test historical queries
- [ ] Test comparison functionality
- [ ] Test snapshot creation
- [ ] Verify audit logging

---

## 17. Implementation Status & Completion Checklist

### 17.1 Core Components Status

#### ✅ Completed Components

1. **Database Schema**
   - [x] Eligibility schema created in `smart_warehouse`
   - [x] All tables created (`eligibility_snapshots`, `scheme_eligibility_rules`, `candidate_lists`, etc.)
   - [x] Foreign key relationships to `public.scheme_master`
   - [x] Version control tables (`rule_set_snapshots`, `dataset_versions`, `evaluation_comparison`)
   - [x] Indexes created for performance

2. **Rule Engine**
   - [x] Dynamic rule loading from database (not hard-coded)
   - [x] Rule evaluation logic implemented
   - [x] Support for multiple rule types (AGE, INCOME, GENDER, etc.)
   - [x] Mandatory and optional rule handling
   - [x] Rule caching for performance
   - [x] Exclusion rules support

3. **ML Model Components**
   - [x] XGBoost model training pipeline
   - [x] MLflow integration for model registry
   - [x] Model versioning and tracking
   - [x] SHAP explainability integration
   - [x] Multi-flavor model loading (xgboost, sklearn, pyfunc)
   - [x] Models trained for 12 schemes

4. **Hybrid Evaluator**
   - [x] Rule-based evaluation
   - [x] ML-based scoring
   - [x] Hybrid combination logic
   - [x] Conflict resolution
   - [x] Final status determination

5. **Prioritization & Ranking**
   - [x] Priority score calculation
   - [x] Vulnerability-based ranking
   - [x] Under-coverage identification
   - [x] Citizen hints generation
   - [x] Departmental worklist generation

6. **Main Evaluation Service**
   - [x] Batch evaluation
   - [x] On-demand evaluation
   - [x] Event-driven evaluation (structure ready)
   - [x] Data loading from Golden Records and 360° Profiles
   - [x] Evaluation snapshot saving
   - [x] Version tracking (rule set version, dataset versions)

7. **Rule Management**
   - [x] Python service for CRUD operations
   - [x] Rule versioning
   - [x] Rule change history tracking
   - [x] Rule set snapshots
   - [x] Sample rules loading script

8. **REST APIs (Spring Boot Controllers)**
   - [x] EligibilityEvaluationController (4 endpoints)
   - [x] CandidateListController (3 endpoints)
   - [x] RuleManagementController (14 endpoints)
   - [x] All endpoints documented in Technical Design

9. **Testing & Validation**
   - [x] Database schema test script
   - [x] Rule management test script
   - [x] Model training test script
   - [x] Batch evaluation test script
   - [x] End-to-end pipeline test script

10. **Web Interface**
    - [x] Flask-based rules viewer
    - [x] Browser-based interface for viewing all rules
    - [x] Real-time database queries

11. **Documentation**
    - [x] Technical Design Document (comprehensive)
    - [x] API documentation (all endpoints)
    - [x] Setup guides (QUICK_START.md, SETUP.md)
    - [x] Model retraining workflows documented
    - [x] Database consolidation documentation

#### ⚠️ Pending/Incomplete Components

1. **Spring Boot Service Implementation**
   - [ ] Java service layer implementation (`EligibilityEvaluationService.java`)
   - [ ] Java service layer for rule management (`RuleManagementService.java`)
   - [ ] DTO classes for all API responses
   - [ ] Python client integration (`PythonEvaluationClient.java`)
   - [ ] **Status**: Controllers exist, but service layer needs implementation

2. **Frontend Rule Management UI**
   - [ ] React components for rule CRUD operations
   - [ ] Rule version history viewer
   - [ ] Rule set snapshot management UI
   - [ ] Rule comparison UI
   - [ ] **Status**: Design documented, implementation pending (part of Departmental Portal)

3. **Integration & Deployment**
   - [ ] Spring Boot application configuration
   - [ ] Integration with portal authentication
   - [ ] Production deployment configuration
   - [ ] Docker containerization (optional)
   - [ ] **Status**: Development environment ready, production deployment pending

4. **Monitoring & Alerting** (See Future Enhancements)
   - [ ] Prometheus/Grafana integration
   - [ ] Real-time dashboards
   - [ ] Alerting rules configuration
   - [ ] **Status**: Planned for future release

5. **Performance Optimizations** (See Future Enhancements)
   - [ ] Parallel batch processing
   - [ ] Response caching (Redis)
   - [ ] Database query optimizations
   - [ ] **Status**: Planned for future release

### 17.2 Current Status Summary

**✅ Production-Ready Components**:
- Database schema and data persistence
- Python evaluation engine (rule engine, ML scorer, hybrid evaluator)
- Prioritization and ranking logic
- Model training pipeline
- Rule management Python service
- Test scripts and validation

**⚠️ Requires Implementation**:
- Spring Boot service layer (Java implementation of service interfaces)
- Frontend UI for rule management (React components)
- Production deployment configuration
- Authentication integration

**📋 Ready for Integration**:
- REST API controllers are defined and documented
- API contracts are clear and well-documented
- Python services can be called from Java via `PythonEvaluationClient`

### 17.3 Next Steps for Complete Production Deployment

#### Immediate (Before Portal Integration)

1. **Implement Spring Boot Service Layer** (Priority: High)
   - Implement `EligibilityEvaluationService.java` to call Python services
   - Implement `RuleManagementService.java` to call Python services
   - Create all DTO classes
   - Test API endpoints end-to-end

2. **Integration Testing** (Priority: High)
   - Test API endpoints with portal frontend
   - Validate data flow from API → Python services → Database
   - Performance testing with expected load

#### Short-term (For Portal Development)

3. **Frontend Rule Management UI** (Priority: Medium)
   - Build React components based on API documentation
   - Implement rule CRUD operations
   - Rule version history viewer
   - Rule comparison tools

4. **Authentication Integration** (Priority: High)
   - Integrate with portal authentication system
   - Add authorization checks to API endpoints
   - User role management (admin vs. viewer)

#### Medium-term (Production Readiness)

5. **Monitoring Setup** (Priority: Medium)
   - Configure metrics collection
   - Set up dashboards
   - Configure alerting rules

6. **Performance Optimization** (Priority: Low)
   - Implement caching layer
   - Optimize database queries
   - Parallel processing for batch jobs

### 17.4 Can We Move to Next Model?

**Answer: YES, with caveats**

**✅ Ready to Move If**:
- Current model is functionally complete (core evaluation works)
- Spring Boot service layer can be implemented in parallel with next model
- Portal integration can proceed independently

**⚠️ Before Moving to Next Model, Ensure**:
1. **Documentation is Complete** ✅ (Done)
2. **Core Functionality Tested** ✅ (Done - End-to-end tests passing)
3. **API Contracts Defined** ✅ (Done - All controllers documented)
4. **Service Layer Implementation Plan** - Clear (Java services call Python)

**Recommendation**:
- ✅ **Core AI/ML components are complete and tested**
- ✅ **Python services are production-ready**
- ✅ **API contracts are defined and documented**
- ⚠️ **Java service layer** can be implemented in parallel or after next model
- ⚠️ **Frontend UI** is part of portal development (separate timeline)

**You can proceed to the next model**, as the remaining work (Java service layer, frontend UI) can be done independently and doesn't block other use cases.

---

## 18. Future Enhancements & TODO List

This section tracks planned enhancements and improvements for future releases.

### 18.1 Performance Optimization

#### 18.1.1 Batch Processing Optimization
- [ ] **Parallel Processing**: Implement multi-threaded/multi-process batch evaluation for larger datasets
  - Split families across multiple workers
  - Use multiprocessing or distributed computing (Dask, Ray)
  - Target: Reduce batch processing time from 6 hours to <2 hours for full scan
- [ ] **Database Query Optimization**: 
  - Implement batch loading of family data (load multiple families in single query)
  - Add database connection pooling optimizations
  - Implement query result caching for repeated evaluations
- [ ] **Incremental Evaluation**: 
  - Only evaluate families with changed data since last evaluation
  - Track data change timestamps in source systems
  - Reduce unnecessary re-evaluations

#### 18.1.2 API Performance
- [ ] **Response Caching**: 
  - Implement Redis caching for precomputed results
  - Cache candidate lists with TTL
  - Cache scheme configurations
- [ ] **Database Indexing**: 
  - Add composite indexes on frequently queried columns
  - Optimize indexes on eligibility_snapshots table
  - Implement partition pruning strategies
- [ ] **API Response Optimization**: 
  - Implement pagination for large candidate lists
  - Add response compression (gzip)
  - Implement field filtering (only return requested fields)

### 18.2 Monitoring and Alerting

#### 18.2.1 Operational Monitoring
- [ ] **Metrics Collection**: 
  - Integrate Prometheus/Grafana for metrics collection
  - Track API latency percentiles (p50, p95, p99)
  - Monitor database connection pool usage
  - Track batch job execution times
- [ ] **Alerting System**: 
  - Configure alerts for batch evaluation failures
  - Alert on API error rate > 5%
  - Alert on model loading failures
  - Alert on database connection failures
- [ ] **Health Checks**: 
  - Implement health check endpoints for all services
  - Database connectivity health check
  - MLflow connectivity health check
  - Model availability health check

#### 18.2.2 Business Metrics Dashboard
- [ ] **Real-time Dashboards**: 
  - Eligible candidates by scheme (real-time)
  - Coverage and precision metrics dashboard
  - Geographic distribution visualizations
  - Vulnerability breakdown charts
- [ ] **Historical Analysis**: 
  - Trend analysis of eligibility rates over time
  - Rule change impact analysis charts
  - Model performance trends
  - Feature importance evolution over time

#### 18.2.3 ML Model Monitoring
- [ ] **Model Performance Tracking**: 
  - Track model prediction latency
  - Monitor feature importance changes (detect data drift)
  - Track SHAP value distributions
  - Compare predicted vs. actual eligibility (when verification data available)
- [ ] **Automated Alerts**: 
  - Alert on model performance degradation
  - Alert on feature drift (distribution changes)
  - Alert on prediction confidence drops

### 18.3 Model Improvements

#### 18.3.1 Advanced Model Architectures
- [ ] **Multi-scheme Models**: 
  - Shared models for scheme families (e.g., all pension schemes)
  - Transfer learning across similar schemes
  - Reduce training time and improve generalization
- [ ] **Ensemble Models**: 
  - Combine XGBoost with other algorithms (Random Forest, Neural Networks)
  - Stacking and blending techniques
  - Improve prediction accuracy and robustness
- [ ] **Deep Learning Models**: 
  - Explore neural networks for complex pattern recognition
  - Use for schemes with non-linear eligibility patterns
  - Evaluate TensorFlow/PyTorch implementations

#### 18.3.2 Online Learning
- [ ] **Incremental Model Updates**: 
  - Update models with new data without full retraining
  - Implement online learning algorithms
  - Reduce computational cost of retraining

### 18.4 Feature Enhancements

#### 18.4.1 Real-time Capabilities
- [ ] **Event Streaming Integration**: 
  - Integrate with Kafka for real-time event processing
  - Real-time eligibility evaluation on data updates
  - Stream processing for immediate candidate list updates
- [ ] **WebSocket Support**: 
  - Real-time updates for batch job progress
  - Push notifications for eligible candidates
  - Live dashboard updates

#### 18.4.2 Explainability
- [ ] **Advanced Explainability**: 
  - Interactive SHAP visualizations in web UI
  - Individual prediction explanations (LIME, SHAP)
  - Feature interaction analysis
- [ ] **Multi-language Support**: 
  - Generate explanations in local languages (Hindi, Rajasthani)
  - Translate rule paths and explanations
  - Localized citizen hints

#### 18.4.3 Testing and Validation
- [ ] **A/B Testing Framework**: 
  - Compare multiple model versions in production
  - Split traffic between model versions
  - Statistical significance testing
- [ ] **Model Validation Framework**: 
  - Automated model validation before deployment
  - Fairness testing (bias detection)
  - Adversarial testing

### 18.5 Integration Enhancements

#### 18.5.1 API Enhancements
- [ ] **GraphQL API**: 
  - Flexible querying for complex data requirements
  - Reduce over-fetching of data
  - Single endpoint for all queries
- [ ] **Webhook Support**: 
  - Subscribe to eligibility events
  - Notify external systems of eligible candidates
  - Integration with notification services

#### 18.5.2 Mobile and Voice
- [ ] **Mobile App Integration**: 
  - REST API compatible with mobile apps
  - Optimized responses for mobile (reduced payload)
  - Offline capability considerations
- [ ] **Voice Assistant Integration**: 
  - Voice queries for eligibility status
  - Voice-based eligibility hints
  - Integration with IVR systems

### 18.6 Data and Feature Engineering

#### 18.6.1 Additional Data Sources
- [ ] **External Data Integration**: 
  - Weather data for disaster relief schemes
  - Economic indicators for livelihood schemes
  - Health records for health scheme eligibility
- [ ] **Temporal Features**: 
  - Seasonal patterns in eligibility
  - Time-based eligibility windows
  - Historical eligibility trends

#### 18.6.2 Feature Engineering
- [ ] **Advanced Feature Engineering**: 
  - Polynomial features for non-linear relationships
  - Feature interactions and cross-products
  - Domain-specific feature engineering per scheme type
- [ ] **Feature Selection Optimization**: 
  - Automated feature selection
  - Feature importance-based selection
  - Remove redundant features

### 18.7 Security and Governance

#### 18.7.1 Enhanced Security
- [ ] **API Authentication**: 
  - JWT token-based authentication
  - OAuth 2.0 integration
  - Role-based access control (RBAC)
- [ ] **Audit Logging**: 
  - Comprehensive audit trail for all operations
  - Log all API calls with user context
  - Compliance reporting capabilities

#### 18.7.2 Privacy Enhancements
- [ ] **Differential Privacy**: 
  - Add noise to aggregate statistics
  - Protect individual privacy in reports
- [ ] **Consent Management**: 
  - Enhanced consent tracking
  - Consent expiration handling
  - Granular consent per data source

### 18.8 Portal Integration & Deployment (Critical for Production)

**Note**: These items are required for portal integration and can be implemented when portal development starts.

#### 18.8.1 Spring Boot Service Layer Implementation (Priority: High)
- [ ] **EligibilityEvaluationService.java**
  - Implement service to call Python evaluation services
  - Handle request/response mapping
  - Error handling and validation
  - Integration with PythonEvaluationClient
  
- [ ] **RuleManagementService.java**
  - Implement service to call Python rule management services
  - Handle rule CRUD operations
  - Rule versioning support
  - Snapshot management
  
- [ ] **DTO Classes**
  - Create all request/response DTOs for API endpoints
  - Validation annotations
  - Documentation annotations
  - Mapping between DTOs and internal models
  
- [ ] **PythonEvaluationClient.java**
  - Implement Java client for Python service communication
  - REST API client or process execution wrapper
  - Error handling and retry logic
  - Connection pooling and timeout configuration

#### 18.8.2 Frontend Rule Management UI (Priority: Medium)
- [ ] **React Components for Rule Management**
  - RuleList component (view all rules)
  - RuleForm component (create/edit rules)
  - RuleVersionHistory component
  - RuleComparison component
  - RuleSetSnapshot component
  
- [ ] **Integration with Backend APIs**
  - API client service
  - Error handling and loading states
  - Form validation
  - Success/error notifications
  
- [ ] **UI/UX Enhancements**
  - Responsive design
  - Rule expression builder/validator
  - Rule testing interface
  - Bulk operations support

#### 18.8.3 Authentication & Authorization Integration (Priority: High)
- [ ] **Portal Authentication Integration**
  - JWT token validation
  - Session management
  - OAuth 2.0 integration (if applicable)
  
- [ ] **Authorization Implementation**
  - Role-based access control (RBAC)
  - Permission checks on API endpoints
  - Admin vs. viewer role separation
  - Audit logging with user context
  
- [ ] **Security Enhancements**
  - API key management (if needed)
  - Rate limiting
  - CORS configuration
  - Input sanitization

#### 18.8.4 Production Deployment Configuration (Priority: High)
- [ ] **Spring Boot Application Configuration**
  - Application properties for production
  - Database connection pooling configuration
  - Logging configuration
  - Environment-specific configurations (dev, staging, prod)
  
- [ ] **Deployment Setup**
  - Docker containerization (optional)
  - Kubernetes deployment manifests (if applicable)
  - CI/CD pipeline integration
  - Health check endpoints
  
- [ ] **Infrastructure Setup**
  - Load balancer configuration
  - Auto-scaling policies
  - Backup and disaster recovery
  - Database migration scripts

#### 18.8.5 Integration Testing (Priority: High)
- [ ] **End-to-End API Testing**
  - Test all API endpoints
  - Validate request/response formats
  - Error scenario testing
  - Performance testing
  
- [ ] **Integration with Portal**
  - Test frontend-backend integration
  - Validate data flow
  - Test authentication flow
  - User acceptance testing

---

## Appendices

### A. Rule Expression Syntax

Examples of rule expressions:
- `age >= 60`
- `income_band IN ('VERY_LOW', 'LOW')`
- `gender = 'Female' AND marital_status = 'WIDOW'`
- `district_id IN (101, 102, 103)`
- `family_size >= 4 AND children_count > 0`

### B. Scheme Categories

- **PENSION**: Old age, widow, disability pensions
- **PDS**: Public Distribution System (food security)
- **HEALTH**: Health insurance, medical schemes
- **EDUCATION**: Free education, scholarships
- **HOUSING**: Housing schemes, subsidies
- **EMPLOYMENT**: Skill development, employment schemes
- **AGRICULTURE**: Crop insurance, farmer schemes
- **DISABILITY**: Disability-specific schemes

### C. Evaluation Status Values

- **RULE_ELIGIBLE**: All mandatory rules passed
- **NOT_ELIGIBLE**: Mandatory rule failed
- **POSSIBLE_ELIGIBLE**: Some rules passed, needs review
- **UNCERTAIN**: Low confidence, insufficient data
- **ERROR**: Evaluation error

---

**Document Status**: ✅ Complete  
**Approved By**: AI/ML Team  
**Next Review**: Quarterly

