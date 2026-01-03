-- Script to re-transliterate all citizen names using the improved transliteration service
-- This should be run after updating the TransliterationService with new patterns

-- Note: This is a SQL-based transliteration for existing records
-- For new/updated records, the Java TransliterationService will handle it automatically

-- Update citizens with common name patterns
UPDATE citizens 
SET full_name_hindi = CASE
    -- First names
    WHEN LOWER(full_name) LIKE '%shanti%' THEN REPLACE(REPLACE(LOWER(full_name), 'shanti', 'शांति'), 'Shanti', 'शांति')
    WHEN LOWER(full_name) LIKE '%rani%' THEN REPLACE(REPLACE(LOWER(full_name), 'rani', 'रानी'), 'Rani', 'रानी')
    WHEN LOWER(full_name) LIKE '%priya%' THEN REPLACE(REPLACE(LOWER(full_name), 'priya', 'प्रिया'), 'Priya', 'प्रिया')
    WHEN LOWER(full_name) LIKE '%ram%' THEN REPLACE(REPLACE(LOWER(full_name), 'ram', 'राम'), 'Ram', 'राम')
    WHEN LOWER(full_name) LIKE '%krishna%' THEN REPLACE(REPLACE(LOWER(full_name), 'krishna', 'कृष्ण'), 'Krishna', 'कृष्ण')
    -- Surnames
    WHEN LOWER(full_name) LIKE '%thakur%' THEN REPLACE(REPLACE(LOWER(full_name), 'thakur', 'ठाकुर'), 'Thakur', 'ठाकुर')
    WHEN LOWER(full_name) LIKE '%sharma%' THEN REPLACE(REPLACE(LOWER(full_name), 'sharma', 'शर्मा'), 'Sharma', 'शर्मा')
    WHEN LOWER(full_name) LIKE '%kumar%' THEN REPLACE(REPLACE(LOWER(full_name), 'kumar', 'कुमार'), 'Kumar', 'कुमार')
    WHEN LOWER(full_name) LIKE '%singh%' THEN REPLACE(REPLACE(LOWER(full_name), 'singh', 'सिंह'), 'Singh', 'सिंह')
    WHEN LOWER(full_name) LIKE '%patel%' THEN REPLACE(REPLACE(LOWER(full_name), 'patel', 'पटेल'), 'Patel', 'पटेल')
    WHEN LOWER(full_name) LIKE '%devi%' THEN REPLACE(REPLACE(LOWER(full_name), 'devi', 'देवी'), 'Devi', 'देवी')
    WHEN LOWER(full_name) LIKE '%lal%' THEN REPLACE(REPLACE(LOWER(full_name), 'lal', 'लाल'), 'Lal', 'लाल')
    ELSE full_name_hindi  -- Keep existing if no pattern matches
END
WHERE full_name_hindi IS NULL 
   OR full_name_hindi LIKE '%[a-zA-Z]%';  -- Has English characters

-- For names with multiple patterns, we need to handle them separately
-- Example: "Shanti Thakur" needs both "shanti" and "thakur" replaced
UPDATE citizens 
SET full_name_hindi = REPLACE(
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(LOWER(full_name), 'shanti', 'शांति'),
                                    'rani', 'रानी'
                                ),
                                'priya', 'प्रिया'
                            ),
                            'ram', 'राम'
                        ),
                        'thakur', 'ठाकुर'
                    ),
                    'sharma', 'शर्मा'
                ),
                'kumar', 'कुमार'
            ),
            'singh', 'सिंह'
        ),
        'patel', 'पटेल'
    ),
    'devi', 'देवी'
)
WHERE full_name_hindi IS NULL 
   OR (full_name_hindi LIKE '%[a-zA-Z]%' AND LOWER(full_name) LIKE '%shanti%');

-- Verify the updates
SELECT 
    full_name,
    full_name_hindi,
    CASE 
        WHEN full_name_hindi IS NULL THEN '✗ Missing'
        WHEN full_name_hindi ~ '[a-zA-Z]' THEN '⚠ Partially transliterated'
        ELSE '✓ Fully transliterated'
    END AS status
FROM citizens
WHERE LOWER(full_name) LIKE '%shanti%' OR LOWER(full_name) LIKE '%rani%'
ORDER BY full_name
LIMIT 20;

