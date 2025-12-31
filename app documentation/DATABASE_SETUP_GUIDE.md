# SMART Platform - Database Setup Guide

This guide explains how to create all databases and execute schema files for the SMART Platform.

## Prerequisites

- PostgreSQL installed and running
- PostgreSQL user `sameer` with password `anjali143` (or update credentials)
- PostgreSQL superuser access (postgres user) for database creation
- psql command-line client available

## Quick Setup

### Option 1: Automated Setup (Recommended)

#### Windows PowerShell:
```powershell
cd C:\Projects\SMART
.\scripts\setup-all-databases.ps1
```

#### Linux/WSL:
```bash
cd /mnt/c/Projects/SMART
./scripts/setup-all-databases.sh
```

### Option 2: Manual Setup

#### Step 1: Create All Databases

Run as PostgreSQL superuser:
```sql
\i scripts/create-all-databases-simple.sql
```

Or manually:
```sql
CREATE DATABASE smart_citizen WITH OWNER = sameer ENCODING = 'UTF8';
CREATE DATABASE smart_dept WITH OWNER = sameer ENCODING = 'UTF8';
CREATE DATABASE smart_aiml WITH OWNER = sameer ENCODING = 'UTF8';
CREATE DATABASE smart_monitor WITH OWNER = sameer ENCODING = 'UTF8';
CREATE DATABASE smart_warehouse WITH OWNER = sameer ENCODING = 'UTF8';

GRANT ALL PRIVILEGES ON DATABASE smart_citizen TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_dept TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_aiml TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_monitor TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_warehouse TO sameer;
```

#### Step 2: Execute Schema Files

**Windows PowerShell:**
```powershell
cd C:\Projects\SMART
.\scripts\execute-schemas.ps1
```

**Manual execution:**
```bash
# Citizen Portal
psql -h localhost -p 5432 -U sameer -d smart_citizen -f portals/citizen/database/schemas/01_citizen_schema.sql

# Department Portal
psql -h localhost -p 5432 -U sameer -d smart_dept -f portals/dept/database/schemas/01_dept_schema.sql

# AIML Portal
psql -h localhost -p 5432 -U sameer -d smart_aiml -f portals/aiml/database/schemas/01_aiml_schema.sql

# Monitor Portal
psql -h localhost -p 5432 -U sameer -d smart_monitor -f portals/monitor/database/schemas/01_monitor_schema.sql

# AIML Warehouse
psql -h localhost -p 5432 -U sameer -d smart_warehouse -f ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql
```

## Verify Schema Creation

### Using Python Script:
```bash
cd /mnt/c/Projects/SMART
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/verify-database-schemas.py
```

### Manual Verification:

Check tables in each database:
```sql
-- Connect to database
\c smart_citizen

-- List tables
\dt

-- Count tables
SELECT count(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

## Expected Tables Per Database

### smart_citizen (9 tables)
- citizens
- schemes
- service_applications
- documents
- application_status_history
- notifications
- payments
- feedback
- audit_log

### smart_dept (11 tables)
- departments
- dept_users
- designations
- workflows
- application_assignments
- processing_actions
- approval_chains
- document_verifications
- dashboard_metrics
- dept_notifications
- dept_audit_log

### smart_aiml (9 tables)
- ml_use_cases
- ml_models
- mlflow_experiments
- mlflow_runs
- predictions
- batch_prediction_jobs
- pipeline_runs
- model_monitoring
- analytics_cache

### smart_monitor (10 tables)
- system_components
- health_checks
- system_metrics
- performance_metrics
- system_logs
- log_aggregations
- alert_rules
- alert_incidents
- admin_users
- monitor_audit_log

### smart_warehouse (10+ tables)
**Dimensions:**
- dim_date
- dim_citizen
- dim_scheme
- dim_department

**Facts:**
- fact_service_applications
- fact_application_processing
- fact_eligibility_scoring

**Aggregations:**
- agg_daily_applications

**ETL Metadata:**
- etl_batches
- etl_data_quality

## Troubleshooting

### Permission Denied
If you get permission errors, ensure the user has privileges:
```sql
-- As superuser
GRANT ALL PRIVILEGES ON DATABASE smart_citizen TO sameer;
ALTER DATABASE smart_citizen OWNER TO sameer;
```

### Schema File Not Found
Ensure you're running scripts from the project root directory.

### Connection Refused
- Check PostgreSQL is running: `pg_isready`
- Verify host/port: `172.17.16.1:5432` (or `localhost:5432`)
- Check firewall settings

### Table Already Exists
If tables already exist, drop and recreate:
```sql
-- Drop database (CAREFUL!)
DROP DATABASE smart_citizen CASCADE;

-- Recreate
CREATE DATABASE smart_citizen WITH OWNER = sameer;
```

## Sample Data

After schema creation, you can add sample data records directly based on your requirements. The schemas are designed to be flexible and support various use cases.

## Next Steps

1. ✅ Databases created
2. ✅ Tables created
3. ⏭️ Add sample data (as per your requirements)
4. ⏭️ Test database connections from applications
5. ⏭️ Set up ETL pipelines for warehouse

## Related Documentation

- [Database Schema Design](DATABASE_SCHEMA_DESIGN.md)
- [Development Configuration](DEVELOPMENT_CONFIG.md)

