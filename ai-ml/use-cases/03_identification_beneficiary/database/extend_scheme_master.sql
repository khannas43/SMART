-- Extend public.scheme_master with eligibility fields
-- Use Case: AI-PLATFORM-03
-- Database: smart_warehouse
-- Schema: public

-- This script extends the existing scheme_master table (from AI-PLATFORM-02)
-- with eligibility-specific fields needed for Auto Identification

-- ============================================================================
-- STEP 1: Add Eligibility Columns
-- ============================================================================

-- Add is_auto_id_enabled column
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true;

-- Add scheme_type column
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20);

-- ============================================================================
-- STEP 2: Update Existing Schemes
-- ============================================================================

-- Enable auto-identification for all existing schemes by default
UPDATE scheme_master 
SET is_auto_id_enabled = true 
WHERE is_auto_id_enabled IS NULL;

-- Set scheme_type based on category
UPDATE scheme_master 
SET scheme_type = CASE 
    WHEN category IN ('SOCIAL_SECURITY', 'LIVELIHOOD') THEN 'CASH'
    WHEN category IN ('HEALTH', 'EDUCATION', 'FOOD') THEN 'NON_CASH'
    WHEN category = 'HOUSING' THEN 'CASH'
    ELSE 'CASH'
END
WHERE scheme_type IS NULL;

-- ============================================================================
-- STEP 3: Add Comments
-- ============================================================================

COMMENT ON COLUMN scheme_master.is_auto_id_enabled IS 'Whether scheme participates in auto-identification (AI-PLATFORM-03)';
COMMENT ON COLUMN scheme_master.scheme_type IS 'Scheme type: CASH or NON_CASH (AI-PLATFORM-03)';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify columns added
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'scheme_master'
AND column_name IN ('is_auto_id_enabled', 'scheme_type');

-- Verify data updated
SELECT 
    scheme_code, 
    scheme_name, 
    category, 
    is_auto_id_enabled, 
    scheme_type
FROM scheme_master
ORDER BY scheme_code
LIMIT 10;

