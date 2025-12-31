# Quick Setup Guide: Auto Identification of Beneficiaries

**Use Case ID:** AI-PLATFORM-03

---

## Step 1: Install Missing Dependencies

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
pip install shap>=0.42.0
```

Or install all requirements:
```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
pip install -r requirements.txt
```

---

## Step 2: Create Database Schema

### Option A: Using Setup Script (Recommended)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

### Option B: Manual Setup

```bash
# Set password
export PGPASSWORD='anjali143'

# Note: Using smart_warehouse database (shared with AI-PLATFORM-02)
# The database should already exist from eligibility_scoring_360_profile setup

# Create schema (in existing smart_warehouse database)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql

# Create versioning extensions (optional but recommended)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema_versioning.sql

unset PGPASSWORD
```

---

## Step 3: Load Initial Scheme Data

```bash
export PGPASSWORD='anjali143'
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/load_initial_schemes.sql
unset PGPASSWORD
```

Or in pgAdmin4:
```sql
-- Run the contents of scripts/load_initial_schemes.sql
```

---

## Step 4: Verify Setup

### Check Database Schema

```bash
export PGPASSWORD='anjali143'
# Check eligibility schema in smart_warehouse
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'eligibility' 
ORDER BY table_name;"

# Check all schemas in smart_warehouse
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -c "
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('smart_warehouse', 'eligibility')
ORDER BY schema_name;"
unset PGPASSWORD
```

### Check Schemes

```sql
SELECT * FROM eligibility.scheme_master;
```

### Check Configuration

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_config.py
```

---

## Step 5: Train First Model (Optional)

**Note**: Requires training data in `smart_warehouse` database (application/benefit events).

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

# Train model for a scheme
python src/train_eligibility_model.py --scheme_id SCHEME_001
```

---

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check credentials in `config/db_config.yaml`
- Test connection: `psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse`

### Missing Python Modules

```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
pip install -r use-cases/03_identification_beneficiary/requirements.txt
```

### Schema Already Exists

If schema already exists, the setup script will show warnings but continue. To recreate:

```sql
DROP SCHEMA IF EXISTS eligibility CASCADE;
-- Then run setup again
```

---

## Verification Checklist

- [ ] Database `smart_warehouse` exists (shared with AI-PLATFORM-02)
- [ ] Schema `eligibility` created
- [ ] Tables created (check `eligibility.scheme_master` exists)
- [ ] Initial schemes loaded (check `SELECT * FROM eligibility.scheme_master;`)
- [ ] Python dependencies installed (`shap` module)
- [ ] Configuration validated (`python scripts/check_config.py`)

---

**Status**: Ready for model training once training data is available.

