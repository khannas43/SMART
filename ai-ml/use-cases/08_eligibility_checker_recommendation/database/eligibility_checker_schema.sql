-- ============================================================================
-- Eligibility Checker & Recommendations Schema
-- Use Case ID: AI-PLATFORM-08
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS eligibility_checker;
GRANT USAGE ON SCHEMA eligibility_checker TO sameer;
ALTER SCHEMA eligibility_checker OWNER TO sameer;

SET search_path TO eligibility_checker;

-- Eligibility check records
CREATE TABLE IF NOT EXISTS eligibility_checks (
    check_id SERIAL PRIMARY KEY,
    
    -- User identification
    family_id UUID,  -- For logged-in users
    beneficiary_id VARCHAR(255),  -- Optional, for specific beneficiary
    session_id VARCHAR(255) NOT NULL,  -- Session ID for guest users
    user_type VARCHAR(20) NOT NULL,  -- 'LOGGED_IN', 'GUEST', 'ANONYMOUS'
    
    -- Check context
    check_type VARCHAR(50) NOT NULL,  -- 'FULL_CHECK', 'SCHEME_SPECIFIC', 'QUICK_CHECK'
    check_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_mode VARCHAR(50),  -- 'WEB', 'MOBILE_APP', 'CHATBOT', 'ASSISTED'
    
    -- Input data (for guest/anonymous checks)
    questionnaire_responses JSONB,  -- Guest user answers
    input_context JSONB,  -- Additional context (location, preferences, etc.)
    
    -- Results summary
    total_schemes_checked INTEGER DEFAULT 0,
    eligible_count INTEGER DEFAULT 0,
    possible_eligible_count INTEGER DEFAULT 0,
    not_eligible_count INTEGER DEFAULT 0,
    
    -- Processing metadata
    processing_time_ms INTEGER,  -- Time taken to process check
    data_sources_used TEXT[],  -- Which data sources were used
    eligibility_engine_version VARCHAR(50),
    
    -- Privacy and consent
    consent_given BOOLEAN DEFAULT FALSE,
    data_retention_until DATE,
    
    metadata JSONB
);

CREATE INDEX idx_eligibility_checks_family_id ON eligibility_checks(family_id) WHERE family_id IS NOT NULL;
CREATE INDEX idx_eligibility_checks_session_id ON eligibility_checks(session_id);
CREATE INDEX idx_eligibility_checks_user_type ON eligibility_checks(user_type);
CREATE INDEX idx_eligibility_checks_timestamp ON eligibility_checks(check_timestamp DESC);
CREATE INDEX idx_eligibility_checks_type ON eligibility_checks(check_type);

-- Individual scheme eligibility results
CREATE TABLE IF NOT EXISTS scheme_eligibility_results (
    result_id SERIAL PRIMARY KEY,
    check_id INTEGER REFERENCES eligibility_checks(check_id) ON DELETE CASCADE,
    
    -- Scheme identification
    scheme_code VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(500),
    
    -- Eligibility status
    eligibility_status VARCHAR(50) NOT NULL,  -- 'ELIGIBLE', 'POSSIBLE_ELIGIBLE', 'NOT_ELIGIBLE'
    eligibility_score DECIMAL(5,4) NOT NULL,  -- 0-1 probability
    confidence_level VARCHAR(20),  -- 'HIGH', 'MEDIUM', 'LOW'
    
    -- Detailed evaluation
    rule_evaluations JSONB,  -- Detailed rule check results
    met_rules TEXT[],  -- Rules that passed
    failed_rules TEXT[],  -- Rules that failed
    rule_path TEXT,  -- Path through rule tree
    
    -- Recommendation ranking
    recommendation_rank INTEGER,  -- Position in recommendations (1 = top)
    priority_score DECIMAL(5,4),  -- Combined priority score
    impact_score DECIMAL(5,4),  -- Benefit impact/urgency score
    under_coverage_boost DECIMAL(5,4),  -- Boost from under-coverage indicators
    
    -- Explanation
    explanation_text TEXT,  -- Human-readable explanation
    explanation_template_id VARCHAR(100),  -- Template used
    explanation_tokens JSONB,  -- Tokens/placeholders filled
    
    -- Next steps
    next_steps TEXT[],  -- Recommended next actions
    application_link VARCHAR(500),  -- Link to application if available
    
    -- Timestamps
    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_scheme_eligibility_results_check_id ON scheme_eligibility_results(check_id);
CREATE INDEX idx_scheme_eligibility_results_scheme_code ON scheme_eligibility_results(scheme_code);
CREATE INDEX idx_scheme_eligibility_results_status ON scheme_eligibility_results(eligibility_status);
CREATE INDEX idx_scheme_eligibility_results_rank ON scheme_eligibility_results(recommendation_rank) WHERE recommendation_rank IS NOT NULL;
CREATE INDEX idx_scheme_eligibility_results_score ON scheme_eligibility_results(eligibility_score DESC);

-- Recommendation sets (for logged-in users, can be cached)
CREATE TABLE IF NOT EXISTS recommendation_sets (
    recommendation_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    beneficiary_id VARCHAR(255),  -- Optional, for specific beneficiary
    
    -- Recommendation metadata
    recommendation_type VARCHAR(50) NOT NULL,  -- 'TOP_RECOMMENDATIONS', 'ALL_ELIGIBLE', 'PERSONALIZED'
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- When recommendation should be refreshed
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Summary
    total_schemes INTEGER DEFAULT 0,
    top_recommendations_count INTEGER DEFAULT 0,
    
    -- Generation context
    generation_context JSONB,  -- Preferences, filters, etc.
    data_snapshot_hash VARCHAR(64),  -- Hash of data used for generation
    
    -- Related check
    based_on_check_id INTEGER REFERENCES eligibility_checks(check_id) ON DELETE SET NULL,
    
    metadata JSONB
);

CREATE INDEX idx_recommendation_sets_family_id ON recommendation_sets(family_id);
CREATE INDEX idx_recommendation_sets_beneficiary_id ON recommendation_sets(beneficiary_id) WHERE beneficiary_id IS NOT NULL;
CREATE INDEX idx_recommendation_sets_active ON recommendation_sets(is_active, expires_at) WHERE is_active = TRUE;
CREATE INDEX idx_recommendation_sets_generated_at ON recommendation_sets(generated_at DESC);

-- Recommendation items (schemes in a recommendation set)
CREATE TABLE IF NOT EXISTS recommendation_items (
    item_id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendation_sets(recommendation_id) ON DELETE CASCADE,
    
    -- Scheme identification
    scheme_code VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(500),
    
    -- Ranking
    rank INTEGER NOT NULL,  -- Position in recommendation list
    priority_score DECIMAL(5,4) NOT NULL,
    
    -- Eligibility details
    eligibility_status VARCHAR(50) NOT NULL,
    eligibility_score DECIMAL(5,4) NOT NULL,
    
    -- Why recommended
    recommendation_reasons TEXT[],  -- Why this scheme is recommended
    match_factors JSONB,  -- Factors that make this a good match
    
    -- Presentation
    category VARCHAR(100),  -- Health, Education, Financial, etc.
    benefit_summary TEXT,  -- Brief summary of benefits
    estimated_benefit_value DECIMAL(12,2),  -- Estimated benefit amount
    
    -- Links to eligibility result
    eligibility_result_id INTEGER REFERENCES scheme_eligibility_results(result_id) ON DELETE SET NULL,
    
    metadata JSONB
);

CREATE INDEX idx_recommendation_items_recommendation_id ON recommendation_items(recommendation_id);
CREATE INDEX idx_recommendation_items_rank ON recommendation_items(recommendation_id, rank);
CREATE INDEX idx_recommendation_items_scheme_code ON recommendation_items(scheme_code);

-- Guest questionnaire templates
CREATE TABLE IF NOT EXISTS questionnaire_templates (
    template_id SERIAL PRIMARY KEY,
    template_name VARCHAR(200) NOT NULL,
    template_version VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Questions
    questions JSONB NOT NULL,  -- Array of question objects
    question_flow JSONB,  -- Conditional flow logic
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    UNIQUE(template_name, template_version)
);

CREATE INDEX idx_questionnaire_templates_active ON questionnaire_templates(is_active) WHERE is_active = TRUE;

-- Explanation templates (for NLG)
CREATE TABLE IF NOT EXISTS explanation_templates (
    template_id SERIAL PRIMARY KEY,
    template_key VARCHAR(200) NOT NULL,  -- e.g., 'ELIGIBLE_AGE_INCOME'
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    
    -- Template content
    template_text TEXT NOT NULL,  -- Template with placeholders like {age}, {income}
    placeholders JSONB,  -- Available placeholders and their descriptions
    
    -- Context
    applies_to_status VARCHAR(50),  -- 'ELIGIBLE', 'POSSIBLE_ELIGIBLE', 'NOT_ELIGIBLE'
    applies_to_scheme_category VARCHAR(100),  -- Optional scheme category
    
    -- Metadata
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(template_key, language, version)
);

CREATE INDEX idx_explanation_templates_key ON explanation_templates(template_key, language, is_active);
CREATE INDEX idx_explanation_templates_status ON explanation_templates(applies_to_status, is_active);

-- Analytics: aggregated check metrics
CREATE TABLE IF NOT EXISTS eligibility_check_analytics (
    analytics_id SERIAL PRIMARY KEY,
    analytics_date DATE NOT NULL,
    
    -- Aggregated metrics
    total_checks INTEGER DEFAULT 0,
    logged_in_checks INTEGER DEFAULT 0,
    guest_checks INTEGER DEFAULT 0,
    anonymous_checks INTEGER DEFAULT 0,
    
    -- By check type
    full_checks INTEGER DEFAULT 0,
    scheme_specific_checks INTEGER DEFAULT 0,
    quick_checks INTEGER DEFAULT 0,
    
    -- Conversion metrics
    checks_to_applications INTEGER DEFAULT 0,  -- Checks that led to applications
    conversion_rate DECIMAL(5,4),  -- Percentage conversion
    
    -- Recommendation metrics
    recommendations_generated INTEGER DEFAULT 0,
    top_recommendations_clicked INTEGER DEFAULT 0,
    
    -- Accuracy metrics (for logged-in users with known outcomes)
    eligible_recommendations_confirmed INTEGER DEFAULT 0,  -- Later confirmed as eligible
    false_positives INTEGER DEFAULT 0,  -- Recommended but not eligible
    
    -- Demographic breakdowns (anonymized)
    checks_by_category JSONB,  -- Breakdown by user category
    checks_by_scheme JSONB,  -- Popular schemes checked
    checks_by_mode JSONB,  -- Web, mobile, chatbot, etc.
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_eligibility_check_analytics_date ON eligibility_check_analytics(analytics_date DESC);

-- Audit logs for compliance
CREATE TABLE IF NOT EXISTS eligibility_checker_audit_logs (
    audit_id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,  -- 'CHECK_PERFORMED', 'RECOMMENDATION_GENERATED', 'DATA_ACCESSED'
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL,  -- 'USER', 'SYSTEM', 'ADMIN'
    actor_id VARCHAR(100),  -- User ID, session ID, etc.
    
    -- Event details
    check_id INTEGER REFERENCES eligibility_checks(check_id) ON DELETE SET NULL,
    recommendation_id INTEGER REFERENCES recommendation_sets(recommendation_id) ON DELETE SET NULL,
    family_id UUID,
    session_id VARCHAR(255),
    
    -- Event data
    event_description TEXT NOT NULL,
    event_data JSONB,
    privacy_flags JSONB,  -- Privacy-related flags (consent, anonymization, etc.)
    
    metadata JSONB
);

CREATE INDEX idx_eligibility_checker_audit_logs_event_type ON eligibility_checker_audit_logs(event_type);
CREATE INDEX idx_eligibility_checker_audit_logs_timestamp ON eligibility_checker_audit_logs(event_timestamp DESC);
CREATE INDEX idx_eligibility_checker_audit_logs_family_id ON eligibility_checker_audit_logs(family_id) WHERE family_id IS NOT NULL;
CREATE INDEX idx_eligibility_checker_audit_logs_session_id ON eligibility_checker_audit_logs(session_id);

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_questionnaire_templates_updated_at BEFORE UPDATE ON questionnaire_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_explanation_templates_updated_at BEFORE UPDATE ON explanation_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial Data
-- ============================================================================

-- Insert default questionnaire template
INSERT INTO eligibility_checker.questionnaire_templates (template_name, template_version, questions, created_by)
VALUES (
    'default_guest_questionnaire',
    '1.0',
    '[
        {"id": "age", "question": "What is your age?", "type": "number", "required": true},
        {"id": "gender", "question": "What is your gender?", "type": "select", "options": ["Male", "Female", "Other"], "required": true},
        {"id": "district", "question": "Which district do you live in?", "type": "text", "required": true},
        {"id": "income_band", "question": "What is your approximate monthly household income?", "type": "select", "options": ["Below 5000", "5000-10000", "10000-20000", "Above 20000"], "required": true},
        {"id": "category", "question": "Which category do you belong to?", "type": "select", "options": ["General", "SC", "ST", "OBC"], "required": false},
        {"id": "disability", "question": "Do you have a disability?", "type": "boolean", "required": false},
        {"id": "education_level", "question": "What is your education level?", "type": "select", "options": ["Illiterate", "Primary", "Secondary", "Graduate", "Post-Graduate"], "required": false}
    ]'::jsonb,
    'system'
)
ON CONFLICT (template_name, template_version) DO NOTHING;

-- Insert default explanation templates
INSERT INTO eligibility_checker.explanation_templates (template_key, language, template_text, applies_to_status, placeholders)
VALUES
    ('ELIGIBLE_AGE_INCOME', 'en', 'You are eligible based on your age ({age} years) and income level ({income_band}).', 'ELIGIBLE', '{"age": "Age in years", "income_band": "Income band description"}'::jsonb),
    ('NOT_ELIGIBLE_AGE', 'en', 'You are not eligible because you are {age} years old, but this scheme requires age {required_age} or above.', 'NOT_ELIGIBLE', '{"age": "Current age", "required_age": "Required minimum age"}'::jsonb),
    ('POSSIBLE_ELIGIBLE_INCOME', 'en', 'You might be eligible. Your income ({income_band}) is close to the threshold. Please verify with official documents.', 'POSSIBLE_ELIGIBLE', '{"income_band": "Income band description"}'::jsonb),
    ('ELIGIBLE_CATEGORY_LOCATION', 'en', 'You are eligible based on your category ({category}) and location ({district}).', 'ELIGIBLE', '{"category": "Category name", "district": "District name"}'::jsonb)
ON CONFLICT (template_key, language, version) DO NOTHING;

COMMENT ON SCHEMA eligibility_checker IS 'Schema for Eligibility Checker & Recommendations (AI-PLATFORM-08)';

