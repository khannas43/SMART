-- Quick fix to update "Rani Thakur" to proper Hindi transliteration
-- This will fix the mixed case issue

UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE LOWER(full_name) LIKE '%rani%thakur%' 
   OR LOWER(full_name) LIKE '%rani%ठाकुर%'
   OR (LOWER(full_name) LIKE '%rani%' AND LOWER(full_name) LIKE '%thakur%');

-- Also update any other records with "rani" that might have similar issues
UPDATE citizens 
SET full_name_hindi = REPLACE(
    REPLACE(LOWER(full_name_hindi), 'rani', 'रानी'),
    'Rani', 'रानी'
)
WHERE full_name_hindi IS NOT NULL 
  AND (full_name_hindi LIKE '%rani%' OR full_name_hindi LIKE '%Rani%');

-- Verify the fix
SELECT 
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi LIKE '%रानी%' THEN '✓ Fixed'
        WHEN full_name_hindi LIKE '%rani%' OR full_name_hindi LIKE '%Rani%' THEN '✗ Still has English'
        ELSE '?'
    END AS status
FROM citizens
WHERE LOWER(full_name) LIKE '%rani%'
LIMIT 10;

