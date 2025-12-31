# Load Citizens Data for Golden Record Training

## Quick Fix Applied

The `citizens` table has been created in `smart_warehouse`. Now load the 100K synthetic citizens:

```bash
cd /mnt/c/Projects/SMART/ai-ml/pipelines/warehouse/data
export PGPASSWORD='anjali143'

# Load all 100K citizens (this takes 2-3 minutes)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -f 08_insert_citizens.sql
```

## Verify Data Loaded

```bash
export PGPASSWORD='anjali143'
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse \
  -c "SELECT count(*) as total_citizens, 
      count(*) FILTER (WHERE status = 'active') as active_citizens 
      FROM citizens;"
```

Expected: ~100,000 total citizens

## Then Retry Training

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/golden_record
source ../../.venv/bin/activate
python src/train.py
```


