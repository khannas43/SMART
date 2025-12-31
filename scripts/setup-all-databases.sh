#!/bin/bash
# Setup All SMART Platform Databases
# Creates all databases and executes schema files

set -e

# Configuration
HOST="${DB_HOST:-localhost}"
PORT="${DB_PORT:-5432}"
USER="${DB_USER:-sameer}"
PASSWORD="${DB_PASSWORD:-anjali143}"
SUPERUSER="${DB_SUPERUSER:-postgres}"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}SMART Platform - Database Setup Script${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL client (psql) not found${NC}"
    echo "Please install PostgreSQL client"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL client found: $(psql --version)${NC}"
echo ""

# Set PGPASSWORD
export PGPASSWORD="$PASSWORD"

# Databases to setup
declare -a databases=(
    "smart_citizen:portals/citizen/database/schemas/01_citizen_schema.sql:Citizen Portal"
    "smart_dept:portals/dept/database/schemas/01_dept_schema.sql:Department Portal"
    "smart_aiml:portals/aiml/database/schemas/01_aiml_schema.sql:AIML Portal"
    "smart_monitor:portals/monitor/database/schemas/01_monitor_schema.sql:Monitor Portal"
    "smart_warehouse:ai-ml/pipelines/warehouse/schemas/01_warehouse_schema.sql:AIML Warehouse"
)

success_count=0
fail_count=0

# Function to check if database exists
check_database_exists() {
    local db_name=$1
    local result=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" 2>/dev/null)
    [ "$result" = "1" ]
}

# Function to create database
create_database() {
    local db_name=$1
    echo -n "  Creating database... "
    
    export PGPASSWORD="${DB_SUPERPASSWORD:-$PASSWORD}"
    
    if psql -h "$HOST" -p "$PORT" -U "$SUPERUSER" -d postgres -c "CREATE DATABASE $db_name WITH OWNER = $USER ENCODING = 'UTF8';" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        export PGPASSWORD="$PASSWORD"
        return 0
    else
        echo -e "${RED}❌${NC}"
        export PGPASSWORD="$PASSWORD"
        return 1
    fi
}

# Function to execute schema file
execute_schema() {
    local db_name=$1
    local schema_file=$2
    local full_path="$PROJECT_ROOT/$schema_file"
    
    if [ ! -f "$full_path" ]; then
        echo -e "    ${YELLOW}⚠️  Schema file not found: $schema_file${NC}"
        return 1
    fi
    
    echo -n "  Executing schema file... "
    
    if psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -f "$full_path" 2>&1 | tail -5
        return 1
    fi
}

# Process each database
for db_info in "${databases[@]}"; do
    IFS=':' read -r db_name schema_file description <<< "$db_info"
    
    echo ""
    echo -e "${YELLOW}Processing: $description ($db_name)${NC}"
    echo -e "  Schema: $schema_file"
    
    # Check if database exists
    if check_database_exists "$db_name"; then
        echo -e "  ${CYAN}Database already exists${NC}"
        read -p "  Recreate database? (y/N): " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -n "  Dropping existing database... "
            export PGPASSWORD="${DB_SUPERPASSWORD:-$PASSWORD}"
            psql -h "$HOST" -p "$PORT" -U "$SUPERUSER" -d postgres -c "DROP DATABASE IF EXISTS $db_name;" > /dev/null 2>&1
            export PGPASSWORD="$PASSWORD"
            echo -e "${GREEN}✅${NC}"
            
            if ! create_database "$db_name"; then
                ((fail_count++))
                continue
            fi
        else
            echo -e "  ${CYAN}Skipping database creation${NC}"
        fi
    else
        if ! create_database "$db_name"; then
            ((fail_count++))
            continue
        fi
    fi
    
    # Grant schema privileges
    echo -n "  Granting privileges... "
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "GRANT ALL ON SCHEMA public TO $USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $USER;" > /dev/null 2>&1
    
    if [ "$db_name" = "smart_warehouse" ]; then
        psql -h "$HOST" -p "$PORT" -U "$USER" -d "$db_name" -c "CREATE SCHEMA IF NOT EXISTS staging; GRANT ALL ON SCHEMA staging TO $USER;" > /dev/null 2>&1
    fi
    echo -e "${GREEN}✅${NC}"
    
    # Execute schema file
    if execute_schema "$db_name" "$schema_file"; then
        ((success_count++))
        echo -e "  ${GREEN}✅ Database setup completed successfully${NC}"
    else
        ((fail_count++))
    fi
done

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}Setup Summary${NC}"
echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}Successfully setup: $success_count${NC}"
if [ $fail_count -gt 0 ]; then
    echo -e "${RED}Failed: $fail_count${NC}"
else
    echo -e "${GREEN}Failed: $fail_count${NC}"
fi
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✅ All databases setup successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some databases failed to setup${NC}"
    exit 1
fi

