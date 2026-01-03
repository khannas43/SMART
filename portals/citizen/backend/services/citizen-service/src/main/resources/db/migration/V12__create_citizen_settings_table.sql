-- Citizen settings and preferences
CREATE TABLE citizen_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_id UUID NOT NULL UNIQUE REFERENCES citizens(id) ON DELETE CASCADE,
    
    -- Notification Preferences (JSONB for flexibility)
    notification_preferences JSONB DEFAULT '{
        "applicationStatusUpdates": {"email": true, "sms": true, "push": true, "inApp": true},
        "paymentNotifications": {"email": true, "sms": false, "push": true, "inApp": true},
        "documentVerification": {"email": true, "sms": true, "push": false, "inApp": true},
        "schemeAnnouncements": {"email": false, "sms": false, "push": true, "inApp": true},
        "systemUpdates": {"email": false, "sms": false, "push": false, "inApp": true}
    }'::jsonb,
    
    -- Quiet Hours
    quiet_hours_enabled BOOLEAN DEFAULT false,
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '08:00:00',
    
    -- Opt-Out Schemes (array of scheme IDs)
    opted_out_schemes UUID[] DEFAULT ARRAY[]::UUID[],
    
    -- Account Settings
    language_preference VARCHAR(10) DEFAULT 'en',
    theme_preference VARCHAR(20) DEFAULT 'light',
    
    -- Security Settings
    two_factor_enabled BOOLEAN DEFAULT false,
    session_timeout_minutes INTEGER DEFAULT 30,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_citizen_settings_citizen ON citizen_settings(citizen_id);

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_citizen_settings_updated_at
    BEFORE UPDATE ON citizen_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

