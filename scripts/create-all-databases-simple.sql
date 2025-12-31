-- Simple script to create all SMART Platform databases
-- Run this as PostgreSQL superuser (postgres)
-- This script only creates databases - run schema files separately

-- Citizen Portal Database
CREATE DATABASE smart_citizen
    WITH OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Department Portal Database
CREATE DATABASE smart_dept
    WITH OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- AIML Portal Database
CREATE DATABASE smart_aiml
    WITH OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Monitor Portal Database
CREATE DATABASE smart_monitor
    WITH OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- AIML Data Warehouse Database
CREATE DATABASE smart_warehouse
    WITH OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_citizen TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_dept TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_aiml TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_monitor TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_warehouse TO sameer;

-- Display created databases
SELECT datname, datowner, encoding 
FROM pg_database 
WHERE datname IN ('smart_citizen', 'smart_dept', 'smart_aiml', 'smart_monitor', 'smart_warehouse')
ORDER BY datname;

