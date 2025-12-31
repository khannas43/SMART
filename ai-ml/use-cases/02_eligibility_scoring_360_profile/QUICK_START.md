# Eligibility Scoring & 360° Profiles: Quick Start Guide

## 🚀 Quick Setup (6 Steps)

### Step 0: Setup Neo4j (First Time Only)

```bash
# 1. Install Neo4j Desktop from https://neo4j.com/download/
# 2. Create a database and start it
# 3. Set password (default: neo4j)

# Verify connection
cd /mnt/c/Projects/SMART/ai-ml/use-cases/eligibility_scoring_360_profile
python scripts/check_neo4j.py
```

### Step 1: Create Database Schema

```bash
cd database
export PGPASSWORD='anjali143'
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f smart_warehouse.sql
```

### Step 2: Generate Synthetic Data (45K records)

```bash
cd ../data
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python generate_synthetic.py
```

### Step 3: Train Income Band Model

```bash
cd ../src
python income_band_train.py
```

### Step 4: Run Graph Clustering (Neo4j)

```bash
python graph_clustering_neo4j.py
```

**Note:** If Neo4j is not available, it will fall back to NetworkX (slower).

### Step 5: Run Anomaly Detection

```bash
python anomaly_detection.py
```

## ✅ Verify Setup

### Check Database

```sql
-- Quick count check
SELECT 
    'Golden Records' as table_name, COUNT(*) FROM golden_records
UNION ALL SELECT 'Relationships', COUNT(*) FROM gr_relationships
UNION ALL SELECT 'Benefits', COUNT(*) FROM benefit_events
UNION ALL SELECT 'Profiles 360', COUNT(*) FROM profile_360;
```

### Check Neo4j

```bash
python scripts/check_neo4j.py
```

### Check MLflow

Visit: `http://127.0.0.1:5000`

Look for experiments:
- `smart/eligibility_scoring_360_profile/income_band`
- `smart/eligibility_scoring_360_profile/eligibility_scoring` (when created)

### Run Data Exploration

```bash
# Start Jupyter
cd ../notebooks
jupyter lab

# Open: 01_profile_eda.ipynb
```

## 📊 Expected Results

After setup, you should have:
- ✅ 45,000 Golden Records
- ✅ ~56,000+ Relationships
- ✅ ~137,000 Benefit Events
- ✅ ~53,000 Applications
- ✅ 360° Profiles with income bands
- ✅ Clusters assigned (via Neo4j)
- ✅ Anomaly flags generated

## 🔄 Daily Operations

### Update Profiles (Orchestrator)

```bash
cd src
python profile_recompute_service.py
```

### Process Recompute Queue

```bash
python profile_recompute_service.py --scheduler
```

## 🐛 Troubleshooting

**Neo4j connection failed?**
- Check Neo4j Desktop is running
- Verify password in `config/db_config.yaml`
- Run `python scripts/check_neo4j.py`

**Database connection failed?**
- Check PostgreSQL is running
- Verify credentials in `config/db_config.yaml`

**No data generated?**
- Check database schema was created
- Verify `generate_synthetic.py` completed without errors

**ML model training failed?**
- Ensure MLflow is running: `mlflow ui`
- Check training data exists in database

**Graph clustering slow?**
- Ensure Neo4j is enabled and running
- Install GDS plugin for better performance
- Check `docs/NEO4J_SETUP.md` for optimization tips

---

**Need help?** Check `SETUP.md` for detailed instructions or `docs/NEO4J_SETUP.md` for Neo4j-specific setup.
