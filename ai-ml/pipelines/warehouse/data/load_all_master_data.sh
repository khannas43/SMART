#!/bin/bash
# Load All Master Data into SMART Warehouse
# Run from WSL: bash load_all_master_data.sh

set -e

# Configuration
HOST="${DB_HOST:-172.17.16.1}"
PORT="${DB_PORT:-5432}"
USER="${DB_USER:-sameer}"
PASSWORD="${DB_PASSWORD:-anjali143}"
DATABASE="smart_warehouse"

export PGPASSWORD="$PASSWORD"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "Loading Master Data into SMART Warehouse"
echo "============================================================"
echo ""

# First, create master tables schema
echo "Step 1: Creating master tables schema..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f ../schemas/02_master_tables.sql
echo "✅ Master tables created"
echo ""

# Load master data
echo "Step 2: Loading master data..."
echo ""

echo "  → Loading districts (33)..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 01_insert_districts.sql > /dev/null 2>&1
echo "    ✅ Districts loaded"

echo "  → Loading castes..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 02_insert_castes.sql > /dev/null 2>&1
echo "    ✅ Castes loaded"

echo "  → Loading scheme categories..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 03_insert_scheme_categories.sql > /dev/null 2>&1
echo "    ✅ Scheme categories loaded"

echo "  → Loading education levels..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 04_insert_education_levels.sql > /dev/null 2>&1
echo "    ✅ Education levels loaded"

echo "  → Loading employment types..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 05_insert_employment_types.sql > /dev/null 2>&1
echo "    ✅ Employment types loaded"

echo "  → Loading house types..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 06_insert_house_types.sql > /dev/null 2>&1
echo "    ✅ House types loaded"

echo "  → Loading schemes (12)..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 07_insert_schemes.sql > /dev/null 2>&1
echo "    ✅ Schemes loaded"

echo ""
echo "  → Loading 100K citizens (this may take a few minutes)..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 08_insert_citizens.sql > /dev/null 2>&1
echo "    ✅ Citizens loaded"

echo "  → Loading 50K applications..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -f 09_insert_applications.sql > /dev/null 2>&1
echo "    ✅ Applications loaded"

echo ""
echo "============================================================"
echo "Verification"
echo "============================================================"
echo ""

psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" <<EOF
SELECT 'districts' as table_name, count(*) as count FROM districts
UNION ALL
SELECT 'castes', count(*) FROM castes
UNION ALL
SELECT 'scheme_categories', count(*) FROM scheme_categories
UNION ALL
SELECT 'education_levels', count(*) FROM education_levels
UNION ALL
SELECT 'employment_types', count(*) FROM employment_types
UNION ALL
SELECT 'house_types', count(*) FROM house_types
UNION ALL
SELECT 'schemes', count(*) FROM schemes
UNION ALL
SELECT 'citizens', count(*) FROM citizens
UNION ALL
SELECT 'applications', count(*) FROM applications
ORDER BY table_name;
EOF

echo ""
echo "✅ All master data loaded successfully!"
echo ""

