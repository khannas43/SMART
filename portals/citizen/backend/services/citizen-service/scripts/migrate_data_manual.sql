-- Manual Data Migration Script
-- Use this if dblink doesn't work or you prefer manual approach
-- This script should be run from smart_citizen database

-- ============================================================
-- OPTION 1: If both databases are on same server
-- Use COPY command to export from warehouse and import to citizen
-- ============================================================

-- Step 1: Export data from smart_warehouse
-- Run these commands from smart_warehouse database:

-- Export citizens
\copy (SELECT citizen_id, aadhaar_number, mobile_number, email, full_name, date_of_birth, gender, city_village, district_id, pincode, status, created_at, updated_at FROM citizens WHERE mobile_number IS NOT NULL) TO 'C:/Projects/SMART/temp/citizens_export.csv' WITH CSV HEADER;

-- Export schemes
\copy (SELECT scheme_id, scheme_code, scheme_name, description, category_id, min_age, max_age, max_income, min_marks, target_caste, bpl_required, farmer_required, house_type_required, benefit_amount, benefit_type, status, created_at, updated_at FROM schemes) TO 'C:/Projects/SMART/temp/schemes_export.csv' WITH CSV HEADER;

-- Export applications
\copy (SELECT app_id, application_number, citizen_id, scheme_id, application_date, application_status, eligibility_score, eligibility_status, eligibility_notes, assigned_to_dept, approval_date, approved_amount, disbursed_amount, documents_verified, documents_count, rejection_reason, created_at, updated_at FROM applications) TO 'C:/Projects/SMART/temp/applications_export.csv' WITH CSV HEADER;

-- ============================================================
-- OPTION 2: Direct SQL with connection string
-- Connect to smart_warehouse and run queries, then insert into smart_citizen
-- ============================================================

-- This approach requires running queries in two separate database connections
-- Use the PowerShell or Bash scripts provided for automated execution

