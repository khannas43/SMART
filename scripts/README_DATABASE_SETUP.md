# Quick Database Setup - Instructions

## Problem
- `psql` is not in Windows PATH
- PowerShell execution policy restrictions

## Solution: Use WSL

All database setup should be done from **WSL terminal**.

## Complete Setup (One Command)

**Open WSL terminal and run:**
```bash
cd /mnt/c/Projects/SMART
bash scripts/setup-all-dbs-complete.sh
```

This script will:
1. ✅ Create all 5 databases
2. ✅ Execute all schema files
3. ✅ Verify tables are created
4. ✅ Show summary

## Manual Setup (If Automated Fails)

### Step 1: Create Databases

```bash
cd /mnt/c/Projects/SMART
export PGPASSWORD="anjali143"

# As postgres superuser
psql -h 172.17.16.1 -p 5432 -U postgres -d postgres <<'EOF'
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
EOF
```

### Step 2: Execute Schemas

```bash
export PGPASSWORD="anjali143"

# Execute each schema
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_citizen -f portals/citizen/database/schemas/01_citizen_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_dept -f portals/dept/database/schemas/01_dept_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_aiml -f portals/aiml/database/schemas/01_aiml_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_monitor -f portals/monitor/database/schemas/01_monitor_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql
```

### Step 3: Verify

```bash
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/verify-database-schemas.py
```

## Troubleshooting

### If postgres user doesn't work:
- Try with your PostgreSQL admin user
- Or create databases using pgAdmin GUI

### If connection fails:
- Check PostgreSQL is running: `pg_isready -h 172.17.16.1 -p 5432`
- Verify credentials

### If tables already exist:
- Script will skip creation
- Or drop database and recreate: `DROP DATABASE smart_citizen CASCADE;`

