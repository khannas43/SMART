# Golden Record Creation & Maintenance

**Use Case ID:** AI-PLATFORM-01  
**Tier:** Tier 1 (Foundational)  
**Status:** Planning → Implementation  
**MLflow Experiment:** `smart/golden_record/baseline_v1`

## Overview

Create and maintain verified Golden Records as the single source of truth for key citizen attributes by using ML to deduplicate records, reconcile conflicts, and select the "best truth" across multi-departmental data sources (DOB, address, occupation, income, relationships), enabling accurate eligibility assessment for schemes.

## Project Structure

```
golden_record/
├── README.md                           # This file
├── config/
│   ├── db_config.yaml                 # PostgreSQL connection & queries
│   ├── model_config.yaml              # ML model hyperparameters
│   └── feature_config.yaml            # Feature engineering rules
├── notebooks/
│   ├── 01_data_exploration.ipynb      # EDA on citizen data
│   ├── 02_feature_engineering.ipynb   # Feature analysis
│   ├── 03_deduplication_analysis.ipynb # Deduplication patterns
│   └── 04_model_training.ipynb        # Model training & evaluation
├── src/
│   ├── data_loader.py                 # PostgreSQL data extraction
│   ├── features.py                    # Feature engineering logic
│   ├── deduplication.py               # Deduplication models
│   ├── conflict_reconciliation.py     # Conflict resolution
│   ├── best_truth.py                  # Best truth selection
│   ├── train.py                       # Training pipeline
│   └── evaluate.py                    # Model evaluation
├── data/
│   ├── raw/                           # Cached raw data from PostgreSQL
│   └── processed/                     # Processed feature sets
├── models/
│   └── checkpoints/                   # Saved model artifacts
└── tests/                             # Unit tests

```

## Quick Start

### 1. Setup Environment

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install pandas numpy scikit-learn xgboost mlflow rapidfuzz phonetics geopy
```

### 3. Load Data

```python
from src.data_loader import GoldenRecordDataLoader

loader = GoldenRecordDataLoader()
citizens = loader.load_all_citizens()
print(f"Loaded {len(citizens)} citizens")
```

### 4. Compute Features

```python
from src.features import GoldenRecordFeatureEngineer

engineer = GoldenRecordFeatureEngineer()
features = engineer.compute_match_features(record1, record2)
```

## Components

### 1. Data Loader (`src/data_loader.py`)
- Loads citizen data from PostgreSQL
- Batch processing for large datasets
- Supports multiple data sources

### 2. Feature Engineering (`src/features.py`)
- Fuzzy string matching (Jaro-Winkler, Levenshtein)
- Phonetic encoding (Soundex, Metaphone)
- Geospatial distance calculation
- Numeric similarity (income, age)

### 3. Deduplication Models
- **Fellegi-Sunter**: Probabilistic record linkage
- **Siamese NN**: Neural network similarity learning
- Thresholds: >95% auto-merge, 80-95% manual review

### 4. Conflict Reconciliation
- **XGBoost Ensemble**: Ranks attribute versions
- Factors: Recency, source authority, completeness
- Outputs confidence scores per attribute

### 5. Best Truth Selection
- **Survival Analysis**: Predicts record staleness
- Rule-based source priority
- Weekly retraining on admin corrections

## Configuration

### Database (`config/db_config.yaml`)
- PostgreSQL connection details
- Data source priorities
- Query definitions

### Model (`config/model_config.yaml`)
- ML model hyperparameters
- Deduplication thresholds
- Training parameters
- MLflow experiment name

### Features (`config/feature_config.yaml`)
- Attribute matching rules
- Fuzzy matching configurations
- Source authority weights
- Data quality rules

## MLflow Tracking

**Experiment Name:** `smart/golden_record/baseline_v1`

**Tracked Metrics:**
- Deduplication precision/recall
- Conflict resolution accuracy
- False positive rate
- Processing time

**Tracked Parameters:**
- Model type
- Feature weights
- Thresholds
- Data version

## Success Metrics

- ✅ **Deduplication**: Precision/recall >95%
- ✅ **Coverage**: Golden Record coverage >90% of Jan Aadhaar base
- ✅ **TAT**: Conflict resolution <24 hours
- ✅ **Accuracy**: >99% Golden Record accuracy
- ✅ **Downstream Errors**: <0.5% downstream eligibility errors

## Implementation Phases

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Configuration files
- [x] Data loader
- [x] Feature engineering basics

### Phase 2: ML Models (Next)
- [ ] Fellegi-Sunter implementation
- [ ] Siamese neural network
- [ ] XGBoost conflict resolution
- [ ] Survival analysis model

### Phase 3: Integration
- [ ] FastAPI microservice
- [ ] Spring Boot integration
- [ ] Real-time APIs
- [ ] Admin review interface

### Phase 4: Governance
- [ ] DPDP compliance module
- [ ] Bias monitoring
- [ ] Audit trail system
- [ ] OpenMetadata integration

## Documentation

- **Use Case Spec**: `docs/USE_CASE_SPEC.md` - Detailed requirements
- **Configuration**: `config/` - All configuration files
- **Source Code**: `src/` - Implementation code

## Dependencies

```txt
pandas
numpy
scikit-learn
xgboost
mlflow
rapidfuzz
phonetics
geopy
psycopg2-binary
pyyaml
```

## Next Steps

1. Create initial notebook for data exploration
2. Implement Fellegi-Sunter model
3. Build conflict reconciliation pipeline
4. Set up FastAPI service

---

**Use Case Owner:** AI/ML Team  
**Last Updated:** 2024-12-26
