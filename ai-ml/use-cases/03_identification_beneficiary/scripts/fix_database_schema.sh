#!/bin/bash
# Fix Database Schema Issues
# Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries

set -e

echo "================================================================================
Fixing Database Schema Issues
================================================================================"

# Database connection details
DB_HOST="172.17.16.1"
DB_PORT="5432"
DB_NAME="smart_warehouse"
DB_USER="sameer"
DB_PASSWORD="anjali143"

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

echo ""
echo "📋 Configuration:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🔧 Fixing rule_change_history table..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -f "$SCRIPT_DIR/fix_rule_change_history.sql"

echo ""
echo "✅ Database schema fixes complete!"
echo ""
echo "Next steps:"
echo "1. Run: python scripts/load_sample_rules.py"
echo "2. Run: python scripts/test_train_models.py --scheme-code CHIRANJEEVI"

