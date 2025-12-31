#!/bin/bash
# Setup Database Schema for Auto Intimation & Smart Consent Triggering
# Use Case ID: AI-PLATFORM-04

echo "=================================================================================="
echo "Setting up Intimation Database Schema"
echo "=================================================================================="

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
DATABASE="${DB_NAME:-smart_warehouse}"
USER="${DB_USER:-sameer}"
SCHEMA_FILE="$(dirname "$0")/../database/intimation_schema.sql"

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

echo "📦 Creating intimation schema and tables..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database schema setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Initialize message templates: python scripts/init_message_templates.py"
    echo "2. Validate configuration: python scripts/check_config.py"
    echo "3. Run intake test: python scripts/test_intake.py"
else
    echo ""
    echo "❌ Database schema setup failed!"
    exit 1
fi

