-- Migration Script: Copy data from smart_warehouse to smart_citizen
-- This script migrates citizens, schemes, and applications data
-- Run this script after the warehouse data is populated
-- 
-- Prerequisites:
-- 1. smart_warehouse database must have data populated
-- 2. smart_citizen database must have all tables created (via Flyway migrations)
-- 3. Both databases must be accessible from the same PostgreSQL instance
-- 4. dblink extension must be enabled (for cross-database access)
--
-- IMPORTANT: This script uses dblink to access smart_warehouse database
-- If both are in the same database with different schemas, modify the queries
--
-- Usage:
-- Option 1: Via Flyway (automatic on next startup) - connects to smart_citizen DB
-- Option 2: Manual execution via psql:
--   psql -h localhost -U sameer -d smart_citizen -f V11__migrate_data_from_warehouse.sql
-- Option 3: Execute via pgAdmin4 Query Tool (connect to smart_citizen database)
--
-- Enable dblink extension for cross-database access
CREATE EXTENSION IF NOT EXISTS dblink;

-- ============================================================
-- STEP 1: Create temporary mapping tables for ID translation
-- ============================================================

-- Map warehouse citizen_id (BIGINT) to smart_citizen UUID
-- Using dblink to access smart_warehouse database
CREATE TEMP TABLE IF NOT EXISTS citizen_id_mapping AS
SELECT 
    c.citizen_id AS warehouse_id,
    gen_random_uuid() AS new_uuid
FROM dblink(
    'host=localhost port=5432 dbname=smart_warehouse user=sameer password=anjali143',
    'SELECT citizen_id FROM citizens ORDER BY citizen_id'
) AS c(citizen_id BIGINT)
ORDER BY c.citizen_id;

-- Map warehouse scheme_id (INTEGER) to smart_citizen UUID  
CREATE TEMP TABLE IF NOT EXISTS scheme_id_mapping AS
SELECT 
    s.scheme_id AS warehouse_id,
    gen_random_uuid() AS new_uuid
FROM dblink(
    'host=localhost port=5432 dbname=smart_warehouse user=sameer password=anjali143',
    'SELECT scheme_id FROM schemes ORDER BY scheme_id'
) AS s(scheme_id INTEGER)
ORDER BY s.scheme_id;

-- ============================================================
-- STEP 2: Migrate Citizens
-- ============================================================

INSERT INTO citizens (
    id,
    aadhaar_number,
    mobile_number,
    email,
    full_name,
    date_of_birth,
    gender,
    address_line1,
    city,
    district,
    state,
    pincode,
    status,
    verification_status,
    created_at,
    updated_at
)
SELECT 
    cim.new_uuid AS id,
    c.aadhaar_number,
    c.mobile_number,
    c.email,
    -- Handle NULL full_name: Use Aadhaar last 4 digits or mobile number as fallback
    COALESCE(
        c.full_name, 
        'Citizen ' || RIGHT(c.aadhaar_number, 4),
        'Citizen ' || c.mobile_number,
        'Unknown Citizen'
    ) AS full_name,
    c.date_of_birth,
    CASE 
        WHEN c.gender = 'Male' THEN 'MALE'
        WHEN c.gender = 'Female' THEN 'FEMALE'
        ELSE 'OTHER'
    END AS gender,
    COALESCE(c.city_village, '') AS address_line1,
    c.city_village AS city,
    COALESCE(c.district_name, 'Unknown') AS district,
    'Rajasthan' AS state,
    c.pincode,
    CASE 
        WHEN c.status = 'active' THEN 'ACTIVE'
        WHEN c.status = 'inactive' THEN 'INACTIVE'
        ELSE 'ACTIVE'
    END AS status,
    'PENDING' AS verification_status,
    c.created_at,
    c.updated_at
FROM dblink(
    'host=localhost port=5432 dbname=smart_warehouse user=sameer password=anjali143',
    'SELECT c.citizen_id, c.aadhaar_number, c.mobile_number, c.email, c.full_name, 
            c.date_of_birth, c.gender, c.city_village, c.district_id, c.pincode, 
            c.status, c.created_at, c.updated_at,
            d.district_name
     FROM citizens c
     LEFT JOIN districts d ON c.district_id = d.district_id
     WHERE c.mobile_number IS NOT NULL'
) AS c(citizen_id BIGINT, aadhaar_number VARCHAR(12), mobile_number VARCHAR(10), 
       email VARCHAR(255), full_name VARCHAR(300), date_of_birth DATE, 
       gender VARCHAR(10), city_village VARCHAR(100), district_id INTEGER, 
       pincode VARCHAR(6), status VARCHAR(20), created_at TIMESTAMP, 
       updated_at TIMESTAMP, district_name VARCHAR(100))
INNER JOIN citizen_id_mapping cim ON c.citizen_id = cim.warehouse_id
WHERE c.mobile_number IS NOT NULL  -- Only migrate citizens with mobile numbers
ON CONFLICT (aadhaar_number) DO NOTHING;  -- Skip duplicates

-- ============================================================
-- STEP 3: Migrate Schemes
-- ============================================================

INSERT INTO schemes (
    id,
    code,
    name,
    description,
    category,
    department,
    eligibility_criteria,
    start_date,
    end_date,
    status,
    created_at,
    updated_at
)
SELECT 
    sim.new_uuid AS id,
    s.scheme_code AS code,
    s.scheme_name AS name,
    COALESCE(s.description, '') AS description,
    COALESCE(s.category_name, 'General') AS category,
    'Government of Rajasthan' AS department,  -- Default department
    -- Build eligibility criteria JSON from warehouse data
    jsonb_build_object(
        'min_age', s.min_age,
        'max_age', s.max_age,
        'income_max', s.max_income,
        'min_marks', s.min_marks,
        'target_caste', s.target_caste,
        'bpl_required', COALESCE(s.bpl_required, false),
        'farmer_required', COALESCE(s.farmer_required, false),
        'house_type_required', s.house_type_required,
        'benefit_amount', s.benefit_amount,
        'benefit_type', s.benefit_type
    ) AS eligibility_criteria,
    NULL AS start_date,  -- Not available in warehouse
    NULL AS end_date,    -- Not available in warehouse
    CASE 
        WHEN s.status = 'active' THEN 'ACTIVE'
        WHEN s.status = 'inactive' THEN 'INACTIVE'
        WHEN s.status = 'suspended' THEN 'INACTIVE'
        ELSE 'ACTIVE'
    END AS status,
    s.created_at,
    s.updated_at
FROM dblink(
    'host=localhost port=5432 dbname=smart_warehouse user=sameer password=anjali143',
    'SELECT s.scheme_id, s.scheme_code, s.scheme_name, s.description, s.category_id,
            s.min_age, s.max_age, s.max_income, s.min_marks, s.target_caste,
            s.bpl_required, s.farmer_required, s.house_type_required,
            s.benefit_amount, s.benefit_type, s.status, s.created_at, s.updated_at,
            sc.category_name
     FROM schemes s
     LEFT JOIN scheme_categories sc ON s.category_id = sc.category_id'
) AS s(scheme_id INTEGER, scheme_code VARCHAR(50), scheme_name VARCHAR(200), 
       description TEXT, category_id INTEGER, min_age INTEGER, max_age INTEGER,
       max_income DECIMAL(12,2), min_marks DECIMAL(5,2), target_caste VARCHAR(10),
       bpl_required BOOLEAN, farmer_required BOOLEAN, house_type_required INTEGER,
       benefit_amount DECIMAL(12,2), benefit_type VARCHAR(50), status VARCHAR(20),
       created_at TIMESTAMP, updated_at TIMESTAMP, category_name VARCHAR(100))
INNER JOIN scheme_id_mapping sim ON s.scheme_id = sim.warehouse_id
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    department = EXCLUDED.department,
    eligibility_criteria = EXCLUDED.eligibility_criteria,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at;

-- ============================================================
-- STEP 4: Migrate Applications
-- ============================================================

INSERT INTO service_applications (
    id,
    application_number,
    citizen_id,
    scheme_id,
    service_type,
    application_type,
    subject,
    description,
    priority,
    status,
    current_stage,
    submission_date,
    assigned_to_dept,
    expected_completion_date,
    application_data,
    created_at,
    updated_at
)
SELECT 
    gen_random_uuid() AS id,
    a.application_number,
    cim.new_uuid AS citizen_id,
    sim.new_uuid AS scheme_id,
    COALESCE(a.scheme_name, 'Government Scheme') AS service_type,
    'SCHEME_APPLICATION' AS application_type,
    'Application for ' || COALESCE(a.scheme_name, 'Government Scheme') AS subject,
    COALESCE(a.eligibility_notes, '') AS description,
    CASE 
        WHEN a.application_status IN ('approved', 'disbursed') THEN 'HIGH'
        WHEN a.application_status = 'rejected' THEN 'LOW'
        ELSE 'NORMAL'
    END AS priority,
    CASE 
        WHEN a.application_status = 'pending' THEN 'SUBMITTED'
        WHEN a.application_status = 'under_review' THEN 'UNDER_REVIEW'
        WHEN a.application_status = 'approved' THEN 'APPROVED'
        WHEN a.application_status = 'rejected' THEN 'REJECTED'
        WHEN a.application_status = 'disbursed' THEN 'COMPLETED'
        WHEN a.application_status = 'closed' THEN 'COMPLETED'
        ELSE 'SUBMITTED'
    END AS status,
    a.application_status AS current_stage,
    a.application_date::timestamp AS submission_date,
    'Government of Rajasthan' AS assigned_to_dept,  -- Default department
    a.approval_date AS expected_completion_date,
    jsonb_build_object(
        'eligibility_score', a.eligibility_score,
        'eligibility_status', a.eligibility_status,
        'approved_amount', a.approved_amount,
        'disbursed_amount', a.disbursed_amount,
        'documents_verified', a.documents_verified,
        'documents_count', a.documents_count,
        'rejection_reason', a.rejection_reason
    ) AS application_data,
    a.created_at,
    a.updated_at
FROM dblink(
    'host=localhost port=5432 dbname=smart_warehouse user=sameer password=anjali143',
    'SELECT a.app_id, a.application_number, a.citizen_id, a.scheme_id, 
            a.application_date, a.application_status, a.eligibility_score,
            a.eligibility_status, a.eligibility_notes, a.assigned_to_dept,
            a.approval_date, a.approved_amount, a.disbursed_amount,
            a.documents_verified, a.documents_count, a.rejection_reason,
            a.created_at, a.updated_at,
            s.scheme_name
     FROM applications a
     LEFT JOIN schemes s ON a.scheme_id = s.scheme_id'
) AS a(app_id BIGINT, application_number VARCHAR(50), citizen_id BIGINT, 
       scheme_id INTEGER, application_date DATE, application_status VARCHAR(50),
       eligibility_score DECIMAL(5,2), eligibility_status VARCHAR(20),
       eligibility_notes TEXT, assigned_to_dept INTEGER, approval_date DATE,
       approved_amount DECIMAL(12,2), disbursed_amount DECIMAL(12,2),
       documents_verified BOOLEAN, documents_count INTEGER, rejection_reason TEXT,
       created_at TIMESTAMP, updated_at TIMESTAMP, scheme_name VARCHAR(200))
INNER JOIN citizen_id_mapping cim ON a.citizen_id = cim.warehouse_id
INNER JOIN scheme_id_mapping sim ON a.scheme_id = sim.warehouse_id
ON CONFLICT (application_number) DO UPDATE SET
    status = EXCLUDED.status,
    current_stage = EXCLUDED.current_stage,
    updated_at = EXCLUDED.updated_at;

-- ============================================================
-- STEP 5: Migrate Application Status History
-- ============================================================

-- Create status history entries for migrated applications
INSERT INTO application_status_history (
    id,
    application_id,
    from_status,
    to_status,
    stage,
    comments,
    changed_at,
    changed_by_type
)
SELECT 
    gen_random_uuid() AS id,
    sa.id AS application_id,
    NULL AS from_status,
    sa.status AS to_status,
    sa.current_stage AS stage,
    CASE 
        WHEN sa.status = 'REJECTED' THEN 
            COALESCE((sa.application_data->>'rejection_reason')::text, 'Application rejected')
        WHEN sa.status = 'APPROVED' THEN 'Application approved'
        WHEN sa.status = 'COMPLETED' THEN 'Application completed and disbursed'
        ELSE 'Application submitted'
    END AS comments,
    COALESCE(sa.submission_date, sa.created_at) AS changed_at,
    'system' AS changed_by_type
FROM service_applications sa
WHERE sa.submission_date IS NOT NULL OR sa.created_at IS NOT NULL;

-- Add status change entry if status was updated
INSERT INTO application_status_history (
    id,
    application_id,
    from_status,
    to_status,
    stage,
    comments,
    changed_at,
    changed_by_type
)
SELECT 
    gen_random_uuid() AS id,
    sa.id AS application_id,
    'SUBMITTED' AS from_status,
    sa.status AS to_status,
    sa.current_stage AS stage,
    'Status updated during migration' AS comments,
    sa.updated_at AS changed_at,
    'system' AS changed_by_type
FROM service_applications sa
WHERE sa.updated_at > COALESCE(sa.submission_date, sa.created_at)
  AND sa.status != 'SUBMITTED'
ON CONFLICT DO NOTHING;

-- ============================================================
-- STEP 6: Cleanup temporary tables
-- ============================================================

DROP TABLE IF EXISTS citizen_id_mapping;
DROP TABLE IF EXISTS scheme_id_mapping;

-- ============================================================
-- STEP 7: Display Migration Summary
-- ============================================================

DO $$
DECLARE
    v_citizens_count INTEGER;
    v_schemes_count INTEGER;
    v_applications_count INTEGER;
    v_history_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_citizens_count FROM citizens;
    SELECT COUNT(*) INTO v_schemes_count FROM schemes;
    SELECT COUNT(*) INTO v_applications_count FROM service_applications;
    SELECT COUNT(*) INTO v_history_count FROM application_status_history;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration Summary';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Citizens migrated: %', v_citizens_count;
    RAISE NOTICE 'Schemes migrated: %', v_schemes_count;
    RAISE NOTICE 'Applications migrated: %', v_applications_count;
    RAISE NOTICE 'Status history entries: %', v_history_count;
    RAISE NOTICE '========================================';
END $$;

