-- Create All SMART Platform Databases
-- Run this FIRST as PostgreSQL superuser (postgres)
-- Then run the schema execution scripts

-- Citizen Portal Database
CREATE DATABASE smart_citizen WITH OWNER = sameer ENCODING = 'UTF8' TEMPLATE = template0;

-- Department Portal Database  
CREATE DATABASE smart_dept WITH OWNER = sameer ENCODING = 'UTF8' TEMPLATE = template0;

-- AIML Portal Database
CREATE DATABASE smart_aiml WITH OWNER = sameer ENCODING = 'UTF8' TEMPLATE = template0;

-- Monitor Portal Database
CREATE DATABASE smart_monitor WITH OWNER = sameer ENCODING = 'UTF8' TEMPLATE = template0;

-- AIML Warehouse Database
CREATE DATABASE smart_warehouse WITH OWNER = sameer ENCODING = 'UTF8' TEMPLATE = template0;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE smart_citizen TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_dept TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_aiml TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_monitor TO sameer;
GRANT ALL PRIVILEGES ON DATABASE smart_warehouse TO sameer;

-- Verify creation
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size 
FROM pg_database 
WHERE datname IN ('smart_citizen', 'smart_dept', 'smart_aiml', 'smart_monitor', 'smart_warehouse')
ORDER BY datname;

