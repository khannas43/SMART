#!/bin/bash
# Fix permissions on eligibility schema
# Run this as postgres superuser or use sudo

set -e

echo "============================================================"
echo "Fixing Permissions on Eligibility Schema"
echo "============================================================"
echo ""

# Database configuration
DB_HOST="${DB_HOST:-172.17.16.1}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart_warehouse}"
DB_USER="${DB_USER:-postgres}"  # Use postgres user to grant permissions
DB_PASSWORD="${DB_PASSWORD:-postgres}"  # Change this to your postgres password

export PGPASSWORD="$DB_PASSWORD"

PERMISSIONS_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/grant_schema_permissions.sql"

echo "📋 Configuration:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER (superuser)"
echo ""

echo "🔧 Granting permissions on eligibility schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$PERMISSIONS_FILE"

if [ $? -eq 0 ]; then
    echo "   ✅ Permissions granted successfully"
else
    echo "   ❌ Error granting permissions"
    echo "   Try running as postgres user:"
    echo "   psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -f $PERMISSIONS_FILE"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ Permissions fixed!"
echo "============================================================"
echo ""
echo "Next: Run create_eligibility_schema.sh again:"
echo "   ./scripts/create_eligibility_schema.sh"
echo ""

unset PGPASSWORD

