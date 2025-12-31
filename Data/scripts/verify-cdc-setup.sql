-- Verification script for CDC setup
-- Run this to verify Debezium CDC is properly configured

-- ============================================================
-- Check WAL Level
-- ============================================================
SELECT 
    name,
    setting,
    unit,
    context,
    CASE 
        WHEN setting = 'logical' THEN '✅ OK'
        ELSE '❌ ERROR: Must be "logical"'
    END as status
FROM pg_settings 
WHERE name = 'wal_level';

-- ============================================================
-- Check Replication Slots
-- ============================================================
SELECT 
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    CASE 
        WHEN active THEN '✅ Active'
        ELSE '⚠️  Inactive'
    END as status
FROM pg_replication_slots;

-- ============================================================
-- Check WAL Senders
-- ============================================================
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    sync_state,
    CASE 
        WHEN state = 'streaming' THEN '✅ Streaming'
        ELSE '⚠️  ' || state
    END as status
FROM pg_stat_replication;

-- ============================================================
-- Check Debezium User Permissions
-- ============================================================
SELECT 
    usename,
    usecreatedb,
    usesuper,
    userepl,
    CASE 
        WHEN userepl = true THEN '✅ Replication enabled'
        ELSE '❌ Replication NOT enabled'
    END as replication_status
FROM pg_user 
WHERE usename = 'debezium_user';

-- ============================================================
-- Check Table Access for Debezium User
-- ============================================================
SELECT 
    schemaname,
    tablename,
    hasinsert,
    hasselect,
    hasupdate,
    hasdelete,
    CASE 
        WHEN hasselect = true THEN '✅ Read access'
        ELSE '❌ No read access'
    END as read_access_status
FROM pg_tables t
JOIN (
    SELECT 
        table_schema,
        table_name,
        has_table_privilege('debezium_user', table_schema || '.' || table_name, 'SELECT') as hasselect,
        has_table_privilege('debezium_user', table_schema || '.' || table_name, 'INSERT') as hasinsert,
        has_table_privilege('debezium_user', table_schema || '.' || table_name, 'UPDATE') as hasupdate,
        has_table_privilege('debezium_user', table_schema || '.' || table_name, 'DELETE') as hasdelete
    FROM information_schema.tables
    WHERE table_schema IN ('public', 'eligibility')
) p ON t.schemaname = p.table_schema AND t.tablename = p.table_name
ORDER BY schemaname, tablename;

