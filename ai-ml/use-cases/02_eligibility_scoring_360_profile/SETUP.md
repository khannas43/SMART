# Eligibility Scoring & 360° Profiles: Setup Guide

## Prerequisites

1. **PostgreSQL** running at `172.17.16.1:5432`
2. **`smart_warehouse` database** created
3. **Python 3.12** with venv activated (WSL: `/mnt/c/Projects/SMART/ai-ml/.venv`)
4. **MLflow UI** running at `http://127.0.0.1:5000`
5. **AI-PLATFORM-01 (Golden Records)** completed (prerequisite)

## Setup Steps

### 1. Create Database Schema

```bash
cd ai-ml/use-cases/02_eligibility_scoring_360_profile/database
export PGPASSWORD='anjali143'
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f smart_warehouse.sql
```

This creates 12 tables:
- `golden_records` - Golden Records with family linking
- `gr_relationships` - Relationship graph edges
- `scheme_master` - Scheme master data
- `benefit_events` - Benefit transaction history
- `application_events` - Application history
- `socio_economic_facts` - Socio-economic proxies
- `consent_flags` - Consent management
- `data_quality_flags` - Data quality scores
- `profile_360` - 360° profiles (JSONB)
- `analytics_benefit_summary` - Aggregated benefit analytics
- `analytics_flags` - Anomaly flags
- `profile_recompute_queue` - Recompute queue

### 2. Generate Synthetic Data

```bash
cd ../data
source ../../../.venv/bin/activate  # If using WSL
python generate_synthetic.py
```

This will create:
- ✅ 45,000 Golden Records
- ✅ ~50,000+ Relationships
- ✅ ~135,000 Benefit Events
- ✅ ~18,000 Applications
- ✅ Socio-economic facts

### 3. Install Python Dependencies

```bash
cd ..
source ../../.venv/bin/activate  # If using WSL
pip install -r requirements.txt
```

### 4. Train Income Band Model

```bash
cd src
python income_band_train.py
```

This will:
- Load training data from `socio_economic_facts` and `benefit_events`
- Train RandomForest classifier
- Log metrics to MLflow (`smart/eligibility_scoring_360_profile/income_band`)
- Save model to `models/checkpoints/`

### 5. Run Graph Clustering

```bash
python graph_clustering.py
```

This will:
- Build relationship graph from `gr_relationships`
- Detect communities using Louvain algorithm
- Calculate centrality measures (degree, betweenness, closeness, pagerank)
- Update `cluster_id` in `profile_360` table

### 6. Run Anomaly Detection

```bash
python anomaly_detection.py
```

This will:
- Detect over-concentration (benefits > 3x local average)
- Detect under-coverage (eligible but not enrolled)
- Save flags to `analytics_flags` table

### 7. Train Eligibility Scoring Model (To be implemented)

```bash
python eligibility_scoring_train.py  # To be created
```

### 8. Run Profile Orchestrator

For one-time recomputation:
```bash
python profile_recompute_service.py
```

For scheduler mode (hourly recomputation):
```bash
python profile_recompute_service.py --scheduler
```

## Verification

### Check Database

```sql
-- Quick count check
SELECT 
    'Golden Records' as table_name, COUNT(*) as count FROM golden_records
UNION ALL
SELECT 'Relationships', COUNT(*) FROM gr_relationships
UNION ALL
SELECT 'Benefits', COUNT(*) FROM benefit_events
UNION ALL
SELECT 'Applications', COUNT(*) FROM application_events
UNION ALL
SELECT 'Profiles 360', COUNT(*) FROM profile_360;

-- Check profile coverage
SELECT 
    COUNT(DISTINCT gr.gr_id) as total_golden_records,
    COUNT(DISTINCT p.gr_id) as profiles_with_360,
    ROUND(COUNT(DISTINCT p.gr_id) * 100.0 / COUNT(DISTINCT gr.gr_id), 2) as coverage_pct
FROM golden_records gr
LEFT JOIN profile_360 p ON gr.gr_id = p.gr_id
WHERE gr.status = 'active';
```

### Check MLflow

Visit: `http://127.0.0.1:5000`

Look for experiments:
- `smart/eligibility_scoring_360_profile/income_band`
- `smart/eligibility_scoring_360_profile/eligibility_scoring` (when created)

### Test APIs (if Spring Boot is running)

```bash
# Get 360° profile
curl http://localhost:8080/profiles/360/{gr_id}

# Get network
curl http://localhost:8080/profiles/360/{gr_id}/network

# Get eligibility score
curl http://localhost:8080/eligibility/score?gr_id={gr_id}&scheme_id={scheme_id}

# Get cluster analytics
curl http://localhost:8080/analytics/benefits/clusters?scheme=HEALTH&district=JAIPUR

# Get under-coverage
curl http://localhost:8080/analytics/benefits/undercoverage?limit=100
```

### Run Data Exploration Notebook

```bash
cd ../notebooks
jupyter lab
# Open: 01_profile_eda.ipynb
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready -h 172.17.16.1 -p 5432`
- Check credentials in `config/db_config.yaml`
- Ensure `smart_warehouse` database exists: `psql -h 172.17.16.1 -U sameer -l`

### Missing Data

- Run `generate_synthetic.py` to populate data
- Check that schema was created correctly
- Verify Golden Records exist from AI-PLATFORM-01

### ML Model Errors

- Ensure training data is available in database
- Check MLflow is running: `mlflow ui --port 5000`
- Verify model files are saved to `models/checkpoints/`

### Import Errors

- Ensure you're using the correct Python venv
- Check that `shared/utils/db_connector.py` exists
- Verify all dependencies are installed: `pip list`

### Path Issues (WSL)

- Use WSL paths: `/mnt/c/Projects/SMART/ai-ml`
- Activate venv: `source .venv/bin/activate`
- Use `python` not `python3` when venv is active

## Next Steps

1. ✅ Complete data exploration notebook
2. ⏳ Implement eligibility scoring training
3. ⏳ Create fairness audit notebook (`02_fairness_audit.ipynb`)
4. ⏳ Configure Spring Boot service
5. ⏳ Set up scheduled recomputation (cron/systemd)
6. ⏳ Integrate with portals
7. ⏳ Set up monitoring and alerts

---

**Need help?** Check `QUICK_START.md` for simplified instructions or `README.md` for full documentation.

