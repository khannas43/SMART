-- Database Cleanup Script for Citizen Service
-- Run this script to clean up the database before running Flyway migrations
-- WARNING: This will delete all data and tables in the public schema

-- Connect to the smart_citizen database first:
-- psql -U sameer -d smart_citizen

-- Drop all tables in the public schema (CASCADE will also drop dependent objects)
DROP SCHEMA public CASCADE;

-- Recreate the public schema
CREATE SCHEMA public;

-- Grant necessary permissions
GRANT ALL ON SCHEMA public TO sameer;
GRANT ALL ON SCHEMA public TO public;

-- Now you can run the Spring Boot application and Flyway will create all tables

