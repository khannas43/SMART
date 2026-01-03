-- Fix "Sherni Thakur" transliteration
-- This will be automatically handled by ICU4J going forward, but this fixes existing records

UPDATE citizens 
SET full_name_hindi = 'शेरनी ठाकुर'
WHERE LOWER(full_name) LIKE '%sherni%thakur%' 
   OR (LOWER(full_name) LIKE '%sherni%' AND LOWER(full_name) LIKE '%thakur%');

-- Verify the fix
SELECT 
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi LIKE '%शेरनी%' AND full_name_hindi LIKE '%ठाकुर%' THEN '✓ Correct'
        WHEN full_name_hindi LIKE '%[a-zA-Z]%' THEN '⚠ Still has English'
        WHEN full_name_hindi IS NULL THEN '✗ Missing'
        ELSE '?'
    END AS status
FROM citizens
WHERE LOWER(full_name) LIKE '%sherni%'
ORDER BY full_name;

