# Quick Fix: Database Schema & Missing Dependencies

**Use Case ID:** AI-PLATFORM-03

---

## Issue 1: Database Schema Doesn't Exist ✅ FIXED

The `eligibility.scheme_master` table doesn't exist because the database schema hasn't been created yet.

**Note**: We're using `smart_warehouse` database (shared with AI-PLATFORM-02), not a separate `smart_eligibility` database.

### Solution: Create Eligibility Schema in smart_warehouse

#### Option A: Using pgAdmin4

1. **Verify Database Exists**:
   ```sql
   -- Check if smart_warehouse exists (should already exist from AI-PLATFORM-02)
   SELECT datname FROM pg_database WHERE datname = 'smart_warehouse';
   
   -- If doesn't exist, create it:
   CREATE DATABASE smart_warehouse;
   ```

2. **Connect to `smart_warehouse` database**

3. **Run Schema Script**:
   - Open: `database/eligibility_schema.sql`
   - Execute the entire file in pgAdmin4 query window
   - This creates the `eligibility` schema within `smart_warehouse`

4. **Run Versioning Extensions** (Optional but recommended):
   - Open: `database/eligibility_schema_versioning.sql`
   - Execute in pgAdmin4

5. **Load Initial Schemes**:
   - Open: `scripts/load_initial_schemes.sql`
   - Execute to load sample schemes

#### Option B: Using Command Line (WSL)

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary

# Set password
export PGPASSWORD='anjali143'

# Note: Using smart_warehouse database (shared with AI-PLATFORM-02)
# Database should already exist, but if not:
# psql -h 172.17.16.1 -p 5432 -U sameer -d postgres -c "CREATE DATABASE smart_warehouse;"

# Create eligibility schema in smart_warehouse database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql

# Create versioning extensions
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema_versioning.sql

# Load initial schemes
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/load_initial_schemes.sql

unset PGPASSWORD
```

#### Option C: Using Setup Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

### Verify Schema Created

In pgAdmin4 (connected to `smart_warehouse` database):
```sql
-- Check if eligibility schema exists
SELECT schema_name FROM information_schema.schemata 
WHERE catalog_name = 'smart_warehouse' AND schema_name = 'eligibility';

-- Check if table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'eligibility' 
ORDER BY table_name;

-- Check schemes
SELECT * FROM eligibility.scheme_master;

-- View all schemas in smart_warehouse
SELECT schema_name 
FROM information_schema.schemata 
WHERE catalog_name = 'smart_warehouse'
ORDER BY schema_name;
```

---

## Issue 2: Missing SHAP Module ✅ FIXED

The `shap` module was missing from the Python environment.

### Solution: Install SHAP

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

### Verify Installation

```bash
python -c "import shap; print(f'✅ SHAP version: {shap.__version__}')"
```

---

## Complete Setup Steps

### 1. Install Dependencies
```bash
cd /mnt/c/Projects/SMART/ai-ml
source .venv/bin/activate
pip install shap>=0.42.0
```

### 2. Create Eligibility Schema in smart_warehouse

**In pgAdmin4**:
```sql
-- Connect to smart_warehouse database (should already exist from AI-PLATFORM-02)
-- If not exists: CREATE DATABASE smart_warehouse;

-- Execute: database/eligibility_schema.sql
-- This creates the 'eligibility' schema within smart_warehouse
```

### 3. Load Initial Data

**In pgAdmin4** (connected to `smart_warehouse`):
```sql
-- Execute: scripts/load_initial_schemes.sql
```

### 4. Verify Setup

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/check_config.py
```

### 5. Test Training (Once Training Data Available)

```bash
python src/train_eligibility_model.py --scheme_id SCHEME_001
```

---

## Files Created

1. ✅ `scripts/setup_database.sh` - Automated database setup script (uses smart_warehouse)
2. ✅ `scripts/load_initial_schemes.sql` - Initial scheme data
3. ✅ `QUICK_SETUP.md` - Complete setup guide
4. ✅ `requirements.txt` - Updated with `shap` dependency
5. ✅ `config/db_config.yaml` - Updated to use `smart_warehouse`

---

## Database Architecture

```
smart_warehouse (database)
│
├── public schema (or smart_warehouse schema)
│   └── AI-PLATFORM-02: 360° Profiles
│       ├── golden_records
│       ├── profile_360
│       ├── benefit_events
│       └── ...
│
└── eligibility schema
    └── AI-PLATFORM-03: Auto Identification
        ├── scheme_master
        ├── eligibility_snapshots
        ├── candidate_lists
        └── ...
```

---

## Next Steps After Setup

1. ✅ Database schema created in `smart_warehouse`
2. ✅ Initial schemes loaded
3. ⏳ Configure scheme rules (via frontend or SQL)
4. ⏳ Train models (requires training data in `smart_warehouse`)
5. ⏳ Test evaluation service

---

## Verification Checklist

- [ ] Database `smart_warehouse` exists (shared with AI-PLATFORM-02)
- [ ] Schema `eligibility` created in `smart_warehouse` database
- [ ] Tables created (check `eligibility.scheme_master` exists)
- [ ] Initial schemes loaded (check `SELECT * FROM eligibility.scheme_master;`)
- [ ] Python dependencies installed (`shap` module)
- [ ] Configuration validated (`python scripts/check_config.py`)
- [ ] Database config updated to use `smart_warehouse` (not `smart_eligibility`)

---

**Status**: ✅ All configurations updated to use `smart_warehouse` database. Ready for schema creation.
