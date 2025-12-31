#!/bin/bash
# Create Eligibility Schema in smart_warehouse database
# Use Case: AI-PLATFORM-03

set -e

echo "============================================================"
echo "Creating Eligibility Schema in smart_warehouse"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Database configuration
DB_HOST="${DB_HOST:-172.17.16.1}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart_warehouse}"
DB_USER="${DB_USER:-sameer}"
DB_PASSWORD="${DB_PASSWORD:-anjali143}"

export PGPASSWORD="$DB_PASSWORD"

# Schema files
SCHEMA_FILE="$PROJECT_DIR/database/eligibility_schema.sql"
VERSIONING_FILE="$PROJECT_DIR/database/eligibility_schema_versioning.sql"

echo "📋 Configuration:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Create eligibility schema
echo "📦 Creating eligibility schema and tables..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "   ✅ Eligibility schema created successfully"
else
    echo "   ❌ Error creating schema"
    exit 1
fi

# Create versioning extensions (if file exists)
if [ -f "$VERSIONING_FILE" ]; then
    echo ""
    echo "📦 Creating versioning extensions..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$VERSIONING_FILE"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Versioning extensions created successfully"
    else
        echo "   ⚠️  Warning: Some versioning objects may already exist (this is OK)"
    fi
fi

# Verify tables
echo ""
echo "🔍 Verifying tables..."
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'eligibility';")

echo "   ✅ Found $TABLE_COUNT tables in 'eligibility' schema"

# List key tables
echo ""
echo "📋 Key tables:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'eligibility' 
    ORDER BY table_name;" -t

echo ""
echo "============================================================"
echo "✅ Eligibility schema setup complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Run test script: python scripts/STEP3_TEST_UPDATES.py"
echo "2. Load initial schemes (optional): psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f scripts/load_initial_schemes.sql"
echo ""

unset PGPASSWORD

