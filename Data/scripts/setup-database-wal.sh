#!/bin/bash

# Setup PostgreSQL WAL for Change Data Capture (CDC)
# This script enables logical replication on PostgreSQL databases

set -e

echo "========================================="
echo "PostgreSQL WAL Setup for CDC"
echo "========================================="

DB_HOST="${DB_HOST:-172.17.16.1}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"

# Databases to configure
DATABASES=("smart_warehouse" "smart_citizen")

for DB_NAME in "${DATABASES[@]}"; do
    echo ""
    echo "Configuring $DB_NAME..."
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Display current settings
SELECT name, setting, unit, context 
FROM pg_settings 
WHERE name IN ('wal_level', 'max_replication_slots', 'max_wal_senders');

EOF

    echo "✅ Configuration updated for $DB_NAME"
    echo "⚠️  PostgreSQL restart required for changes to take effect"
done

echo ""
echo "========================================="
echo "Next Steps:"
echo "1. Restart PostgreSQL server"
echo "2. Run: SELECT name, setting FROM pg_settings WHERE name = 'wal_level';"
echo "3. Verify it returns 'logical'"
echo "========================================="

