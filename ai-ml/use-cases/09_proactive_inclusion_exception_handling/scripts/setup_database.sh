#!/bin/bash
# Setup Database Schema for Proactive Inclusion & Exception Handling
# Use Case ID: AI-PLATFORM-09

set -e

echo "=================================================================================="
echo "Setting up Proactive Inclusion Database Schema"
echo "=================================================================================="

# Database configuration
DB_HOST="172.17.16.1"
DB_PORT="5432"
DB_NAME="smart_warehouse"
DB_USER="sameer"
DB_PASSWORD="anjali143"
SCHEMA_FILE="database/inclusion_schema.sql"

echo ""
echo "📋 Configuration:"
echo "   Host: ${DB_HOST}:${DB_PORT}"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo ""

echo "📦 Creating inclusion schema and tables..."
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
    WHERE table_schema = 'inclusion' AND table_type = 'BASE TABLE'
" | xargs)

echo "   ✅ Found ${TABLE_COUNT} tables in 'inclusion' schema"
echo ""
echo "📋 Key tables:"
PGPASSWORD="${DB_PASSWORD}" psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'inclusion' 
    ORDER BY table_name
" | grep -v "^$" | grep -v "table_name" | grep -v "^-" | grep -v "^("

echo ""
echo "Next steps:"
echo "1. Verify configuration: python scripts/check_config.py"
echo "2. Test inclusion detection: python scripts/test_inclusion_workflow.py"
echo "=================================================================================="
echo "✅ Inclusion schema setup complete!"
echo "=================================================================================="

