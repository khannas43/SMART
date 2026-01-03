-- Script to populate sample Hindi data for testing
-- This will add Hindi names/descriptions for a few records to test the localization

-- ============================================================
-- 1. Update a few citizens with Hindi names (for testing)
-- ============================================================
-- Get the first few citizens and update them with sample Hindi names
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE full_name = 'Rani Thakur'
   OR full_name LIKE 'Rani%'
LIMIT 1;

-- Update more citizens (you can customize these based on your actual data)
UPDATE citizens 
SET full_name_hindi = 'राम कुमार'
WHERE full_name LIKE '%Ram%' OR full_name LIKE '%Kumar%'
LIMIT 5;

UPDATE citizens 
SET full_name_hindi = 'प्रिया शर्मा'
WHERE full_name LIKE '%Priya%' OR full_name LIKE '%Sharma%'
LIMIT 5;

-- ============================================================
-- 2. Update schemes with Hindi names and descriptions
-- ============================================================
-- Update a few schemes with sample Hindi content
UPDATE schemes 
SET 
    name_hindi = 'राजस्थान सरकार योजना',
    description_hindi = 'यह योजना राजस्थान के नागरिकों के लिए है। इस योजना के माध्यम से नागरिकों को विभिन्न लाभ प्रदान किए जाते हैं।'
WHERE code LIKE '%EDU%' OR category = 'EDUCATION'
LIMIT 3;

UPDATE schemes 
SET 
    name_hindi = 'स्वास्थ्य योजना',
    description_hindi = 'यह स्वास्थ्य संबंधी योजना है जो नागरिकों को चिकित्सा सुविधाएं प्रदान करती है।'
WHERE code LIKE '%HEALTH%' OR category = 'HEALTH'
LIMIT 3;

UPDATE schemes 
SET 
    name_hindi = 'आवास योजना',
    description_hindi = 'इस योजना के तहत नागरिकों को आवास सुविधाएं प्रदान की जाती हैं।'
WHERE code LIKE '%HOUSING%' OR category = 'HOUSING'
LIMIT 3;

-- Generic update for any remaining schemes (if you want to add a placeholder)
-- UPDATE schemes 
-- SET 
--     name_hindi = name || ' (हिंदी)',
--     description_hindi = COALESCE(description, '') || ' (हिंदी में विवरण)'
-- WHERE name_hindi IS NULL
-- LIMIT 10;

-- ============================================================
-- 3. Verify the updates
-- ============================================================
-- Check citizens with Hindi names
SELECT 
    aadhaar_number,
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi IS NOT NULL THEN '✓ Has Hindi name'
        ELSE '✗ Missing Hindi name'
    END AS status
FROM citizens
WHERE full_name_hindi IS NOT NULL
ORDER BY full_name
LIMIT 10;

-- Check schemes with Hindi names
SELECT 
    code,
    name,
    name_hindi,
    CASE 
        WHEN name_hindi IS NOT NULL THEN '✓ Has Hindi name'
        ELSE '✗ Missing Hindi name'
    END AS name_status,
    CASE 
        WHEN description_hindi IS NOT NULL THEN '✓ Has Hindi description'
        ELSE '✗ Missing Hindi description'
    END AS description_status
FROM schemes
WHERE name_hindi IS NOT NULL OR description_hindi IS NOT NULL
ORDER BY name
LIMIT 10;

