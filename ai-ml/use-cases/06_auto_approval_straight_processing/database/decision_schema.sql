-- Auto Approval & Straight-through Processing Database Schema
-- Use Case ID: AI-PLATFORM-06
-- Database: smart_warehouse (consolidated with other AI/ML use cases)
-- Schema: decision

-- Note: This schema is part of smart_warehouse database
-- All AI/ML use cases use the same smart_warehouse database with different schemas for organization

CREATE SCHEMA IF NOT EXISTS decision;

-- Grant permissions to sameer user
GRANT USAGE ON SCHEMA decision TO sameer;
GRANT CREATE ON SCHEMA decision TO sameer;
ALTER SCHEMA decision OWNER TO sameer;

-- ============================================================================
-- DECISION MANAGEMENT
-- ============================================================================

-- Decisions
-- Main decision records for applications
CREATE TABLE IF NOT EXISTS decision.decisions (
    decision_id SERIAL PRIMARY KEY,
    
    -- Application Reference
    application_id INTEGER NOT NULL, -- FK to application.applications (no FK constraint to allow flexibility)
    application_number VARCHAR(100),
    family_id UUID NOT NULL,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Decision
    decision_type VARCHAR(50) NOT NULL, 
    -- AUTO_APPROVE, ROUTE_TO_OFFICER, ROUTE_TO_FRAUD, AUTO_REJECT, OFFICER_APPROVED, OFFICER_REJECTED
    decision_status VARCHAR(50) DEFAULT 'pending',
    -- pending, approved, rejected, under_review, overridden
    
    -- Risk Assessment
    risk_score DECIMAL(5,4), -- 0.0 to 1.0
    risk_band VARCHAR(20), -- LOW, MEDIUM, HIGH
    risk_factors JSONB, -- Top contributing factors for explainability
    
    -- Rule Evaluation Summary
    rules_passed BOOLEAN,
    rules_failed_count INTEGER DEFAULT 0,
    critical_rules_failed TEXT[], -- List of critical rule failures
    
    -- Routing
    routed_to VARCHAR(100), -- Officer ID, fraud queue, etc.
    routing_reason TEXT,
    
    -- Decision Metadata
    decision_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision_by VARCHAR(100) DEFAULT 'decision_engine', -- decision_engine, officer_id, system
    
    -- Model Information (for explainability and audit)
    model_version VARCHAR(50),
    model_type VARCHAR(50), -- xgboost, logistic_regression, etc.
    thresholds_used JSONB, -- Risk thresholds applied
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP, -- When decision was processed (payment triggered, etc.)
    
    -- Constraints
    CONSTRAINT valid_risk_score CHECK (risk_score >= 0.0 AND risk_score <= 1.0)
);

CREATE INDEX idx_decisions_application ON decision.decisions(application_id);
CREATE INDEX idx_decisions_family ON decision.decisions(family_id);
CREATE INDEX idx_decisions_scheme ON decision.decisions(scheme_code);
CREATE INDEX idx_decisions_type ON decision.decisions(decision_type);
CREATE INDEX idx_decisions_status ON decision.decisions(decision_status);
CREATE INDEX idx_decisions_risk_band ON decision.decisions(risk_band);
CREATE INDEX idx_decisions_timestamp ON decision.decisions(decision_timestamp);
CREATE INDEX idx_decisions_application_scheme ON decision.decisions(application_id, scheme_code);

COMMENT ON TABLE decision.decisions IS 'Main decision records for application evaluations';

-- Rule Evaluations
-- Detailed results of rule-based checks
CREATE TABLE IF NOT EXISTS decision.rule_evaluations (
    evaluation_id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Rule Information
    rule_category VARCHAR(50) NOT NULL, 
    -- ELIGIBILITY, AUTHENTICITY, DOCUMENT, DUPLICATE, FRAUD, CROSS_SCHEME
    rule_name VARCHAR(255) NOT NULL,
    rule_id VARCHAR(100), -- Reference to rule definition
    
    -- Evaluation Result
    passed BOOLEAN NOT NULL,
    severity VARCHAR(20), -- CRITICAL, HIGH, MEDIUM, LOW, INFO
    result_message TEXT,
    result_details JSONB, -- Detailed evaluation results
    
    -- Rule Inputs (for audit)
    rule_inputs JSONB, -- Input data used for evaluation
    
    -- Timestamps
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rule_eval_decision ON decision.rule_evaluations(decision_id);
CREATE INDEX idx_rule_eval_category ON decision.rule_evaluations(rule_category);
CREATE INDEX idx_rule_eval_passed ON decision.rule_evaluations(passed);
CREATE INDEX idx_rule_eval_severity ON decision.rule_evaluations(severity);

COMMENT ON TABLE decision.rule_evaluations IS 'Detailed rule evaluation results for each decision';

-- Risk Scores
-- ML model risk assessment results
CREATE TABLE IF NOT EXISTS decision.risk_scores (
    score_id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Score Information
    overall_score DECIMAL(5,4) NOT NULL,
    score_band VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH
    
    -- Feature Contributions (for explainability)
    feature_contributions JSONB, -- Top contributing features with weights
    top_risk_factors TEXT[], -- Top 5 risk factors
    
    -- Model Information
    model_version VARCHAR(50),
    model_type VARCHAR(50),
    model_id INTEGER, -- FK to risk_models.model_id
    
    -- Feature Values Used (for audit)
    input_features JSONB, -- Feature values used for scoring
    
    -- Timestamps
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_overall_score CHECK (overall_score >= 0.0 AND overall_score <= 1.0)
);

CREATE INDEX idx_risk_scores_decision ON decision.risk_scores(decision_id);
CREATE INDEX idx_risk_scores_band ON decision.risk_scores(score_band);
CREATE INDEX idx_risk_scores_model ON decision.risk_scores(model_id);

COMMENT ON TABLE decision.risk_scores IS 'ML model risk score results';

-- Decision History
-- Historical record of all decisions and status changes
CREATE TABLE IF NOT EXISTS decision.decision_history (
    history_id BIGSERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Status Change
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    from_decision_type VARCHAR(50),
    to_decision_type VARCHAR(50) NOT NULL,
    
    -- Change Reason
    change_reason TEXT,
    change_details JSONB,
    
    -- Actor
    changed_by VARCHAR(100) NOT NULL, -- decision_engine, officer_id, system, citizen
    changed_by_type VARCHAR(50), -- system, officer, citizen, admin
    
    -- Timestamps
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_decision_history_decision ON decision.decision_history(decision_id);
CREATE INDEX idx_decision_history_timestamp ON decision.decision_history(changed_at);
CREATE INDEX idx_decision_history_changed_by ON decision.decision_history(changed_by);

COMMENT ON TABLE decision.decision_history IS 'Immutable history of all decision status changes';

-- Decision Overrides
-- Officer overrides of automated decisions
CREATE TABLE IF NOT EXISTS decision.decision_overrides (
    override_id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Original Decision
    original_decision_type VARCHAR(50) NOT NULL,
    original_risk_score DECIMAL(5,4),
    original_routing_reason TEXT,
    
    -- Override Decision
    override_decision_type VARCHAR(50) NOT NULL,
    override_reason TEXT NOT NULL, -- Mandatory justification
    override_details JSONB,
    
    -- Officer Information
    officer_id VARCHAR(100) NOT NULL,
    officer_name VARCHAR(255),
    officer_role VARCHAR(100),
    
    -- Approval (for high-risk overrides)
    requires_supervisor_approval BOOLEAN DEFAULT false,
    supervisor_approved BOOLEAN,
    supervisor_id VARCHAR(100),
    supervisor_approved_at TIMESTAMP,
    
    -- Timestamps
    overridden_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_override CHECK (
        (original_decision_type != override_decision_type) OR
        (override_reason IS NOT NULL AND LENGTH(override_reason) > 10)
    )
);

CREATE INDEX idx_overrides_decision ON decision.decision_overrides(decision_id);
CREATE INDEX idx_overrides_officer ON decision.decision_overrides(officer_id);
CREATE INDEX idx_overrides_timestamp ON decision.decision_overrides(overridden_at);

COMMENT ON TABLE decision.decision_overrides IS 'Officer overrides of automated decisions with mandatory justification';

-- ============================================================================
-- RISK MODELS MANAGEMENT
-- ============================================================================

-- Risk Models
-- ML model metadata and versioning
CREATE TABLE IF NOT EXISTS decision.risk_models (
    model_id SERIAL PRIMARY KEY,
    
    -- Model Identification
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- xgboost, logistic_regression, random_forest
    model_version VARCHAR(50) NOT NULL,
    scheme_code VARCHAR(50) REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    category VARCHAR(50), -- HEALTH, EDUCATION, PENSION, etc. (NULL = general model)
    
    -- Model Storage
    model_path TEXT, -- Path to saved model file
    model_artifact_uri TEXT, -- MLflow artifact URI
    
    -- Model Performance
    training_accuracy DECIMAL(5,4),
    validation_accuracy DECIMAL(5,4),
    test_accuracy DECIMAL(5,4),
    auc_score DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    performance_metrics JSONB, -- Additional metrics
    
    -- Training Information
    training_data_range_start DATE,
    training_data_range_end DATE,
    training_samples_count INTEGER,
    feature_list TEXT[], -- Features used in training
    
    -- Model Status
    is_active BOOLEAN DEFAULT false,
    is_production BOOLEAN DEFAULT false,
    deployed_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trained_at TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255),
    training_script_path TEXT,
    hyperparameters JSONB,
    
    UNIQUE(model_name, model_version)
);

CREATE INDEX idx_risk_models_type ON decision.risk_models(model_type);
CREATE INDEX idx_risk_models_scheme ON decision.risk_models(scheme_code);
CREATE INDEX idx_risk_models_active ON decision.risk_models(is_active) WHERE is_active = true;
CREATE INDEX idx_risk_models_production ON decision.risk_models(is_production) WHERE is_production = true;

COMMENT ON TABLE decision.risk_models IS 'ML model metadata and versioning for risk scoring';

-- ============================================================================
-- DECISION CONFIGURATION
-- ============================================================================

-- Decision Configuration
-- Per-scheme decision thresholds and rules
CREATE TABLE IF NOT EXISTS decision.decision_config (
    config_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Risk Thresholds
    low_risk_max DECIMAL(5,4) DEFAULT 0.3,
    medium_risk_min DECIMAL(5,4) DEFAULT 0.3,
    medium_risk_max DECIMAL(5,4) DEFAULT 0.7,
    high_risk_min DECIMAL(5,4) DEFAULT 0.7,
    
    -- Auto Approval Configuration
    enable_auto_approval BOOLEAN DEFAULT true,
    require_document_verification BOOLEAN DEFAULT true,
    require_bank_validation BOOLEAN DEFAULT true,
    
    -- Routing Configuration
    route_medium_risk_to_officer BOOLEAN DEFAULT true,
    route_high_risk_to_fraud BOOLEAN DEFAULT true,
    require_human_review_medium BOOLEAN DEFAULT true,
    require_human_review_high BOOLEAN DEFAULT true,
    
    -- Model Configuration
    default_model_id INTEGER REFERENCES decision.risk_models(model_id) ON DELETE SET NULL,
    model_type VARCHAR(50), -- Override default model type
    
    -- Additional Rules
    auto_reject_rules TEXT[], -- Rules that trigger auto reject
    mandatory_checks TEXT[], -- Mandatory checks before auto approval
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_until TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    UNIQUE(scheme_code, effective_from)
);

CREATE INDEX idx_decision_config_scheme ON decision.decision_config(scheme_code);
CREATE INDEX idx_decision_config_active ON decision.decision_config(is_active) WHERE is_active = true;

COMMENT ON TABLE decision.decision_config IS 'Per-scheme decision configuration and thresholds';

-- ============================================================================
-- EXTERNAL VERIFICATIONS
-- ============================================================================

-- External Verifications
-- Results from external verification services (Aadhaar, bank, etc.)
CREATE TABLE IF NOT EXISTS decision.external_verifications (
    verification_id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Verification Type
    verification_type VARCHAR(50) NOT NULL,
    -- AADHAAR_KYC, BANK_VALIDATION, NAME_MATCH, DOCUMENT_VERIFICATION, CROSS_SCHEME_CHECK
    
    -- Verification Details
    verification_service VARCHAR(100), -- Service/provider name
    verification_status VARCHAR(50) NOT NULL, -- SUCCESS, FAILED, PENDING, ERROR
    verification_result JSONB, -- Detailed verification result
    
    -- Reference Data
    reference_id VARCHAR(255), -- Aadhaar number, account number, etc. (hashed if sensitive)
    reference_type VARCHAR(50),
    
    -- Timestamps
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_duration_ms INTEGER
);

CREATE INDEX idx_verifications_decision ON decision.external_verifications(decision_id);
CREATE INDEX idx_verifications_type ON decision.external_verifications(verification_type);
CREATE INDEX idx_verifications_status ON decision.external_verifications(verification_status);

COMMENT ON TABLE decision.external_verifications IS 'External verification results (Aadhaar, bank, etc.)';

-- ============================================================================
-- AUDIT & COMPLIANCE
-- ============================================================================

-- Decision Audit Logs
-- Comprehensive audit trail for compliance
CREATE TABLE IF NOT EXISTS decision.decision_audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Audit Event
    event_type VARCHAR(100) NOT NULL,
    -- DECISION_CREATED, RULE_EVALUATED, RISK_SCORED, DECISION_ROUTED, 
    -- DECISION_OVERRIDDEN, PAYMENT_TRIGGERED, etc.
    event_description TEXT,
    
    -- Event Data
    event_data JSONB, -- Complete event data for audit
    
    -- Input Snapshot (hashed for sensitive data)
    input_snapshot_hash VARCHAR(255), -- Hash of input data snapshot
    input_snapshot_uri TEXT, -- URI to full snapshot if stored separately
    
    -- Context
    model_version VARCHAR(50),
    thresholds_used JSONB,
    rules_evaluated TEXT[],
    
    -- Actor
    actor_type VARCHAR(50), -- system, officer, citizen, admin
    actor_id VARCHAR(255),
    actor_name VARCHAR(255),
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_decision ON decision.decision_audit_logs(decision_id);
CREATE INDEX idx_audit_event_type ON decision.decision_audit_logs(event_type);
CREATE INDEX idx_audit_timestamp ON decision.decision_audit_logs(event_timestamp);
CREATE INDEX idx_audit_actor ON decision.decision_audit_logs(actor_type, actor_id);

COMMENT ON TABLE decision.decision_audit_logs IS 'Comprehensive audit trail for compliance and explainability';

-- Fairness Monitoring
-- Track decision patterns for bias detection
CREATE TABLE IF NOT EXISTS decision.fairness_metrics (
    metric_id SERIAL PRIMARY KEY,
    
    -- Metric Period
    metric_period_start DATE NOT NULL,
    metric_period_end DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- DAILY, WEEKLY, MONTHLY
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Scheme
    scheme_code VARCHAR(50) REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Demographic Breakdown (for fairness analysis)
    demographic_category VARCHAR(50), -- GENDER, CASTE, DISTRICT, AGE_BAND, etc.
    demographic_value VARCHAR(100), -- MALE, FEMALE, SC, ST, etc.
    
    -- Metrics
    total_decisions INTEGER DEFAULT 0,
    auto_approved_count INTEGER DEFAULT 0,
    officer_reviewed_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    override_count INTEGER DEFAULT 0,
    
    -- Approval Rates
    auto_approval_rate DECIMAL(5,4),
    overall_approval_rate DECIMAL(5,4),
    
    -- Average Risk Scores
    avg_risk_score DECIMAL(5,4),
    
    -- Additional Metrics
    additional_metrics JSONB
);

CREATE INDEX idx_fairness_period ON decision.fairness_metrics(metric_period_start, metric_period_end);
CREATE INDEX idx_fairness_scheme ON decision.fairness_metrics(scheme_code);
CREATE INDEX idx_fairness_category ON decision.fairness_metrics(demographic_category, demographic_value);

COMMENT ON TABLE decision.fairness_metrics IS 'Fairness metrics for bias detection and monitoring';

-- ============================================================================
-- PAYMENT INTEGRATION
-- ============================================================================

-- Payment Triggers
-- Records of payment/DBT triggers for auto-approved applications
CREATE TABLE IF NOT EXISTS decision.payment_triggers (
    trigger_id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decision.decisions(decision_id) ON DELETE CASCADE,
    
    -- Payment Information
    payment_status VARCHAR(50) DEFAULT 'pending',
    -- pending, triggered, processing, completed, failed
    payment_system VARCHAR(50), -- JAN_AADHAAR_DBT, BANK_TRANSFER, etc.
    payment_reference_id VARCHAR(255),
    
    -- Payment Details
    payment_amount DECIMAL(12,2),
    payment_account VARCHAR(255), -- Bank account (hashed)
    payment_beneficiary_name VARCHAR(255),
    
    -- Validation Results
    bank_validation_status VARCHAR(50),
    name_match_status VARCHAR(50),
    jan_aadhaar_validation_status VARCHAR(50),
    
    -- Timestamps
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Error Information
    error_message TEXT,
    error_details JSONB
);

CREATE INDEX idx_payment_triggers_decision ON decision.payment_triggers(decision_id);
CREATE INDEX idx_payment_triggers_status ON decision.payment_triggers(payment_status);
CREATE INDEX idx_payment_triggers_timestamp ON decision.payment_triggers(triggered_at);

COMMENT ON TABLE decision.payment_triggers IS 'Payment/DBT triggers for auto-approved applications';

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION decision.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_decisions_updated_at
    BEFORE UPDATE ON decision.decisions
    FOR EACH ROW
    EXECUTE FUNCTION decision.update_updated_at_column();

CREATE TRIGGER update_decision_config_updated_at
    BEFORE UPDATE ON decision.decision_config
    FOR EACH ROW
    EXECUTE FUNCTION decision.update_updated_at_column();

CREATE TRIGGER update_risk_models_updated_at
    BEFORE UPDATE ON decision.risk_models
    FOR EACH ROW
    EXECUTE FUNCTION decision.update_updated_at_column();

-- Trigger to log decision history
CREATE OR REPLACE FUNCTION decision.log_decision_history()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO decision.decision_history (
            decision_id, to_status, to_decision_type,
            change_reason, changed_by, changed_by_type
        ) VALUES (
            NEW.decision_id, NEW.decision_status, NEW.decision_type,
            'Initial decision created', NEW.decision_by, 'system'
        );
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF (OLD.decision_status IS DISTINCT FROM NEW.decision_status OR 
            OLD.decision_type IS DISTINCT FROM NEW.decision_type) THEN
            INSERT INTO decision.decision_history (
                decision_id, from_status, to_status,
                from_decision_type, to_decision_type,
                change_reason, changed_by, changed_by_type
            ) VALUES (
                NEW.decision_id, OLD.decision_status, NEW.decision_status,
                OLD.decision_type, NEW.decision_type,
                COALESCE(NEW.routing_reason, 'Status changed'), 
                NEW.decision_by, 'system'
            );
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_decision_history_trigger
    AFTER INSERT OR UPDATE ON decision.decisions
    FOR EACH ROW
    EXECUTE FUNCTION decision.log_decision_history();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON SCHEMA decision IS 'Auto Approval & Straight-through Processing - Decision and Risk Management Schema';

