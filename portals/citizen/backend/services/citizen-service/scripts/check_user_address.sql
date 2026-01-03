-- Check the current user's address and find potential family members
-- Replace 'USER_AADHAAR' with the actual Aadhaar number you're testing with

WITH current_user AS (
    SELECT 
        id,
        full_name,
        aadhaar_number,
        address_line1,
        district,
        city,
        date_of_birth,
        gender
    FROM citizens
    WHERE aadhaar_number = '387193279353'  -- Replace with your test Aadhaar
)
SELECT 
    'Current User' as type,
    cu.id,
    cu.full_name,
    cu.aadhaar_number,
    cu.address_line1,
    cu.district,
    cu.city,
    cu.date_of_birth,
    cu.gender,
    EXTRACT(YEAR FROM AGE(cu.date_of_birth)) as age
FROM current_user cu

UNION ALL

SELECT 
    'Potential Family (Same Address)' as type,
    c.id,
    c.full_name,
    c.aadhaar_number,
    c.address_line1,
    c.district,
    c.city,
    c.date_of_birth,
    c.gender,
    EXTRACT(YEAR FROM AGE(c.date_of_birth)) as age
FROM citizens c
CROSS JOIN current_user cu
WHERE c.id != cu.id
  AND c.address_line1 IS NOT NULL
  AND c.address_line1 = cu.address_line1
ORDER BY type, full_name;

