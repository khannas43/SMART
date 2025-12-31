# Quick Start Guide - Auto Approval & Straight-through Processing

**Use Case ID:** AI-PLATFORM-06

## Prerequisites

1. **Virtual Environment**: Ensure Python virtual environment is activated
   ```bash
   source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
   ```

2. **Database**: PostgreSQL should be running and accessible

3. **Dependencies**: Install required packages
   ```bash
   cd /mnt/c/Projects/SMART/ai-ml/use-cases/06_auto_approval_straight_processing
   pip install -r requirements.txt
   ```

## Setup Steps

### 1. Database Setup

```bash
# Create decision schema and tables
./scripts/setup_database.sh
```

### 2. Initialize Configuration

```bash
# Initialize decision configuration for all schemes
python scripts/init_decision_config.py
```

### 3. Verify Setup

```bash
# Check database connectivity and configuration
python scripts/check_config.py
```

## Usage

### Evaluate an Application

```python
from decision_engine import DecisionEngine

# Initialize engine
engine = DecisionEngine()

# Connect to databases
engine.connect()

try:
    # Evaluate application
    result = engine.evaluate_application(application_id=1)
    
    print(f"Decision: {result['decision']['decision_type']}")
    print(f"Risk Score: {result['risk_results']['risk_score']}")
    print(f"Status: {result['decision']['decision_status']}")
    
finally:
    engine.disconnect()
```

### Get Decision History

```python
# Get decision history for an application
# (API will be available via Spring Boot)
```

## Architecture Overview

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

## Key Components

1. **Decision Engine** (`src/decision_engine.py`)
   - Main orchestrator
   - Coordinates rule evaluation, risk scoring, and routing

2. **Rule Engine** (`src/engines/rule_engine.py`)
   - Eligibility checks
   - Authenticity verification
   - Document validation
   - Duplicate detection

3. **Risk Scorer** (`src/models/risk_scorer.py`)
   - ML-based risk assessment
   - Feature engineering
   - Model inference
   - Explainability

4. **Decision Router** (`src/engines/decision_router.py`)
   - Decision logic based on rules and risk
   - Routing to payment/worklist
   - Notification triggers

## Configuration

### Decision Configuration

Edit `config/use_case_config.yaml` to configure:
- Risk thresholds (low/medium/high)
- Auto approval settings
- Routing rules
- Model configuration

### Database Configuration

Edit `config/db_config.yaml` to configure:
- Database connections
- External database access (applications, golden records, etc.)

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing instructions.

## Next Steps

1. ✅ Database schema created
2. ✅ Decision Engine skeleton created
3. ⏳ Implement Rule Engine
4. ⏳ Implement Risk Scorer
5. ⏳ Implement Decision Router
6. ⏳ Create Spring Boot APIs
7. ⏳ Add testing scripts

## Support

For issues or questions:
- Check [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for current status
- Review [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) for detailed design

