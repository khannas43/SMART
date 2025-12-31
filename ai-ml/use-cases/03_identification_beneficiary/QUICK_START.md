# Quick Start: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03

## Quick Setup (5 minutes)

### 1. Create Database

```bash
export PGPASSWORD='anjali143'
# Note: Using smart_warehouse database (shared with AI-PLATFORM-02)
# Database should already exist from eligibility_scoring_360_profile setup
# If not: psql -h 172.17.16.1 -p 5432 -U sameer -d postgres -c "CREATE DATABASE smart_warehouse;"

# Create eligibility schema in smart_warehouse database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql
```

### 2. Activate Virtual Environment

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
cd use-cases/03_identification_beneficiary
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Setup

```bash
python scripts/check_config.py
```

### 5. Test Rule Engine

```python
from src.rule_engine import RuleEngine

# Initialize
engine = RuleEngine()

# Sample family data
family_data = {
    'family_id': 'test-123',
    'head_age': 65,
    'head_gender': 'M',
    'district_id': 101,
    'income_band': 'LOW',
    'family_size': 4
}

# Evaluate eligibility
result = engine.evaluate_scheme_eligibility('SCHEME_001', family_data)
print(result)

engine.close()
```

## Key Files

- **Rule Engine**: `src/rule_engine.py`
- **Database Schema**: `database/eligibility_schema.sql`
- **Configuration**: `config/use_case_config.yaml`

## What's Next?

See `IMPLEMENTATION_STATUS.md` for current progress and next steps.

