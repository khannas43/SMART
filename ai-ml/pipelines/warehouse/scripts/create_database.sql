-- Create AIML Data Warehouse Database
-- Run this as PostgreSQL superuser

-- Create database
CREATE DATABASE smart_warehouse
    WITH 
    OWNER = sameer
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_warehouse TO sameer;

-- Connect to the new database
\c smart_warehouse

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO sameer;
GRANT ALL ON SCHEMA staging TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON TABLES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON SEQUENCES TO sameer;

-- Run schema creation
\i ../schemas/01_warehouse_schema.sql

