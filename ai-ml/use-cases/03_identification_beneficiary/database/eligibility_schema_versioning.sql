-- Enhanced Schema for Rule Versioning and Historical Tracking
-- Use Case ID: AI-PLATFORM-03
-- This extends the base schema with version control capabilities

-- ============================================================================
-- RULE SET SNAPSHOTS
-- ============================================================================

-- Rule Set Snapshots: Store complete rule sets at specific points in time
CREATE TABLE IF NOT EXISTS eligibility.rule_set_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    snapshot_name VARCHAR(200), -- e.g., "Rule Set v2.0 - Dec 2024"
    snapshot_version VARCHAR(50) NOT NULL, -- e.g., "v2.0"
    snapshot_date DATE NOT NULL,
    
    -- Rule data (denormalized for snapshot)
    rule_ids INTEGER[], -- Array of rule IDs active at this snapshot
    rule_data JSONB,    -- Complete rule definitions (JSON array)
    
    -- Exclusion rules
    exclusion_rule_ids INTEGER[],
    exclusion_rule_data JSONB,
    
    -- Metadata
    description TEXT,
    change_summary TEXT, -- What changed from previous snapshot
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(scheme_code, snapshot_version)
);

CREATE INDEX idx_rule_set_snapshots_scheme ON eligibility.rule_set_snapshots(scheme_code);
CREATE INDEX idx_rule_set_snapshots_date ON eligibility.rule_set_snapshots(snapshot_date);

-- ============================================================================
-- DATASET VERSIONS
-- ============================================================================

-- Dataset Versions: Track versions of source datasets
CREATE TABLE IF NOT EXISTS eligibility.dataset_versions (
    dataset_version_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL, -- 'golden_records', 'profile_360', 'jrdr'
    version VARCHAR(50) NOT NULL, -- e.g., "v2.1", "2024-12-27"
    version_date DATE NOT NULL,
    
    -- Dataset metadata
    description TEXT,
    metadata JSONB, -- Record counts, schema changes, data quality metrics
    schema_hash VARCHAR(64), -- Hash of schema for change detection
    
    -- Source information
    source_system VARCHAR(100),
    extraction_date TIMESTAMP,
    total_records BIGINT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(dataset_name, version)
);

CREATE INDEX idx_dataset_versions_name ON eligibility.dataset_versions(dataset_name);
CREATE INDEX idx_dataset_versions_date ON eligibility.dataset_versions(version_date);

-- ============================================================================
-- ENHANCE ELIGIBILITY SNAPSHOTS FOR VERSION TRACKING
-- ============================================================================

-- Add version columns to eligibility_snapshots (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'eligibility' 
        AND table_name = 'eligibility_snapshots' 
        AND column_name = 'rule_set_version'
    ) THEN
        ALTER TABLE eligibility.eligibility_snapshots
        ADD COLUMN rule_set_version VARCHAR(50),
        ADD COLUMN rule_set_snapshot_id INTEGER REFERENCES eligibility.rule_set_snapshots(snapshot_id),
        ADD COLUMN dataset_version_golden_records VARCHAR(50),
        ADD COLUMN dataset_version_profile_360 VARCHAR(50),
        ADD COLUMN dataset_version_jrdr VARCHAR(50);
        
        CREATE INDEX idx_eligibility_snapshots_rule_version 
        ON eligibility.eligibility_snapshots(rule_set_version);
        
        CREATE INDEX idx_eligibility_snapshots_dataset_version 
        ON eligibility.eligibility_snapshots(dataset_version_golden_records, dataset_version_profile_360);
    END IF;
END $$;

-- ============================================================================
-- RULE CHANGE TRACKING (Enhanced)
-- ============================================================================

-- Enhanced rule change history with detailed diff
CREATE TABLE IF NOT EXISTS eligibility.rule_change_detail (
    change_detail_id SERIAL PRIMARY KEY,
    change_id INTEGER REFERENCES eligibility.rule_change_history(change_id),
    
    -- What changed
    field_name VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    change_type VARCHAR(50), -- CREATED, UPDATED, DELETED, ACTIVATED, DEACTIVATED
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EVALUATION COMPARISON
-- ============================================================================

-- Compare evaluations across rule versions
CREATE TABLE IF NOT EXISTS eligibility.evaluation_comparison (
    comparison_id SERIAL PRIMARY KEY,
    family_id UUID NOT NULL,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Rule set versions being compared
    rule_set_version_old VARCHAR(50),
    rule_set_version_new VARCHAR(50),
    
    -- Evaluation results
    evaluation_old_snapshot_id INTEGER REFERENCES eligibility.eligibility_snapshots(snapshot_id),
    evaluation_new_snapshot_id INTEGER REFERENCES eligibility.eligibility_snapshots(snapshot_id),
    
    -- Comparison metrics
    status_changed BOOLEAN,
    score_delta DECIMAL(5,4), -- Change in eligibility score
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    
    -- Metadata
    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compared_by VARCHAR(100)
);

CREATE INDEX idx_evaluation_comparison_family ON eligibility.evaluation_comparison(family_id);
CREATE INDEX idx_evaluation_comparison_scheme ON eligibility.evaluation_comparison(scheme_code);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to create rule set snapshot
CREATE OR REPLACE FUNCTION eligibility.create_rule_set_snapshot(
    p_scheme_code VARCHAR(50),
    p_snapshot_version VARCHAR(50),
    p_snapshot_name VARCHAR(200),
    p_description TEXT,
    p_created_by VARCHAR(100)
) RETURNS INTEGER AS $$
DECLARE
    v_snapshot_id INTEGER;
    v_rule_data JSONB;
    v_exclusion_data JSONB;
BEGIN
    -- Collect all active rules for the scheme
    SELECT jsonb_agg(
        jsonb_build_object(
            'rule_id', rule_id,
            'rule_name', rule_name,
            'rule_type', rule_type,
            'rule_expression', rule_expression,
            'rule_operator', rule_operator,
            'rule_value', rule_value,
            'is_mandatory', is_mandatory,
            'priority', priority,
            'version', version,
            'effective_from', effective_from,
            'effective_to', effective_to
        )
    ) INTO v_rule_data
    FROM eligibility.scheme_eligibility_rules
    WHERE scheme_code = p_scheme_code
        AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
        AND (effective_from <= CURRENT_DATE);
    
    -- Collect exclusion rules
    SELECT jsonb_agg(
        jsonb_build_object(
            'exclusion_id', exclusion_id,
            'exclusion_condition', exclusion_condition,
            'exclusion_type', exclusion_type
        )
    ) INTO v_exclusion_data
    FROM eligibility.scheme_exclusion_rules
    WHERE scheme_code = p_scheme_code
        AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
        AND (effective_from <= CURRENT_DATE);
    
    -- Insert snapshot
    INSERT INTO eligibility.rule_set_snapshots (
        scheme_code, snapshot_version, snapshot_name, snapshot_date,
        rule_data, exclusion_rule_data, description, created_by
    ) VALUES (
        p_scheme_code, p_snapshot_version, p_snapshot_name, CURRENT_DATE,
        v_rule_data, v_exclusion_data, p_description, p_created_by
    ) RETURNING snapshot_id INTO v_snapshot_id;
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get current dataset versions
CREATE OR REPLACE FUNCTION eligibility.get_current_dataset_versions()
RETURNS TABLE (
    dataset_name VARCHAR(100),
    version VARCHAR(50),
    version_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dv.dataset_name,
        dv.version,
        dv.version_date
    FROM eligibility.dataset_versions dv
    WHERE (dataset_name, version_date) IN (
        SELECT dataset_name, MAX(version_date)
        FROM eligibility.dataset_versions
        GROUP BY dataset_name
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE eligibility.rule_set_snapshots IS 'Snapshots of rule sets at specific points in time for historical tracking';
COMMENT ON TABLE eligibility.dataset_versions IS 'Versions of source datasets used for evaluation';
COMMENT ON TABLE eligibility.evaluation_comparison IS 'Compare evaluation results across different rule versions';
COMMENT ON FUNCTION eligibility.create_rule_set_snapshot IS 'Create a snapshot of current rule set for a scheme';

