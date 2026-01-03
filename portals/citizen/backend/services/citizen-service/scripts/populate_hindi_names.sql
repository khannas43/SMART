-- Script to populate Hindi names for citizens
-- This is a template - you'll need to update the names based on your actual data

-- Example: Update specific citizens with Hindi names
-- Replace the English names and Aadhaar numbers with actual values from your database

-- Method 1: Update by Aadhaar number (recommended)
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE aadhaar_number = '123456789012';  -- Replace with actual Aadhaar number

-- Method 2: Update by full name (if unique)
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE full_name = 'Rani Thakur';

-- Method 3: Bulk update using a mapping table (if you have a mapping)
-- First, create a temporary mapping table:
/*
CREATE TEMP TABLE name_mapping (
    english_name VARCHAR(255),
    hindi_name VARCHAR(255)
);

-- Insert mappings
INSERT INTO name_mapping VALUES
    ('Rani Thakur', 'रानी ठाकुर'),
    ('John Doe', 'जॉन डो'),
    -- Add more mappings as needed
;

-- Update citizens using the mapping
UPDATE citizens c
SET full_name_hindi = nm.hindi_name
FROM name_mapping nm
WHERE c.full_name = nm.english_name
  AND c.full_name_hindi IS NULL;
*/

-- Method 4: Get list of citizens without Hindi names for manual update
SELECT 
    id,
    aadhaar_number,
    full_name,
    mobile_number
FROM citizens
WHERE full_name_hindi IS NULL
ORDER BY full_name
LIMIT 100;

-- Method 5: Update all citizens with a transliteration pattern (basic example)
-- Note: This is a simple example and may not be accurate for all names
-- For production, use a proper transliteration library or manual mapping
/*
UPDATE citizens
SET full_name_hindi = full_name  -- This is just a placeholder
WHERE full_name_hindi IS NULL;
*/

-- Verify updates
SELECT 
    aadhaar_number,
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi IS NOT NULL THEN 'Has Hindi name'
        ELSE 'Missing Hindi name'
    END AS status
FROM citizens
ORDER BY full_name
LIMIT 50;

