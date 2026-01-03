-- Check family members for Aadhaar 387193279353
-- First, find the citizen with this Aadhaar
SELECT 
    c.id,
    c.full_name,
    c.aadhaar_number,
    c.mobile_number,
    c.date_of_birth,
    c.gender
FROM citizens c
WHERE c.aadhaar_number = '387193279353';

-- Check if there are other citizens with similar family identifiers
-- (This is a placeholder - we need to understand how family relationships are stored)
-- For now, let's check if there are citizens with similar names or addresses that might be family

-- Check for potential family members by address
SELECT 
    c.id,
    c.full_name,
    c.aadhaar_number,
    c.mobile_number,
    c.district,
    c.city,
    c.address_line1
FROM citizens c
WHERE c.aadhaar_number != '387193279353'
  AND (
    c.district = (SELECT district FROM citizens WHERE aadhaar_number = '387193279353')
    OR c.city = (SELECT city FROM citizens WHERE aadhaar_number = '387193279353')
  )
LIMIT 20;

