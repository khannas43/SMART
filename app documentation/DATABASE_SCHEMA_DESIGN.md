# SMART Platform - Database Schema Design

This document describes the database schema design for all portals and the AIML data warehouse, following **Option 3: Separate Databases with Integration Layer**.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Portal Databases (Production)                   │
├─────────────────────────────────────────────────────────────┤
│ smart_citizen  │ smart_dept │ smart_aiml │ smart_monitor   │
│ (Public DC)    │ (Internal) │ (Restricted│  (Admin DC)     │
│                │   DC)      │   DC)      │                 │
└────────────────┴────────────┴────────────┴─────────────────┘
                        │
                        │  ETL / CDC
                        ▼
        ┌───────────────────────────────┐
        │   smart_warehouse             │
        │   (Analytical / OLAP)         │
        │   (Restricted DC)             │
        └───────────────────────────────┘
```

## Portal Database Schemas

### 1. Citizen Portal (`smart_citizen`)

**Location:** Public-facing Data Center  
**Purpose:** Store citizen-facing data

#### Core Tables:
- `citizens` - Citizen user accounts and profiles
- `schemes` - Government schemes available for application
- `service_applications` - Service applications submitted by citizens
- `documents` - Documents uploaded by citizens
- `application_status_history` - Status change tracking
- `notifications` - Notifications to citizens
- `payments` - Payment transactions
- `feedback` - Feedback and complaints
- `audit_log` - Audit trail

#### Key Features:
- UUID-based primary keys
- Comprehensive indexing for performance
- Audit trails with created_at/updated_at
- Status tracking with history
- Document verification workflow

#### File: `portals/citizen/database/schemas/01_citizen_schema.sql`

---

### 2. Department Portal (`smart_dept`)

**Location:** Internal Government Network Data Center  
**Purpose:** Workflow management and processing

#### Core Tables:
- `departments` - Department hierarchy
- `dept_users` - Department officers and staff
- `designations` - Job designations/positions
- `workflows` - Workflow definitions
- `application_assignments` - Application assignments to officers
- `processing_actions` - Processing decisions and actions
- `approval_chains` - Multi-level approval chains
- `document_verifications` - Document verification records
- `dashboard_metrics` - Cached dashboard metrics
- `dept_notifications` - Internal notifications
- `dept_audit_log` - Department audit trail

#### Key Features:
- Role-based access control structure
- Workflow engine support
- Assignment and delegation tracking
- Performance metrics caching
- Comprehensive audit logging

#### File: `portals/dept/database/schemas/01_dept_schema.sql`

---

### 3. AIML Portal (`smart_aiml`)

**Location:** Restricted Data Center  
**Purpose:** ML models, experiments, and predictions

#### Core Tables:
- `ml_use_cases` - 27 ML use cases registry
- `ml_models` - ML model registry and metadata
- `mlflow_experiments` - MLflow experiments cache
- `mlflow_runs` - MLflow runs cache
- `predictions` - Model predictions/inferences
- `batch_prediction_jobs` - Batch prediction job tracking
- `pipeline_runs` - ETL pipeline execution tracking
- `model_monitoring` - Model performance monitoring
- `analytics_cache` - Cached analytics data

#### Key Features:
- Model versioning and lifecycle management
- MLflow integration
- Prediction tracking with ground truth
- Model performance monitoring
- Batch processing support

#### File: `portals/aiml/database/schemas/01_aiml_schema.sql`

---

### 4. Monitor Portal (`smart_monitor`)

**Location:** Admin Data Center  
**Purpose:** System monitoring and administration

#### Core Tables:
- `system_components` - Registered components for monitoring
- `health_checks` - Health check results
- `system_metrics` - System metrics collection
- `performance_metrics` - CPU, Memory, Disk, Network metrics
- `system_logs` - Aggregated system logs
- `log_aggregations` - Pre-aggregated log statistics
- `alert_rules` - Alert rule definitions
- `alert_incidents` - Alert incidents and resolution
- `admin_users` - Monitor portal administrators
- `monitor_audit_log` - Comprehensive audit trail

#### Key Features:
- Component-based monitoring
- Real-time health checks
- Performance metrics collection
- Alert management
- Log aggregation and analysis

#### File: `portals/monitor/database/schemas/01_monitor_schema.sql`

---

## AIML Data Warehouse Schema (`smart_warehouse`)

**Location:** Restricted Data Center (same as AIML portal)  
**Purpose:** Analytical database for ML training and analytics  
**Design:** Star/Snowflake Schema (Dimensional Model)

### Schema Structure

#### Dimensions (Type 2 SCD - Slowly Changing Dimensions)

1. **dim_date** - Time dimension
   - Date keys (YYYYMMDD format)
   - Fiscal year support
   - Holiday tracking
   - Pre-populated for date ranges

2. **dim_citizen** - Citizen dimension
   - Demographics
   - Location (city, district, region)
   - Type 2 SCD for historical tracking
   - Aggregated from citizen portal

3. **dim_scheme** - Scheme dimension
   - Scheme details
   - Categories and departments
   - Type 2 SCD for historical tracking
   - Aggregated from citizen portal

4. **dim_department** - Department dimension
   - Department hierarchy
   - Organizational structure
   - Type 2 SCD for historical tracking
   - Aggregated from dept portal

#### Fact Tables

1. **fact_service_applications**
   - **Grain:** One row per application
   - Measures: processing_days, sla_compliance, amounts
   - Links to citizen, scheme, department, date dimensions
   - Aggregated from citizen portal

2. **fact_application_processing**
   - **Grain:** One row per processing action
   - Measures: processing_time, action counts
   - Tracks workflow steps and decisions
   - Aggregated from dept portal

3. **fact_eligibility_scoring**
   - **Grain:** One row per eligibility prediction
   - Measures: eligibility_score, confidence_score, accuracy
   - Links predictions to actual outcomes
   - Used for model training and evaluation

#### Aggregated Tables (Pre-computed)

1. **agg_daily_applications**
   - Daily aggregations by scheme, department, district
   - Pre-calculated for dashboard performance
   - Measures: counts, rates, amounts

#### ETL Metadata

1. **etl_batches** - ETL batch tracking
2. **etl_data_quality** - Data quality check results
3. **staging** schema - Staging area for ETL

#### File: `ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql`

---

## Database Connection Details

### Development (Current)
- Host: `localhost` / `172.17.16.1`
- Port: `5432`
- Databases: `smart_citizen`, `smart_dept`, `smart_aiml`, `smart_monitor`, `smart_warehouse`
- Username: `sameer`
- Password: `anjali143`

### Production (Per Portal)
Each portal will connect to its own database in its respective data center:
- Citizen Portal → `smart_citizen` DB (Public DC)
- Dept Portal → `smart_dept` DB (Internal DC)
- AIML Portal → `smart_aiml` DB (Restricted DC)
- Monitor Portal → `smart_monitor` DB (Admin DC)
- AIML ETL → `smart_warehouse` DB (Restricted DC)

---

## Data Integration Strategy

### ETL Process Flow

```
Portal DBs → ETL Pipeline → Staging → Warehouse (Dimensions + Facts)
```

1. **Extract:** Pull data from portal databases
2. **Transform:** 
   - Clean and validate data
   - Create surrogate keys
   - Handle SCD Type 2 changes
   - Calculate derived measures
3. **Load:** Insert into warehouse dimensions and facts

### ETL Schedule
- **Full Load:** Weekly (weekends)
- **Incremental Load:** Daily (nightly)
- **Real-time:** Critical metrics (via CDC if needed)

---

## Key Design Decisions

### 1. UUID vs BIGSERIAL
- **Portal DBs:** Use UUID for distributed systems and merging
- **Warehouse:** Use BIGSERIAL for performance in analytical queries

### 2. Normalization Level
- **Portal DBs:** Normalized (3NF) for transactional integrity
- **Warehouse:** Denormalized (star schema) for analytical performance

### 3. Audit Trails
- All portal tables include: `created_at`, `updated_at`, `created_by`, `updated_by`
- Comprehensive audit_log tables for compliance

### 4. Soft Deletes
- Use `status` columns instead of hard deletes where appropriate
- Maintain historical data

### 5. Indexing Strategy
- Index all foreign keys
- Index frequently queried columns (status, dates, codes)
- Composite indexes for common query patterns

---

## Migration Strategy

### Step 1: Create Portal Databases
```sql
CREATE DATABASE smart_citizen;
CREATE DATABASE smart_dept;
CREATE DATABASE smart_aiml;
CREATE DATABASE smart_monitor;
CREATE DATABASE smart_warehouse;
```

### Step 2: Run Schema Scripts
Execute schema SQL files in order:
1. Portal schemas first
2. Warehouse schema after portals are established

### Step 3: Set Up ETL
- Configure ETL pipelines
- Set up scheduled jobs
- Test data extraction and loading

---

## Next Steps

1. ✅ Database schema definitions created
2. ✅ AIML warehouse schema designed
3. ⏭️ Create Flyway/Liquibase migration scripts
4. ⏭️ Set up ETL pipeline infrastructure
5. ⏭️ Create data quality checks
6. ⏭️ Set up backup and recovery procedures

---

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Development Configuration](app%20documentation/DEVELOPMENT_CONFIG.md)

