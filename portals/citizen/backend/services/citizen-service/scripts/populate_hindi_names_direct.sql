-- Direct SQL script to populate Hindi names for schemes
-- This uses a simple transliteration approach
-- Note: For better results, use the Java TransliterationService via the API endpoint

-- First, check which schemes are missing Hindi names
SELECT 
    id,
    code,
    name,
    name_hindi,
    description,
    description_hindi
FROM schemes
WHERE name_hindi IS NULL OR name_hindi = ''
ORDER BY name;

-- Update schemes with basic transliteration patterns
-- This is a simple approach - for production, use the TransliterationService
UPDATE schemes
SET 
    name_hindi = CASE
        WHEN name_hindi IS NULL OR name_hindi = '' THEN
            -- Basic transliteration patterns
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                LOWER(name),
                'government', 'सरकार'),
                'scheme', 'योजना'),
                'rajasthan', 'राजस्थान'),
                'welfare', 'कल्याण'),
                'education', 'शिक्षा'),
                'health', 'स्वास्थ्य'),
                'financial', 'वित्तीय'),
                'aid', 'सहायता'),
                'benefit', 'लाभ'),
                'support', 'समर्थन')
        ELSE name_hindi
    END,
    description_hindi = CASE
        WHEN (description_hindi IS NULL OR description_hindi = '') AND description IS NOT NULL THEN
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                LOWER(description),
                'government', 'सरकार'),
                'scheme', 'योजना'),
                'rajasthan', 'राजस्थान'),
                'welfare', 'कल्याण'),
                'education', 'शिक्षा'),
                'health', 'स्वास्थ्य'),
                'financial', 'वित्तीय'),
                'aid', 'सहायता'),
                'benefit', 'लाभ'),
                'support', 'समर्थन')
        ELSE description_hindi
    END
WHERE name_hindi IS NULL OR name_hindi = '';

-- Verify the update
SELECT 
    code,
    name,
    name_hindi,
    CASE 
        WHEN name_hindi IS NULL OR name_hindi = '' THEN 'Missing'
        ELSE 'Present'
    END as hindi_status
FROM schemes
ORDER BY name;

