# Fix: Citizens Table Missing

## Problem
The `citizens` table doesn't exist in `smart_warehouse` database, causing training to fail.

## Solution Options

### Option 1: Load Master Data (Recommended)

The master data includes 100K synthetic citizens. Load it:

```bash
cd /mnt/c/Projects/SMART/ai-ml/pipelines/warehouse/data
export PGPASSWORD='anjali143'

# Step 1: Create master tables schema
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -f ../schemas/02_master_tables.sql

# Step 2: Load master data (this may take a few minutes for 100K records)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -f 08_insert_citizens.sql

# Verify
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -c "SELECT count(*) FROM citizens;"
```

### Option 2: Use Automated Script

```bash
cd /mnt/c/Projects/SMART/ai-ml/pipelines/warehouse/data
bash load_all_master_data.sh
```

### Option 3: Use Portal Database (Quick Fix)

Update config to use `smart_citizen` portal database temporarily:

```yaml
# In config/db_config.yaml
database:
  dbname: smart_citizen  # Change from smart_warehouse
```

**Note:** Portal database may be empty. Use this only for testing structure.

## Verify Fix

After loading data:

```bash
# Check citizens table exists and has data
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -c "SELECT count(*) FROM citizens;"
```

Should show ~100,000 records.

## Retry Training

After fixing:

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python src/train.py
```


