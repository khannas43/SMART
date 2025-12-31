#!/bin/bash
# Fix Schema Errors Script
# Run this if schema creation had errors

echo "=================================================================================="
echo "Fixing Schema Errors"
echo "=================================================================================="

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
DATABASE="${DB_NAME:-smart_warehouse}"
USER="${DB_USER:-sameer}"
FIX_FILE="$(dirname "$0")/fix_schema_errors.sql"

echo ""
echo "📋 Configuration:"
echo "   Host: $HOST:$PORT"
echo "   Database: $DATABASE"
echo "   User: $USER"
echo ""

# Run fix script
echo "🔧 Fixing schema errors..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f "$FIX_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Schema errors fixed!"
    echo ""
    echo "Next: Run verification: python scripts/verify_database_setup.py"
else
    echo ""
    echo "❌ Fix failed!"
    exit 1
fi

