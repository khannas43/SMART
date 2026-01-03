-- Add Hindi fields to schemes table for multilingual support
ALTER TABLE schemes 
ADD COLUMN name_hindi VARCHAR(255),
ADD COLUMN description_hindi TEXT;

COMMENT ON COLUMN schemes.name_hindi IS 'Scheme name in Hindi (Devanagari script)';
COMMENT ON COLUMN schemes.description_hindi IS 'Scheme description in Hindi (Devanagari script)';

