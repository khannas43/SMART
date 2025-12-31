-- ============================================================================
-- Proactive Inclusion & Exception Handling Schema
-- Use Case ID: AI-PLATFORM-09
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS inclusion;
GRANT USAGE ON SCHEMA inclusion TO sameer;
ALTER SCHEMA inclusion OWNER TO sameer;

SET search_path TO inclusion;

-- Priority households (identified as underserved)
CREATE TABLE IF NOT EXISTS priority_households (
    priority_id SERIAL PRIMARY KEY,
    
    -- Household identification
    family_id UUID NOT NULL,
    household_head_id VARCHAR(255),
    
    -- Location
    block_id VARCHAR(100),
    district VARCHAR(100),
    gram_panchayat VARCHAR(100),
    
    -- Inclusion gap score
    inclusion_gap_score DECIMAL(5,4) NOT NULL,  -- 0-1 score
    vulnerability_score DECIMAL(5,4) NOT NULL,  -- Vulnerability indicators
    coverage_gap_score DECIMAL(5,4) NOT NULL,  -- Eligibility vs uptake gap
    benchmark_score DECIMAL(5,4),  -- Local coverage benchmark
    
    -- Priority classification
    priority_level VARCHAR(20) NOT NULL,  -- 'HIGH', 'MEDIUM', 'LOW'
    priority_segments TEXT[],  -- ['TRIBAL', 'PWD', 'SINGLE_WOMAN', etc.]
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Detection metadata
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detected_by VARCHAR(50) DEFAULT 'AUTO_DETECTION',
    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Eligibility vs uptake gap details
    predicted_eligible_schemes_count INTEGER DEFAULT 0,
    actual_enrolled_schemes_count INTEGER DEFAULT 0,
    eligibility_gap_count INTEGER DEFAULT 0,
    
    metadata JSONB
);

CREATE INDEX idx_priority_households_family_id ON priority_households(family_id);
CREATE INDEX idx_priority_households_block_id ON priority_households(block_id) WHERE block_id IS NOT NULL;
CREATE INDEX idx_priority_households_district ON priority_households(district);
CREATE INDEX idx_priority_households_priority_level ON priority_households(priority_level, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_priority_households_gap_score ON priority_households(inclusion_gap_score DESC) WHERE is_active = TRUE;
CREATE INDEX idx_priority_households_segments ON priority_households USING GIN(priority_segments);

-- Exception flags (atypical circumstances requiring human review)
CREATE TABLE IF NOT EXISTS exception_flags (
    exception_id SERIAL PRIMARY KEY,
    
    -- Related to
    family_id UUID NOT NULL,
    beneficiary_id VARCHAR(255),  -- Optional, specific beneficiary
    
    -- Exception details
    exception_category VARCHAR(100) NOT NULL,  -- 'RECENTLY_DISABLED', 'MIGRANT_WORKER', etc.
    exception_description TEXT,
    anomaly_score DECIMAL(5,4),  -- Anomaly detection score
    
    -- Detection context
    detected_features JSONB,  -- Features that triggered exception
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detected_by VARCHAR(50) DEFAULT 'ANOMALY_DETECTION',
    
    -- Review status
    review_status VARCHAR(50) DEFAULT 'PENDING_REVIEW',  -- 'PENDING_REVIEW', 'UNDER_REVIEW', 'RESOLVED', 'FALSE_POSITIVE'
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    review_decision TEXT,  -- Outcome of human review
    
    -- Routing
    routed_to VARCHAR(100),  -- Department/team assigned
    routing_priority INTEGER DEFAULT 5,  -- 1-10
    
    metadata JSONB
);

CREATE INDEX idx_exception_flags_family_id ON exception_flags(family_id);
CREATE INDEX idx_exception_flags_category ON exception_flags(exception_category);
CREATE INDEX idx_exception_flags_review_status ON exception_flags(review_status) WHERE review_status = 'PENDING_REVIEW';
CREATE INDEX idx_exception_flags_anomaly_score ON exception_flags(anomaly_score DESC) WHERE review_status = 'PENDING_REVIEW';

-- Nudge records (proactive suggestions and nudges sent)
CREATE TABLE IF NOT EXISTS nudge_records (
    nudge_id SERIAL PRIMARY KEY,
    
    -- Target
    family_id UUID NOT NULL,
    household_head_id VARCHAR(255),
    
    -- Nudge content
    nudge_type VARCHAR(50) NOT NULL,  -- 'SCHEME_SUGGESTION', 'ACTION_REMINDER', 'UPDATE_REQUEST'
    nudge_message TEXT NOT NULL,
    recommended_actions TEXT[],  -- ['Apply for disability pension', 'Enroll in scholarship', etc.]
    scheme_codes TEXT[],  -- Related schemes
    
    -- Delivery
    channel VARCHAR(50) NOT NULL,  -- 'PORTAL', 'MOBILE_APP', 'SMS', 'FIELD_WORKER', 'EMAIL'
    priority_level VARCHAR(20) NOT NULL,  -- 'HIGH', 'MEDIUM', 'LOW'
    scheduled_at TIMESTAMP,
    delivered_at TIMESTAMP,
    delivery_status VARCHAR(50) DEFAULT 'SCHEDULED',  -- 'SCHEDULED', 'DELIVERED', 'FAILED', 'CANCELLED'
    delivery_metadata JSONB,  -- Channel-specific metadata
    
    -- Effectiveness tracking
    viewed_at TIMESTAMP,  -- When user viewed/interacted
    action_taken_at TIMESTAMP,  -- When user took recommended action
    converted_to_application BOOLEAN DEFAULT FALSE,
    application_id VARCHAR(255),  -- If converted to application
    
    -- Related records
    priority_household_id INTEGER REFERENCES priority_households(priority_id) ON DELETE SET NULL,
    exception_id INTEGER REFERENCES exception_flags(exception_id) ON DELETE SET NULL,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_nudge_records_family_id ON nudge_records(family_id);
CREATE INDEX idx_nudge_records_priority_household_id ON nudge_records(priority_household_id) WHERE priority_household_id IS NOT NULL;
CREATE INDEX idx_nudge_records_channel ON nudge_records(channel, delivery_status);
CREATE INDEX idx_nudge_records_priority ON nudge_records(priority_level, scheduled_at) WHERE delivery_status = 'SCHEDULED';
CREATE INDEX idx_nudge_records_delivery_status ON nudge_records(delivery_status, delivered_at);

-- Inclusion gap analysis (detailed breakdown)
CREATE TABLE IF NOT EXISTS inclusion_gap_analysis (
    analysis_id SERIAL PRIMARY KEY,
    
    -- Subject
    family_id UUID NOT NULL,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Gap components
    predicted_eligible_schemes JSONB,  -- List of schemes with eligibility scores
    actual_enrolled_schemes TEXT[],  -- Schemes actually enrolled
    gap_schemes TEXT[],  -- Schemes eligible but not enrolled
    
    -- Vulnerability indicators
    vulnerability_flags TEXT[],  -- ['tribal', 'pwd', 'single_woman', etc.]
    vulnerability_details JSONB,  -- Detailed vulnerability data
    
    -- Coverage comparison
    local_benchmark_coverage DECIMAL(5,4),  -- Average coverage in same area
    household_coverage DECIMAL(5,4),  -- This household's coverage
    coverage_deviation DECIMAL(5,4),  -- Deviation from benchmark
    
    -- Scores
    inclusion_gap_score DECIMAL(5,4) NOT NULL,
    component_scores JSONB,  -- Breakdown of score components
    
    -- Related priority household
    priority_household_id INTEGER REFERENCES priority_households(priority_id) ON DELETE SET NULL,
    
    metadata JSONB
);

CREATE INDEX idx_inclusion_gap_analysis_family_id ON inclusion_gap_analysis(family_id);
CREATE INDEX idx_inclusion_gap_analysis_analysis_date ON inclusion_gap_analysis(analysis_date DESC);
CREATE INDEX idx_inclusion_gap_analysis_priority_id ON inclusion_gap_analysis(priority_household_id) WHERE priority_household_id IS NOT NULL;

-- Field worker priority lists (for outreach)
CREATE TABLE IF NOT EXISTS field_worker_priority_lists (
    list_id SERIAL PRIMARY KEY,
    
    -- List assignment
    field_worker_id VARCHAR(100) NOT NULL,
    block_id VARCHAR(100),
    gram_panchayat VARCHAR(100),
    
    -- List criteria
    segment_filters TEXT[],  -- Filter by segments
    priority_level_filter VARCHAR(20),  -- Filter by priority level
    max_households INTEGER DEFAULT 50,  -- Limit households per list
    
    -- List generation
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(50) DEFAULT 'AUTO',
    expires_at TIMESTAMP,  -- When list should be refreshed
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Households in list (stored as JSONB array of family_ids)
    household_list JSONB NOT NULL,  -- Array of {family_id, priority_level, inclusion_gap_score, segments}
    
    metadata JSONB
);

CREATE INDEX idx_field_worker_priority_lists_worker_id ON field_worker_priority_lists(field_worker_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_field_worker_priority_lists_block_id ON field_worker_priority_lists(block_id) WHERE block_id IS NOT NULL;

-- Nudge effectiveness analytics
CREATE TABLE IF NOT EXISTS nudge_effectiveness_analytics (
    analytics_id SERIAL PRIMARY KEY,
    
    -- Time period
    analytics_date DATE NOT NULL,
    analytics_period VARCHAR(20) DEFAULT 'DAILY',  -- 'DAILY', 'WEEKLY', 'MONTHLY'
    
    -- Segment breakdown
    segment VARCHAR(50),  -- 'TRIBAL', 'PWD', etc., or NULL for overall
    channel VARCHAR(50),  -- 'PORTAL', 'SMS', etc., or NULL for all channels
    
    -- Metrics
    nudges_sent INTEGER DEFAULT 0,
    nudges_delivered INTEGER DEFAULT 0,
    nudges_viewed INTEGER DEFAULT 0,
    nudges_actioned INTEGER DEFAULT 0,
    applications_generated INTEGER DEFAULT 0,
    
    -- Conversion rates
    delivery_rate DECIMAL(5,4),  -- delivered / sent
    view_rate DECIMAL(5,4),  -- viewed / delivered
    action_rate DECIMAL(5,4),  -- actioned / viewed
    conversion_rate DECIMAL(5,4),  -- applications / actioned
    
    -- Response time metrics
    avg_time_to_view_minutes INTEGER,  -- Average time from delivery to view
    avg_time_to_action_minutes INTEGER,  -- Average time from view to action
    
    -- Created
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_nudge_effectiveness_analytics_date ON nudge_effectiveness_analytics(analytics_date DESC);
CREATE INDEX idx_nudge_effectiveness_analytics_segment ON nudge_effectiveness_analytics(segment) WHERE segment IS NOT NULL;

-- Inclusion monitoring dashboard data
CREATE TABLE IF NOT EXISTS inclusion_monitoring (
    monitoring_id SERIAL PRIMARY KEY,
    
    -- Monitoring period
    monitoring_date DATE NOT NULL,
    block_id VARCHAR(100),
    district VARCHAR(100),
    
    -- Overall metrics
    total_households INTEGER DEFAULT 0,
    priority_households_count INTEGER DEFAULT 0,
    exception_flags_count INTEGER DEFAULT 0,
    
    -- Segment breakdowns
    segment_counts JSONB,  -- {'TRIBAL': 150, 'PWD': 80, etc.}
    segment_gap_scores JSONB,  -- Average gap scores per segment
    
    -- Coverage metrics
    avg_inclusion_gap_score DECIMAL(5,4),
    avg_vulnerability_score DECIMAL(5,4),
    avg_coverage_gap DECIMAL(5,4),
    
    -- Nudge effectiveness (aggregated)
    total_nudges_sent INTEGER DEFAULT 0,
    total_nudges_delivered INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    
    -- Created
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_inclusion_monitoring_date ON inclusion_monitoring(monitoring_date DESC);
CREATE INDEX idx_inclusion_monitoring_block_id ON inclusion_monitoring(block_id) WHERE block_id IS NOT NULL;
CREATE INDEX idx_inclusion_monitoring_district ON inclusion_monitoring(district) WHERE district IS NOT NULL;

-- Audit logs
CREATE TABLE IF NOT EXISTS inclusion_audit_logs (
    audit_id SERIAL PRIMARY KEY,
    
    event_type VARCHAR(100) NOT NULL,  -- 'PRIORITY_DETECTED', 'EXCEPTION_FLAGGED', 'NUDGE_SENT', etc.
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL,  -- 'SYSTEM', 'USER', 'FIELD_WORKER'
    actor_id VARCHAR(100),
    
    -- Event details
    family_id UUID,
    priority_household_id INTEGER REFERENCES priority_households(priority_id) ON DELETE SET NULL,
    exception_id INTEGER REFERENCES exception_flags(exception_id) ON DELETE SET NULL,
    nudge_id INTEGER REFERENCES nudge_records(nudge_id) ON DELETE SET NULL,
    
    -- Event data
    event_description TEXT NOT NULL,
    event_data JSONB,
    
    metadata JSONB
);

CREATE INDEX idx_inclusion_audit_logs_event_type ON inclusion_audit_logs(event_type);
CREATE INDEX idx_inclusion_audit_logs_timestamp ON inclusion_audit_logs(event_timestamp DESC);
CREATE INDEX idx_inclusion_audit_logs_family_id ON inclusion_audit_logs(family_id) WHERE family_id IS NOT NULL;

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update last_updated_at timestamp
CREATE OR REPLACE FUNCTION update_last_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_priority_households_updated_at BEFORE UPDATE ON priority_households
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_at_column();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON SCHEMA inclusion IS 'Schema for Proactive Inclusion & Exception Handling (AI-PLATFORM-09)';
COMMENT ON TABLE priority_households IS 'Households identified as priority for proactive inclusion';
COMMENT ON TABLE exception_flags IS 'Exception flags for atypical circumstances requiring human review';
COMMENT ON TABLE nudge_records IS 'Records of nudges and proactive suggestions sent to households';
COMMENT ON TABLE inclusion_gap_analysis IS 'Detailed inclusion gap analysis for households';
COMMENT ON TABLE field_worker_priority_lists IS 'Priority household lists assigned to field workers';
COMMENT ON TABLE nudge_effectiveness_analytics IS 'Analytics on nudge delivery and conversion effectiveness';
COMMENT ON TABLE inclusion_monitoring IS 'Monitoring dashboard data for inclusion metrics';

