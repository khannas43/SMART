# Quick Database Setup Instructions

## Step-by-Step Setup

### 1. Create All Databases (Run as postgres superuser)

**Using psql:**
```bash
# Connect as postgres superuser
psql -h 172.17.16.1 -p 5432 -U postgres -d postgres

# Run the creation script
\i scripts/create-all-databases-simple.sql

# Or create manually:
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

### 2. Execute Schema Files (Run as sameer user)

**Windows PowerShell:**
```powershell
$env:PGPASSWORD="anjali143"

# Citizen Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_citizen -f portals\citizen\database\schemas\01_citizen_schema.sql

# Department Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_dept -f portals\dept\database\schemas\01_dept_schema.sql

# AIML Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_aiml -f portals\aiml\database\schemas\01_aiml_schema.sql

# Monitor Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_monitor -f portals\monitor\database\schemas\01_monitor_schema.sql

# AIML Warehouse
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f ai-ml\pipelines\warehouse\schemas\01_warehouse_schema.sql
```

**Linux/WSL:**
```bash
export PGPASSWORD="anjali143"

# Citizen Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_citizen -f portals/citizen/database/schemas/01_citizen_schema.sql

# Department Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_dept -f portals/dept/database/schemas/01_dept_schema.sql

# AIML Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_aiml -f portals/aiml/database/schemas/01_aiml_schema.sql

# Monitor Portal
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_monitor -f portals/monitor/database/schemas/01_monitor_schema.sql

# AIML Warehouse
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql
```

### 3. Verify Tables Created

```bash
# Verify using Python script
cd /mnt/c/Projects/SMART
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/verify-database-schemas.py
```

Or manually check:
```sql
\c smart_citizen
\dt  -- List tables

-- Count tables
SELECT count(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

## Expected Results

After successful setup:
- ✅ **smart_citizen**: 9 tables
- ✅ **smart_dept**: 11 tables
- ✅ **smart_aiml**: 9 tables
- ✅ **smart_monitor**: 10 tables
- ✅ **smart_warehouse**: 10+ tables (dimensions, facts, aggregates, ETL)

All tables ready for sample data insertion!

