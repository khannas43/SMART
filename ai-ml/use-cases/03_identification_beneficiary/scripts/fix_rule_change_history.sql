-- Fix rule_change_history table: Change scheme_id to scheme_code
-- Run this in pgAdmin4 or psql if the table already exists with old schema

-- Step 1: Drop the old column if it exists and add new one
DO $$
BEGIN
    -- Check if scheme_id column exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'eligibility' 
        AND table_name = 'rule_change_history' 
        AND column_name = 'scheme_id'
    ) THEN
        -- Drop the old column (cascade to constraints)
        ALTER TABLE eligibility.rule_change_history DROP COLUMN IF EXISTS scheme_id CASCADE;
        
        -- Add the new scheme_code column
        ALTER TABLE eligibility.rule_change_history 
        ADD COLUMN IF NOT EXISTS scheme_code VARCHAR(50);
        
        -- Add foreign key constraint
        ALTER TABLE eligibility.rule_change_history
        ADD CONSTRAINT rule_change_history_scheme_code_fkey
        FOREIGN KEY (scheme_code) REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE;
        
        -- Create index
        CREATE INDEX IF NOT EXISTS idx_rule_change_history_scheme_code 
        ON eligibility.rule_change_history(scheme_code);
        
        RAISE NOTICE '✅ Updated rule_change_history: scheme_id -> scheme_code';
    ELSE
        RAISE NOTICE '✅ rule_change_history already has scheme_code column';
    END IF;
END $$;

-- Verify the change
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'eligibility' 
    AND table_name = 'rule_change_history'
    AND column_name IN ('scheme_id', 'scheme_code')
ORDER BY column_name;

