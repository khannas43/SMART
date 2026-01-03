#!/bin/bash
# Bash script to migrate data from smart_warehouse to smart_citizen
# This script executes the Flyway migration V11 which contains the data migration SQL

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart}"
DB_USER="${DB_USER:-sameer}"
DB_PASSWORD="${DB_PASSWORD:-anjali143}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Data Migration: smart_warehouse -> smart_citizen${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Set password for psql
export PGPASSWORD="$DB_PASSWORD"

# Check if both databases exist
echo -e "${YELLOW}Checking databases...${NC}"
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_warehouse -t -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: smart_warehouse database does not exist or is not accessible!${NC}"
    exit 1
fi

if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: smart_citizen database does not exist or is not accessible!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Both databases exist and are accessible${NC}"
echo ""

# Check if warehouse has data
echo -e "${YELLOW}Checking warehouse data...${NC}"
WAREHOUSE_CITIZENS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_warehouse -t -c "SELECT COUNT(*) FROM citizens;" | tr -d ' ')
WAREHOUSE_SCHEMES=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_warehouse -t -c "SELECT COUNT(*) FROM schemes;" | tr -d ' ')
WAREHOUSE_APPLICATIONS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_warehouse -t -c "SELECT COUNT(*) FROM applications;" | tr -d ' ')

echo -e "${CYAN}  Warehouse Citizens: $WAREHOUSE_CITIZENS${NC}"
echo -e "${CYAN}  Warehouse Schemes: $WAREHOUSE_SCHEMES${NC}"
echo -e "${CYAN}  Warehouse Applications: $WAREHOUSE_APPLICATIONS${NC}"
echo ""

if [ "$WAREHOUSE_CITIZENS" -eq 0 ]; then
    echo -e "${YELLOW}WARNING: No citizens found in warehouse. Migration will have no effect.${NC}"
fi

# Check current citizen data
echo -e "${YELLOW}Checking current smart_citizen data...${NC}"
CURRENT_CITIZENS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM citizens;" | tr -d ' ')
CURRENT_SCHEMES=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM schemes;" | tr -d ' ')
CURRENT_APPLICATIONS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM service_applications;" | tr -d ' ')

echo -e "${CYAN}  Current Citizens: $CURRENT_CITIZENS${NC}"
echo -e "${CYAN}  Current Schemes: $CURRENT_SCHEMES${NC}"
echo -e "${CYAN}  Current Applications: $CURRENT_APPLICATIONS${NC}"
echo ""

# Confirm migration
read -p "Do you want to proceed with migration? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Migration cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting migration...${NC}"
echo ""

# Execute migration via Flyway
# Note: This will run the V11 migration script
MIGRATION_PATH="src/main/resources/db/migration/V11__migrate_data_from_warehouse.sql"

if [ -f "$MIGRATION_PATH" ]; then
    echo -e "${YELLOW}Executing migration script...${NC}"
    
    # Execute SQL file directly (connect to smart_citizen database)
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -f "$MIGRATION_PATH"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Migration completed successfully!${NC}"
        echo ""
        
        # Show final counts
        echo -e "${CYAN}Final data counts:${NC}"
        FINAL_CITIZENS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM citizens;" | tr -d ' ')
        FINAL_SCHEMES=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM schemes;" | tr -d ' ')
        FINAL_APPLICATIONS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM service_applications;" | tr -d ' ')
        FINAL_HISTORY=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d smart_citizen -t -c "SELECT COUNT(*) FROM application_status_history;" | tr -d ' ')
        
        echo -e "${GREEN}  Citizens: $FINAL_CITIZENS${NC}"
        echo -e "${GREEN}  Schemes: $FINAL_SCHEMES${NC}"
        echo -e "${GREEN}  Applications: $FINAL_APPLICATIONS${NC}"
        echo -e "${GREEN}  Status History: $FINAL_HISTORY${NC}"
    else
        echo ""
        echo -e "${RED}✗ Migration failed. Check error messages above.${NC}"
        exit 1
    fi
else
    echo -e "${RED}ERROR: Migration script not found at: $MIGRATION_PATH${NC}"
    echo -e "${YELLOW}Please run this script from the citizen-service directory.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Migration Complete!${NC}"
echo -e "${CYAN}========================================${NC}"

