# Golden Record Extraction - Design Document

**Document Version:** 1.0  
**Last Updated:** 2024-12-26  
**Use Case ID:** AI-PLATFORM-01  
**Author:** SMART AI/ML Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Data Sources](#2-data-sources)
3. [Extraction Parameters](#3-extraction-parameters)
4. [Extraction Process Flow](#4-extraction-process-flow)
5. [Feature Engineering](#5-feature-engineering)
6. [ML Models & Algorithms](#6-ml-models--algorithms)
7. [Output Format](#7-output-format)
8. [Configuration Reference](#8-configuration-reference)
9. [Architecture](#9-architecture)
10. [Implementation Details](#10-implementation-details)

---

## 1. Executive Summary

### 1.1 Purpose

The Golden Record Extraction system creates and maintains a **single source of truth** for citizen data by:

1. **Deduplicating** records across multiple sources
2. **Reconciling conflicts** when the same attribute has different values
3. **Selecting the best truth** for each citizen attribute
4. **Maintaining** a unified Golden Record with metadata and lineage

### 1.2 Key Capabilities

- **Probabilistic Deduplication**: Uses Fellegi-Sunter model to identify duplicate records
- **Multi-Source Integration**: Combines data from 34+ schemes and 171+ services
- **Conflict Resolution**: ML-powered reconciliation with source authority ranking
- **Continuous Learning**: Weekly retraining on admin corrections

### 1.3 Success Metrics

- **Precision**: >95% (correct merges)
- **Recall**: >95% (duplicates found)
- **Coverage**: >90% of Jan Aadhaar base
- **Accuracy**: >99% Golden Record accuracy
- **False Positive Rate**: <1%

---

## 2. Data Sources

### 2.1 Primary Data Sources

| Source | Priority | Authority Score | Description | Enabled |
|--------|----------|-----------------|-------------|---------|
| **Jan Aadhaar** | High | 10.0 | Rajasthan's Aadhaar database | ✅ |
| **Raj D.Ex** | High | 8.0 | Rajasthan Digital Exchange | ✅ |
| **Citizens Table** | High | 5.0 | Master citizen data (smart_warehouse) | ✅ |
| **Schemes** | Medium | 5.0 | 34+ government schemes data | ✅ |
| **Services** | Medium | 5.0 | 171+ government services data | ✅ |

### 2.2 Validation Sources

| Source | Authority Score | Purpose |
|--------|-----------------|---------|
| **Aadhaar** | 10.0 | Highest authority for personal identification |
| **Passport** | 8.0 | Official travel document |
| **Birth Certificate** | 7.0 | Legal proof of birth |
| **Employment Ledger** | 6.0 | Employment history verification |
| **Educational Certificate** | 6.0 | Education qualification proof |
| **Scheme Data** | 5.0 | Government scheme enrollment records |
| **Self Declared** | 3.0 | Citizen-provided information |

### 2.3 Data Source Priority Hierarchy

```
Priority 1 (Highest Authority):
├── Jan Aadhaar (10.0)
└── Raj D.Ex (8.0)

Priority 2 (Validation Documents):
├── Passport (8.0)
├── Birth Certificate (7.0)
├── Employment Ledger (6.0)
└── Educational Certificate (6.0)

Priority 3 (Operational Data):
├── Schemes Data (5.0)
├── Services Data (5.0)
└── Citizens Table (5.0)

Priority 4 (Lowest Authority):
└── Self Declared (3.0)
```

### 2.4 Data Source Queries

**Database Connection:**
- **Host**: 172.17.16.1
- **Port**: 5432
- **Database**: smart_warehouse
- **Schema**: public

**Key Queries:**
```sql
-- Get all active citizens
SELECT * FROM citizens WHERE status = 'active'

-- Get citizen by Jan Aadhaar
SELECT * FROM citizens WHERE jan_aadhaar = %s

-- Get active schemes
SELECT * FROM schemes WHERE status = 'active'
```

---

## 3. Extraction Parameters

### 3.1 Deduplication Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Model Type** | `fellegi_sunter` | Probabilistic record linkage algorithm |
| **Auto Merge Threshold** | 0.95 (95%) | >95% confidence → automatic merge |
| **Manual Review Threshold** | 0.80 (80%) | 80-95% confidence → manual review |
| **Reject Threshold** | 0.80 (80%) | <80% confidence → reject (different people) |

### 3.2 Feature Weights

| Feature | Type | Algorithm | Weight | Description |
|---------|------|-----------|--------|-------------|
| **Fuzzy String Name** | fuzzy_match | Jaro-Winkler | 0.30 (30%) | Name similarity (handles typos) |
| **Date of Birth** | exact_match | Exact | 0.25 (25%) | Birth date matching |
| **Phonetic Name** | phonetic | Soundex | 0.20 (20%) | Phonetic name encoding |
| **Geospatial Address** | geospatial | Haversine | 0.15 (15%) | Address distance (km) |
| **Income Similarity** | numeric_similarity | Percentage | 0.10 (10%) | Income within 10% tolerance |

**Total Weight**: 1.00 (100%)

### 3.3 Attribute Matching Parameters

#### Personal Attributes

| Attribute | Matching Method | Weight | Tolerance |
|-----------|----------------|--------|-----------|
| `full_name` | fuzzy_phonetic | 0.35 | Jaro-Winkler ≥ 0.85 |
| `date_of_birth` | exact | 0.25 | Exact match required |
| `gender` | exact | 0.05 | Exact match |
| `caste_id` | exact | 0.05 | Exact match |

#### Location Attributes

| Attribute | Matching Method | Weight | Tolerance |
|-----------|----------------|--------|-----------|
| `address` | fuzzy_geospatial | 0.15 | Distance ≤ 5 km |
| `district_id` | exact | 0.05 | Exact match |
| `pincode` | exact | 0.05 | Exact match |
| `city_village` | fuzzy | 0.03 | Fuzzy similarity |

#### Economic Attributes

| Attribute | Matching Method | Weight | Tolerance |
|-----------|----------------|--------|-----------|
| `family_income` | similarity | 0.10 | ±10% tolerance |
| `employment_id` | exact | 0.02 | Exact match |

### 3.4 Conflict Reconciliation Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Model Type** | `xgboost_ensemble` | Gradient boosting classifier |
| **N Estimators** | 200 | Number of boosting rounds |
| **Max Depth** | 8 | Maximum tree depth |
| **Learning Rate** | 0.1 | Shrinkage parameter |

**Ranking Factors:**
- **Recency Weight**: 0.4 (40%) - Recent data preferred
- **Source Authority Weight**: Dynamic - Based on source hierarchy
- **Completeness Weight**: 0.2 (20%) - Complete records preferred
- **Min Completeness**: 0.7 (70%)

### 3.5 Best Truth Selection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Model Type** | `survival_analysis` | Predicts record staleness |
| **Retrain Frequency** | Weekly | Model retraining schedule |
| **Staleness Threshold** | 365 days | Records older than 1 year flagged |

### 3.6 Data Quality Parameters

**Validation Rules:**

| Attribute | Min | Max | Pattern | Required |
|-----------|-----|-----|---------|----------|
| `date_of_birth` | Age 0 | Age 120 | Date format | ✅ Yes |
| `income` | 0 | 1,00,00,000 | Numeric | No |
| `mobile_number` | - | - | `^[6-9][0-9]{9}$` | No |
| `pincode` | - | - | `^[0-9]{6}$` | No |

**Completeness Requirements:**
- **Required Fields**: `jan_aadhaar`, `full_name`, `date_of_birth`
- **Min Completeness Score**: 0.7 (70%)

### 3.7 Fuzzy Matching Parameters

| Algorithm | Threshold | Description |
|-----------|-----------|-------------|
| **Levenshtein** | Max distance: 3 | Edit distance for typos |
| **Jaro-Winkler** | ≥ 0.85 | String similarity (preferred) |
| **Jaro** | ≥ 0.90 | Alternative similarity metric |

### 3.8 Geospatial Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Distance Metric** | Haversine | Great-circle distance |
| **Max Distance** | 5.0 km | Maximum distance for match |
| **Address Parsing** | Enabled | NLP-based address parsing |

### 3.9 Numeric Similarity Parameters

| Attribute | Tolerance | Method |
|-----------|-----------|--------|
| **Income** | ±10% | Percentage tolerance |
| **Age** | ±1 year | Absolute tolerance |

---

## 4. Extraction Process Flow

### 4.1 Overall Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOLDEN RECORD EXTRACTION                      │
└─────────────────────────────────────────────────────────────────┘

Step 1: Data Ingestion
├── Load from Jan Aadhaar (Priority: High)
├── Load from Raj D.Ex (Priority: High)
├── Load from Citizens Table (smart_warehouse)
├── Load from 34+ Schemes
└── Load from 171+ Services

Step 2: Data Preprocessing
├── Validate data quality
├── Handle missing values (median/median imputation)
├── Normalize features
└── Encode categorical variables (one-hot encoding)

Step 3: Feature Engineering
├── Compute fuzzy string matches (Jaro-Winkler, Levenshtein)
├── Generate phonetic encodings (Soundex, Metaphone)
├── Calculate geospatial distances (Haversine)
├── Compute numeric similarities (Income, Age)
└── Create feature vectors for each record pair

Step 4: Deduplication (Fellegi-Sunter Model)
├── Estimate m-probabilities (match given agreement)
├── Estimate u-probabilities (non-match given agreement)
├── Compute match scores for all record pairs
├── Apply thresholds:
│   ├── >95% → Auto Merge
│   ├── 80-95% → Manual Review
│   └── <80% → Reject
└── Generate candidate duplicate pairs

Step 5: Conflict Reconciliation (XGBoost Ensemble)
├── For each conflicting attribute:
│   ├── Rank versions by recency (40% weight)
│   ├── Rank versions by source authority (dynamic weight)
│   ├── Rank versions by completeness (20% weight)
│   └── Generate confidence scores
└── Select best version per attribute

Step 6: Best Truth Selection (Survival Analysis)
├── Predict record staleness
├── Apply source priority rules:
│   ├── Aadhaar > Passport > Birth Certificate
│   ├── Employment Ledger > Educational Certificate
│   └── Scheme Data > Self Declared
└── Select final "best truth"

Step 7: Golden Record Creation
├── Merge duplicate records
├── Resolve conflicts using best truth
├── Create unified record with metadata:
│   ├── Source attribution
│   ├── Confidence scores
│   ├── Last updated timestamp
│   └── Merge history
└── Store in PostgreSQL (JSONB format)

Step 8: Output & API
├── Generate Golden Record JSON
├── Store in database (smart_warehouse)
├── Create 360° profile extensions
└── Expose via REST API
```

### 4.2 Detailed Step-by-Step Process

#### Step 1: Data Ingestion

**Sources to Extract:**
1. **Jan Aadhaar**: `SELECT * FROM citizens WHERE jan_aadhaar IS NOT NULL`
2. **Raj D.Ex**: External API integration (future)
3. **Citizens Table**: `SELECT * FROM citizens WHERE status = 'active'`
4. **Schemes**: `SELECT * FROM schemes WHERE status = 'active'`
5. **Services**: Service-specific queries (future)

**Output**: Raw records DataFrame with source attribution

#### Step 2: Data Preprocessing

**Operations:**
- Remove duplicate records within same source
- Validate data quality (age, income ranges)
- Handle missing values:
  - Numeric: Median imputation
  - Categorical: Mode imputation
  - Dates: Flag as missing
- Normalize features for ML models
- One-hot encode categorical variables

**Output**: Cleaned, normalized records

#### Step 3: Feature Engineering

**For Each Record Pair:**
1. **Name Similarity**:
   - Jaro-Winkler score
   - Levenshtein distance
   - Phonetic encoding match (Soundex, Metaphone)

2. **Date of Birth**:
   - Exact match (binary)
   - Age difference (numeric)

3. **Address Similarity**:
   - Haversine distance (if coordinates available)
   - Fuzzy string match for address text
   - Pincode exact match

4. **Economic Similarity**:
   - Income percentage difference
   - Employment type match

**Output**: Feature vector for each record pair

#### Step 4: Deduplication

**Fellegi-Sunter Algorithm:**
1. **Training Phase**:
   - Create training pairs (matches + non-matches)
   - Estimate m-probabilities (P(agreement | match))
   - Estimate u-probabilities (P(agreement | non-match))

2. **Prediction Phase**:
   - For each record pair, compute agreement vector
   - Calculate log-likelihood ratio
   - Convert to match probability (0-1)

3. **Decision Making**:
   - Match score ≥ 0.95 → Auto merge
   - Match score 0.80-0.95 → Manual review
   - Match score < 0.80 → Reject

**Output**: Candidate duplicate pairs with match scores and decisions

#### Step 5: Conflict Reconciliation

**For Conflicting Attributes:**
1. **Collect all versions** of the attribute from different sources
2. **Rank versions** using XGBoost ensemble:
   - Feature 1: Recency score (0-1, based on age)
   - Feature 2: Source authority score (0-10)
   - Feature 3: Completeness score (0-1)
3. **Generate confidence scores** for each version
4. **Select top-ranked version** as reconciled value

**Output**: Reconciled attributes with confidence scores

#### Step 6: Best Truth Selection

**Survival Analysis + Rules:**
1. **ML Component**: Predict record staleness (time until record becomes outdated)
2. **Rule Component**: Apply source priority hierarchy
3. **Combine**: Weight ML predictions with rule-based priorities
4. **Select**: Final "best truth" for each attribute

**Output**: Final attribute values with staleness predictions

#### Step 7: Golden Record Creation

**Merge Process:**
1. **Group duplicates**: Cluster records identified as duplicates
2. **Merge attributes**: Use reconciled "best truth" values
3. **Generate metadata**:
   - Source list (all sources contributing)
   - Confidence scores per attribute
   - Last updated timestamp
   - Merge history (which records were merged)
4. **Store**: Save to `golden_records` table in PostgreSQL

**Output**: Unified Golden Record JSON

#### Step 8: Output & API

**Golden Record Format:**
```json
{
  "golden_record_id": "GR-12345",
  "jan_aadhaar": "RJ123456789",
  "personal": {
    "full_name": "Rajesh Kumar",
    "date_of_birth": "1990-01-15",
    "gender": "Male",
    "caste": "OBC"
  },
  "location": {
    "address": "123 Main Street, Jaipur",
    "district": "Jaipur",
    "pincode": "302001"
  },
  "economic": {
    "income": 250000,
    "employment": "Regular"
  },
  "metadata": {
    "sources": ["jan_aadhaar", "raj_dex", "scheme_001"],
    "confidence_scores": {
      "full_name": 0.98,
      "date_of_birth": 0.99,
      "income": 0.85
    },
    "last_updated": "2024-12-26T10:30:00Z",
    "merge_history": ["record_001", "record_045", "record_123"]
  }
}
```

---

## 5. Feature Engineering

### 5.1 Fuzzy String Matching

**Algorithms Used:**
- **Jaro-Winkler**: Preferred for name matching (threshold: ≥ 0.85)
- **Levenshtein Distance**: Edit distance (max: 3 characters)
- **Jaro**: Alternative similarity metric (threshold: ≥ 0.90)

**Weight**: 0.30 (30% of total feature weight)

**Example:**
```
Name 1: "Rajesh Kumar"
Name 2: "Rajesh Kumar "  (extra space)
Jaro-Winkler: 0.98 → Match ✅
```

### 5.2 Phonetic Encoding

**Algorithms Used:**
- **Soundex**: Primary phonetic encoding
- **Metaphone**: Alternative phonetic encoding
- **Double Metaphone**: Enhanced phonetic matching

**Weight**: 0.20 (20% of total feature weight)

**Example:**
```
Name 1: "Rajesh"
Name 2: "Rajash"  (typo)
Soundex(Rajesh) = "R220"
Soundex(Rajash) = "R220"
→ Phonetic Match ✅
```

### 5.3 Geospatial Distance

**Algorithm**: Haversine formula for great-circle distance

**Parameters:**
- Max distance: 5.0 km
- Coordinates: Latitude, Longitude

**Weight**: 0.15 (15% of total feature weight)

**Example:**
```
Address 1: (26.9124°N, 75.7873°E)  // Jaipur
Address 2: (26.9130°N, 75.7880°E)  // Nearby
Distance: 0.12 km → Match ✅ (within 5 km)
```

### 5.4 Numeric Similarity

**Algorithms:**
- **Percentage Tolerance**: For income (±10%)
- **Absolute Tolerance**: For age (±1 year)

**Weight**: 0.10 (10% of total feature weight)

**Example:**
```
Income 1: ₹2,50,000
Income 2: ₹2,55,000
Difference: 2% → Match ✅ (within 10% tolerance)
```

### 5.5 Exact Matching

**Attributes:**
- Date of Birth (weight: 0.25)
- Gender (weight: 0.05)
- Caste ID (weight: 0.05)
- District ID (weight: 0.05)
- Pincode (weight: 0.05)
- Employment ID (weight: 0.02)

**Total Exact Match Weight**: 0.47 (47%)

---

## 6. ML Models & Algorithms

### 6.1 Deduplication Model: Fellegi-Sunter

**Type**: Probabilistic Record Linkage

**Algorithm Details:**
- **m-probabilities**: P(agreement | records match)
- **u-probabilities**: P(agreement | records don't match)
- **Log-likelihood ratio**: log(m/u) for match evidence

**Training:**
- Requires labeled training pairs (matches + non-matches)
- Estimates m and u probabilities from training data
- Parameters stored in model checkpoint

**Inference:**
1. Compute agreement vector for record pair
2. Calculate log-likelihood ratio
3. Convert to match probability using sigmoid
4. Apply thresholds for decision

**Alternative**: Siamese Neural Network (future implementation)

### 6.2 Conflict Reconciliation Model: XGBoost

**Type**: Gradient Boosting Classifier

**Parameters:**
- n_estimators: 200
- max_depth: 8
- learning_rate: 0.1
- random_state: 42

**Features:**
1. Recency score (0-1)
2. Source authority score (0-10)
3. Completeness score (0-1)

**Output**: Ranked attribute versions with confidence scores

### 6.3 Best Truth Selection: Survival Analysis

**Type**: Cox Proportional Hazards Model

**Purpose**: Predict record staleness (when record becomes outdated)

**Rule-Based Component:**
- Source priority hierarchy
- Recency weights
- Completeness requirements

**Retraining**: Weekly on admin corrections

---

## 7. Output Format

### 7.1 Golden Record Schema

```json
{
  "golden_record_id": "string",
  "jan_aadhaar": "string (12 digits)",
  "personal": {
    "full_name": "string",
    "first_name": "string",
    "middle_name": "string (optional)",
    "last_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "age": "integer",
    "gender": "Male | Female | Other",
    "caste_id": "integer",
    "caste_name": "string"
  },
  "location": {
    "district_id": "integer",
    "district_name": "string",
    "city_village": "string",
    "address": "string",
    "pincode": "string (6 digits)",
    "is_urban": "boolean",
    "latitude": "float (optional)",
    "longitude": "float (optional)"
  },
  "economic": {
    "family_income": "decimal",
    "family_size": "integer",
    "employment_id": "integer",
    "employment_type": "string",
    "education_id": "integer",
    "education_level": "string",
    "bpl_card": "boolean",
    "farmer": "boolean",
    "disabled": "boolean",
    "house_type_id": "integer"
  },
  "relationships": {
    "spouse": "object (optional)",
    "dependents": "array (optional)",
    "family_tree": "object (optional)"
  },
  "entitlements": {
    "schemes": "array",
    "services": "array",
    "eligibility_scores": "object"
  },
  "metadata": {
    "sources": ["array of source names"],
    "confidence_scores": {
      "attribute_name": "float (0-1)"
    },
    "created_at": "ISO 8601 timestamp",
    "last_updated": "ISO 8601 timestamp",
    "merge_history": ["array of record IDs"],
    "conflict_resolution": {
      "attribute_name": {
        "selected_value": "any",
        "selected_source": "string",
        "confidence": "float (0-1)",
        "alternatives": ["array of alternative values"]
      }
    },
    "lineage": {
      "data_source": "string",
      "extraction_timestamp": "ISO 8601",
      "transformation_steps": ["array"]
    }
  },
  "status": "active | inactive | merged | archived"
}
```

### 7.2 Database Storage

**Table**: `golden_records`

**Schema:**
```sql
CREATE TABLE golden_records (
    golden_record_id BIGSERIAL PRIMARY KEY,
    jan_aadhaar VARCHAR(12) UNIQUE,
    record_data JSONB NOT NULL,
    sources TEXT[],
    confidence_scores JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    merge_history BIGINT[]
);

-- Indexes
CREATE INDEX idx_golden_records_jan_aadhaar ON golden_records(jan_aadhaar);
CREATE INDEX idx_golden_records_status ON golden_records(status);
CREATE INDEX idx_golden_records_updated_at ON golden_records(updated_at);
CREATE INDEX idx_golden_records_gin_data ON golden_records USING GIN(record_data);
```

---

## 8. Configuration Reference

### 8.1 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `db_config.yaml` | `config/` | Database connection & data sources |
| `model_config.yaml` | `config/` | ML model parameters & thresholds |
| `feature_config.yaml` | `config/` | Feature engineering rules |
| `use_case_config.yaml` | `config/` | Use case specifications |

### 8.2 Key Configuration Sections

**Database Configuration** (`db_config.yaml`):
- Host, port, database, credentials
- Data source priorities
- SQL queries for data extraction

**Model Configuration** (`model_config.yaml`):
- Deduplication thresholds
- Feature weights
- Conflict reconciliation parameters
- Training configuration

**Feature Configuration** (`feature_config.yaml`):
- Attribute matching methods
- Fuzzy matching parameters
- Geospatial settings
- Data quality rules

---

## 9. Architecture

### 9.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SMART Platform Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React) → Backend (Spring Boot) → AI/ML (Python)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Golden Record Extraction Module                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Data Loader  │→ │ Feature      │→ │ Deduplication│      │
│  │              │  │ Engineering  │  │ Model        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                              ↓                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Conflict     │→ │ Best Truth   │→ │ Golden Record│      │
│  │ Reconciliation│  │ Selection   │  │ Creator      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                              ↓                               │
│                      ┌──────────────┐                        │
│                      │   Storage    │                        │
│                      │ (PostgreSQL) │                        │
│                      └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Sources Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Jan Aadhaar | Raj D.Ex | Schemes | Services | Validation   │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Component Interactions

1. **Data Loader** → Extracts from multiple sources
2. **Feature Engineer** → Computes similarity features
3. **Deduplication Model** → Identifies duplicates
4. **Conflict Reconciler** → Resolves conflicts
5. **Best Truth Selector** → Chooses final values
6. **Golden Record Creator** → Generates unified record
7. **Storage** → Persists in PostgreSQL

### 9.3 API Integration

**FastAPI Service** (Port: 8001)
- `/api/v1/golden-record/{jan_aadhaar}` - Get Golden Record
- `/api/v1/golden-record/search` - Search Golden Records
- `/api/v1/golden-record/extract` - Trigger extraction
- `/api/v1/golden-record/merge` - Manual merge approval

**Spring Boot Integration**
- REST client calls FastAPI service
- Caches frequently accessed records
- Handles authentication & authorization

---

## 10. Implementation Details

### 10.1 Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.12 |
| **ML Framework** | scikit-learn, XGBoost |
| **Database** | PostgreSQL 14+ |
| **API** | FastAPI |
| **MLOps** | MLflow |
| **Data Processing** | pandas, numpy |
| **String Matching** | rapidfuzz |
| **Phonetics** | phonetics |
| **Geospatial** | geopy |

### 10.2 File Structure

```
golden_record/
├── config/
│   ├── db_config.yaml          # Data sources & queries
│   ├── model_config.yaml       # ML parameters
│   ├── feature_config.yaml     # Feature rules
│   └── use_case_config.yaml    # Use case spec
├── src/
│   ├── data_loader.py          # Data extraction
│   ├── features.py             # Feature engineering
│   ├── deduplication.py        # Deduplication models
│   ├── conflict_reconciliation.py  # Conflict resolution
│   ├── best_truth.py           # Best truth selection
│   ├── train.py                # Training pipeline
│   └── extract.py              # Extraction pipeline
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_feature_engineering.ipynb
├── models/
│   └── checkpoints/            # Saved models
└── docs/
    └── GOLDEN_RECORD_EXTRACTION_DESIGN.md  # This document
```

### 10.3 Extraction Pipeline

**Entry Point**: `src/extract.py`

**Workflow:**
1. Load configuration files
2. Initialize data loader
3. Extract from all enabled sources
4. Preprocess data
5. Engineer features
6. Run deduplication
7. Resolve conflicts
8. Select best truth
9. Create Golden Records
10. Store in database
11. Log to MLflow

**Command:**
```bash
python src/extract.py --batch-size 10000 --output-dir ./output
```

---

## 11. Performance & Scalability

### 11.1 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| **Deduplication Precision** | >95% | TBD |
| **Deduplication Recall** | >95% | TBD |
| **Processing Time (100K records)** | <24 hours | TBD |
| **API Response Time** | <200ms | TBD |
| **Batch Size** | 10,000 records | Configurable |

### 11.2 Scalability Considerations

- **Blocking**: Use Jan Aadhaar + District for record blocking
- **Parallel Processing**: Process batches in parallel
- **Database Optimization**: Indexes on key columns
- **Caching**: Cache frequently accessed Golden Records

---

## 12. Monitoring & Governance

### 12.1 MLflow Tracking

**Experiment**: `smart/golden_record/baseline_v1`

**Tracked Metrics:**
- Precision, Recall, F1 Score
- True Positives, False Positives
- True Negatives, False Negatives
- Processing time
- Data quality scores

### 12.2 Audit Trail

- All merges logged with timestamps
- Source attribution tracked
- Admin corrections recorded
- Model retraining events logged

### 12.3 Compliance

- **DPDP Act 2023**: Consent tracking, PII minimization
- **Bias Monitoring**: Demographic parity checks
- **Data Lineage**: OpenMetadata integration

---

## 13. Future Enhancements

1. **Siamese Neural Network**: Alternative deduplication model
2. **Real-time Processing**: Stream processing for updates
3. **Graph Database**: Store relationships in Neo4j
4. **Advanced NLP**: Entity extraction from unstructured text
5. **Active Learning**: Human-in-the-loop feedback

---

## 14. References

- **Use Case Specification**: `docs/USE_CASE_SPEC.md`
- **Configuration Files**: `config/*.yaml`
- **Source Code**: `src/*.py`
- **MLflow Guide**: `docs/MLFLOW_GUIDE.md`

---

**Document End**

