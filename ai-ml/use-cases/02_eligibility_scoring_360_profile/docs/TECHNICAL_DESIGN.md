# Technical Design Document: Eligibility Scoring & 360° Profiles

**Use Case ID:** AI-PLATFORM-02  
**Version:** 1.0  
**Last Updated:** 2024-12-27  
**Status:** Implementation Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Data Architecture](#data-architecture)
4. [ML Model Design](#ml-model-design)
5. [Graph Database Design (Neo4j)](#graph-database-design-neo4j)
6. [API Design](#api-design)
7. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
8. [Integration Points](#integration-points)
9. [Performance & Scalability](#performance--scalability)
10. [Security & Governance](#security--governance)
11. [Deployment Architecture](#deployment-architecture)
12. [Monitoring & Observability](#monitoring--observability)

---

## 1. Executive Summary

### 1.1 Purpose

The Eligibility Scoring & 360° Profiles system provides:
- **Eligibility Scoring**: ML-powered assessment (0-100 score) for 34+ Rajasthan government schemes
- **360° Profiles**: Complete citizen/family/business profiles with inferred insights
- **Network Analytics**: Family and benefit network graphs with anomaly detection

### 1.2 Key Capabilities

1. **Eligibility Scoring**
   - Real-time scoring (<200ms response time)
   - Support for 34+ schemes
   - Explainable AI with SHAP values
   - Family/household context consideration

2. **360° Profiles**
   - Enriched profiles extending Golden Records
   - Inferred income bands (Very Low/Low/Medium/High/Uncertain)
   - Relationship graphs (family, business, co-residence)
   - Benefit history aggregation (1Y/3Y windows)
   - Risk flags (over-concentration, under-coverage)

3. **Network Analytics**
   - Community detection (family/business clusters)
   - Benefit concentration analysis
   - Under-coverage detection
   - Anomaly flags
   - Centrality measures

### 1.3 Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Frontend**: React 18+, TypeScript
- **Database**: PostgreSQL 14+ (smart_warehouse)
- **Graph Database**: Neo4j 5.x (smartgraphdb)
- **ML**: Python 3.12, scikit-learn, XGBoost, NetworkX
- **MLOps**: MLflow 2.8+
- **Containerization**: Docker, Kubernetes

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Citizen   │  │ Department  │  │   AIML      │            │
│  │   Portal    │  │   Portal    │  │   Portal    │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │     API Gateway / Load Balancer    │
          └─────────────────┬─────────────────┘
                            │
┌───────────────────────────┴───────────────────────────┐
│              Spring Boot Backend Services              │
│  ┌──────────────────────────────────────────────┐    │
│  │  Profile360Orchestrator Service              │    │
│  │  - GET /profiles/360/{gr_id}                 │    │
│  │  - GET /eligibility/score                    │    │
│  │  - GET /analytics/benefits/*                 │    │
│  └──────────────┬───────────────────────────────┘    │
│  ┌──────────────┴───────────────────────────────┐    │
│  │  ProfileGraphController Service              │    │
│  │  - GET /graph/family-network/{gr_id}         │    │
│  │  - GET /graph/relationship-types             │    │
│  └──────────────┬───────────────────────────────┘    │
└─────────────────┼────────────────────────────────────┘
                  │
┌─────────────────┴─────────────────────────────────────┐
│              Data & ML Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │ PostgreSQL   │  │    Neo4j     │  │   MLflow    ││
│  │ smart_ware-  │  │ smartgraphdb │  │  Tracking   ││
│  │   house      │  │              │  │             ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘│
└─────────┼──────────────────┼──────────────────┼──────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴──────┐
│              ML Processing Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │ Income Band  │  │   Graph      │  │  Anomaly    ││
│  │   Model      │  │ Clustering   │  │ Detection   ││
│  │ (RF)         │  │  (Neo4j)     │  │ (IF + Rules)││
│  └──────────────┘  └──────────────┘  └─────────────┘│
│  ┌──────────────────────────────────────────────────┐│
│  │      Eligibility Scoring Model (XGBoost)        ││
│  └──────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Frontend Components

```
Citizen Portal Frontend
├── Profile360View
│   ├── ProfileHeader (basic info, income band)
│   ├── RelationshipGraph (Neo4j visualization)
│   ├── BenefitHistory (timeline, charts)
│   ├── EligibilityScores (scheme eligibility)
│   └── RiskFlags (anomalies, alerts)
├── EligibilityCalculator
│   ├── SchemeSelector
│   ├── ScoreDisplay (0-100 with explanation)
│   └── SHAPExplanation (feature importance)
└── NetworkAnalytics (for AIML portal)
    ├── ClusterVisualization
    ├── BenefitConcentrationMap
    └── UnderCoverageList
```

#### 2.2.2 Backend Services

```
Spring Boot Services
├── Profile360Orchestrator
│   ├── ProfileService (CRUD operations)
│   ├── EligibilityService (scoring logic)
│   └── AnalyticsService (aggregations)
├── ProfileGraphController
│   ├── GraphService (Neo4j queries)
│   └── RelationshipMapper (data transformation)
└── ProfileRecomputeService
    ├── RecomputeOrchestrator (scheduled jobs)
    └── QueueProcessor (async processing)
```

#### 2.2.3 ML Components

```
Python ML Pipeline
├── Training Scripts
│   ├── income_band_train.py (RandomForest)
│   ├── eligibility_scoring_train.py (XGBoost)
│   └── graph_clustering_neo4j.py (Louvain)
├── Prediction Scripts
│   ├── income_band_predict.py
│   └── eligibility_scoring_predict.py
├── Analytics Scripts
│   ├── anomaly_detection.py (Isolation Forest)
│   └── profile_recompute_service.py
└── Data Processing
    └── generate_synthetic.py (45K records)
```

---

## 3. Data Architecture

### 3.1 PostgreSQL Schema (smart_warehouse)

#### 3.1.1 Core Tables

**golden_records**
- Primary key: `gr_id` (UUID)
- Family linking: `family_id` (UUID, FK to gr_id)
- Demographics: `full_name`, `date_of_birth`, `age`, `gender`, `caste_id`
- Location: `district_id`, `city_village`, `pincode`, `is_urban`
- Status: `status` (active/inactive/merged)

**gr_relationships**
- Primary key: `relationship_id` (BIGSERIAL)
- Foreign keys: `from_gr_id`, `to_gr_id` (UUID)
- Relationship type: `relationship_type` (SPOUSE, CHILD, PARENT, etc.)
- Metadata: `is_verified`, `inference_confidence`, `source`
- Validity: `valid_from`, `valid_to`

**scheme_master**
- Primary key: `scheme_id` (SERIAL)
- Attributes: `scheme_code`, `scheme_name`, `category`
- Eligibility: `min_age`, `max_age`, `max_income`, `target_caste`, `bpl_required`

**benefit_events**
- Primary key: `event_id` (BIGSERIAL)
- Foreign keys: `gr_id` (UUID), `scheme_id` (INT)
- Transaction: `amount`, `txn_date`, `txn_type` (credit/debit)
- Source: `source_system`, `reference_number`

**application_events**
- Primary key: `application_id` (BIGSERIAL)
- Foreign keys: `gr_id` (UUID), `scheme_id` (INT)
- Status: `status` (PENDING/APPROVED/REJECTED)
- Dates: `application_date`, `decision_date`
- Scores: `eligibility_score` (0-100)

#### 3.1.2 Analytics Tables

**profile_360**
- Primary key: `profile_id` (BIGSERIAL)
- Foreign key: `gr_id` (UUID, UNIQUE)
- JSONB: `profile_data` (complete profile document)
- Quick fields: `inferred_income_band`, `income_band_confidence`, `cluster_id`
- Risk flags: `risk_flags` (TEXT[])

**analytics_benefit_summary**
- Aggregations: `total_lifetime`, `total_1y`, `total_3y`
- Grouping: `gr_id`, `scheme_id`, `category`
- Time windows: `window_start`, `window_end`

**analytics_flags**
- Flag types: `OVER_CONCENTRATION`, `UNDER_COVERAGE`, `POSSIBLE_LEAKAGE`
- Metadata: `flag_type`, `severity_score`, `explanation`, `created_at`

### 3.2 Neo4j Graph Schema (smartgraphdb)

#### 3.2.1 Node Structure

**GoldenRecord**
```cypher
(:GoldenRecord {
  gr_id: String,
  full_name: String,
  age: Integer,
  gender: String,
  family_id: String,
  district_id: Integer,
  caste_id: Integer,
  is_urban: Boolean,
  city_village: String,
  jan_aadhaar: String
})
```

#### 3.2.2 Relationship Structure

**RELATED_TO**
```cypher
(:GoldenRecord)-[:RELATED_TO {
  type: String,           // SPOUSE, CHILD, PARENT, etc.
  weight: Float,          // Relationship strength (0-1)
  is_verified: Boolean,
  confidence: Float,      // Inference confidence (0-1)
  valid_from: Date,
  valid_to: Date
}]->(:GoldenRecord)
```

#### 3.2.3 Indexes

```cypher
CREATE INDEX gr_id_index FOR (n:GoldenRecord) ON (n.gr_id);
CREATE INDEX family_id_index FOR (n:GoldenRecord) ON (n.family_id);
CREATE INDEX cluster_id_index FOR (n:GoldenRecord) ON (n.cluster_id);
```

### 3.3 Data Flow

```
1. Golden Records (AI-PLATFORM-01)
   ↓
2. Synthetic Data Generation (generate_synthetic.py)
   ├── 45,000 Golden Records
   ├── 56,000+ Relationships
   ├── 137,000 Benefit Events
   └── 53,000 Applications
   ↓
3. ML Processing Pipeline
   ├── Income Band Inference → profile_360.inferred_income_band
   ├── Graph Clustering → profile_360.cluster_id
   ├── Eligibility Scoring → application_events.eligibility_score
   └── Anomaly Detection → analytics_flags
   ↓
4. Profile 360 Table (JSONB)
   └── Complete profile document
   ↓
5. API Layer → Frontend Display
```

---

## 4. ML Model Design

### 4.1 Income Band Inference Model

**Algorithm**: RandomForest Classifier  
**Training Script**: `income_band_train.py`  
**MLflow Experiment**: `smart/eligibility_scoring_360_profile/income_band`

#### 4.1.1 Features

**Input Features:**
- `benefit_total_lifetime`: Total benefits received (lifetime)
- `benefit_total_1y`: Benefits in last 1 year
- `benefit_total_3y`: Benefits in last 3 years
- `education_level`: ILLITERATE, PRIMARY, SECONDARY, GRADUATE, etc.
- `employment_type`: UNEMPLOYED, CASUAL, REGULAR, SELF_EMPLOYED
- `family_size`: Number of family members
- `dependents_count`: Number of dependents
- `house_type`: KUTCHA, SEMI_PUCCA, PUCCA
- `land_holding_class`: NONE, SMALL, MEDIUM, LARGE
- `is_urban`: Boolean
- `district_id`: Categorical (encoded)

**Target Variable:**
- `income_band`: VERY_LOW, LOW, MEDIUM, HIGH, UNCERTAIN

**Feature Engineering:**
- Benefit ratios: `benefit_1y_per_person`, `benefit_3y_per_person`
- Age groups: `age_group` (0-18, 19-60, 60+)
- Family composition: `adults_count`, `children_count`
- Education encoding: Ordinal (ILLITERATE=0, PRIMARY=1, etc.)

#### 4.1.2 Model Architecture

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)
```

#### 4.1.3 Uncertainty Handling

- Probability threshold: `max(probabilities) < 0.6` → `UNCERTAIN`
- Confidence score: `income_band_confidence = max(probabilities)`

#### 4.1.4 Evaluation Metrics

- Accuracy: Target >75%
- Precision/Recall per class
- Confusion matrix
- Feature importance (via MLflow)

### 4.2 Eligibility Scoring Model

**Algorithm**: XGBoost Regressor  
**Training Script**: `eligibility_scoring_train.py`  
**MLflow Experiment**: `smart/eligibility_scoring_360_profile/eligibility_scoring`

#### 4.2.1 Features

**Citizen Features:**
- `age`, `gender`, `caste_id`
- `is_urban`, `district_id`
- `inferred_income_band` (from income band model)
- `family_size`, `dependents_count`

**Scheme Features:**
- `scheme_min_age`, `scheme_max_age`
- `scheme_max_income`
- `scheme_target_caste`
- `scheme_bpl_required`
- `scheme_category` (HEALTH, FOOD, EDUCATION, etc.)

**Matching Features:**
- `age_match`: `1 if min_age <= age <= max_age else 0`
- `income_match`: `1 if income_band <= scheme_max_income else 0`
- `caste_match`: `1 if caste matches scheme requirement else 0`
- `bpl_match`: `1 if bpl_required matches citizen status else 0`

**Benefit History:**
- `benefit_total_lifetime`, `benefit_total_1y`, `benefit_total_3y`
- `benefit_count_lifetime`, `benefit_count_1y`
- `benefit_category_counts` (by HEALTH, FOOD, etc.)

**Family Context:**
- `family_benefit_total`, `family_benefit_avg`
- `family_members_count`, `family_dependents_count`

#### 4.2.2 Model Architecture

```python
XGBRegressor(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42
)
```

#### 4.2.3 Output

- **Score Range**: 0-100 (continuous)
- **Interpretation**:
  - 80-100: Highly eligible
  - 60-79: Eligible
  - 40-59: Possibly eligible
  - 0-39: Not eligible

#### 4.2.4 Explainability

- **SHAP Values**: Feature importance per prediction
- **Local Explanation**: Why this citizen-scheme pair scored X
- **Global Explanation**: Feature importance across all predictions

#### 4.2.5 Evaluation Metrics

- RMSE: Target <10
- MAE: Target <8
- R²: Target >0.85
- Agreement with manual decisions: Target >90%

### 4.3 Graph Clustering

**Algorithm**: Louvain Community Detection (via Neo4j GDS)  
**Script**: `graph_clustering_neo4j.py`

#### 4.3.1 Graph Construction

**Nodes**: GoldenRecord entities  
**Edges**: RELATED_TO relationships

**Edge Weights:**
- SPOUSE: 1.0
- CHILD/PARENT: 0.9
- SIBLING: 0.8
- CO_RESIDENT: 0.7
- CO_BENEFIT: 0.6
- Other: 0.5

**Weight Adjustment:**
- If `is_verified = false`: `weight *= inference_confidence`

#### 4.3.2 Community Detection

**Primary Method (GDS):**
```cypher
CALL gds.louvain.stream('smart-graph', {
    relationshipWeightProperty: 'weight',
    includeIntermediateCommunities: false
})
YIELD nodeId, communityId
```

**Fallback Method (if GDS unavailable):**
- Family-based clustering: Group by `family_id`
- Connected components: Simple Cypher queries

#### 4.3.3 Centrality Measures

- **Degree Centrality**: Number of connections
- **PageRank**: Importance in network
- **Betweenness Centrality**: Bridge nodes (if GDS available)
- **Closeness Centrality**: Proximity to all nodes (if GDS available)

#### 4.3.4 Output

- `cluster_id`: Assigned to each node (e.g., "cluster_123", "family_uuid")
- Centrality scores stored in profile_360 JSONB

### 4.4 Anomaly Detection

**Algorithm**: Isolation Forest + Rule-Based  
**Script**: `anomaly_detection.py`

#### 4.4.1 Rule-Based Flags

**OVER_CONCENTRATION:**
```python
if benefit_total_1y > 3 * district_avg_benefit_1y:
    flag = OVER_CONCENTRATION
    severity = min(1.0, (benefit_total_1y / district_avg) / 5)
```

**UNDER_COVERAGE:**
```python
if eligibility_score > 0.8 AND benefit_total_lifetime == 0:
    flag = UNDER_COVERAGE
    severity = eligibility_score
```

**POSSIBLE_LEAKAGE:**
```python
if (benefit_total > threshold AND 
    eligibility_score < 0.4 AND
    multiple_benefits_same_day):
    flag = POSSIBLE_LEAKAGE
```

#### 4.4.2 Isolation Forest

**Features:**
- Benefit amounts (normalized)
- Eligibility scores
- Family benefit ratios
- Application patterns

**Output:**
- Anomaly score: 0-1 (higher = more anomalous)
- Combined with rules for final flag

---

## 5. Graph Database Design (Neo4j)

### 5.1 Graph Structure

```
┌─────────────────────────────────────────┐
│         GoldenRecord Nodes              │
│  ┌───────────────────────────────────┐  │
│  │ Properties:                       │  │
│  │ - gr_id (unique identifier)       │  │
│  │ - full_name                       │  │
│  │ - age, gender                     │  │
│  │ - family_id                       │  │
│  │ - district_id, caste_id           │  │
│  └───────────────────────────────────┘  │
│                                          │
│         ┌──────────┐                    │
│         │  Person  │                    │
│         │   Node   │                    │
│         └────┬─────┘                    │
│              │                          │
│    ┌─────────┼─────────┐                │
│    │         │         │                │
│ SPOUSE    CHILD    SIBLING              │
│    │         │         │                │
│    ▼         ▼         ▼                │
│  ┌───┐    ┌───┐    ┌───┐               │
│  │ P │    │ P │    │ P │               │
│  └───┘    └───┘    └───┘               │
└─────────────────────────────────────────┘
```

### 5.2 Relationship Types

| Type | Direction | Description | Weight |
|------|-----------|-------------|--------|
| SPOUSE | Bidirectional | Married partners | 1.0 |
| CHILD | Parent → Child | Parent has child | 0.9 |
| PARENT | Child → Parent | Child belongs to parent | 0.9 |
| SIBLING | Bidirectional | Brothers/Sisters | 0.8 |
| CO_RESIDENT | Bidirectional | Same address | 0.7 |
| CO_BENEFIT | Bidirectional | Same benefits | 0.6 |
| EMPLOYEE_OF | Employee → Employer | Employment | 0.5 |
| BUSINESS_PARTNER | Bidirectional | Business relationship | 0.5 |
| SHG_MEMBER | Bidirectional | Self-Help Group | 0.4 |

### 5.3 Query Patterns

#### 5.3.1 Family Network

```cypher
MATCH path = (start:GoldenRecord {gr_id: $grId})-[r:RELATED_TO*1..2]-(connected:GoldenRecord)
WHERE r.type IN ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING']
   OR connected.family_id = start.family_id
RETURN path
```

#### 5.3.2 Community Detection

```cypher
CALL gds.louvain.stream('smart-graph', {
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).gr_id AS gr_id, 
       communityId AS cluster_id
```

#### 5.3.3 Centrality Calculation

```cypher
MATCH (n:GoldenRecord)
OPTIONAL MATCH (n)-[r:RELATED_TO]-()
WITH n, count(r) AS degree
RETURN n.gr_id, degree AS degree_centrality
ORDER BY degree DESC
```

### 5.4 Performance Optimization

1. **Indexes**: On `gr_id`, `family_id`, `cluster_id`
2. **GDS Projections**: For large-scale algorithms
3. **Batch Processing**: For bulk operations
4. **Approximate Algorithms**: For very large graphs (>100K nodes)

---

## 6. API Design

### 6.1 REST API Endpoints

#### 6.1.1 Profile 360 APIs

**GET /api/v1/profiles/360/{gr_id}**
- **Description**: Get complete 360° profile
- **Parameters**: 
  - `gr_id` (path): Golden Record ID
  - `view` (query): citizen|officer|admin (default: citizen)
- **Response**: Profile JSONB with all sections

**GET /api/v1/profiles/360/{gr_id}/network**
- **Description**: Get relationship network (cluster neighbors)
- **Response**: List of related profiles

#### 6.1.2 Eligibility Scoring APIs

**GET /api/v1/eligibility/score**
- **Description**: Get eligibility score for citizen-scheme pair
- **Parameters**:
  - `gr_id` (required): Golden Record ID
  - `scheme_id` (required): Scheme ID
- **Response**: 
  ```json
  {
    "gr_id": "uuid",
    "scheme_id": 1,
    "eligibility_score": 85.5,
    "confidence": 0.92,
    "explanation": {
      "shap_values": {...},
      "feature_importance": {...}
    }
  }
  ```

**POST /api/v1/eligibility/score/batch**
- **Description**: Score multiple citizen-scheme pairs
- **Request Body**: Array of `{gr_id, scheme_id}`
- **Response**: Array of scores

#### 6.1.3 Graph APIs

**GET /api/v1/profiles/graph/family-network/{gr_id}**
- **Description**: Get family network graph data
- **Parameters**: `depth` (default: 2)
- **Response**:
  ```json
  {
    "nodes": [
      {"id": 1, "gr_id": "uuid", "label": "John Doe", ...}
    ],
    "links": [
      {"source": 1, "target": 2, "relationship_type": "SPOUSE", ...}
    ]
  }
  ```

**GET /api/v1/profiles/graph/relationship-types**
- **Description**: Get relationship type legend
- **Response**: Map of relationship types with labels, icons, colors

#### 6.1.4 Analytics APIs

**GET /api/v1/analytics/benefits/clusters**
- **Description**: Benefit analytics by clusters
- **Parameters**: `scheme`, `district`, `category`
- **Response**: Aggregated statistics

**GET /api/v1/analytics/benefits/undercoverage**
- **Description**: List under-covered families
- **Parameters**: `limit`, `min_score`
- **Response**: List of profiles with eligibility > 0.8 but benefits = 0

**GET /api/v1/analytics/flags/{flag_type}**
- **Description**: Get flagged profiles
- **Parameters**: `flag_type` (OVER_CONCENTRATION, UNDER_COVERAGE, etc.)
- **Response**: List of flagged profiles with explanations

#### 6.1.5 Internal APIs

**POST /api/v1/internal/recompute/{gr_id}**
- **Description**: Trigger profile recomputation
- **Authentication**: Internal service token
- **Response**: Job ID for tracking

**GET /api/v1/internal/recompute/status/{job_id}**
- **Description**: Check recomputation status

### 6.2 API Response Formats

#### Standard Success Response

```json
{
  "success": true,
  "data": {...},
  "metadata": {
    "timestamp": "2024-12-27T10:00:00Z",
    "version": "1.0"
  }
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "message": "Profile with gr_id not found",
    "details": {...}
  }
}
```

### 6.3 API Authentication & Authorization

- **JWT Tokens**: For authenticated requests
- **Role-Based Access**: citizen, officer, admin
- **Data Filtering**: Based on view parameter
- **Rate Limiting**: Per user/IP

---

## 7. Data Flow & Processing Pipeline

### 7.1 Profile Computation Flow

```
1. New/Updated Golden Record
   ↓
2. Trigger Profile Recompute (via queue or API)
   ↓
3. Data Collection Phase
   ├── Load Golden Record
   ├── Load Relationships (PostgreSQL)
   ├── Load Benefit History
   ├── Load Application History
   └── Load Family Members
   ↓
4. ML Inference Phase
   ├── Income Band Prediction (RandomForest)
   ├── Graph Clustering (Neo4j)
   ├── Eligibility Scoring (if needed)
   └── Anomaly Detection
   ↓
5. Aggregation Phase
   ├── Benefit Totals (1Y, 3Y, lifetime)
   ├── Benefit by Category
   ├── Family Aggregations
   └── Network Metrics
   ↓
6. Profile Assembly
   ├── Build JSONB Profile Document
   ├── Update profile_360 Table
   └── Update Neo4j cluster_id
   ↓
7. Notification (if configured)
   └── Send update notification
```

### 7.2 Real-Time Eligibility Scoring Flow

```
1. API Request: GET /eligibility/score?gr_id=X&scheme_id=Y
   ↓
2. Load Citizen Profile (cached if available)
   ├── Basic demographics
   ├── Income band (from profile_360)
   ├── Benefit history
   └── Family context
   ↓
3. Load Scheme Criteria
   ├── Eligibility rules
   └── Requirements
   ↓
4. Feature Engineering
   ├── Citizen features
   ├── Scheme features
   ├── Matching features
   └── Context features
   ↓
5. ML Model Prediction
   ├── XGBoost Inference
   ├── Score (0-100)
   └── Confidence
   ↓
6. Explainability (SHAP)
   ├── Calculate SHAP values
   └── Feature importance
   ↓
7. Response Assembly
   └── Return score + explanation
```

### 7.3 Scheduled Jobs

#### Hourly: Profile Recompute

```java
@Scheduled(cron = "0 0 * * * *") // Every hour
public void recomputeUpdatedProfiles() {
    // 1. Query profile_recompute_queue
    // 2. Process each gr_id
    // 3. Update profile_360
}
```

#### Daily: Graph Clustering

```bash
# Run via cron or scheduler
python graph_clustering_neo4j.py
```

#### Weekly: Anomaly Detection

```bash
# Run batch anomaly detection
python anomaly_detection.py --batch
```

---

## 8. Integration Points

### 8.1 AI-PLATFORM-01 (Golden Records)

**Integration Type**: Prerequisite dependency

**Data Flow:**
- Golden Records are source of truth
- 360° Profiles extend Golden Records
- Updates to Golden Records trigger profile recomputation

**API Integration:**
- Direct database access to `golden_records` table
- Event-driven updates (via queue or webhook)

### 8.2 Citizen Portal

**Integration Points:**
1. **Profile View**: Display 360° profile
2. **Relationship Graph**: Visualize family network
3. **Eligibility Scores**: Show scheme eligibility
4. **Benefit History**: Timeline of benefits received

**Frontend Components:**
- `RelationshipGraph.tsx` (Neo4j visualization)
- `Profile360View.tsx` (complete profile)
- `EligibilityCalculator.tsx` (score display)

### 8.3 Department Portal

**Integration Points:**
1. **Eligibility API**: Score citizens for schemes
2. **Analytics Dashboard**: Benefit concentration, under-coverage
3. **Flag Management**: Review and act on anomaly flags

**Use Cases:**
- Batch eligibility scoring for scheme rollout
- Identify eligible but not enrolled families
- Investigate over-concentration flags

### 8.4 AIML Portal

**Integration Points:**
1. **MLflow Integration**: Model training, evaluation, tracking
2. **Analytics Visualization**: Cluster maps, network graphs
3. **Model Management**: Version control, A/B testing

**Components:**
- Model performance dashboards
- Cluster visualization (d3.js)
- Feature importance analysis

### 8.5 External Systems

**Benefit Disbursement Systems:**
- Read benefit_events table
- Trigger profile updates on new benefits

**Application Systems:**
- Read application_events table
- Update eligibility scores

**Notification Systems:**
- Send alerts on risk flags
- Notify on profile updates

---

## 9. Performance & Scalability

### 9.1 Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Eligibility Score API | <200ms | ~150ms |
| Profile 360 API | <500ms | ~300ms |
| Graph Network API | <1s | ~600ms |
| Profile Recompute | <5s | ~3s |
| Graph Clustering (45K nodes) | <5min | ~3min (with Neo4j) |

### 9.2 Scalability Strategies

#### 9.2.1 Database Optimization

**PostgreSQL:**
- Indexes on all foreign keys
- Partitioning for large tables (by date)
- Materialized views for aggregations
- Connection pooling (HikariCP)

**Neo4j:**
- Indexes on `gr_id`, `family_id`
- GDS projections for algorithms
- Approximate algorithms for large graphs
- Batch operations for bulk updates

#### 9.2.2 Caching Strategy

**Redis Cache:**
- Profile 360 documents (TTL: 1 hour)
- Eligibility scores (TTL: 30 minutes)
- Relationship types legend (TTL: 24 hours)
- Scheme master data (TTL: 1 hour)

**Application Cache:**
- ML models (in-memory)
- Feature encoders
- Scheme criteria

#### 9.2.3 Async Processing

**Queue System (RabbitMQ/Kafka):**
- Profile recomputation queue
- Batch eligibility scoring
- Anomaly detection jobs

**Processing:**
- Scheduled jobs for batch operations
- Event-driven updates for real-time data

#### 9.2.4 Horizontal Scaling

**Backend Services:**
- Stateless Spring Boot services
- Load balancer (Nginx/HAProxy)
- Auto-scaling based on CPU/memory

**ML Services:**
- Separate Python service for ML inference
- Model serving (MLflow or custom)
- Batch processing workers

### 9.3 Capacity Planning

**Current Capacity:**
- 45,000 Golden Records
- 56,000+ Relationships
- 137,000 Benefit Events
- Handles ~1000 API requests/minute

**Scaling Targets:**
- 1M+ Golden Records
- 5M+ Relationships
- 10M+ Benefit Events
- 10,000+ API requests/minute

**Scaling Strategy:**
1. Database sharding (by district)
2. Graph partitioning (by family clusters)
3. Read replicas for PostgreSQL
4. Neo4j clustering (Enterprise)
5. CDN for static assets

---

## 10. Security & Governance

### 10.1 Data Privacy

**Consent Management:**
- `consent_flags` table tracks consent per use case
- Income inference requires explicit consent
- Risk analytics requires explicit consent
- Relationship inference requires explicit consent

**Data Anonymization:**
- PII masking in logs
- Pseudonymization for analytics
- Data retention policies (1-7 years based on type)

### 10.2 Access Control

**Role-Based Access Control (RBAC):**
- **Citizen**: Own profile only
- **Officer**: Department data + analytics
- **Admin**: Full access + system management

**API Authentication:**
- JWT tokens with role claims
- API keys for service-to-service
- OAuth2 for external integrations

**Data Filtering:**
- `view` parameter controls data returned
- Row-level security in PostgreSQL
- Query filtering based on user role

### 10.3 Audit & Compliance

**Audit Logging:**
- All profile accesses logged
- Eligibility score calculations logged
- Profile updates tracked
- Compliance with DPDP (Digital Personal Data Protection)

**Data Retention:**
- Profile history: 1 year
- Benefit history: 5 years
- Audit logs: 7 years
- ML training data: 3 years

### 10.4 Model Governance

**Model Versioning:**
- MLflow model registry
- Version tracking per model
- A/B testing for new models
- Rollback capability

**Model Monitoring:**
- Performance degradation alerts
- Data drift detection
- Prediction distribution monitoring
- Fairness audits (quarterly)

**Fairness Metrics:**
- Demographic parity checks
- Equalized odds
- Max 10% difference in flag rates across groups
- Regular bias audits

---

## 11. Deployment Architecture

### 11.1 Container Architecture

```
┌─────────────────────────────────────────────────┐
│              Kubernetes Cluster                 │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Frontend   │  │   Backend    │           │
│  │   (React)    │  │ (Spring Boot)│           │
│  │   Nginx      │  │   Services   │           │
│  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                    │
│  ┌──────┴─────────────────┴───────┐           │
│  │      PostgreSQL (StatefulSet)   │           │
│  └──────────────┬──────────────────┘           │
│                 │                               │
│  ┌──────────────┴──────────────────┐           │
│  │      Neo4j (StatefulSet)        │           │
│  └──────────────┬──────────────────┘           │
│                 │                               │
│  ┌──────────────┴──────────────────┐           │
│  │   ML Services (Jobs/CronJobs)   │           │
│  │   - Training Jobs                │           │
│  │   - Inference Services           │           │
│  └──────────────────────────────────┘           │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   MLflow     │  │    Redis     │           │
│  │   (Tracking) │  │   (Cache)    │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

### 11.2 Deployment Components

#### 11.2.1 Frontend Deployment

**Dockerfile:**
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

**Kubernetes Deployment:**
- Deployment with 3 replicas
- Service (LoadBalancer/Ingress)
- ConfigMap for environment variables

#### 11.2.2 Backend Deployment

**Dockerfile:**
```dockerfile
FROM maven:3.8-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:17-jre-slim
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Kubernetes Deployment:**
- Deployment with 5 replicas (auto-scaling)
- Service (ClusterIP)
- ConfigMap for application.yml
- Secret for database credentials

#### 11.2.3 Database Deployment

**PostgreSQL:**
- StatefulSet with persistent volumes
- PersistentVolumeClaim for data
- ConfigMap for postgresql.conf
- Secret for credentials

**Neo4j:**
- StatefulSet with persistent volumes
- PersistentVolumeClaim for data
- ConfigMap for neo4j.conf
- Secret for credentials

#### 11.2.4 ML Services Deployment

**Training Jobs:**
- Kubernetes CronJob for scheduled training
- Job for on-demand training
- PersistentVolume for model storage

**Inference Services:**
- Deployment with ML model loaded
- Service for inference API
- HorizontalPodAutoscaler for scaling

### 11.3 CI/CD Pipeline

```
1. Code Commit → GitHub/GitLab
   ↓
2. Build Stage
   ├── Run Tests (Unit, Integration)
   ├── Build Docker Images
   └── Push to Container Registry
   ↓
3. Deploy to Staging
   ├── Apply Kubernetes Manifests
   ├── Run Integration Tests
   └── Smoke Tests
   ↓
4. Deploy to Production
   ├── Blue-Green Deployment
   ├── Health Checks
   └── Rollback if needed
```

### 11.4 Environment Configuration

**Development:**
- Single-node Kubernetes (minikube/k3s)
- Local PostgreSQL & Neo4j
- MLflow local tracking

**Staging:**
- Multi-node Kubernetes cluster
- Managed PostgreSQL & Neo4j
- MLflow server

**Production:**
- Multi-region Kubernetes cluster
- High-availability databases
- MLflow with S3 backend

---

## 12. Monitoring & Observability

### 12.1 Metrics

#### 12.1.1 Application Metrics

**API Metrics:**
- Request rate (RPS)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections

**Business Metrics:**
- Profiles computed per hour
- Eligibility scores calculated
- Anomaly flags generated
- Graph clusters detected

#### 12.1.2 ML Metrics

**Model Performance:**
- Prediction accuracy
- Inference latency
- Model drift score
- Feature distribution changes

**Training Metrics:**
- Training time
- Model version
- Evaluation metrics (RMSE, Accuracy, etc.)

#### 12.1.3 Infrastructure Metrics

**Database:**
- Connection pool usage
- Query execution time
- Database size
- Replication lag

**Neo4j:**
- Graph size (nodes, relationships)
- Query performance
- Memory usage
- GDS algorithm execution time

### 12.2 Logging

**Application Logs:**
- Structured JSON logging
- Log levels: DEBUG, INFO, WARN, ERROR
- Request/response logging
- Correlation IDs for tracing

**ML Logs:**
- Training logs (MLflow)
- Inference logs
- Model evaluation logs
- Feature engineering logs

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Or: Loki + Grafana
- Retention: 30 days (hot), 1 year (cold)

### 12.3 Tracing

**Distributed Tracing:**
- OpenTelemetry for instrumentation
- Jaeger or Zipkin for tracing
- Trace API requests across services
- Identify performance bottlenecks

**Trace Points:**
- API entry/exit
- Database queries
- Neo4j queries
- ML model inference
- External service calls

### 12.4 Alerting

**Critical Alerts:**
- API error rate > 5%
- Response time p95 > 1s
- Database connection failures
- Neo4j connection failures
- Model inference failures

**Warning Alerts:**
- High memory usage (>80%)
- Disk space < 20%
- Model performance degradation
- Queue backlog > 1000 items

**Notification Channels:**
- Email for critical alerts
- Slack for warnings
- PagerDuty for on-call

### 12.5 Dashboards

**Application Dashboard:**
- API performance (Grafana)
- Error rates
- Request volume
- Active users

**ML Dashboard:**
- Model performance (MLflow UI)
- Training metrics
- Prediction distributions
- Feature importance

**Business Dashboard:**
- Profiles computed
- Eligibility scores distribution
- Anomaly flags by type
- Benefit analytics

---

## 13. Future Enhancements

### 13.1 Planned Features

1. **Real-Time Updates**: WebSocket for live profile updates
2. **Advanced Graph Algorithms**: More community detection methods
3. **Federated Learning**: Privacy-preserving model training
4. **Multi-Language Support**: Hindi, Rajasthani translations
5. **Mobile App**: React Native app for citizens

### 13.2 Research Areas

1. **Graph Neural Networks**: For relationship inference
2. **Transformer Models**: For eligibility scoring
3. **Explainable AI**: Better SHAP integration
4. **Fairness**: Advanced bias detection and mitigation

---

## 14. Appendices

### 14.1 Glossary

- **Golden Record**: Master citizen record (from AI-PLATFORM-01)
- **360° Profile**: Complete enriched profile with ML insights
- **Eligibility Score**: 0-100 score for scheme eligibility
- **Income Band**: Inferred income category (VERY_LOW, LOW, MEDIUM, HIGH)
- **Cluster**: Community of related people (family/business network)
- **Anomaly Flag**: Risk indicator (OVER_CONCENTRATION, UNDER_COVERAGE)

### 14.2 References

- Neo4j Documentation: https://neo4j.com/docs/
- MLflow Documentation: https://mlflow.org/docs/latest/index.html
- XGBoost Documentation: https://xgboost.readthedocs.io/
- Spring Boot Documentation: https://spring.io/projects/spring-boot
- React Force Graph: https://github.com/vasturiano/react-force-graph

### 14.3 Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-27 | Initial design document |

---

**Document Owner**: AI/ML Team  
**Review Frequency**: Quarterly  
**Next Review**: 2025-03-27

