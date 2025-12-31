-- Auto Intimation & Smart Consent Triggering Database Schema
-- Use Case ID: AI-PLATFORM-04
-- Database: smart_warehouse (consolidated with other AI/ML use cases)
-- Schema: intimation

-- Note: This schema is part of smart_warehouse database
-- All AI/ML use cases use the same smart_warehouse database with different schemas for organization

CREATE SCHEMA IF NOT EXISTS intimation;

-- Grant permissions to sameer user
GRANT USAGE ON SCHEMA intimation TO sameer;
GRANT CREATE ON SCHEMA intimation TO sameer;
ALTER SCHEMA intimation OWNER TO sameer;

-- ============================================================================
-- CAMPAIGN MANAGEMENT
-- ============================================================================

-- Intimation Campaigns
-- Groups eligible candidates for batch notification
CREATE TABLE IF NOT EXISTS intimation.campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(255) NOT NULL,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Campaign Configuration
    campaign_type VARCHAR(50) NOT NULL, -- INITIAL, RETRY, ESCALATION, MANUAL
    eligibility_score_threshold DECIMAL(5,4), -- Min score to include
    priority_threshold DECIMAL(5,4), -- High priority threshold
    
    -- Targeting
    target_districts TEXT[], -- NULL = all districts
    target_segments JSONB, -- Vulnerability, under-coverage filters
    max_candidates INTEGER, -- Limit campaign size
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, scheduled, running, paused, completed, cancelled
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Statistics
    total_candidates INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_failed INTEGER DEFAULT 0,
    consents_given INTEGER DEFAULT 0,
    consents_rejected INTEGER DEFAULT 0,
    
    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_scheme ON intimation.campaigns(scheme_code);
CREATE INDEX idx_campaigns_status ON intimation.campaigns(status);
CREATE INDEX idx_campaigns_scheduled ON intimation.campaigns(scheduled_at) WHERE status = 'scheduled';

-- Campaign Candidates
-- Individual family/scheme combinations selected for intimation
CREATE TABLE IF NOT EXISTS intimation.campaign_candidates (
    candidate_id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES intimation.campaigns(campaign_id) ON DELETE CASCADE,
    family_id UUID NOT NULL,
    member_id UUID, -- NULL for family-level schemes
    
    -- Eligibility Context (from AI-PLATFORM-03)
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    eligibility_score DECIMAL(5,4) NOT NULL,
    priority_score DECIMAL(10,4),
    vulnerability_level VARCHAR(20),
    under_coverage_indicator BOOLEAN,
    eligibility_reason TEXT, -- Human-readable reason
    
    -- Contact Information
    primary_mobile VARCHAR(20),
    secondary_mobile VARCHAR(20),
    email VARCHAR(255),
    preferred_language VARCHAR(10) DEFAULT 'hi', -- Language code (hi, en, etc.)
    preferred_channel VARCHAR(50), -- sms, mobile_app, web, whatsapp, email, ivr
    
    -- Intimation Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, failed, skipped, expired
    scheduled_send_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    -- Retry Tracking
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    
    -- Consent Status (linked to consent_records)
    consent_status VARCHAR(50), -- pending, given, rejected, revoked, expired
    consent_id INTEGER, -- FK to consent_records
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidates_campaign ON intimation.campaign_candidates(campaign_id);
CREATE INDEX idx_candidates_family ON intimation.campaign_candidates(family_id);
CREATE INDEX idx_candidates_status ON intimation.campaign_candidates(status);
CREATE INDEX idx_candidates_scheduled ON intimation.campaign_candidates(scheduled_send_at) WHERE status = 'pending';
CREATE INDEX idx_candidates_retry ON intimation.campaign_candidates(next_retry_at) WHERE status IN ('pending', 'failed');

-- ============================================================================
-- MESSAGE LOGS & DELIVERY TRACKING
-- ============================================================================

-- Message Logs
-- Records of all messages sent through various channels
CREATE TABLE IF NOT EXISTS intimation.message_logs (
    message_id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES intimation.campaign_candidates(candidate_id) ON DELETE CASCADE,
    campaign_id INTEGER NOT NULL REFERENCES intimation.campaigns(campaign_id) ON DELETE CASCADE,
    
    -- Message Details
    channel VARCHAR(50) NOT NULL, -- sms, mobile_app, web, whatsapp, email, ivr
    message_type VARCHAR(50) NOT NULL, -- intimation, reminder, consent_request, confirmation
    recipient_type VARCHAR(20) NOT NULL, -- family, member
    
    -- Recipient Information
    recipient_id UUID NOT NULL, -- family_id or member_id
    recipient_mobile VARCHAR(20),
    recipient_email VARCHAR(255),
    recipient_device_id VARCHAR(255), -- For app push notifications
    
    -- Message Content
    message_subject TEXT, -- For email/web
    message_body TEXT NOT NULL, -- Full message content
    message_template_id VARCHAR(100), -- Reference to template used
    message_language VARCHAR(10),
    
    -- Deep Links & Actions
    deep_link_url TEXT, -- For SMS/app
    action_buttons JSONB, -- [{label: "Yes", action: "consent_yes"}, ...]
    short_code_response VARCHAR(10), -- For SMS responses
    
    -- Delivery Status
    status VARCHAR(50) NOT NULL, -- queued, sent, delivered, failed, bounced, unsubscribed
    provider_message_id VARCHAR(255), -- External provider's message ID
    provider_response JSONB, -- Full provider response
    
    -- Timestamps
    queued_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP, -- For app/web
    clicked_at TIMESTAMP, -- When user clicked link/button
    failed_at TIMESTAMP,
    
    -- Error Handling
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_candidate ON intimation.message_logs(candidate_id);
CREATE INDEX idx_messages_campaign ON intimation.message_logs(campaign_id);
CREATE INDEX idx_messages_recipient ON intimation.message_logs(recipient_id);
CREATE INDEX idx_messages_channel ON intimation.message_logs(channel);
CREATE INDEX idx_messages_status ON intimation.message_logs(status);
CREATE INDEX idx_messages_sent_at ON intimation.message_logs(sent_at);

-- ============================================================================
-- CONSENT MANAGEMENT
-- ============================================================================

-- Consent Records
-- Main table for all consent records (soft and strong)
CREATE TABLE IF NOT EXISTS intimation.consent_records (
    consent_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID, -- NULL for family-level schemes
    
    -- Scheme & Context
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES intimation.campaigns(campaign_id) ON DELETE SET NULL,
    candidate_id INTEGER REFERENCES intimation.campaign_candidates(candidate_id) ON DELETE SET NULL,
    
    -- Consent Type & Level
    consent_type VARCHAR(20) NOT NULL, -- soft, strong
    level_of_assurance VARCHAR(20) NOT NULL, -- LOA1 (soft), LOA2 (OTP), LOA3 (e-sign)
    consent_purpose VARCHAR(100) NOT NULL, -- enrollment, data_sharing, notification
    
    -- Consent Status
    status VARCHAR(50) NOT NULL, -- given, rejected, revoked, expired, pending
    consent_value BOOLEAN, -- true = given, false = rejected, NULL = pending/revoked
    
    -- Consent Details
    consent_method VARCHAR(50), -- click, tap, otp, e_sign, offline, field_worker
    consent_channel VARCHAR(50), -- sms, mobile_app, web, whatsapp, ivr, offline
    consent_device_id VARCHAR(255), -- Device identifier for audit
    consent_ip_address INET, -- IP address for audit
    consent_session_id VARCHAR(255), -- Session identifier
    
    -- Strong Consent Specific (OTP/e-sign)
    otp_verified BOOLEAN DEFAULT false,
    otp_verified_at TIMESTAMP,
    e_sign_provider VARCHAR(50), -- jan_aadhaar, digilocker, etc.
    e_sign_transaction_id VARCHAR(255),
    e_sign_verified_at TIMESTAMP,
    
    -- Terms & Conditions
    terms_version VARCHAR(50) NOT NULL, -- Version of terms accepted
    terms_accepted_at TIMESTAMP,
    terms_url TEXT, -- Link to terms document
    
    -- Data Usage Disclosure
    data_usage_disclosure JSONB, -- What data will be shared
    scheme_description TEXT, -- Human-readable scheme description shown
    benefit_description TEXT, -- Expected benefits shown
    
    -- Validity
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP, -- NULL = no expiration, or expiration date
    expired_at TIMESTAMP,
    
    -- Revocation
    revoked_at TIMESTAMP,
    revocation_reason TEXT,
    revoked_by VARCHAR(255), -- user, admin, system, expired
    
    -- Audit Trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) -- User/system identifier
);

CREATE INDEX idx_consent_family ON intimation.consent_records(family_id);
CREATE INDEX idx_consent_scheme ON intimation.consent_records(scheme_code);
CREATE INDEX idx_consent_status ON intimation.consent_records(status);
CREATE INDEX idx_consent_validity ON intimation.consent_records(valid_from, valid_until) WHERE status = 'given';
CREATE INDEX idx_consent_type ON intimation.consent_records(consent_type);

-- Consent History (Audit Trail)
-- Immutable log of all consent changes for compliance
CREATE TABLE IF NOT EXISTS intimation.consent_history (
    history_id SERIAL PRIMARY KEY,
    consent_id INTEGER NOT NULL REFERENCES intimation.consent_records(consent_id) ON DELETE CASCADE,
    
    -- Change Details
    action VARCHAR(50) NOT NULL, -- created, updated, revoked, expired, renewed
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    old_consent_value BOOLEAN,
    new_consent_value BOOLEAN,
    
    -- Change Context
    changed_by VARCHAR(255),
    changed_via VARCHAR(50), -- api, portal, admin, system
    change_reason TEXT,
    
    -- Audit Metadata
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    device_id VARCHAR(255),
    session_id VARCHAR(255),
    
    -- Change Details JSON
    change_details JSONB -- Full snapshot of change
);

CREATE INDEX idx_consent_history_consent ON intimation.consent_history(consent_id);
CREATE INDEX idx_consent_history_action ON intimation.consent_history(action);
CREATE INDEX idx_consent_history_changed_at ON intimation.consent_history(changed_at);

-- ============================================================================
-- USER PREFERENCES & FATIGUE MANAGEMENT
-- ============================================================================

-- User Communication Preferences
-- Stores user preferences for channels, language, quiet hours, etc.
CREATE TABLE IF NOT EXISTS intimation.user_preferences (
    preference_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID, -- NULL = family-level preferences
    
    -- Channel Preferences
    preferred_channels TEXT[] NOT NULL DEFAULT ARRAY['sms', 'mobile_app'], -- Ordered by preference
    enabled_channels TEXT[] NOT NULL DEFAULT ARRAY['sms', 'mobile_app', 'web'], -- Which channels enabled
    disabled_channels TEXT[] DEFAULT ARRAY[]::TEXT[], -- Explicitly disabled
    
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

CREATE UNIQUE INDEX idx_preferences_family ON intimation.user_preferences(family_id) WHERE member_id IS NULL;
CREATE UNIQUE INDEX idx_preferences_member ON intimation.user_preferences(family_id, member_id) WHERE member_id IS NOT NULL;

-- Message Fatigue Tracking
-- Tracks message counts to enforce fatigue limits
CREATE TABLE IF NOT EXISTS intimation.message_fatigue (
    fatigue_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID,
    
    -- Time Period
    period_type VARCHAR(20) NOT NULL, -- day, week, month
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Message Counts
    total_messages INTEGER DEFAULT 0,
    messages_by_channel JSONB, -- {sms: 3, mobile_app: 2, ...}
    messages_by_scheme JSONB, -- {CHIRANJEEVI: 2, OLD_AGE_PENSION: 1, ...}
    
    -- Fatigue Status
    fatigue_threshold_exceeded BOOLEAN DEFAULT false,
    last_message_at TIMESTAMP,
    
    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fatigue_family ON intimation.message_fatigue(family_id);
CREATE INDEX idx_fatigue_period ON intimation.message_fatigue(period_type, period_start, period_end);

-- ============================================================================
-- CAMPAIGN POLICIES & CONFIGURATION
-- ============================================================================

-- Scheme Intimation Configuration
-- Per-scheme configuration for intimation and consent
CREATE TABLE IF NOT EXISTS intimation.scheme_intimation_config (
    config_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL UNIQUE REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Intimation Settings
    auto_intimation_enabled BOOLEAN DEFAULT true,
    min_eligibility_score DECIMAL(5,4) DEFAULT 0.6,
    priority_threshold DECIMAL(5,4) DEFAULT 0.8,
    
    -- Consent Requirements
    consent_type_required VARCHAR(20) NOT NULL DEFAULT 'soft', -- soft, strong
    require_otp BOOLEAN DEFAULT false,
    require_e_sign BOOLEAN DEFAULT false,
    consent_validity_days INTEGER DEFAULT 365,
    
    -- Channel Configuration
    allowed_channels TEXT[] DEFAULT ARRAY['sms', 'mobile_app', 'web'],
    preferred_channels TEXT[] DEFAULT ARRAY['mobile_app', 'sms'],
    
    -- Message Limits
    max_intimations_per_family INTEGER DEFAULT 3,
    retry_enabled BOOLEAN DEFAULT true,
    retry_schedule_days INTEGER[] DEFAULT ARRAY[1, 7, 30],
    max_retries INTEGER DEFAULT 3,
    
    -- Legal & Compliance
    legal_constraints JSONB, -- Any legal/regulatory constraints
    requires_aadhaar_auth BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

CREATE INDEX idx_scheme_config_enabled ON intimation.scheme_intimation_config(auto_intimation_enabled) WHERE auto_intimation_enabled = true;

-- ============================================================================
-- MESSAGE TEMPLATES
-- ============================================================================

-- Message Templates
-- Templates for different message types and channels
CREATE TABLE IF NOT EXISTS intimation.message_templates (
    template_id SERIAL PRIMARY KEY,
    template_code VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    
    -- Template Configuration
    message_type VARCHAR(50) NOT NULL, -- intimation, reminder, consent_request, confirmation
    channel VARCHAR(50) NOT NULL, -- sms, mobile_app, web, whatsapp, email, ivr
    language VARCHAR(10) NOT NULL DEFAULT 'hi',
    
    -- Template Content
    subject_template TEXT, -- For email/web
    body_template TEXT NOT NULL, -- Jinja2 template
    variables_required JSONB, -- List of required variables
    
    -- Actions & Links
    default_action_buttons JSONB, -- Default action buttons
    deep_link_template TEXT, -- Template for deep link
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, draft
    version INTEGER DEFAULT 1,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

CREATE INDEX idx_templates_code ON intimation.message_templates(template_code);
CREATE INDEX idx_templates_type_channel ON intimation.message_templates(message_type, channel, language);

-- ============================================================================
-- EVENT LOGGING
-- ============================================================================

-- Intimation Events
-- Event log for intimation lifecycle events
CREATE TABLE IF NOT EXISTS intimation.intimation_events (
    event_id SERIAL PRIMARY KEY,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- INTIMATION_SENT, CONSENT_GIVEN, CONSENT_REJECTED, etc.
    event_category VARCHAR(50) NOT NULL, -- intimation, consent, campaign, system
    
    -- Entity References
    campaign_id INTEGER REFERENCES intimation.campaigns(campaign_id) ON DELETE SET NULL,
    candidate_id INTEGER REFERENCES intimation.campaign_candidates(candidate_id) ON DELETE SET NULL,
    consent_id INTEGER REFERENCES intimation.consent_records(consent_id) ON DELETE SET NULL,
    message_id INTEGER REFERENCES intimation.message_logs(message_id) ON DELETE SET NULL,
    
    -- Entity Identifiers
    family_id UUID,
    member_id UUID,
    scheme_code VARCHAR(50),
    
    -- Event Data
    event_data JSONB, -- Additional event-specific data
    event_metadata JSONB, -- System metadata
    
    -- Timestamp
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Source
    source_system VARCHAR(50) DEFAULT 'intimation_service',
    source_user VARCHAR(255)
);

CREATE INDEX idx_events_type ON intimation.intimation_events(event_type);
CREATE INDEX idx_events_family ON intimation.intimation_events(family_id);
CREATE INDEX idx_events_scheme ON intimation.intimation_events(scheme_code);
CREATE INDEX idx_events_timestamp ON intimation.intimation_events(event_timestamp);
CREATE INDEX idx_events_campaign ON intimation.intimation_events(campaign_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION intimation.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers for updated_at
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON intimation.campaigns
    FOR EACH ROW EXECUTE FUNCTION intimation.update_updated_at_column();

CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON intimation.campaign_candidates
    FOR EACH ROW EXECUTE FUNCTION intimation.update_updated_at_column();

CREATE TRIGGER update_consent_updated_at BEFORE UPDATE ON intimation.consent_records
    FOR EACH ROW EXECUTE FUNCTION intimation.update_updated_at_column();

CREATE TRIGGER update_preferences_updated_at BEFORE UPDATE ON intimation.user_preferences
    FOR EACH ROW EXECUTE FUNCTION intimation.update_updated_at_column();

-- Function to log consent history
CREATE OR REPLACE FUNCTION intimation.log_consent_history()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO intimation.consent_history (
            consent_id, action, old_status, new_status, old_consent_value, new_consent_value,
            changed_by, changed_via, changed_at, change_details
        )
        VALUES (
            NEW.consent_id,
            CASE 
                WHEN OLD.status != NEW.status THEN 'status_changed'
                WHEN OLD.consent_value != NEW.consent_value THEN 'value_changed'
                ELSE 'updated'
            END,
            OLD.status,
            NEW.status,
            OLD.consent_value,
            NEW.consent_value,
            NEW.updated_by,
            'system',
            CURRENT_TIMESTAMP,
            jsonb_build_object(
                'old_record', row_to_json(OLD),
                'new_record', row_to_json(NEW)
            )
        );
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO intimation.consent_history (
            consent_id, action, new_status, new_consent_value,
            changed_by, changed_via, changed_at, change_details
        )
        VALUES (
            NEW.consent_id,
            'created',
            NEW.status,
            NEW.consent_value,
            NEW.created_by,
            'system',
            CURRENT_TIMESTAMP,
            jsonb_build_object('new_record', row_to_json(NEW))
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for consent history logging
CREATE TRIGGER log_consent_history_trigger
    AFTER INSERT OR UPDATE ON intimation.consent_records
    FOR EACH ROW EXECUTE FUNCTION intimation.log_consent_history();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON SCHEMA intimation IS 'Auto Intimation & Smart Consent Triggering (AI-PLATFORM-04)';
COMMENT ON TABLE intimation.campaigns IS 'Intimation campaigns grouping eligible candidates for batch notification';
COMMENT ON TABLE intimation.campaign_candidates IS 'Individual candidates selected for intimation within campaigns';
COMMENT ON TABLE intimation.message_logs IS 'Logs of all messages sent through various channels';
COMMENT ON TABLE intimation.consent_records IS 'Main table for all consent records (soft and strong)';
COMMENT ON TABLE intimation.consent_history IS 'Immutable audit trail of all consent changes';
COMMENT ON TABLE intimation.user_preferences IS 'User communication preferences and opt-out settings';
COMMENT ON TABLE intimation.message_fatigue IS 'Message fatigue tracking to enforce frequency limits';
COMMENT ON TABLE intimation.scheme_intimation_config IS 'Per-scheme configuration for intimation and consent';
COMMENT ON TABLE intimation.message_templates IS 'Message templates for different channels and languages';
COMMENT ON TABLE intimation.intimation_events IS 'Event log for intimation lifecycle events';

