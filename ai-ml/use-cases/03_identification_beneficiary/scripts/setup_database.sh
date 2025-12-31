#!/bin/bash
# Setup Database Schema for Auto Identification of Beneficiaries
# Use Case: AI-PLATFORM-03

set -e

echo "================================================================================
Database Setup: Auto Identification of Beneficiaries
================================================================================
"

# Database configuration (from db_config.yaml or env)
# Note: Using smart_warehouse database (consolidated with AI-PLATFORM-02)
DB_HOST="${DB_HOST:-172.17.16.1}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart_warehouse}"  # Consolidated database
DB_USER="${DB_USER:-sameer}"
DB_PASSWORD="${DB_PASSWORD:-anjali143}"

export PGPASSWORD="$DB_PASSWORD"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCHEMA_FILE="$PROJECT_DIR/database/eligibility_schema.sql"
VERSIONING_FILE="$PROJECT_DIR/database/eligibility_schema_versioning.sql"

echo "📋 Configuration:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Check if database exists
echo "🔍 Checking if database exists..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "   ✅ Database '$DB_NAME' exists (shared with AI-PLATFORM-02)"
else
    echo "   ⚠️  Database '$DB_NAME' does not exist. Creating..."
    echo "   Note: This database is shared with eligibility_scoring_360_profile use case"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
    echo "   ✅ Database created"
fi

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "   ❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Create schema
echo ""
echo "📦 Creating schema and tables..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "   ✅ Base schema created successfully"
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
echo "================================================================================
✅ Database setup complete!
================================================================================
"
echo "Next steps:"
echo "1. Insert scheme master data (see database/load_initial_data.sql or scripts/)"
echo "2. Configure scheme rules"
echo "3. Train models: python src/train_eligibility_model.py --scheme_id SCHEME_001"
echo ""

unset PGPASSWORD

