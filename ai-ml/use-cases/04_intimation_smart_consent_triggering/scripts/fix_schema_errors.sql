-- Fix Schema Errors
-- Run this after the main schema script if there were errors

-- Fix user_preferences table if it doesn't exist
CREATE TABLE IF NOT EXISTS intimation.user_preferences (
    preference_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID, -- NULL = family-level preferences
    
    -- Channel Preferences
    preferred_channels TEXT[] NOT NULL DEFAULT ARRAY['sms', 'mobile_app'], -- Ordered by preference
    enabled_channels TEXT[] NOT NULL DEFAULT ARRAY['sms', 'mobile_app', 'web'], -- Which channels enabled
    disabled_channels TEXT[] DEFAULT ARRAY[]::TEXT[], -- Explicitly disabled (FIXED)
    
    -- Language Preferences
    preferred_language VARCHAR(10) DEFAULT 'hi',
    fallback_languages TEXT[] DEFAULT ARRAY['en'],
    
    -- Quiet Hours
    quiet_hours_enabled BOOLEAN DEFAULT true,
    quiet_hours_start TIME DEFAULT '21:00', -- 9 PM
    quiet_hours_end TIME DEFAULT '08:00', -- 8 AM
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    
    -- Frequency Limits
    max_messages_per_month INTEGER DEFAULT 10,
    max_messages_per_week INTEGER DEFAULT 5,
    max_messages_per_day INTEGER DEFAULT 2,
    
    -- Opt-out Flags
    opt_out_all BOOLEAN DEFAULT false,
    opt_out_reason TEXT,
    opt_out_date TIMESTAMP,
    
    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

-- Create indexes for user_preferences
CREATE UNIQUE INDEX IF NOT EXISTS idx_preferences_family ON intimation.user_preferences(family_id) WHERE member_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_preferences_member ON intimation.user_preferences(family_id, member_id) WHERE member_id IS NOT NULL;

-- Create trigger for user_preferences
CREATE TRIGGER update_preferences_updated_at BEFORE UPDATE ON intimation.user_preferences
    FOR EACH ROW EXECUTE FUNCTION intimation.update_updated_at_column();

-- Add comment
COMMENT ON TABLE intimation.user_preferences IS 'User communication preferences and opt-out settings';

