-- Find potential family members for Aadhaar 387193279353
-- First, get the citizen details
WITH target_citizen AS (
    SELECT 
        id,
        full_name,
        aadhaar_number,
        mobile_number,
        district,
        city,
        address_line1,
        date_of_birth,
        gender
    FROM citizens
    WHERE aadhaar_number = '387193279353'
)
-- Find potential family members (same district/city)
SELECT 
    c.id,
    c.full_name,
    c.aadhaar_number,
    c.mobile_number,
    c.district,
    c.city,
    c.address_line1,
    c.date_of_birth,
    c.gender,
    CASE 
        WHEN c.gender != tc.gender AND 
             ABS(EXTRACT(YEAR FROM AGE(c.date_of_birth)) - EXTRACT(YEAR FROM AGE(tc.date_of_birth))) <= 10
        THEN 'Potential Spouse'
        WHEN c.date_of_birth IS NOT NULL AND tc.date_of_birth IS NOT NULL AND
             EXTRACT(YEAR FROM AGE(c.date_of_birth)) < EXTRACT(YEAR FROM AGE(tc.date_of_birth)) - 15
        THEN 'Potential Child'
        ELSE 'Potential Family Member'
    END as relationship_type
FROM citizens c
CROSS JOIN target_citizen tc
WHERE c.aadhaar_number != '387193279353'
  AND (
    (c.district = tc.district AND c.district IS NOT NULL) OR
    (c.city = tc.city AND c.city IS NOT NULL) OR
    (c.address_line1 = tc.address_line1 AND c.address_line1 IS NOT NULL)
  )
ORDER BY 
    CASE 
        WHEN c.address_line1 = tc.address_line1 THEN 1
        WHEN c.city = tc.city THEN 2
        WHEN c.district = tc.district THEN 3
        ELSE 4
    END,
    c.full_name
LIMIT 20;

