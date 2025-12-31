-- Create Debezium replication user for CDC
-- Run this script on both smart_warehouse and smart_citizen databases

-- ============================================================
-- For smart_warehouse database
-- ============================================================
\c smart_warehouse

-- Create user
CREATE USER IF NOT EXISTS debezium_user WITH REPLICATION PASSWORD 'CHANGE_ME_SECURE_PASSWORD';

-- Grant database access
GRANT CONNECT ON DATABASE smart_warehouse TO debezium_user;

-- Grant schema access
GRANT USAGE ON SCHEMA public TO debezium_user;
GRANT USAGE ON SCHEMA eligibility TO debezium_user;

-- Grant table read access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA eligibility TO debezium_user;

-- Grant access to future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT SELECT ON TABLES TO debezium_user;

-- Verify
SELECT usename, usecreatedb, usesuper, userepl 
FROM pg_user 
WHERE usename = 'debezium_user';

-- ============================================================
-- For smart_citizen database
-- ============================================================
\c smart_citizen

-- Create user
CREATE USER IF NOT EXISTS debezium_user WITH REPLICATION PASSWORD 'CHANGE_ME_SECURE_PASSWORD';

-- Grant database access
GRANT CONNECT ON DATABASE smart_citizen TO debezium_user;

-- Grant schema access
GRANT USAGE ON SCHEMA public TO debezium_user;

-- Grant table read access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;

-- Grant access to future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium_user;

-- Verify
SELECT usename, usecreatedb, usesuper, userepl 
FROM pg_user 
WHERE usename = 'debezium_user';

-- ============================================================
-- Notes:
-- 1. Change 'CHANGE_ME_SECURE_PASSWORD' to a secure password
-- 2. Store password securely (use password manager)
-- 3. Update connector configuration files with the password
-- ============================================================

