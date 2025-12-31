#!/bin/bash
# Complete Database Setup - Creates databases and executes schemas
# Run from WSL: bash scripts/setup-all-dbs-complete.sh

set -e

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
USER="${DB_USER:-sameer}"
PASSWORD="${DB_PASSWORD:-anjali143}"
SUPERUSER="${DB_SUPERUSER:-postgres}"

export PGPASSWORD="$PASSWORD"

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "SMART Platform - Complete Database Setup"
echo "============================================================"
echo ""

# Check psql
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL client (psql) not found"
    exit 1
fi

echo "✅ PostgreSQL client found"
echo ""

# Step 1: Create databases
echo "Step 1: Creating databases..."
echo ""

databases=("smart_citizen" "smart_dept" "smart_aiml" "smart_monitor" "smart_warehouse")

for db in "${databases[@]}"; do
    echo -n "  Creating $db... "
    
    # Check if exists
    exists=$(psql -h "$HOST" -p "$PORT" -U "$SUPERUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$db'" 2>/dev/null || echo "0")
    
    if [ "$exists" = "1" ]; then
        echo "already exists"
    else
        export PGPASSWORD="${DB_SUPERPASSWORD:-$PASSWORD}"
        if psql -h "$HOST" -p "$PORT" -U "$SUPERUSER" -d postgres -c "CREATE DATABASE $db WITH OWNER = $USER ENCODING = 'UTF8';" > /dev/null 2>&1; then
            echo "✅"
            export PGPASSWORD="$PASSWORD"
        else
            echo "❌ (may need superuser password)"
            export PGPASSWORD="$PASSWORD"
        fi
    fi
    
    # Grant privileges
    export PGPASSWORD="${DB_SUPERPASSWORD:-$PASSWORD}"
    psql -h "$HOST" -p "$PORT" -U "$SUPERUSER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $db TO $USER;" > /dev/null 2>&1 || true
    export PGPASSWORD="$PASSWORD"
done

echo ""
echo "Step 2: Executing schema files..."
echo ""

# Step 2: Execute schemas
declare -a schemas=(
    "smart_citizen:portals/citizen/database/schemas/01_citizen_schema.sql:Citizen Portal"
    "smart_dept:portals/dept/database/schemas/01_dept_schema.sql:Department Portal"
    "smart_aiml:portals/aiml/database/schemas/01_aiml_schema.sql:AIML Portal"
    "smart_monitor:portals/monitor/database/schemas/01_monitor_schema.sql:Monitor Portal"
    "smart_warehouse:ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql:AIML Warehouse"
)

success_count=0
fail_count=0

for schema_info in "${schemas[@]}"; do
    IFS=':' read -r db_name schema_file description <<< "$schema_info"
    
    echo "Processing: $description ($db_name)"
    
    full_path="$PROJECT_ROOT/$schema_file"
    
    if [ ! -f "$full_path" ]; then
        echo "  ❌ Schema file not found: $schema_file"
        ((fail_count++))
        continue
    fi
    
    # Grant schema privileges
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "GRANT ALL ON SCHEMA public TO $USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $USER;" > /dev/null 2>&1
    
    # Create staging schema for warehouse
    if [ "$db_name" = "smart_warehouse" ]; then
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "CREATE SCHEMA IF NOT EXISTS staging; GRANT ALL ON SCHEMA staging TO $USER;" > /dev/null 2>&1
    fi
    
    # Execute schema
    echo -n "  Executing schema... "
    if psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" > /dev/null 2>&1; then
        echo "✅"
        
        # Count tables
        table_count=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null || echo "0")
        echo "  ✅ Tables created: $table_count"
        ((success_count++))
    else
        echo "❌"
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" 2>&1 | tail -3 | sed 's/^/    /'
        ((fail_count++))
    fi
    echo ""
done

echo "============================================================"
echo "Summary"
echo "============================================================"
echo "Successfully setup: $success_count"
echo "Failed: $fail_count"
echo ""

if [ $fail_count -eq 0 ]; then
    echo "✅ All databases and schemas setup successfully!"
    echo ""
    echo "Next step: Add sample data based on your requirements"
    exit 0
else
    echo "⚠️  Some databases failed to setup"
    exit 1
fi

