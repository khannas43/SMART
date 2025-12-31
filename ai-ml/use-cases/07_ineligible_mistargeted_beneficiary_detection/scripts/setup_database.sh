#!/bin/bash
# Setup Database Schema for Ineligible/Mistargeted Beneficiary Detection
# Use Case ID: AI-PLATFORM-07

set -e

echo "=================================================================================="
echo "Setting up Detection Database Schema"
echo "=================================================================================="

# Database configuration
DB_HOST="172.17.16.1"
DB_PORT="5432"
DB_NAME="smart_warehouse"
DB_USER="sameer"
DB_PASSWORD="anjali143"
SCHEMA_FILE="database/detection_schema.sql"

echo ""
echo "📋 Configuration:"
echo "   Host: ${DB_HOST}:${DB_PORT}"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo ""

echo "📦 Creating detection schema and tables..."
export PGPASSWORD="${DB_PASSWORD}"
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -f ${SCHEMA_FILE}

echo ""
echo "✅ Database schema setup complete!"
echo ""
echo "📊 Verifying tables..."

# Verify tables were created
TABLE_COUNT=$(PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'detection' AND table_type = 'BASE TABLE'
" | xargs)

echo "   ✅ Found ${TABLE_COUNT} tables in 'detection' schema"
echo ""
echo "📋 Key tables:"
PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'detection' 
    ORDER BY table_name
" | grep -v "^$" | grep -v "table_name" | grep -v "^-" | grep -v "^("

echo ""
echo "Next steps:"
echo "1. Initialize detection configuration: python scripts/init_detection_config.py"
echo "2. Initialize scheme exclusion rules: python scripts/init_exclusion_rules.py"
echo "3. Validate configuration: python scripts/check_config.py"
echo "=================================================================================="
echo "✅ Detection schema setup complete!"
echo "=================================================================================="

