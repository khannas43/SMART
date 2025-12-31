# Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03  
**Tier:** Tier 1 (Foundational)  
**Status:** Development  
**MLflow Experiment:** `smart/identification_beneficiary/*`

## Overview

Automatically identify citizens/families who are potentially eligible for one or more welfare schemes and services using Jan Aadhaar Resident Data Repository (JRDR) plus seeded departmental databases.

### Key Capabilities

1. **Auto Identification Engine**: Rule-based + ML hybrid approach to identify eligible beneficiaries
2. **Multi-Scheme Support**: Works across 157+ schemes (cash and non-cash) integrated with Jan Aadhaar
3. **Prioritized Lists**: Generate explainable candidate lists for citizen-facing flows, departmental worklists, and auto intimation
4. **Extensible Design**: Support for new schemes through configurable rules and ML models

## Key Technologies

- **PostgreSQL**: Eligibility snapshots, candidate lists, rule definitions (in `smart_warehouse` database, `eligibility` schema)
- **Python/ML**: XGBoost, scikit-learn, MLflow
- **Spring Boot**: REST APIs for evaluation and candidate lists
- **Integration**: AI-PLATFORM-01 (Golden Records), AI-PLATFORM-02 (360° Profiles)

## Architecture

```
Jan Aadhaar (JRDR) + Departmental DBs
         ↓
Golden Records (AI-PLATFORM-01)
         ↓
360° Profiles (AI-PLATFORM-02)
         ↓
Auto Identification Engine (AI-PLATFORM-03)
    ├── Rule Engine (Deterministic)
    └── ML Scorer (XGBoost per scheme)
         ↓
Prioritized Candidate Lists
    ├── Citizen Portal (Eligibility Hints)
    ├── Departmental Worklists
    └── Auto Intimation Service
```

## Components

### 1. Rule Engine
- **Type**: Deterministic decision tables and expressions
- **Input**: Golden Records + 360° Profile derived fields
- **Rules**: Age, gender, income band, disability status, geography, category, prior participation, exclusions
- **Output**: RULE_ELIGIBLE / NOT_ELIGIBLE / POSSIBLE_ELIGIBLE

### 2. ML Eligibility Scorer
- **Model**: XGBoost (per scheme or scheme family)
- **Features**: Demographics, household composition, income band, assets, geography, historical participation
- **Output**: Eligibility probability (0-1) and confidence score
- **Purpose**: Ranking and "soft eligible" identification

### 3. Hybrid Evaluation Service
- Combines rule engine output with ML scores
- Conflict handling using confidence weighting
- Prioritization by eligibility score, vulnerability, under-coverage indicators

### 4. Prioritization Logic
- Ranks candidates by combined eligibility score
- Considers vulnerability level from 360° Profiles
- Generates:
  - Citizen-facing hints (top 3-5 schemes per family)
  - Departmental worklists (clusters/wards with high-score non-beneficiaries)

## Project Structure

```
03_identification_beneficiary/
├── config/
│   ├── db_config.yaml          # Database connections
│   ├── model_config.yaml       # ML model configurations
│   └── use_case_config.yaml    # Use case settings
├── database/
│   └── eligibility_schema.sql  # Eligibility snapshots, candidate lists
├── data/
│   ├── load_scheme_rules.py    # Load scheme eligibility rules
│   └── generate_training_data.py  # Generate training data from historical records
├── src/
│   ├── rule_engine.py          # Deterministic eligibility rules
│   ├── ml_scorer.py            # ML eligibility scorer
│   ├── hybrid_evaluator.py     # Combines rule + ML
│   ├── prioritizer.py          # Ranking and prioritization
│   ├── evaluator_service.py    # Main evaluation service
│   └── train_eligibility_model.py  # Training pipeline
├── scripts/
│   ├── check_config.py
│   ├── validate_rules.py
│   └── run_batch_evaluation.py
├── notebooks/
│   ├── 01_eligibility_eda.ipynb
│   └── 02_fairness_audit.ipynb
├── spring_boot/
│   ├── EligibilityEvaluationController.java
│   ├── CandidateListController.java
│   └── EligibilityEvaluationService.java
├── docs/
│   └── TECHNICAL_DESIGN.md
├── README.md
├── SETUP.md
├── QUICK_START.md
└── requirements.txt
```

## APIs

### REST Endpoints

- `POST /eligibility/evaluate?family_id` - On-demand evaluation for a family
- `GET /eligibility/precomputed?family_id` - Precomputed eligibility results
- `GET /eligibility/candidate-list?scheme_id&district&score>=X` - Departmental worklists
- `GET /eligibility/config/scheme/{scheme_id}` - Scheme rules and ML model metadata

### Events

- `POTENTIALLY_ELIGIBLE_IDENTIFIED` - Event per scheme/family

## Data Flow

1. **Batch Processing**: Weekly batch run across all Jan Aadhaar families
2. **Event-Driven**: Triggered on major changes (age threshold, new child, disability registration, calamity tag)
3. **On-Demand**: Real-time evaluation via API for citizen portal checks
4. **Output Storage**: Eligibility snapshots stored with version, timestamp, rule path, model version

## Integration Points

### Dependencies
- **AI-PLATFORM-01**: Golden Records (deduplicated identities)
- **AI-PLATFORM-02**: 360° Profiles (income band, vulnerability, under-coverage indicators)
- **JRDR**: Jan Aadhaar family and member data
- **Departmental Systems**: Scheme rules, current beneficiaries, historical data

### Outputs To
- **Citizen Portal**: Eligibility hints widget (CIT-PROF-04, CIT-SCHEME-10, CIT-SCHEME-12)
- **Departmental Portal**: Beneficiary discovery worklists
- **Auto Intimation Service**: POTENTIALLY_ELIGIBLE_IDENTIFIED events
- **AI/ML Portal**: Configuration and monitoring screens

## Governance & Compliance

### Legal Basis
- Uses Jan Aadhaar Act provisions for beneficiary identification
- Respects consent status for analytic processing
- Proxy datasets flagged in explanations

### Fairness & Non-Discrimination
- Regular bias checks by demographic breakdowns
- Thresholds and features reviewed by policy teams
- Ability to exclude sensitive attributes

### Explainability
- Every auto-identified case stores:
  - Rule path (which conditions met/failed)
  - Top model features driving decision
  - Confidence scores and reason codes

### Audit
- Audit logs for scheme rule changes
- Model version tracking
- Eligibility snapshot versioning

## Success Metrics

### Coverage & Recall
- Share of "actually eligible but not enrolled" beneficiaries identified
- Increase in enrolment of previously underserved households

### Precision / Leakage Control
- Percentage of auto-identified candidates confirmed eligible
- Very low false positive rate

### Operational
- Batch scoring of full JRDR within defined window (overnight)
- Low latency for on-demand checks (<200ms)

## Dependencies

### Python Packages
- `pandas>=2.0.0`, `numpy>=1.24.0`
- `scikit-learn>=1.3.0`, `xgboost>=2.0.0`
- `mlflow>=2.8.0`
- `psycopg2-binary>=2.9.0`
- `pyyaml>=6.0`
- `pyparsing>=3.0.0` (for rule expression parsing)

### System Requirements
- PostgreSQL 14+ (eligibility database)
- Python 3.12+ (WSL venv: `/mnt/c/Projects/SMART/ai-ml/.venv`)
- MLflow UI running at `http://127.0.0.1:5000`
- Spring Boot 3.x (for REST APIs)
- Access to Golden Records database (AI-PLATFORM-01)
- Access to 360° Profiles database (AI-PLATFORM-02)

## Next Steps

1. ⏳ Create database schema
2. ⏳ Implement rule engine
3. ⏳ Implement ML scorer
4. ⏳ Create hybrid evaluator
5. ⏳ Set up Spring Boot REST APIs
6. ⏳ Create training pipeline
7. ⏳ Create data exploration notebooks
8. ⏳ Configure scheme rules

---

**Use Case Owner:** AI/ML Team  
**Last Updated:** 2024-12-27  
**Related Use Cases:** AI-PLATFORM-01 (Golden Records), AI-PLATFORM-02 (Eligibility Scoring & 360° Profiles)

