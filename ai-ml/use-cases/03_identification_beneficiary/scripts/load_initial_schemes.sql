-- Load/Update Initial Scheme Data for Auto-Identification
-- Use Case: AI-PLATFORM-03
-- NOTE: scheme_master is in public schema (shared with AI-PLATFORM-02)
-- This script enables auto-identification for existing schemes

-- First, ensure scheme_master has the required columns
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20);

-- Enable auto-identification for existing schemes
UPDATE scheme_master 
SET is_auto_id_enabled = true,
    scheme_type = CASE 
        WHEN category IN ('SOCIAL_SECURITY', 'LIVELIHOOD') THEN 'CASH'
        WHEN category IN ('HEALTH', 'EDUCATION', 'FOOD') THEN 'NON_CASH'
        ELSE 'CASH'
    END
WHERE scheme_code IN (
    'OLD_AGE_PENSION',
    'DISABILITY_PENSION',
    'NREGA',
    'CHIRANJEEVI',
    'GRAMIN_AWAS',
    'BPL_ASSISTANCE',
    'MAHILA_SHAKTI',
    'SC_ST_SCHOLARSHIP',
    'OBC_SCHOLARSHIP'
);

-- If you need to add new schemes, use:
-- INSERT INTO scheme_master (scheme_code, scheme_name, category, is_auto_id_enabled, scheme_type, status)
-- VALUES ('NEW_SCHEME_CODE', 'New Scheme Name', 'CATEGORY', true, 'CASH', 'active')
-- ON CONFLICT (scheme_code) DO UPDATE SET is_auto_id_enabled = true;

-- Verify
SELECT scheme_id, scheme_code, scheme_name, category, is_auto_id_enabled, scheme_type
FROM scheme_master 
WHERE is_auto_id_enabled = true
ORDER BY scheme_code;

