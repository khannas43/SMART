-- Diagnostic query: Check which Aadhaar numbers exist in the database
SELECT 
    aadhaar_number,
    full_name,
    id,
    status
FROM citizens
WHERE aadhaar_number IN (
    '387193279353',  -- Seed: Sulekha Rajput
    '859689643743',  -- Shyam Rajput (Spouse)
    '859689643991',  -- Bali Rajput (Child)
    '237694608901',  -- Babita Rajput (Child)
    '875205246823',  -- Jugnu Rajput (Child)
    '411886224383',  -- Choteram Gujjar (Family Member)
    '888205246823',  -- Savita Gujjar (Family Member)
    '859548833425',  -- Bholaram Gujjar (Child)
    '876205246823'   -- Chiku Rajput (Family Member)
)
ORDER BY aadhaar_number;

-- Also check which ones are MISSING
SELECT 
    'MISSING' AS status,
    aadhaar_number
FROM (
    VALUES
        ('387193279353'),
        ('859689643743'),
        ('859689643991'),
        ('237694608901'),
        ('875205246823'),
        ('411886224383'),
        ('888205246823'),
        ('859548833425'),
        ('876205246823')
) AS expected(aadhaar_number)
WHERE aadhaar_number NOT IN (
    SELECT aadhaar_number FROM citizens WHERE aadhaar_number IS NOT NULL
);

