#!/bin/bash
# Setup Database Schema for Eligibility Checker & Recommendations
# Use Case ID: AI-PLATFORM-08

set -e

echo "=================================================================================="
echo "Setting up Eligibility Checker Database Schema"
echo "=================================================================================="

# Database configuration
DB_HOST="172.17.16.1"
DB_PORT="5432"
DB_NAME="smart_warehouse"
DB_USER="sameer"
DB_PASSWORD="anjali143"
SCHEMA_FILE="database/eligibility_checker_schema.sql"

echo ""
echo "📋 Configuration:"
echo "   Host: ${DB_HOST}:${DB_PORT}"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo ""

echo "📦 Creating eligibility_checker schema and tables..."
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
    WHERE table_schema = 'eligibility_checker' AND table_type = 'BASE TABLE'
" | xargs)

echo "   ✅ Found ${TABLE_COUNT} tables in 'eligibility_checker' schema"
echo ""
echo "📋 Key tables:"
PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'eligibility_checker' 
    ORDER BY table_name
" | grep -v "^$" | grep -v "table_name" | grep -v "^-" | grep -v "^("

echo ""
echo "Next steps:"
echo "1. Verify configuration: python scripts/check_config.py"
echo "2. Test eligibility checker: python scripts/test_eligibility_checker.py"
echo "=================================================================================="
echo "✅ Eligibility Checker schema setup complete!"
echo "=================================================================================="

