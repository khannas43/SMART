# Database Setup Guide: Auto Application Submission Post-Consent

**Use Case ID:** AI-PLATFORM-05

## Quick Setup

### Option 1: Using Setup Script (Recommended - WSL/Ubuntu)

```bash
# Navigate to use case directory
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent

# Make script executable
chmod +x scripts/setup_database.sh

# Run setup script
./scripts/setup_database.sh
```

### Option 2: Manual Setup (PgAdmin or psql)

```bash
# Connect to database
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse

# Run schema script
\i database/application_schema.sql

# Or from command line:
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/application_schema.sql
```

### Option 3: Using PgAdmin GUI

1. Open PgAdmin 4
2. Connect to PostgreSQL server (172.17.16.1:5432)
3. Navigate to `smart_warehouse` database
4. Right-click on database → Query Tool
5. Open `database/application_schema.sql`
6. Execute the script (F5)

## Initialization Scripts (Run After Schema Creation)

After creating the schema, run these scripts to initialize data:

### 1. Initialize Scheme Form Schemas

```bash
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/init_scheme_form_schemas.py
```

This creates form schemas for all active schemes in `scheme_master`.

### 2. Initialize Submission Modes Configuration

```bash
python scripts/init_submission_modes_config.py
```

This creates submission mode configurations for all schemes.

### 3. Initialize Department Connectors (Optional)

```bash
python scripts/init_department_connectors.py
```

This creates placeholder connector configurations. You'll need to update these with actual API endpoints and credentials.

## Verify Setup

```bash
python scripts/check_config.py
```

This validates:
- Database connectivity
- Schema existence
- Table creation
- External database connections

## Tables Created

The schema creates the following tables in `application` schema:

1. **applications** - Main application records
2. **application_fields** - Field-level data with source tracking
3. **application_documents** - Document attachments
4. **application_validation_results** - Validation results
5. **application_submissions** - Submission records
6. **application_audit_logs** - Audit trail
7. **scheme_form_schemas** - Form schemas per scheme
8. **scheme_field_mappings** - Mapping rules
9. **submission_modes_config** - Submission mode configs
10. **department_connectors** - Department API configs
11. **application_events** - Event log

## Troubleshooting

### Schema Already Exists

If you see "schema already exists", that's fine - the script will continue and create tables.

### Permission Errors

If you see permission errors, ensure the `sameer` user has CREATE privileges:

```sql
GRANT CREATE ON SCHEMA application TO sameer;
ALTER SCHEMA application OWNER TO sameer;
```

### Foreign Key Errors

Ensure these dependencies exist:
- `public.scheme_master` table (should exist from previous use cases)
- `intimation.consent_records` table (from AI-PLATFORM-04)
- `eligibility.eligibility_snapshots` table (from AI-PLATFORM-03)

---

**After running these scripts, proceed with testing the Application Orchestrator service.**

