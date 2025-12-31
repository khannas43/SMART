-- Auto Identification of Beneficiaries Database Schema (CONSOLIDATED)
-- Use Case ID: AI-PLATFORM-03
-- Database: smart_warehouse (consolidated with AI-PLATFORM-02)
-- Schema: eligibility

-- Note: This schema is part of smart_warehouse database
-- All AI/ML use cases use the same smart_warehouse database with different schemas for organization
-- 
-- IMPORTANT: scheme_master table is SHARED (in public schema, not duplicated here)
-- This schema only adds eligibility-specific tables

CREATE SCHEMA IF NOT EXISTS eligibility;

-- ============================================================================
-- SCHEME RULES CONFIGURATION
-- ============================================================================

-- NOTE: scheme_master table is in public schema (shared with AI-PLATFORM-02)
-- We reference it, not duplicate it
-- If you need to add eligibility-specific fields, use a view or extension table

-- Scheme Eligibility Rules (Machine-readable rules)
-- References scheme_master.scheme_id (which is INTEGER in public schema)
-- For compatibility, we'll use scheme_code (VARCHAR) as the link
CREATE TABLE IF NOT EXISTS eligibility.scheme_eligibility_rules (
    rule_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL, -- Links to public.scheme_master.scheme_code
    scheme_id INTEGER, -- Cached reference to scheme_master.scheme_id (for performance)
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50), -- AGE, INCOME, GENDER, DISABILITY, GEOGRAPHY, CATEGORY, etc.
    rule_expression TEXT NOT NULL, -- e.g., "age >= 60", "income_band IN ('VERY_LOW', 'LOW')"
    rule_operator VARCHAR(20), -- >=, <=, =, IN, NOT_IN, EXISTS, etc.
    rule_value TEXT, -- Value or list of values
    is_mandatory BOOLEAN DEFAULT true, -- Must pass vs optional condition
    priority INTEGER DEFAULT 0, -- Evaluation priority
    version INTEGER DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Foreign key to public.scheme_master via scheme_code
    CONSTRAINT fk_scheme_code FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE
);

CREATE INDEX idx_eligibility_rules_scheme ON eligibility.scheme_eligibility_rules(scheme_code);
CREATE INDEX idx_eligibility_rules_type ON eligibility.scheme_eligibility_rules(rule_type);
CREATE INDEX idx_eligibility_rules_active ON eligibility.scheme_eligibility_rules(effective_from, effective_to);

-- Scheme Exclusion Rules (Who is NOT eligible)
CREATE TABLE IF NOT EXISTS eligibility.scheme_exclusion_rules (
    exclusion_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL, -- Links to public.scheme_master.scheme_code
    scheme_id INTEGER, -- Cached reference
    exclusion_condition TEXT NOT NULL, -- e.g., "already_enrolled = true", "benefits_received_1y > threshold"
    exclusion_type VARCHAR(50), -- ALREADY_ENROLLED, INCOME_EXCEEDED, AGE_NOT_MET, etc.
    version INTEGER DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exclusion_scheme_code FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE
);

-- ============================================================================
-- ELIGIBILITY EVALUATION RESULTS
-- ============================================================================

-- Eligibility Snapshots (Main table storing evaluation results)
CREATE TABLE IF NOT EXISTS eligibility.eligibility_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL, -- Jan Aadhaar family ID
    member_id UUID, -- If scheme is member-level (NULL for family-level schemes)
    scheme_code VARCHAR(50) NOT NULL, -- Links to public.scheme_master.scheme_code
    scheme_id INTEGER, -- Cached reference to scheme_master.scheme_id
    
    -- Evaluation Status
    evaluation_status VARCHAR(50) NOT NULL, -- RULE_ELIGIBLE, NOT_ELIGIBLE, POSSIBLE_ELIGIBLE, UNCERTAIN
    eligibility_score DECIMAL(5,4), -- ML probability score (0-1)
    confidence_score DECIMAL(5,4), -- Confidence in the evaluation (0-1)
    
    -- Rule Engine Results
    rule_eligible BOOLEAN,
    rules_passed TEXT[], -- List of rule IDs that passed
    rules_failed TEXT[], -- List of rule IDs that failed
    rule_path TEXT, -- Human-readable rule path, e.g., "Age >= 60, BPL, Widow"
    
    -- ML Model Results
    ml_probability DECIMAL(5,4),
    ml_model_version VARCHAR(50),
    ml_top_features JSONB, -- Top contributing features with SHAP values
    
    -- Prioritization
    priority_score DECIMAL(10,4), -- Combined score for ranking
    vulnerability_level VARCHAR(20), -- VERY_HIGH, HIGH, MEDIUM, LOW (from 360° Profile)
    under_coverage_indicator BOOLEAN, -- True if identified as under-covered
    
    -- Reason Codes
    reason_codes TEXT[], -- Which conditions met/failed
    explanation TEXT, -- Human-readable explanation
    
    -- Metadata
    evaluation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    evaluation_type VARCHAR(20), -- BATCH, EVENT_DRIVEN, ON_DEMAND
    evaluation_version INTEGER DEFAULT 1,
    model_version VARCHAR(50),
    rule_version INTEGER,
    
    -- Version tracking (added by versioning extension)
    rule_set_version VARCHAR(50),
    rule_set_snapshot_id INTEGER,
    dataset_version_golden_records VARCHAR(50),
    dataset_version_profile_360 VARCHAR(50),
    dataset_version_jrdr VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(family_id, member_id, scheme_code, evaluation_timestamp, evaluation_version)
);

-- Indexes for Eligibility Snapshots
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_family_id ON eligibility.eligibility_snapshots(family_id);
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_scheme_code ON eligibility.eligibility_snapshots(scheme_code);
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_status ON eligibility.eligibility_snapshots(evaluation_status);
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_timestamp ON eligibility.eligibility_snapshots(evaluation_timestamp);
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_rule_version ON eligibility.eligibility_snapshots(rule_set_version);

-- Candidate Lists (Pre-computed worklists)
CREATE TABLE IF NOT EXISTS eligibility.candidate_lists (
    list_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL, -- Links to public.scheme_master.scheme_code
    scheme_id INTEGER, -- Cached reference
    list_type VARCHAR(50) NOT NULL, -- CITIZEN_HINTS, DEPARTMENTAL_WORKLIST, AUTO_INTIMATION
    family_id UUID NOT NULL,
    member_id UUID,
    
    -- Ranking
    rank_in_scheme INTEGER NOT NULL,
    priority_score DECIMAL(10,4),
    eligibility_score DECIMAL(5,4),
    confidence_score DECIMAL(5,4),
    
    -- Metadata
    district_id INTEGER,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Expiry
    expires_at TIMESTAMP,
    
    UNIQUE(scheme_code, list_type, family_id, member_id, generated_at)
);

-- Indexes for Candidate Lists
CREATE INDEX IF NOT EXISTS idx_candidate_lists_scheme_district ON eligibility.candidate_lists(scheme_code, district_id);
CREATE INDEX IF NOT EXISTS idx_candidate_lists_rank ON eligibility.candidate_lists(scheme_code, rank_in_scheme);
CREATE INDEX IF NOT EXISTS idx_candidate_lists_type ON eligibility.candidate_lists(list_type, is_active);

-- ============================================================================
-- ML MODEL METADATA
-- ============================================================================

-- ML Model Registry (Tracks model versions per scheme)
CREATE TABLE IF NOT EXISTS eligibility.ml_model_registry (
    model_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL, -- Links to public.scheme_master.scheme_code
    scheme_id INTEGER, -- Cached reference
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- xgboost, random_forest, etc.
    model_path VARCHAR(500), -- Path to model file
    mlflow_run_id VARCHAR(100), -- MLflow run ID
    
    -- Training Info
    training_data_range_start DATE,
    training_data_range_end DATE,
    training_samples_count INTEGER,
    training_metrics JSONB, -- accuracy, precision, recall, etc.
    
    -- Feature Info
    feature_list TEXT[], -- List of features used
    feature_importance JSONB, -- Feature importance scores
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_production BOOLEAN DEFAULT false,
    deployed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(scheme_code, model_version),
    CONSTRAINT fk_model_scheme_code FOREIGN KEY (scheme_code) REFERENCES scheme_master(scheme_code) ON DELETE CASCADE
);

-- ============================================================================
-- AUDIT & GOVERNANCE
-- ============================================================================

-- Evaluation Audit Log
CREATE TABLE IF NOT EXISTS eligibility.evaluation_audit_log (
    audit_id SERIAL PRIMARY KEY,
    family_id UUID,
    scheme_code VARCHAR(50),
    evaluation_timestamp TIMESTAMP,
    evaluation_type VARCHAR(20),
    evaluation_status VARCHAR(50),
    eligibility_score DECIMAL(5,4),
    rule_path TEXT,
    explanation TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_type VARCHAR(50) -- EVALUATION, RULE_CHANGE, MODEL_UPDATE, THRESHOLD_CHANGE
);

-- Rule Change History
CREATE TABLE IF NOT EXISTS eligibility.rule_change_history (
    change_id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES eligibility.scheme_eligibility_rules(rule_id) ON DELETE SET NULL,
    scheme_code VARCHAR(50),
    change_type VARCHAR(50), -- CREATED, UPDATED, DELETED, ACTIVATED, DEACTIVATED
    old_value JSONB,
    new_value JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Batch Evaluation Jobs
CREATE TABLE IF NOT EXISTS eligibility.batch_evaluation_jobs (
    job_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    job_type VARCHAR(50), -- FULL_SCAN, INCREMENTAL, SCHEME_SPECIFIC
    scheme_codes VARCHAR(50)[], -- Array of scheme codes
    district_ids INTEGER[],
    family_id_range_start UUID,
    family_id_range_end UUID,
    
    -- Status
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED
    families_processed INTEGER DEFAULT 0,
    total_families INTEGER,
    evaluations_created INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

-- Consent Status
CREATE TABLE IF NOT EXISTS eligibility.consent_status (
    consent_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID,
    consent_type VARCHAR(50) NOT NULL, -- ELIGIBILITY_PROCESSING, PROXY_DATA_USE, etc.
    has_consent BOOLEAN DEFAULT false,
    consent_date DATE,
    consent_source VARCHAR(100), -- Where consent was obtained
    expires_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(family_id, member_id, consent_type)
);

-- Data Quality Indicators
CREATE TABLE IF NOT EXISTS eligibility.data_quality_indicators (
    quality_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    indicator_type VARCHAR(50), -- COMPLETENESS, ACCURACY, TIMELINESS, etc.
    indicator_value DECIMAL(5,4), -- 0-1 score
    data_source VARCHAR(100),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(family_id, indicator_type, evaluated_at)
);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON SCHEMA eligibility IS 'Schema for Auto Identification of Beneficiaries (AI-PLATFORM-03)';
COMMENT ON TABLE eligibility.scheme_eligibility_rules IS 'Machine-readable eligibility rules per scheme (references public.scheme_master)';
COMMENT ON TABLE eligibility.eligibility_snapshots IS 'Main table storing eligibility evaluation results per family/scheme';
COMMENT ON TABLE eligibility.candidate_lists IS 'Pre-computed worklists for citizen hints and departmental queues';
COMMENT ON TABLE eligibility.ml_model_registry IS 'ML model metadata per scheme (references public.scheme_master)';

