#!/bin/bash
# Setup All Databases and Execute Schemas via WSL
# This script can be run from WSL or called from Windows PowerShell

set -e

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
USER="${DB_USER:-sameer}"
PASSWORD="${DB_PASSWORD:-anjali143}"

# Get project root (works in WSL)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

export PGPASSWORD="$PASSWORD"

echo "============================================================"
echo "SMART Platform - Database Schema Setup"
echo "============================================================"
echo ""

# Databases and schemas
declare -a schemas=(
    "smart_citizen:portals/citizen/database/schemas/01_citizen_schema.sql:Citizen Portal:9"
    "smart_dept:portals/dept/database/schemas/01_dept_schema.sql:Department Portal:11"
    "smart_aiml:portals/aiml/database/schemas/01_aiml_schema.sql:AIML Portal:9"
    "smart_monitor:portals/monitor/database/schemas/01_monitor_schema.sql:Monitor Portal:10"
    "smart_warehouse:ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql:AIML Warehouse:10"
)

success_count=0
fail_count=0

for schema_info in "${schemas[@]}"; do
    IFS=':' read -r db_name schema_file description expected_tables <<< "$schema_info"
    
    echo ""
    echo "Processing: $description ($db_name)"
    echo "  Expected tables: $expected_tables"
    
    full_path="$PROJECT_ROOT/$schema_file"
    
    if [ ! -f "$full_path" ]; then
        echo "  ❌ Schema file not found: $schema_file"
        ((fail_count++))
        continue
    fi
    
    # Check if database exists
    db_exists=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" 2>/dev/null || echo "0")
    
    if [ "$db_exists" != "1" ]; then
        echo "  ⚠️  Database does not exist: $db_name"
        echo "  Please create it first:"
        echo "    CREATE DATABASE $db_name WITH OWNER = $USER ENCODING = 'UTF8';"
        ((fail_count++))
        continue
    fi
    
    echo "  ✅ Database exists"
    
    # Grant privileges
    echo -n "  Granting privileges... "
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "GRANT ALL ON SCHEMA public TO $USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $USER;" > /dev/null 2>&1
    echo "✅"
    
    # Create staging schema for warehouse
    if [ "$db_name" = "smart_warehouse" ]; then
        echo -n "  Creating staging schema... "
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "CREATE SCHEMA IF NOT EXISTS staging; GRANT ALL ON SCHEMA staging TO $USER;" > /dev/null 2>&1
        echo "✅"
    fi
    
    # Execute schema
    echo -n "  Executing schema file... "
    if psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" > /dev/null 2>&1; then
        echo "✅"
        
        # Verify tables
        table_count=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null || echo "0")
        echo "  ✅ Tables created: $table_count (expected: ~$expected_tables)"
        
        ((success_count++))
    else
        echo "❌"
        echo "  Error details:"
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" 2>&1 | tail -5 | sed 's/^/    /'
        ((fail_count++))
    fi
done

echo ""
echo "============================================================"
echo "Summary"
echo "============================================================"
echo "Success: $success_count"
echo "Failed: $fail_count"
echo ""

if [ $fail_count -eq 0 ]; then
    echo "✅ All schemas executed successfully!"
    exit 0
else
    echo "⚠️  Some schemas failed"
    exit 1
fi

