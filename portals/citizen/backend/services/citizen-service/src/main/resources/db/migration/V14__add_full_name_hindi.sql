-- Add Hindi name field to citizens table
ALTER TABLE citizens 
ADD COLUMN full_name_hindi VARCHAR(255);

COMMENT ON COLUMN citizens.full_name_hindi IS 'Full name in Hindi (Devanagari script)';

