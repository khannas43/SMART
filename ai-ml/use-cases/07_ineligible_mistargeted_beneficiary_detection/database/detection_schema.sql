-- Database Schema for Ineligible/Mistargeted Beneficiary Detection
-- Use Case ID: AI-PLATFORM-07
-- Schema: detection (in smart_warehouse database)

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS detection;
GRANT ALL ON SCHEMA detection TO sameer;
ALTER SCHEMA detection OWNER TO sameer;

-- Set search path
SET search_path TO detection;

-- ============================================================================
-- Core Tables
-- ============================================================================

-- Beneficiary detection runs (periodic re-scoring runs)
CREATE TABLE IF NOT EXISTS detection_runs (
    run_id SERIAL PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL,  -- 'FULL', 'INCREMENTAL', 'SCHEME_SPECIFIC', 'PRIORITY_BATCH'
    run_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    run_status VARCHAR(50) NOT NULL,  -- 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'
    schemes_processed TEXT[],  -- Array of scheme codes processed
    total_beneficiaries_scanned INTEGER DEFAULT 0,
    total_cases_flagged INTEGER DEFAULT 0,
    cases_by_classification JSONB,  -- {HARD_INELIGIBLE: 10, LIKELY_MIS_TARGETED: 20, ...}
    started_by VARCHAR(100),
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB  -- Additional run metadata
);

CREATE INDEX idx_detection_runs_date ON detection_runs(run_date DESC);
CREATE INDEX idx_detection_runs_status ON detection_runs(run_status);
CREATE INDEX idx_detection_runs_type ON detection_runs(run_type);

-- Detected cases (flagged beneficiaries)
CREATE TABLE IF NOT EXISTS detected_cases (
    case_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES detection_runs(run_id) ON DELETE SET NULL,
    beneficiary_id VARCHAR(255) NOT NULL,  -- Jan Aadhaar / GR ID
    family_id UUID,
    scheme_code VARCHAR(100) NOT NULL,
    
    -- Case classification
    case_type VARCHAR(50) NOT NULL,  -- 'HARD_INELIGIBLE', 'LIKELY_MIS_TARGETED', 'LOW_CONFIDENCE_FLAG'
    confidence_level VARCHAR(20) NOT NULL,  -- 'HIGH', 'MEDIUM', 'LOW'
    
    -- Detection details
    detection_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detection_method VARCHAR(50) NOT NULL,  -- 'RULE_BASED', 'ML_ANOMALY', 'HYBRID'
    risk_score DECIMAL(5,4),  -- ML risk score (0-1)
    financial_exposure DECIMAL(12,2),  -- Total benefit amount at risk
    vulnerability_score DECIMAL(5,4),  -- Vulnerability indicator (higher = more vulnerable)
    
    -- Status tracking
    case_status VARCHAR(50) NOT NULL DEFAULT 'FLAGGED',  -- 'FLAGGED', 'UNDER_VERIFICATION', 'VERIFIED_INELIGIBLE', 'VERIFIED_ELIGIBLE', 'APPEALED', 'CLOSED'
    assigned_to VARCHAR(100),  -- Officer ID
    assigned_at TIMESTAMP,
    priority INTEGER DEFAULT 5,  -- 1=highest, 10=lowest
    
    -- Eligibility re-check results
    current_eligibility_status VARCHAR(50),  -- 'ELIGIBLE', 'INELIGIBLE', 'UNCERTAIN'
    eligibility_score DECIMAL(5,4),
    eligibility_failure_reasons TEXT[],
    
    -- Detection explanations
    detection_rationale TEXT NOT NULL,  -- Human-readable explanation
    rule_evaluations JSONB,  -- Detailed rule check results
    ml_explanations JSONB,  -- ML model explanations (feature contributions, anomalies)
    
    -- Additional context
    current_benefits JSONB,  -- Current benefit details (amount, frequency, start date)
    historical_benefits JSONB,  -- Historical benefit patterns
    cross_scheme_overlaps JSONB,  -- Other schemes this beneficiary is enrolled in
    duplicate_indicators JSONB,  -- Potential duplicate beneficiary indicators
    
    -- Action recommendations
    recommended_action VARCHAR(100),  -- 'VERIFY', 'SUSPEND', 'CANCEL', 'RECALCULATE', 'RECOVER', 'IGNORE'
    action_urgency VARCHAR(20),  -- 'IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW'
    
    -- Verification and resolution
    verification_notes TEXT,
    verification_status VARCHAR(50),  -- 'PENDING', 'IN_PROGRESS', 'COMPLETED'
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    final_decision VARCHAR(50),  -- 'CONFIRMED_INELIGIBLE', 'FALSE_POSITIVE', 'REQUIRES_RECALCULATION', 'APPEAL_GRANTED'
    final_action_taken VARCHAR(100),
    action_taken_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    metadata JSONB
);

CREATE INDEX idx_detected_cases_run_id ON detected_cases(run_id);
CREATE INDEX idx_detected_cases_beneficiary_id ON detected_cases(beneficiary_id);
CREATE INDEX idx_detected_cases_family_id ON detected_cases(family_id);
CREATE INDEX idx_detected_cases_scheme_code ON detected_cases(scheme_code);
CREATE INDEX idx_detected_cases_case_type ON detected_cases(case_type);
CREATE INDEX idx_detected_cases_status ON detected_cases(case_status);
CREATE INDEX idx_detected_cases_priority ON detected_cases(priority);
CREATE INDEX idx_detected_cases_assigned_to ON detected_cases(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_detected_cases_detection_timestamp ON detected_cases(detection_timestamp DESC);

-- Rule-based detection results
CREATE TABLE IF NOT EXISTS rule_detections (
    detection_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES detected_cases(case_id) ON DELETE CASCADE,
    rule_category VARCHAR(100) NOT NULL,  -- 'ELIGIBILITY', 'OVERLAP', 'DUPLICATE', 'STATUS_CHANGE'
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT,
    
    -- Rule evaluation
    rule_passed BOOLEAN NOT NULL,
    rule_severity VARCHAR(20) NOT NULL,  -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    evaluation_result TEXT NOT NULL,
    evaluation_details JSONB,
    
    -- Current vs previous state
    previous_value TEXT,
    current_value TEXT,
    change_detected BOOLEAN DEFAULT FALSE,
    change_type VARCHAR(50),  -- 'INCOME_INCREASE', 'AGE_CHANGE', 'STATUS_CHANGE', etc.
    
    -- Evidence
    evidence_sources TEXT[],  -- Data sources used for evaluation
    evidence_data JSONB,  -- Snapshot of evidence data
    
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_rule_detections_case_id ON rule_detections(case_id);
CREATE INDEX idx_rule_detections_rule_category ON rule_detections(rule_category);
CREATE INDEX idx_rule_detections_rule_passed ON rule_detections(rule_passed);
CREATE INDEX idx_rule_detections_severity ON rule_detections(rule_severity);

-- ML anomaly detection results
CREATE TABLE IF NOT EXISTS ml_detections (
    detection_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES detected_cases(case_id) ON DELETE CASCADE,
    model_name VARCHAR(200) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- 'ISOLATION_FOREST', 'AUTOENCODER', 'SUPERVISED_FRAUD', etc.
    
    -- Anomaly scores
    anomaly_score DECIMAL(5,4) NOT NULL,  -- 0-1, higher = more anomalous
    risk_score DECIMAL(5,4) NOT NULL,  -- Combined risk score
    anomaly_type VARCHAR(100),  -- 'POSSIBLE_DUPLICATE', 'POSSIBLE_OVER_BENEFITTED', 'POSSIBLE_FAKE_ID', 'POSSIBLE_INCOME_ABOVE_LIMIT'
    
    -- Feature contributions
    top_anomalous_features JSONB,  -- Features contributing most to anomaly
    feature_contributions JSONB,  -- All feature contributions
    cluster_metrics JSONB,  -- Comparison with peer cluster
    
    -- Behavioral patterns
    behavioral_flags TEXT[],  -- Flags like 'FREQUENT_SWITCHING', 'ABNORMAL_GRIEVANCES', etc.
    pattern_explanations JSONB,  -- Explanations for behavioral patterns
    
    -- Model metadata
    model_input_features JSONB,  -- Input features to the model
    model_output_raw JSONB,  -- Raw model output
    prediction_confidence DECIMAL(5,4),
    
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_ml_detections_case_id ON ml_detections(case_id);
CREATE INDEX idx_ml_detections_anomaly_score ON ml_detections(anomaly_score DESC);
CREATE INDEX idx_ml_detections_model_name ON ml_detections(model_name);
CREATE INDEX idx_ml_detections_anomaly_type ON ml_detections(anomaly_type);

-- Beneficiary eligibility snapshots (for comparison over time)
CREATE TABLE IF NOT EXISTS eligibility_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    beneficiary_id VARCHAR(255) NOT NULL,
    family_id UUID,
    scheme_code VARCHAR(100) NOT NULL,
    
    -- Snapshot metadata
    snapshot_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_type VARCHAR(50) NOT NULL,  -- 'BASELINE', 'RE_SCORE', 'VERIFICATION', 'APPEAL'
    trigger_reason VARCHAR(200),  -- Why this snapshot was created
    
    -- Eligibility state
    eligibility_status VARCHAR(50) NOT NULL,  -- 'ELIGIBLE', 'INELIGIBLE', 'UNCERTAIN'
    eligibility_score DECIMAL(5,4),
    eligibility_rules_evaluated JSONB,  -- Rule evaluation results
    
    -- Current attributes (from Golden Record)
    age INTEGER,
    gender VARCHAR(20),
    category VARCHAR(100),  -- Caste/category
    income_band VARCHAR(50),
    disability_status VARCHAR(50),
    address_district VARCHAR(100),
    address_state VARCHAR(100),
    
    -- Status flags
    is_deceased BOOLEAN DEFAULT FALSE,
    is_migrated BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    jan_aadhaar_status VARCHAR(50),
    
    -- Benefit context
    current_benefit_amount DECIMAL(12,2),
    benefit_frequency VARCHAR(50),
    total_active_benefits INTEGER,  -- Number of active schemes
    total_monthly_benefits DECIMAL(12,2),  -- Sum of monthly benefits across all schemes
    
    -- Comparison data
    previous_snapshot_id INTEGER REFERENCES eligibility_snapshots(snapshot_id) ON DELETE SET NULL,
    changes_detected JSONB,  -- What changed from previous snapshot
    change_summary TEXT,
    
    -- Metadata
    created_by VARCHAR(100),
    metadata JSONB
);

CREATE INDEX idx_eligibility_snapshots_beneficiary_id ON eligibility_snapshots(beneficiary_id);
CREATE INDEX idx_eligibility_snapshots_family_id ON eligibility_snapshots(family_id);
CREATE INDEX idx_eligibility_snapshots_scheme_code ON eligibility_snapshots(scheme_code);
CREATE INDEX idx_eligibility_snapshots_date ON eligibility_snapshots(snapshot_date DESC);
CREATE INDEX idx_eligibility_snapshots_type ON eligibility_snapshots(snapshot_type);

-- Worklist assignments (for departmental officers)
CREATE TABLE IF NOT EXISTS worklist_assignments (
    assignment_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES detected_cases(case_id) ON DELETE CASCADE,
    
    -- Assignment details
    assigned_to VARCHAR(100) NOT NULL,  -- Officer ID
    assigned_by VARCHAR(100),
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assignment_priority INTEGER DEFAULT 5,
    assignment_notes TEXT,
    
    -- Worklist details
    worklist_queue VARCHAR(100),  -- 'SCHEME_SPECIFIC', 'HIGH_PRIORITY', 'REGIONAL', etc.
    worklist_group VARCHAR(100),  -- Scheme code, district, department, etc.
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'ASSIGNED',  -- 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'REASSIGNED'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completion_notes TEXT,
    
    -- Reassignment
    reassigned_to VARCHAR(100),
    reassigned_at TIMESTAMP,
    reassignment_reason TEXT,
    
    metadata JSONB
);

CREATE INDEX idx_worklist_assignments_case_id ON worklist_assignments(case_id);
CREATE INDEX idx_worklist_assignments_assigned_to ON worklist_assignments(assigned_to);
CREATE INDEX idx_worklist_assignments_status ON worklist_assignments(status);
CREATE INDEX idx_worklist_assignments_queue ON worklist_assignments(worklist_queue);
CREATE INDEX idx_worklist_assignments_priority ON worklist_assignments(assignment_priority);

-- Case verification and resolution history
CREATE TABLE IF NOT EXISTS case_verification_history (
    history_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES detected_cases(case_id) ON DELETE CASCADE,
    
    -- Verification event
    event_type VARCHAR(50) NOT NULL,  -- 'FLAGGED', 'ASSIGNED', 'VERIFICATION_STARTED', 'VERIFICATION_COMPLETED', 'APPEAL_FILED', 'DECISION_MADE', 'ACTION_TAKEN'
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_by VARCHAR(100),  -- User/officer who triggered the event
    
    -- Event details
    event_description TEXT NOT NULL,
    event_data JSONB,  -- Additional event-specific data
    
    -- Verification details (if applicable)
    verification_method VARCHAR(100),  -- 'FIELD_VERIFICATION', 'DOCUMENT_REVIEW', 'CROSS_CHECK', 'APPEAL_REVIEW'
    verification_result TEXT,
    verification_findings JSONB,
    
    -- Decision (if applicable)
    decision_type VARCHAR(50),  -- 'CONFIRMED_INELIGIBLE', 'FALSE_POSITIVE', 'REQUIRES_RECALCULATION', 'APPEAL_GRANTED'
    decision_rationale TEXT,
    recommended_actions TEXT[],
    
    -- Action taken (if applicable)
    action_taken VARCHAR(100),
    action_details JSONB,
    action_outcome TEXT,
    
    metadata JSONB
);

CREATE INDEX idx_case_verification_history_case_id ON case_verification_history(case_id);
CREATE INDEX idx_case_verification_history_event_type ON case_verification_history(event_type);
CREATE INDEX idx_case_verification_history_timestamp ON case_verification_history(event_timestamp DESC);
CREATE INDEX idx_case_verification_history_event_by ON case_verification_history(event_by);

-- Cross-scheme overlap and exclusion matrix
CREATE TABLE IF NOT EXISTS scheme_exclusion_rules (
    rule_id SERIAL PRIMARY KEY,
    scheme_code_1 VARCHAR(100) NOT NULL,
    scheme_code_2 VARCHAR(100) NOT NULL,
    exclusion_type VARCHAR(50) NOT NULL,  -- 'MUTUALLY_EXCLUSIVE', 'LIMITED_OVERLAP', 'ALLOWED'
    max_beneficiaries_per_family INTEGER,  -- For schemes with family limits
    description TEXT,
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    UNIQUE(scheme_code_1, scheme_code_2)
);

CREATE INDEX idx_scheme_exclusion_rules_scheme1 ON scheme_exclusion_rules(scheme_code_1);
CREATE INDEX idx_scheme_exclusion_rules_scheme2 ON scheme_exclusion_rules(scheme_code_2);
CREATE INDEX idx_scheme_exclusion_rules_active ON scheme_exclusion_rules(is_active) WHERE is_active = TRUE;

-- Detection configuration and thresholds
CREATE TABLE IF NOT EXISTS detection_config (
    config_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(100),  -- NULL for global config
    config_category VARCHAR(100) NOT NULL,  -- 'ELIGIBILITY', 'ML_THRESHOLDS', 'PRIORITIZATION', etc.
    config_key VARCHAR(200) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL,  -- 'INTEGER', 'DECIMAL', 'BOOLEAN', 'STRING', 'JSON'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    
    UNIQUE(scheme_code, config_category, config_key, effective_from)
);

CREATE INDEX idx_detection_config_scheme ON detection_config(scheme_code);
CREATE INDEX idx_detection_config_category ON detection_config(config_category);
CREATE INDEX idx_detection_config_active ON detection_config(is_active) WHERE is_active = TRUE;

-- Leakage analytics and aggregated metrics
CREATE TABLE IF NOT EXISTS leakage_analytics (
    analytics_id SERIAL PRIMARY KEY,
    analytics_date DATE NOT NULL,
    scheme_code VARCHAR(100),  -- NULL for overall analytics
    district VARCHAR(100),
    state VARCHAR(100),
    
    -- Metrics
    total_beneficiaries_scanned INTEGER DEFAULT 0,
    total_cases_flagged INTEGER DEFAULT 0,
    cases_by_type JSONB,  -- {HARD_INELIGIBLE: 10, LIKELY_MIS_TARGETED: 20, ...}
    total_financial_exposure DECIMAL(12,2),
    estimated_savings DECIMAL(12,2),  -- Based on confirmed cases
    
    -- False positive tracking
    false_positive_count INTEGER DEFAULT 0,
    false_positive_rate DECIMAL(5,4),
    confirmed_ineligible_count INTEGER DEFAULT 0,
    confirmation_rate DECIMAL(5,4),
    
    -- Breakdowns
    ineligibility_reasons JSONB,  -- {INCOME_EXCEEDED: 50, STATUS_CHANGED: 30, ...}
    overlap_types JSONB,  -- {MUTUALLY_EXCLUSIVE: 20, DUPLICATE_ID: 15, ...}
    anomaly_types JSONB,  -- ML anomaly breakdown
    
    -- Demographics (for fairness monitoring)
    cases_by_demographic JSONB,  -- Breakdown by category, gender, district, etc.
    
    -- Action outcomes
    cases_verified INTEGER DEFAULT 0,
    cases_suspended INTEGER DEFAULT 0,
    cases_cancelled INTEGER DEFAULT 0,
    cases_recovered INTEGER DEFAULT 0,
    cases_appealed INTEGER DEFAULT 0,
    appeals_granted INTEGER DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_leakage_analytics_date ON leakage_analytics(analytics_date DESC);
CREATE INDEX idx_leakage_analytics_scheme ON leakage_analytics(scheme_code);
CREATE INDEX idx_leakage_analytics_district ON leakage_analytics(district);

-- Audit logs for detection operations
CREATE TABLE IF NOT EXISTS detection_audit_logs (
    audit_id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,  -- 'DETECTION_RUN', 'CASE_FLAGGED', 'CASE_VERIFIED', 'ACTION_TAKEN', etc.
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor_type VARCHAR(50) NOT NULL,  -- 'SYSTEM', 'OFFICER', 'ADMIN', 'BENEFICIARY'
    actor_id VARCHAR(100),
    
    -- Event details
    case_id INTEGER REFERENCES detected_cases(case_id) ON DELETE SET NULL,
    run_id INTEGER REFERENCES detection_runs(run_id) ON DELETE SET NULL,
    beneficiary_id VARCHAR(255),
    scheme_code VARCHAR(100),
    
    -- Event data
    event_description TEXT NOT NULL,
    event_data JSONB,
    input_snapshot_hash VARCHAR(64),  -- Hash of input data for auditability
    output_data JSONB,
    
    -- Model/rule tracking
    model_version VARCHAR(50),
    rule_version VARCHAR(50),
    thresholds_used JSONB,
    
    metadata JSONB
);

CREATE INDEX idx_detection_audit_logs_event_type ON detection_audit_logs(event_type);
CREATE INDEX idx_detection_audit_logs_timestamp ON detection_audit_logs(event_timestamp DESC);
CREATE INDEX idx_detection_audit_logs_actor ON detection_audit_logs(actor_type, actor_id);
CREATE INDEX idx_detection_audit_logs_case_id ON detection_audit_logs(case_id);
CREATE INDEX idx_detection_audit_logs_beneficiary_id ON detection_audit_logs(beneficiary_id);

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

CREATE TRIGGER update_detected_cases_updated_at BEFORE UPDATE ON detected_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scheme_exclusion_rules_updated_at BEFORE UPDATE ON scheme_exclusion_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_detection_config_updated_at BEFORE UPDATE ON detection_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial Data
-- ============================================================================

-- Insert default scheme exclusion rules (examples)
INSERT INTO detection.scheme_exclusion_rules (scheme_code_1, scheme_code_2, exclusion_type, description, effective_from)
VALUES
    ('OLD_AGE_PENSION', 'DISABILITY_PENSION', 'MUTUALLY_EXCLUSIVE', 'Cannot receive both old age and disability pension', CURRENT_DATE),
    ('OBC_SCHOLARSHIP', 'SC_ST_SCHOLARSHIP', 'MUTUALLY_EXCLUSIVE', 'Cannot receive both OBC and SC/ST scholarships', CURRENT_DATE)
ON CONFLICT (scheme_code_1, scheme_code_2) DO NOTHING;

-- Insert default detection configuration
INSERT INTO detection.detection_config (scheme_code, config_category, config_key, config_value, config_type, description, effective_from)
VALUES
    (NULL, 'ML_THRESHOLDS', 'anomaly_score_threshold', '0.7', 'DECIMAL', 'Minimum anomaly score to flag as HIGH risk', CURRENT_DATE),
    (NULL, 'ML_THRESHOLDS', 'risk_score_threshold', '0.6', 'DECIMAL', 'Minimum risk score to flag as LIKELY_MIS_TARGETED', CURRENT_DATE),
    (NULL, 'PRIORITIZATION', 'high_financial_exposure_threshold', '10000', 'DECIMAL', 'Minimum financial exposure for HIGH priority', CURRENT_DATE),
    (NULL, 'PRIORITIZATION', 'high_vulnerability_threshold', '0.8', 'DECIMAL', 'Minimum vulnerability score for cautious handling', CURRENT_DATE),
    (NULL, 'RE_SCORING', 'full_rescore_frequency', 'QUARTERLY', 'STRING', 'Frequency of full re-scoring runs', CURRENT_DATE),
    (NULL, 'RE_SCORING', 'incremental_rescore_triggers', '["INCOME_UPDATE", "STATUS_CHANGE", "DEATH_REGISTRY"]', 'JSON', 'Triggers for incremental re-scoring', CURRENT_DATE)
ON CONFLICT DO NOTHING;

COMMENT ON SCHEMA detection IS 'Schema for Ineligible/Mistargeted Beneficiary Detection (AI-PLATFORM-07)';

