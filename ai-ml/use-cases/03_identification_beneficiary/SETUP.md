# Setup Guide: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03

## Prerequisites

1. **Database**: PostgreSQL 14+ with `smart_warehouse` database (shared with AI-PLATFORM-02)
   - Schema: `eligibility` (for this use case)
   - Schema: `smart_warehouse` (for 360° Profiles use case)
2. **Python**: 3.12+ (WSL venv at `/mnt/c/Projects/SMART/ai-ml/.venv`)
3. **MLflow**: Running at `http://127.0.0.1:5000`
4. **Dependencies**: AI-PLATFORM-01 (Golden Records), AI-PLATFORM-02 (360° Profiles)

## Initial Setup

### 1. Create Database Schema

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
export PGPASSWORD='anjali143'

# Note: smart_warehouse database should already exist from AI-PLATFORM-02 setup
# If not, create it first:
# psql -h 172.17.16.1 -p 5432 -U sameer -d postgres -c "CREATE DATABASE smart_warehouse;"

# Create eligibility schema in smart_warehouse database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql
```

### 2. Install Dependencies

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
cd use-cases/03_identification_beneficiary
pip install -r requirements.txt
```

### 3. Verify Configuration

```bash
python scripts/check_config.py
```

## Configuration Files

### Database Configuration (`config/db_config.yaml`)
- Primary database: `smart_warehouse` (shared with AI-PLATFORM-02)
- Schema: `eligibility` (within smart_warehouse)
- External connections: Golden Records, 360° Profiles, JRDR

### Model Configuration (`config/model_config.yaml`)
- XGBoost hyperparameters
- Feature engineering settings
- Scheme-specific model configs

### Use Case Configuration (`config/use_case_config.yaml`)
- Rule engine settings
- ML scorer settings
- Hybrid evaluator weights
- Governance settings

## Next Steps

1. **Load Scheme Rules**: Define eligibility rules for schemes
2. **Prepare Training Data**: Generate training data from historical beneficiaries
3. **Train Models**: Train ML models per scheme or scheme family
4. **Test Evaluation**: Run test evaluations on sample families
5. **Deploy APIs**: Set up Spring Boot REST APIs

## Testing

```bash
# Test rule engine
python -c "from src.rule_engine import RuleEngine; re = RuleEngine(); print('✅ Rule engine loaded')"

# Test database connection
python scripts/check_config.py
```

---

**Status**: Initial setup complete. Ready for scheme rule configuration and model training.

