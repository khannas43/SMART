#!/bin/bash
# Setup Database Schema for Auto Application Submission Post-Consent
# Use Case ID: AI-PLATFORM-05

echo "=================================================================================="
echo "Setting up Application Database Schema"
echo "=================================================================================="

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
DATABASE="${DB_NAME:-smart_warehouse}"
USER="${DB_USER:-sameer}"
SCHEMA_FILE="$(dirname "$0")/../database/application_schema.sql"

echo ""
echo "📋 Configuration:"
echo "   Host: $HOST:$PORT"
echo "   Database: $DATABASE"
echo "   User: $USER"
echo ""

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

echo "📦 Creating application schema and tables..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database schema setup complete!"
    echo ""
    echo "📊 Verifying tables..."
    
    # Count tables
    TABLE_COUNT=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'application';")
    
    echo "   ✅ Found $TABLE_COUNT tables in 'application' schema"
    echo ""
    echo "📋 Key tables:"
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'application' ORDER BY table_name;" | sed 's/^/   /'
    
    echo ""
    echo "Next steps:"
    echo "1. Initialize scheme form schemas: python scripts/init_scheme_form_schemas.py"
    echo "2. Initialize submission modes: python scripts/init_submission_modes_config.py"
    echo "3. Validate configuration: python scripts/check_config.py"
else
    echo ""
    echo "❌ Database schema setup failed!"
    exit 1
fi

echo ""
echo "=================================================================================="
echo "✅ Application schema setup complete!"
echo "=================================================================================="

