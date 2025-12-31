-- Auto Identification of Beneficiaries Database Schema
-- Use Case ID: AI-PLATFORM-03
-- Database: smart_warehouse (consolidated with AI-PLATFORM-02)
-- Schema: eligibility

-- Note: This schema is part of smart_warehouse database
-- All AI/ML use cases (02_eligibility_scoring_360_profile and 03_identification_beneficiary) 
-- use the same smart_warehouse database with different schemas for organization

CREATE SCHEMA IF NOT EXISTS eligibility;

-- Grant permissions to sameer user
GRANT USAGE ON SCHEMA eligibility TO sameer;
GRANT CREATE ON SCHEMA eligibility TO sameer;
ALTER SCHEMA eligibility OWNER TO sameer;

-- ============================================================================
-- SCHEME RULES CONFIGURATION
-- ============================================================================

-- NOTE: scheme_master table is SHARED in public schema (from AI-PLATFORM-02)
-- We do NOT create a duplicate here. Instead:
-- 1. Extend public.scheme_master with eligibility fields (see migrate_scheme_master.sql)
-- 2. Reference via scheme_code in eligibility tables
-- 3. Use eligibility.scheme_master_view for convenience

-- If public.scheme_master doesn't have eligibility fields, run migration:
-- ALTER TABLE scheme_master 
-- ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
-- ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20);

-- Scheme Eligibility Rules (Machine-readable rules)
-- References public.scheme_master via scheme_code
CREATE TABLE IF NOT EXISTS eligibility.scheme_eligibility_rules (
    rule_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
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
    UNIQUE(scheme_code, rule_name, version)
);

-- Scheme Exclusion Rules (Who is NOT eligible)
-- References public.scheme_master via scheme_code
CREATE TABLE IF NOT EXISTS eligibility.scheme_exclusion_rules (
    exclusion_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES scheme_master(scheme_code) ON DELETE CASCADE,
    scheme_id INTEGER, -- Cached reference
    exclusion_condition TEXT NOT NULL, -- e.g., "already_enrolled = true", "benefits_received_1y > threshold"
    exclusion_type VARCHAR(50), -- ALREADY_ENROLLED, INCOME_EXCEEDED, AGE_NOT_MET, etc.
    version INTEGER DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ELIGIBILITY EVALUATION RESULTS
-- ============================================================================

-- Eligibility Snapshots (Main table storing evaluation results)
-- References public.scheme_master via scheme_code
CREATE TABLE IF NOT EXISTS eligibility.eligibility_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL, -- Jan Aadhaar family ID
    member_id UUID, -- If scheme is member-level (NULL for family-level schemes)
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
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
CREATE INDEX IF NOT EXISTS idx_eligibility_snapshots_priority ON eligibility.eligibility_snapshots(priority_score DESC NULLS LAST);

-- ============================================================================
-- CANDIDATE LISTS (For departmental worklists)
-- ============================================================================

-- Candidate Lists (Pre-computed worklists for departments)
-- References public.scheme_master via scheme_code
CREATE TABLE IF NOT EXISTS eligibility.candidate_lists (
    candidate_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    family_id UUID NOT NULL,
    member_id UUID,
    snapshot_id INTEGER REFERENCES eligibility.eligibility_snapshots(snapshot_id),
    
    -- Ranking
    rank_in_scheme INTEGER, -- Rank within scheme
    rank_in_district INTEGER, -- Rank within district
    rank_in_cluster INTEGER, -- Rank within cluster/ward
    
    -- Geographic Context
    district_id INTEGER,
    block_id INTEGER,
    village_id INTEGER,
    cluster_id VARCHAR(50), -- From 360° Profile graph clustering
    
    -- Metadata
    list_type VARCHAR(50), -- CITIZEN_HINTS, DEPARTMENT_WORKLIST, AUTO_INTIMATION
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP, -- When candidate list entry expires
    
    UNIQUE(scheme_code, family_id, member_id, list_type, generated_at)
);

-- Indexes for Candidate Lists
CREATE INDEX IF NOT EXISTS idx_candidate_lists_scheme_district ON eligibility.candidate_lists(scheme_code, district_id);
CREATE INDEX IF NOT EXISTS idx_candidate_lists_rank ON eligibility.candidate_lists(scheme_code, rank_in_scheme);
CREATE INDEX IF NOT EXISTS idx_candidate_lists_type ON eligibility.candidate_lists(list_type, is_active);

-- ============================================================================
-- ML MODEL METADATA
-- ============================================================================

-- ML Model Registry (Tracks model versions per scheme)
-- References public.scheme_master via scheme_code
CREATE TABLE IF NOT EXISTS eligibility.ml_model_registry (
    model_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
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
    
    UNIQUE(scheme_code, model_version)
);

-- ============================================================================
-- AUDIT & GOVERNANCE
-- ============================================================================

-- Evaluation Audit Log
CREATE TABLE IF NOT EXISTS eligibility.evaluation_audit_log (
    audit_id SERIAL PRIMARY KEY,
    evaluation_type VARCHAR(20), -- BATCH, EVENT_DRIVEN, ON_DEMAND
    batch_id VARCHAR(100), -- For batch evaluations
    family_id UUID,
    scheme_id VARCHAR(50),
    
    -- Changes
    action_type VARCHAR(50), -- EVALUATION, RULE_CHANGE, MODEL_UPDATE, THRESHOLD_CHANGE
    change_description TEXT,
    
    -- Before/After (for changes)
    before_value JSONB,
    after_value JSONB,
    
    -- Metadata
    performed_by VARCHAR(100), -- System or user
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT
);

-- Rule Change History
CREATE TABLE IF NOT EXISTS eligibility.rule_change_history (
    change_id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES eligibility.scheme_eligibility_rules(rule_id),
    scheme_code VARCHAR(50) REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    change_type VARCHAR(50), -- CREATED, UPDATED, DELETED, ACTIVATED, DEACTIVATED
    old_value JSONB,
    new_value JSONB,
    change_reason TEXT,
    
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- BATCH PROCESSING
-- ============================================================================

-- Batch Evaluation Jobs
CREATE TABLE IF NOT EXISTS eligibility.batch_evaluation_jobs (
    job_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    job_type VARCHAR(50), -- FULL_SCAN, INCREMENTAL, SCHEME_SPECIFIC
    
    -- Scope
    scheme_ids TEXT[], -- NULL for all schemes
    district_ids INTEGER[],
    family_id_range_start UUID,
    family_id_range_end UUID,
    
    -- Status
    status VARCHAR(50) NOT NULL, -- PENDING, RUNNING, COMPLETED, FAILED
    progress_percentage INTEGER DEFAULT 0,
    
    -- Statistics
    total_families INTEGER,
    families_processed INTEGER DEFAULT 0,
    evaluations_created INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    error_message TEXT
);

-- ============================================================================
-- CONSENT & DATA QUALITY
-- ============================================================================

-- Consent Status (links to data governance platform)
CREATE TABLE IF NOT EXISTS eligibility.consent_status (
    consent_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    member_id UUID,
    
    -- Consent Flags
    eligibility_processing_consent BOOLEAN DEFAULT false,
    proxy_data_consent BOOLEAN DEFAULT false,
    auto_intimation_consent BOOLEAN DEFAULT false,
    
    -- Metadata
    consent_given_at TIMESTAMP,
    consent_withdrawn_at TIMESTAMP,
    consent_version INTEGER DEFAULT 1,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(family_id, member_id)
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
-- INITIAL DATA: Scheme Master
-- ============================================================================
-- NOTE: Initial scheme data should be loaded into public.scheme_master
-- Use scripts/load_initial_schemes.sql or extend_scheme_master.sql migration
-- This file does not insert into scheme_master as it uses public.scheme_master

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON SCHEMA eligibility IS 'Schema for Auto Identification of Beneficiaries (AI-PLATFORM-03)';
COMMENT ON TABLE eligibility.eligibility_snapshots IS 'Main table storing eligibility evaluation results per family/scheme';
COMMENT ON TABLE eligibility.candidate_lists IS 'Pre-computed worklists for citizen hints and departmental queues';
COMMENT ON TABLE eligibility.scheme_eligibility_rules IS 'Machine-readable eligibility rules per scheme';

