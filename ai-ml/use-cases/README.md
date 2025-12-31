# AI/ML Use Cases

This directory contains all AI/ML use cases for the SMART Platform.

## Use Case Structure

All use cases follow a standardized naming convention:

- `01_golden_record` - Golden Record extraction and deduplication (AI-PLATFORM-01)
- `02_eligibility_scoring_360_profile` - Eligibility scoring and 360° profiles (AI-PLATFORM-02)
- `03_identification_beneficiary` - Auto Identification of Beneficiaries (AI-PLATFORM-03)
- `04_intimation_smart_consent_triggering` - Auto Intimation & Smart Consent Triggering (AI-PLATFORM-04)

## Standard Folder Structure

Each use case follows this structure:

```
XX_use_case_name/
├── README.md                 # Use case overview
├── SETUP.md                  # Setup instructions
├── QUICK_START.md            # Quick start guide
├── requirements.txt          # Python dependencies
├── config/                   # Configuration files
│   ├── db_config.yaml        # Database configuration
│   ├── model_config.yaml     # ML model configuration
│   └── use_case_config.yaml  # Use case specific config
├── database/                 # Database schemas
│   └── *.sql                 # SQL schema files
├── data/                     # Data files
│   ├── raw/                  # Raw data
│   ├── processed/            # Processed data
│   └── generate_synthetic.py # Synthetic data generator
├── src/                      # Source code
│   ├── __init__.py
│   ├── train.py              # Training scripts
│   └── predict.py            # Prediction scripts
├── scripts/                  # Utility scripts
│   ├── check_config.py       # Configuration validation
│   └── validate_data.py      # Data validation
├── notebooks/                # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   └── 02_fairness_audit.ipynb
├── models/                   # Trained models
│   └── checkpoints/          # Model checkpoints
├── docs/                     # Documentation
│   └── *.md                  # Design docs, guides
└── spring_boot/              # Spring Boot APIs (if applicable)
    └── *.java                # Java service files
```

## Current Use Cases

### 01_golden_record

**Status**: ✅ Core Complete  
**Description**: Golden Record extraction and deduplication using Fellegi-Sunter probabilistic record linkage  
**MLflow Experiment**: `smart/golden_record/*`

**Key Features:**
- Fellegi-Sunter deduplication model
- Conflict reconciliation
- Best truth selection
- MLflow integration

**Documentation**: See `01_golden_record/README.md`

### 02_eligibility_scoring_360_profile

**Status**: ✅ Implementation Complete  
**Description**: Eligibility scoring and 360° profiles with network benefit analytics  
**MLflow Experiment**: `smart/eligibility_scoring_360_profile/*`

**Key Features:**
- Eligibility scoring (XGBoost, 0-100 score)
- Income band inference (RandomForest)
- Graph clustering (Neo4j Louvain)
- Anomaly detection (Isolation Forest)
- Neo4j graph visualization

**Documentation**: See `02_eligibility_scoring_360_profile/README.md`

### 03_identification_beneficiary

**Status**: ✅ Core Complete  
**Description**: Auto Identification of Beneficiaries using rule engine + ML hybrid approach  
**MLflow Experiment**: `smart/identification_beneficiary/*`

**Key Features:**
- Rule-based eligibility engine (deterministic rules)
- ML eligibility scorer (XGBoost per scheme)
- Hybrid evaluation (rule + ML combination)
- Prioritization and candidate list generation
- 157+ scheme support

**Documentation**: See `03_identification_beneficiary/README.md`

### 04_intimation_smart_consent_triggering

**Status**: 🚧 In Development  
**Description**: Auto Intimation & Smart Consent Triggering - Notify citizens about eligible schemes and collect explicit, auditable consent  
**MLflow Experiment**: N/A (Non-ML use case)

**Key Features:**
- Multi-channel notifications (SMS, app, web, WhatsApp, email, IVR)
- Personalized message generation with multi-language support
- Smart consent management (soft consent for low-risk, strong consent with OTP/e-sign for high-risk)
- Campaign orchestration with retry logic, fatigue management, and escalation
- DPDP-aligned consent practices with comprehensive audit trails
- Integration with AI-PLATFORM-03 for eligibility signals

**Documentation**: See `04_intimation_smart_consent_triggering/README.md`

## Common Tools & Utilities

### Shared Utilities

Located in `ai-ml/shared/utils/`:
- `db_connector.py` - PostgreSQL database connector
- `neo4j_connector.py` - Neo4j graph database connector

### MLflow Configuration

All use cases use MLflow for experiment tracking:
- **URI**: `http://127.0.0.1:5000`
- **Start MLflow UI**: `mlflow ui --host 0.0.0.0 --port 5000`

### Database Configuration

**PostgreSQL:**
- Host: `172.17.16.1` (or `localhost`)
- Port: `5432`
- Database: Varies by use case

**Neo4j** (for graph use cases):
- URI: `bolt://172.17.16.1:7687` (from WSL) or `bolt://localhost:7687`
- User: `neo4j`
- Database: `smartgraphdb` (or `neo4j`)

## Development Workflow

1. **Setup**: Follow `SETUP.md` in each use case
2. **Data**: Generate or load data using scripts in `data/`
3. **Training**: Run training scripts in `src/`
4. **Evaluation**: Check MLflow UI for results
5. **Notebooks**: Use notebooks for exploration and analysis

## Adding New Use Cases

When creating a new use case:

1. Create folder: `XX_use_case_name/` (where XX is next number)
2. Follow standard folder structure above
3. Copy template files from existing use case
4. Update configuration files
5. Add to this README

## Naming Convention

- Use format: `XX_use_case_name` where XX is zero-padded number (01, 02, 03, ...)
- Use lowercase with underscores
- Keep names descriptive but concise

---

**Last Updated**: 2024-12-29
