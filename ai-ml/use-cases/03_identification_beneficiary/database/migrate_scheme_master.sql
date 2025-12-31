-- Migration Script: Consolidate scheme_master tables
-- Use Case: AI-PLATFORM-03
-- Purpose: Use single scheme_master in public schema, remove duplicate

-- ============================================================================
-- STEP 1: Extend public.scheme_master with eligibility fields
-- ============================================================================

-- Add eligibility-specific columns to existing scheme_master
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20); -- CASH, NON_CASH

-- Update existing schemes to enable auto-identification by default
UPDATE scheme_master 
SET is_auto_id_enabled = true 
WHERE is_auto_id_enabled IS NULL;

-- Set scheme_type based on category (if not set)
UPDATE scheme_master 
SET scheme_type = CASE 
    WHEN category IN ('SOCIAL_SECURITY', 'LIVELIHOOD') THEN 'CASH'
    WHEN category IN ('HEALTH', 'EDUCATION', 'FOOD') THEN 'NON_CASH'
    ELSE 'CASH'
END
WHERE scheme_type IS NULL;

-- ============================================================================
-- STEP 2: Update eligibility tables to use scheme_code instead of scheme_id
-- ============================================================================

-- Add scheme_code column to eligibility tables (if not exists)
ALTER TABLE eligibility.scheme_eligibility_rules
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

ALTER TABLE eligibility.scheme_exclusion_rules
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

ALTER TABLE eligibility.eligibility_snapshots
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

ALTER TABLE eligibility.candidate_lists
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

ALTER TABLE eligibility.ml_model_registry
ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);

-- Populate scheme_code from scheme_id (if scheme_id exists)
-- Note: This assumes scheme_id in eligibility tables maps to scheme_code
-- You may need to adjust this based on your data

-- ============================================================================
-- STEP 3: Add foreign key constraints
-- ============================================================================

-- Add foreign keys to public.scheme_master
ALTER TABLE eligibility.scheme_eligibility_rules
ADD CONSTRAINT fk_scheme_code_rules 
FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE;

ALTER TABLE eligibility.scheme_exclusion_rules
ADD CONSTRAINT fk_scheme_code_exclusions 
FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE;

ALTER TABLE eligibility.eligibility_snapshots
ADD CONSTRAINT fk_scheme_code_snapshots 
FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE;

ALTER TABLE eligibility.candidate_lists
ADD CONSTRAINT fk_scheme_code_candidates 
FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE;

ALTER TABLE eligibility.ml_model_registry
ADD CONSTRAINT fk_scheme_code_models 
FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE;

-- ============================================================================
-- STEP 4: Drop duplicate eligibility.scheme_master (if exists)
-- ============================================================================

-- WARNING: Only run this after migrating all data!
-- DROP TABLE IF EXISTS eligibility.scheme_master CASCADE;

-- ============================================================================
-- STEP 5: Create helper view for convenience
-- ============================================================================

-- View that combines scheme_master with eligibility flags
CREATE OR REPLACE VIEW eligibility.scheme_master_view AS
SELECT 
    sm.scheme_id,
    sm.scheme_code,
    sm.scheme_name,
    sm.category,
    sm.scheme_type,
    sm.is_auto_id_enabled,
    sm.min_age,
    sm.max_age,
    sm.max_income,
    sm.target_caste,
    sm.bpl_required,
    sm.farmer_required,
    sm.status,
    sm.created_at,
    sm.updated_at
FROM scheme_master sm
WHERE sm.is_auto_id_enabled = true;

COMMENT ON VIEW eligibility.scheme_master_view IS 'View of scheme_master with auto-identification enabled schemes';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify scheme_master has new columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'scheme_master'
AND column_name IN ('is_auto_id_enabled', 'scheme_type');

-- Verify eligibility tables have scheme_code
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'eligibility' 
AND column_name = 'scheme_code'
ORDER BY table_name;

