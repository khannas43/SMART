-- Script to populate Hindi names and descriptions for schemes
-- Update scheme names and descriptions in Hindi

-- Method 1: Update specific schemes by code
UPDATE schemes 
SET 
    name_hindi = 'राजस्थान सरकार योजना',  -- Replace with actual Hindi name
    description_hindi = 'यह योजना नागरिकों के लिए है...'  -- Replace with actual Hindi description
WHERE code = 'SCHEME_CODE_001';  -- Replace with actual scheme code

-- Method 2: Update all schemes with a pattern (if you have a mapping)
-- Create a temporary mapping table:
/*
CREATE TEMP TABLE scheme_mapping (
    scheme_code VARCHAR(50),
    name_hindi VARCHAR(255),
    description_hindi TEXT
);

-- Insert mappings
INSERT INTO scheme_mapping VALUES
    ('SCHEME_CODE_001', 'राजस्थान सरकार योजना', 'यह योजना...'),
    ('SCHEME_CODE_002', 'शिक्षा योजना', 'शिक्षा के लिए...'),
    -- Add more mappings as needed
;

-- Update schemes using the mapping
UPDATE schemes s
SET 
    name_hindi = sm.name_hindi,
    description_hindi = sm.description_hindi
FROM scheme_mapping sm
WHERE s.code = sm.scheme_code
  AND (s.name_hindi IS NULL OR s.description_hindi IS NULL);
*/

-- Method 3: Get list of schemes without Hindi names for manual update
SELECT 
    id,
    code,
    name,
    description,
    category,
    department
FROM schemes
WHERE name_hindi IS NULL OR description_hindi IS NULL
ORDER BY name
LIMIT 100;

-- Method 4: Update schemes by category (if you have category-wise translations)
/*
UPDATE schemes
SET 
    name_hindi = name || ' (हिंदी)',  -- Placeholder - replace with actual translations
    description_hindi = description || ' (हिंदी)'  -- Placeholder
WHERE category = 'EDUCATION'
  AND (name_hindi IS NULL OR description_hindi IS NULL);
*/

-- Verify updates
SELECT 
    code,
    name,
    name_hindi,
    CASE 
        WHEN name_hindi IS NOT NULL THEN 'Has Hindi name'
        ELSE 'Missing Hindi name'
    END AS name_status,
    CASE 
        WHEN description_hindi IS NOT NULL THEN 'Has Hindi description'
        ELSE 'Missing Hindi description'
    END AS description_status
FROM schemes
ORDER BY name
LIMIT 50;

