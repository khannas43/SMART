-- Fix "Shanti Thakur" transliteration
-- Run this to update the existing record

UPDATE citizens 
SET full_name_hindi = 'शांति ठाकुर'
WHERE LOWER(full_name) LIKE '%shanti%thakur%' 
   OR (LOWER(full_name) LIKE '%shanti%' AND LOWER(full_name) LIKE '%thakur%');

-- Also fix any other records with "Shanti"
UPDATE citizens 
SET full_name_hindi = REPLACE(
    REPLACE(
        REPLACE(LOWER(full_name), 'shanti', 'शांति'),
        'Shanti', 'शांति'
    ),
    'thakur', 'ठाकुर'
)
WHERE LOWER(full_name) LIKE '%shanti%'
  AND (full_name_hindi IS NULL OR full_name_hindi LIKE '%[a-zA-Z]%');

-- Verify the fix
SELECT 
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi = 'शांति ठाकुर' THEN '✓ Correct'
        WHEN full_name_hindi LIKE '%शांति%' AND full_name_hindi LIKE '%ठाकुर%' THEN '✓ Has both'
        WHEN full_name_hindi LIKE '%[a-zA-Z]%' THEN '⚠ Still has English'
        WHEN full_name_hindi IS NULL THEN '✗ Missing'
        ELSE '?'
    END AS status
FROM citizens
WHERE LOWER(full_name) LIKE '%shanti%'
ORDER BY full_name;

