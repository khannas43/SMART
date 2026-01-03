-- Create a test citizen profile for testing
-- This profile can be used with Aadhaar number: 123456789012

INSERT INTO citizens (
    id,
    aadhaar_number,
    mobile_number,
    email,
    full_name,
    date_of_birth,
    gender,
    address_line1,
    address_line2,
    city,
    district,
    state,
    pincode,
    status,
    verification_status,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '123456789012',  -- Aadhaar number (use this when logging in)
    '9876543210',    -- Mobile number
    'test.citizen@example.com',
    'Test Citizen',
    '1990-01-15',
    'MALE',
    '123 Test Street',
    'Test Colony',
    'Jaipur',
    'Jaipur',
    'Rajasthan',
    '302001',
    'ACTIVE',
    'PENDING',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (aadhaar_number) DO UPDATE
SET
    mobile_number = EXCLUDED.mobile_number,
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    date_of_birth = EXCLUDED.date_of_birth,
    gender = EXCLUDED.gender,
    address_line1 = EXCLUDED.address_line1,
    address_line2 = EXCLUDED.address_line2,
    city = EXCLUDED.city,
    district = EXCLUDED.district,
    pincode = EXCLUDED.pincode,
    updated_at = CURRENT_TIMESTAMP;

-- Verify the profile was created
SELECT 
    id,
    aadhaar_number,
    mobile_number,
    full_name,
    email,
    status,
    verification_status
FROM citizens
WHERE aadhaar_number = '123456789012';

