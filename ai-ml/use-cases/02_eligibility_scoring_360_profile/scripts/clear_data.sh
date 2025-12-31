#!/bin/bash
# Clear all data from tables (for fresh start)

export PGPASSWORD='anjali143'

echo "Clearing all data from smart_warehouse tables..."

psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse << EOF
-- Disable foreign key checks temporarily
SET session_replication_role = replica;

-- Truncate tables (ignore if they don't exist)
DO \$\$
BEGIN
    -- Core tables (in dependency order)
    TRUNCATE TABLE IF EXISTS analytics_flags CASCADE;
    TRUNCATE TABLE IF EXISTS analytics_benefit_summary CASCADE;
    TRUNCATE TABLE IF EXISTS profile_360 CASCADE;
    TRUNCATE TABLE IF EXISTS consent_flags CASCADE;
    TRUNCATE TABLE IF EXISTS data_quality_flags CASCADE;
    TRUNCATE TABLE IF EXISTS socio_economic_facts CASCADE;
    TRUNCATE TABLE IF EXISTS application_events CASCADE;
    TRUNCATE TABLE IF EXISTS benefit_events CASCADE;
    TRUNCATE TABLE IF EXISTS gr_relationships CASCADE;
    TRUNCATE TABLE IF EXISTS golden_records CASCADE;
    
    RAISE NOTICE 'All tables truncated successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
END \$\$;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Verify
SELECT 
    'golden_records' as table_name, COUNT(*) as count FROM golden_records
UNION ALL SELECT 'gr_relationships', COUNT(*) FROM gr_relationships
UNION ALL SELECT 'benefit_events', COUNT(*) FROM benefit_events
UNION ALL SELECT 'application_events', COUNT(*) FROM application_events
UNION ALL SELECT 'socio_economic_facts', COUNT(*) FROM socio_economic_facts
UNION ALL SELECT 'consent_flags', COUNT(*) FROM consent_flags
UNION ALL SELECT 'profile_360', COUNT(*) FROM profile_360
UNION ALL SELECT 'analytics_flags', COUNT(*) FROM analytics_flags;
EOF

echo "✅ Data cleared!"

