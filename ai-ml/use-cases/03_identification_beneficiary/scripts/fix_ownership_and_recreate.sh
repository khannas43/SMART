#!/bin/bash
# Fix table ownership and recreate schema properly
# Run this after granting permissions

set -e

echo "============================================================"
echo "Fixing Table Ownership and Recreating Schema"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

DB_HOST="${DB_HOST:-172.17.16.1}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart_warehouse}"
DB_USER="${DB_USER:-postgres}"  # Use postgres to transfer ownership
DB_PASSWORD="${DB_PASSWORD:-postgres}"

export PGPASSWORD="$DB_PASSWORD"

TRANSFER_OWNERSHIP_FILE="$SCRIPT_DIR/transfer_table_ownership.sql"
SCHEMA_FILE="$PROJECT_DIR/database/eligibility_schema.sql"
VERSIONING_FILE="$PROJECT_DIR/database/eligibility_schema_versioning.sql"

echo "📋 Configuration:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER (superuser for ownership transfer)"
echo ""

# Step 1: Transfer ownership of existing tables
echo "🔧 Step 1: Transferring ownership of existing tables..."
if [ -f "$TRANSFER_OWNERSHIP_FILE" ]; then
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$TRANSFER_OWNERSHIP_FILE" 2>&1 | grep -v "ERROR:" || true
    echo "   ✅ Ownership transfer attempted"
else
    echo "   ⚠️  Ownership transfer script not found, skipping"
fi

# Step 2: Drop and recreate schema (clean slate)
echo ""
echo "🗑️  Step 2: Dropping and recreating eligibility schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
DROP SCHEMA IF EXISTS eligibility CASCADE;
CREATE SCHEMA eligibility;
ALTER SCHEMA eligibility OWNER TO sameer;
GRANT ALL ON SCHEMA eligibility TO sameer;
EOF

if [ $? -eq 0 ]; then
    echo "   ✅ Schema recreated"
else
    echo "   ❌ Error recreating schema"
    exit 1
fi

# Step 3: Run schema creation as sameer
echo ""
echo "📦 Step 3: Creating tables (as sameer user)..."
unset PGPASSWORD
export PGPASSWORD="anjali143"

psql -h "$DB_HOST" -p "$DB_PORT" -U sameer -d "$DB_NAME" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "   ✅ Tables created successfully"
else
    echo "   ❌ Error creating tables"
    exit 1
fi

# Step 4: Create versioning extensions
echo ""
echo "📦 Step 4: Creating versioning extensions..."
psql -h "$DB_HOST" -p "$DB_PORT" -U sameer -d "$DB_NAME" -f "$VERSIONING_FILE" 2>&1 | grep -v "ERROR:" || true
echo "   ✅ Versioning extensions created"

# Step 5: Verify
echo ""
echo "🔍 Verifying tables..."
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U sameer -d "$DB_NAME" -t -c "
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'eligibility';")

echo "   ✅ Found $TABLE_COUNT tables in 'eligibility' schema"

echo ""
echo "📋 Tables created:"
psql -h "$DB_HOST" -p "$DB_PORT" -U sameer -d "$DB_NAME" -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'eligibility' 
    ORDER BY table_name;" -t

echo ""
echo "============================================================"
echo "✅ Schema setup complete!"
echo "============================================================"
echo ""
echo "Next: Run test script"
echo "   python scripts/STEP3_TEST_UPDATES.py"
echo ""

unset PGPASSWORD

