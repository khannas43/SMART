# Database Setup Instructions

Since `psql` is not in Windows PATH, follow these steps:

## Step 1: Create All Databases

You need to create the databases first. You can do this in two ways:

### Option A: Using PostgreSQL GUI (pgAdmin)
1. Open pgAdmin
2. Connect to PostgreSQL server
3. Right-click "Databases" → Create → Database
4. Create each database:
   - `smart_citizen`
   - `smart_dept`
   - `smart_aiml`
   - `smart_monitor`
   - `smart_warehouse`
5. Set owner to `sameer` for each

### Option B: Using WSL (Recommended)

**From WSL terminal:**
```bash
cd /mnt/c/Projects/SMART

# Set password
export PGPASSWORD="anjali143"

# Create databases (requires postgres superuser)
psql -h 172.17.16.1 -p 5432 -U postgres -d postgres -f scripts/create-databases-first.sql

# Or create manually one by one:
psql -h 172.17.16.1 -p 5432 -U postgres -d postgres <<EOF
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

## Step 2: Execute Schema Files

**From WSL terminal:**
```bash
cd /mnt/c/Projects/SMART
export PGPASSWORD="anjali143"

# Execute all schemas
./scripts/setup-databases-wsl.sh

# Or execute manually:
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_citizen -f portals/citizen/database/schemas/01_citizen_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_dept -f portals/dept/database/schemas/01_dept_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_aiml -f portals/aiml/database/schemas/01_aiml_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_monitor -f portals/monitor/database/schemas/01_monitor_schema.sql
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql
```

## Step 3: Verify

```bash
# Using Python script
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/verify-database-schemas.py
```

## All-in-One Command (WSL)

```bash
cd /mnt/c/Projects/SMART
export PGPASSWORD="anjali143"

# Create databases
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

# Execute schemas
./scripts/setup-databases-wsl.sh

# Verify
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate
python scripts/verify-database-schemas.py
```

