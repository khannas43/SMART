-- Migration to transliterate existing records to Hindi
-- This uses a simple transliteration approach for common patterns
-- For production, consider using a proper transliteration library or API

-- ============================================================
-- Transliterate existing citizen names
-- ============================================================
-- Update citizens with common name patterns
UPDATE citizens 
SET full_name_hindi = CASE
    WHEN LOWER(full_name) LIKE '%thakur%' THEN REPLACE(LOWER(full_name), 'thakur', 'ठाकुर')
    WHEN LOWER(full_name) LIKE '%sharma%' THEN REPLACE(LOWER(full_name), 'sharma', 'शर्मा')
    WHEN LOWER(full_name) LIKE '%kumar%' THEN REPLACE(LOWER(full_name), 'kumar', 'कुमार')
    WHEN LOWER(full_name) LIKE '%singh%' THEN REPLACE(LOWER(full_name), 'singh', 'सिंह')
    WHEN LOWER(full_name) LIKE '%patel%' THEN REPLACE(LOWER(full_name), 'patel', 'पटेल')
    WHEN LOWER(full_name) LIKE '%devi%' THEN REPLACE(LOWER(full_name), 'devi', 'देवी')
    WHEN LOWER(full_name) LIKE '%rani%' THEN REPLACE(LOWER(full_name), 'rani', 'रानी')
    WHEN LOWER(full_name) LIKE '%priya%' THEN REPLACE(LOWER(full_name), 'priya', 'प्रिया')
    WHEN LOWER(full_name) LIKE '%ram%' THEN REPLACE(LOWER(full_name), 'ram', 'राम')
    WHEN LOWER(full_name) LIKE '%lal%' THEN REPLACE(LOWER(full_name), 'lal', 'लाल')
    ELSE full_name  -- Keep original if no pattern matches
END
WHERE full_name_hindi IS NULL;

-- ============================================================
-- Transliterate existing scheme names and descriptions
-- ============================================================
-- Update schemes with common patterns
UPDATE schemes 
SET 
    name_hindi = CASE
        WHEN LOWER(name) LIKE '%government%' OR LOWER(name) LIKE '%sarkar%' THEN REPLACE(REPLACE(LOWER(name), 'government', 'सरकार'), 'sarkar', 'सरकार')
        WHEN LOWER(name) LIKE '%scheme%' OR LOWER(name) LIKE '%yojana%' THEN REPLACE(REPLACE(LOWER(name), 'scheme', 'योजना'), 'yojana', 'योजना')
        WHEN LOWER(name) LIKE '%rajasthan%' THEN REPLACE(LOWER(name), 'rajasthan', 'राजस्थान')
        WHEN LOWER(name) LIKE '%education%' OR LOWER(name) LIKE '%shiksha%' THEN REPLACE(REPLACE(LOWER(name), 'education', 'शिक्षा'), 'shiksha', 'शिक्षा')
        WHEN LOWER(name) LIKE '%health%' OR LOWER(name) LIKE '%swasthya%' THEN REPLACE(REPLACE(LOWER(name), 'health', 'स्वास्थ्य'), 'swasthya', 'स्वास्थ्य')
        WHEN LOWER(name) LIKE '%housing%' OR LOWER(name) LIKE '%awas%' THEN REPLACE(REPLACE(LOWER(name), 'housing', 'आवास'), 'awas', 'आवास')
        WHEN LOWER(name) LIKE '%benefit%' OR LOWER(name) LIKE '%labh%' THEN REPLACE(REPLACE(LOWER(name), 'benefit', 'लाभ'), 'labh', 'लाभ')
        ELSE name  -- Keep original if no pattern matches
    END,
    description_hindi = CASE
        WHEN description IS NOT NULL AND LOWER(description) LIKE '%scheme%' THEN REPLACE(LOWER(description), 'scheme', 'योजना')
        WHEN description IS NOT NULL AND LOWER(description) LIKE '%citizen%' THEN REPLACE(LOWER(description), 'citizen', 'नागरिक')
        WHEN description IS NOT NULL AND LOWER(description) LIKE '%rajasthan%' THEN REPLACE(LOWER(description), 'rajasthan', 'राजस्थान')
        ELSE description  -- Keep original if no pattern matches
    END
WHERE name_hindi IS NULL OR description_hindi IS NULL;

-- Note: This is a basic transliteration. For better accuracy, the application
-- will use the TransliterationService which has more comprehensive mappings.

