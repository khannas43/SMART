-- QUICK TEST: Populate Hindi data for immediate testing
-- Run this in pgAdmin or your PostgreSQL client
-- This will update a few records so you can see Hindi content immediately

-- ============================================================
-- STEP 1: Update one citizen with Hindi name (for testing)
-- ============================================================
-- Update the first citizen found (you can change the WHERE clause)
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE id = (SELECT id FROM citizens WHERE full_name_hindi IS NULL LIMIT 1);

-- Or update by specific name if you know it:
-- UPDATE citizens 
-- SET full_name_hindi = 'रानी ठाकुर'
-- WHERE full_name = 'Rani Thakur';

-- ============================================================
-- STEP 2: Update one scheme with Hindi name and description
-- ============================================================
-- Update the first scheme found
UPDATE schemes 
SET 
    name_hindi = 'राजस्थान सरकार योजना',
    description_hindi = 'यह योजना राजस्थान के नागरिकों के लिए है। इस योजना के माध्यम से नागरिकों को विभिन्न लाभ प्रदान किए जाते हैं।'
WHERE id = (SELECT id FROM schemes WHERE name_hindi IS NULL LIMIT 1);

-- Or update by specific code if you know it:
-- UPDATE schemes 
-- SET 
--     name_hindi = 'राजस्थान सरकार योजना',
--     description_hindi = 'यह योजना राजस्थान के नागरिकों के लिए है।'
-- WHERE code = 'YOUR_SCHEME_CODE';

-- ============================================================
-- STEP 3: Verify the updates
-- ============================================================
-- Check if Hindi data exists
SELECT 
    'Citizens with Hindi names' AS check_type,
    COUNT(*) AS count
FROM citizens
WHERE full_name_hindi IS NOT NULL

UNION ALL

SELECT 
    'Schemes with Hindi names' AS check_type,
    COUNT(*) AS count
FROM schemes
WHERE name_hindi IS NOT NULL;

-- Show sample data
SELECT 
    aadhaar_number,
    full_name,
    full_name_hindi
FROM citizens
WHERE full_name_hindi IS NOT NULL
LIMIT 5;

SELECT 
    code,
    name,
    name_hindi
FROM schemes
WHERE name_hindi IS NOT NULL
LIMIT 5;

