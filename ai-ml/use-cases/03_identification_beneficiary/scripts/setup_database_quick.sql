-- Quick Database Setup for Auto Identification of Beneficiaries
-- Run this in pgAdmin4 or psql

-- Step 1: Verify database exists
-- Note: smart_warehouse should already exist from AI-PLATFORM-02 setup
-- If not: CREATE DATABASE smart_warehouse;

-- Step 2: Connect to smart_warehouse database
-- Then run: \i /mnt/c/Projects/SMART/ai-ml/use-cases/03_identification_beneficiary/database/eligibility_schema.sql

-- Or run this script after connecting to smart_warehouse:

-- Create schema
CREATE SCHEMA IF NOT EXISTS eligibility;

-- Verify schema created
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'eligibility';

