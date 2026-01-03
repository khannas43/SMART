-- Script to create missing family members for seed Aadhaar: 387193279353
-- This creates citizens that don't exist yet so relationships can be established

-- Step 1: Check which ones are missing
SELECT 
    'MISSING - Will Create' AS status,
    expected.aadhaar_number,
    expected.expected_name
FROM (
    VALUES
        ('859689643991', 'Bali Rajput'),
        ('237694608901', 'Babita Rajput'),
        ('875205246823', 'Jugnu Rajput'),
        ('888205246823', 'Savita Gujjar'),
        ('876205246823', 'Chiku Rajput')
) AS expected(aadhaar_number, expected_name)
WHERE expected.aadhaar_number NOT IN (
    SELECT aadhaar_number 
    FROM citizens 
    WHERE aadhaar_number IS NOT NULL 
      AND status = 'ACTIVE'
);

-- Step 2: Get seed citizen's address details to use for family members
SELECT 
    id,
    aadhaar_number,
    full_name,
    address_line1,
    city,
    district,
    state,
    pincode
FROM citizens
WHERE aadhaar_number = '387193279353'
  AND status = 'ACTIVE';

-- Step 3: Insert missing family members
-- Note: Update the address details below based on Step 2 results
INSERT INTO citizens (
    id,
    aadhaar_number,
    full_name,
    mobile_number,
    address_line1,
    city,
    district,
    state,
    pincode,
    status,
    verification_status,
    created_at,
    updated_at
)
SELECT 
    gen_random_uuid() AS id,
    member_data.aadhaar_number,
    member_data.full_name,
    NULL AS mobile_number,  -- Can be updated later
    seed.address_line1,     -- Use seed's address
    seed.city,
    seed.district,
    seed.state,
    seed.pincode,
    'ACTIVE' AS status,
    'PENDING' AS verification_status,
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at
FROM (
    VALUES
        ('859689643991', 'Bali Rajput'),
        ('237694608901', 'Babita Rajput'),
        ('875205246823', 'Jugnu Rajput'),
        ('888205246823', 'Savita Gujjar'),
        ('876205246823', 'Chiku Rajput')
) AS member_data(aadhaar_number, full_name)
CROSS JOIN (
    SELECT 
        address_line1,
        city,
        district,
        state,
        pincode
    FROM citizens
    WHERE aadhaar_number = '387193279353'
      AND status = 'ACTIVE'
    LIMIT 1
) AS seed
WHERE member_data.aadhaar_number NOT IN (
    SELECT aadhaar_number 
    FROM citizens 
    WHERE aadhaar_number IS NOT NULL
)
ON CONFLICT (aadhaar_number) DO NOTHING;

-- Step 4: Verify created citizens
SELECT 
    aadhaar_number,
    full_name,
    address_line1,
    city,
    district,
    status
FROM citizens
WHERE aadhaar_number IN (
    '859689643991',
    '237694608901',
    '875205246823',
    '888205246823',
    '876205246823'
)
ORDER BY aadhaar_number;

