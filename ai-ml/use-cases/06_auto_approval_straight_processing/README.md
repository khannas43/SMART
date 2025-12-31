# Auto Approval & Straight-through Processing

**Use Case ID:** AI-PLATFORM-06  
**Version:** 1.0  
**Status:** ✅ **COMPLETE**

## Overview

The Auto Approval & Straight-through Processing system evaluates incoming scheme applications using rules and risk models to automatically approve low-risk, fully compliant cases, enabling true straight-through processing (STP). Medium/high-risk or ambiguous cases are routed to departmental officers, reducing workload and delays while ensuring fairness and compliance with AI governance guidelines.

## Key Capabilities

1. **Rule-Based Evaluation**
   - Eligibility and authenticity verification
   - Document validation checks
   - Red flag detection (duplicates, mismatches, deceased flags)

2. **Risk Scoring**
   - ML-based risk models (XGBoost, Logistic Regression, Random Forest)
   - Profile-based features (age, gender, income, family size)
   - Benefit history and graph analytics
   - Explainable AI with contributing factors
   - Rule-based fallback when ML models unavailable

3. **Decision Logic & Routing**
   - **AUTO_APPROVE**: Low-risk, fully compliant cases → Payment trigger
   - **ROUTE_TO_OFFICER**: Medium-risk or minor data issues → Officer worklist
   - **ROUTE_TO_FRAUD**: High-risk or strong red flags → Fraud investigation queue
   - **AUTO_REJECT**: Mandatory rule failures → Rejection

4. **Governance & Compliance**
   - Explainable decisions with human-readable reasons
   - Audit trails and compliance logging
   - Fairness checks and bias monitoring
   - Officer override mechanisms with mandatory justification

5. **Integration**
   - Applications from AI-PLATFORM-05
   - Payment/DBT systems (Jan Aadhaar enabled)
   - Departmental worklists and notifications

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Navigate to use case directory
cd /mnt/c/Projects/SMART/ai-ml/use-cases/06_auto_approval_straight_processing

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create decision schema and tables
./scripts/setup_database.sh

# Initialize decision configuration for all schemes
python scripts/init_decision_config.py

# Initialize risk models metadata
python src/models/init_risk_models.py
```

### 3. Verify Setup

```bash
# Check database connectivity and configuration
python scripts/check_config.py
```

### 4. Test the System

```bash
# Run end-to-end test
python scripts/test_decision_workflow.py

# Run unit tests
python scripts/run_unit_tests.py
```

## Architecture

```
Application (AI-PLATFORM-05)
    ↓
Decision Engine
    ├── Rule Engine → Eligibility & Authenticity Checks
    ├── Risk Scorer → ML-based Risk Assessment
    └── Decision Router → Route Based on Risk & Rules
    ↓
Decision: AUTO_APPROVE / ROUTE_TO_OFFICER / ROUTE_TO_FRAUD / AUTO_REJECT
    ↓
Payment/DBT (Auto Approved) OR Officer Worklist (Routed)
```

## Components

1. **Decision Engine** (`src/decision_engine.py`)
   - Main orchestrator
   - Coordinates rule evaluation, risk scoring, and routing

2. **Rule Engine** (`src/engines/rule_engine.py`)
   - Eligibility checks
   - Authenticity verification
   - Document validation
   - Duplicate detection
   - Cross-scheme conflict checks
   - Deceased flag verification

3. **Risk Scorer** (`src/models/risk_scorer.py`)
   - ML-based risk assessment
   - Feature engineering
   - Model inference
   - Explainability
   - Rule-based fallback

4. **Decision Router** (`src/engines/decision_router.py`)
   - Decision logic based on rules and risk
   - Routing to payment/worklist
   - Notification triggers

5. **Spring Boot Services** (`spring_boot/`)
   - REST API controllers
   - Service layer (Python integration)
   - DTOs for request/response

## Data Sources

- Applications from AI-PLATFORM-05
- Golden Records (AI-PLATFORM-01)
- 360° Profiles (AI-PLATFORM-02)
- Eligibility snapshots (AI-PLATFORM-03)
- External verifications (Aadhaar, bank validation)

## Technology Stack

- **Backend**: Spring Boot 3.x, Java 17+
- **Python Services**: Python 3.12+ for ML models and decision logic
- **ML Models**: XGBoost, scikit-learn, SHAP (explainability)
- **Database**: PostgreSQL 14+ (`smart_warehouse.decision` schema)
- **Integration**: Payment systems, DBT, departmental worklists
- **Model Tracking**: MLflow (http://127.0.0.1:5000)

## Web Viewer

Access the decision evaluation viewer at:
- **URL:** http://localhost:5001/ai06
- **Features:**
  - Decision statistics dashboard
  - Recent decisions table
  - Payment triggers status
  - Risk score visualization

To start the viewer:
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/view_rules_web.py
```

## ML Model Training

Train risk scoring models using historical decision data:

```bash
# Train XGBoost model (default)
python src/models/train_risk_model.py --model-type xgboost --scheme CHIRANJEEVI

# Train Logistic Regression model
python src/models/train_risk_model.py --model-type logistic_regression

# Train Random Forest model
python src/models/train_risk_model.py --model-type random_forest --scheme OLD_AGE_PENSION
```

Models are tracked in MLflow and saved to:
- Filesystem: `src/models/trained/`
- Database: `decision.risk_models` table
- MLflow: Experiment "AI-PLATFORM-06-Risk-Models"

## Testing

### End-to-End Test
```bash
python scripts/test_decision_workflow.py
```

### Unit Tests
```bash
python scripts/run_unit_tests.py
```

### Individual Component Tests
```bash
# Test Rule Engine
python -m unittest src.tests.test_rule_engine

# Test Risk Scorer
python -m unittest src.tests.test_risk_scorer

# Test Decision Engine
python -m unittest src.tests.test_decision_engine
```

## API Endpoints

**Base URL:** `/decision`

- `POST /decision/evaluateApplication` - Evaluate an application
- `GET /decision/history?applicationId={id}` - Get decision history
- `GET /decision/{decisionId}` - Get decision details
- `POST /decision/override` - Override a decision (officer)
- `GET /decision/family/{familyId}` - Get decisions by family
- `GET /decision/scheme/{schemeCode}` - Get decisions by scheme
- `GET /decision/metrics/stp` - Get STP performance metrics

## Documentation

- **Quick Start**: See [QUICK_START.md](QUICK_START.md)
- **Technical Design**: See [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)
- **Testing Guide**: See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Implementation Status**: See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- **Completion Summary**: See [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
- **Pending Items**: See [PENDING_ITEMS.md](PENDING_ITEMS.md)

## Status

**Current Status**: ✅ **COMPLETE**

- ✅ Database schema (11 tables)
- ✅ Core services (Decision Engine, Rule Engine, Risk Scorer, Router)
- ✅ Spring Boot REST APIs + Service Layer
- ✅ Unit tests (3 test suites)
- ✅ ML model training scripts
- ✅ End-to-end test (tested successfully)
- ✅ Web viewer
- ✅ Technical Design Document (19 sections)
- ✅ Complete documentation

## Test Results

**Last Test Run:** 2024-12-30
- ✅ 2 applications evaluated successfully
- ✅ 2 auto-approved decisions (low risk)
- ✅ All rule checks passed
- ✅ Payment triggers created
- ✅ All components working correctly

---

**Last Updated**: 2024-12-30  
**Use Case Owner**: SMART Platform Team  
**Ready for**: Next Use Case ✅
