-- AI-PLATFORM-02: 360° Profiles Database Schema
-- Database: smart_warehouse (consolidated database for all AI/ML use cases)
-- Schema: public (default schema)
-- Purpose: Store Golden Records, relationships, benefits, and 360° profiles
-- 
-- Note: This database is shared with:
--   - AI-PLATFORM-02: 360° Profiles (this schema)
--   - AI-PLATFORM-03: Auto Identification (eligibility schema)

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity searches

-- ============================================================
-- CORE TABLES
-- ============================================================

-- 1. Golden Records (extends AI-PLATFORM-01)
CREATE TABLE IF NOT EXISTS golden_records (
    gr_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    family_id UUID, -- Links family members together
    citizen_id VARCHAR(50) UNIQUE, -- External citizen identifier
    jan_aadhaar VARCHAR(12) UNIQUE,
    
    -- Demographics (from Golden Record)
    full_name VARCHAR(300),
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(10),
    caste_id INTEGER,
    
    -- Location
    district_id INTEGER,
    city_village VARCHAR(100),
    pincode VARCHAR(6),
    is_urban BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, merged
    
    -- Foreign key to family head (self-reference)
    CONSTRAINT fk_family_head FOREIGN KEY (family_id) REFERENCES golden_records(gr_id) ON DELETE SET NULL
);

CREATE INDEX idx_golden_records_family ON golden_records(family_id);
CREATE INDEX idx_golden_records_citizen_id ON golden_records(citizen_id);
CREATE INDEX idx_golden_records_jan_aadhaar ON golden_records(jan_aadhaar);
CREATE INDEX idx_golden_records_district ON golden_records(district_id);
CREATE INDEX idx_golden_records_status ON golden_records(status);

COMMENT ON TABLE golden_records IS 'Golden Records with family linking for 360° profiles';

-- 2. Relationships (Graph edges)
CREATE TABLE IF NOT EXISTS gr_relationships (
    relationship_id BIGSERIAL PRIMARY KEY,
    from_gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    to_gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    
    -- Relationship type
    relationship_type VARCHAR(50) NOT NULL, 
    -- SPOUSE, CHILD, PARENT, SIBLING, CO_RESIDENT, EMPLOYEE_OF, EMPLOYER_OF, 
    -- CO_BENEFIT (same schemes), BUSINESS_PARTNER, SHG_MEMBER, etc.
    
    -- Relationship metadata
    is_verified BOOLEAN DEFAULT false, -- Verified vs. inferred
    inference_confidence DECIMAL(5,4), -- 0-1 confidence for inferred relationships
    source VARCHAR(100), -- How relationship was discovered
    notes TEXT,
    
    -- Validity period
    valid_from DATE,
    valid_to DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure no duplicate relationships
    CONSTRAINT unique_relationship UNIQUE (from_gr_id, to_gr_id, relationship_type),
    -- Ensure no self-relationships
    CONSTRAINT no_self_relationship CHECK (from_gr_id != to_gr_id)
);

CREATE INDEX idx_relationships_from ON gr_relationships(from_gr_id);
CREATE INDEX idx_relationships_to ON gr_relationships(to_gr_id);
CREATE INDEX idx_relationships_type ON gr_relationships(relationship_type);
CREATE INDEX idx_relationships_verified ON gr_relationships(is_verified);

COMMENT ON TABLE gr_relationships IS 'Graph edges: verified and inferred relationships between Golden Records';

-- 3. Scheme Master
CREATE TABLE IF NOT EXISTS scheme_master (
    scheme_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) UNIQUE NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- HEALTH, FOOD, EDUCATION, HOUSING, SOCIAL_SECURITY, LIVELIHOOD
    description TEXT,
    
    -- Eligibility criteria (summary)
    min_age INTEGER,
    max_age INTEGER,
    max_income DECIMAL(12,2),
    target_caste VARCHAR(50), -- GEN, OBC, SC, ST, or ALL
    bpl_required BOOLEAN DEFAULT false,
    farmer_required BOOLEAN DEFAULT false,
    
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, archived
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scheme_category ON scheme_master(category);
CREATE INDEX idx_scheme_status ON scheme_master(status);

COMMENT ON TABLE scheme_master IS '12+ Rajasthan government schemes with eligibility criteria';

-- ============================================================
-- TRANSACTION TABLES
-- ============================================================

-- 4. Benefit Events (disbursements)
CREATE TABLE IF NOT EXISTS benefit_events (
    benefit_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    scheme_id INTEGER NOT NULL REFERENCES scheme_master(scheme_id),
    family_id UUID, -- Family-level benefits
    
    -- Transaction details
    txn_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Transaction type
    transaction_type VARCHAR(50), -- DISBURSEMENT, INSTALMENT, REFUND, ADJUSTMENT
    instalment_number INTEGER, -- For multi-instalment schemes
    
    -- Channel and source
    channel VARCHAR(50), -- BANK_TRANSFER, CASH, VOUCHER, IN_KIND
    disbursing_agency VARCHAR(100),
    transaction_reference VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_benefits_gr ON benefit_events(gr_id);
CREATE INDEX idx_benefits_scheme ON benefit_events(scheme_id);
CREATE INDEX idx_benefits_family ON benefit_events(family_id);
CREATE INDEX idx_benefits_date ON benefit_events(txn_date);
CREATE INDEX idx_benefits_gr_scheme_date ON benefit_events(gr_id, scheme_id, txn_date);

COMMENT ON TABLE benefit_events IS 'All benefit disbursements and transactions';

-- 5. Application Events
CREATE TABLE IF NOT EXISTS application_events (
    application_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    scheme_id INTEGER NOT NULL REFERENCES scheme_master(scheme_id),
    family_id UUID, -- Family-level applications
    
    -- Application details
    application_date DATE NOT NULL,
    application_status VARCHAR(50) NOT NULL, -- APPROVED, REJECTED, PENDING, WITHDRAWN
    
    -- Eligibility scoring
    eligibility_score DECIMAL(5,2), -- 0-100 score from ML model
    eligibility_probability DECIMAL(5,4), -- Probability of approval
    
    -- Processing
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_gr ON application_events(gr_id);
CREATE INDEX idx_applications_scheme ON application_events(scheme_id);
CREATE INDEX idx_applications_status ON application_events(application_status);
CREATE INDEX idx_applications_date ON application_events(application_date);
CREATE INDEX idx_applications_eligibility ON application_events(eligibility_score);

COMMENT ON TABLE application_events IS 'Scheme application history with eligibility scores';

-- 6. Socio-Economic Facts (proxies for income inference)
CREATE TABLE IF NOT EXISTS socio_economic_facts (
    fact_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    
    -- Education
    education_level VARCHAR(50), -- ILLITERATE, PRIMARY, SECONDARY, GRADUATE, etc.
    education_id INTEGER,
    
    -- Employment
    employment_type VARCHAR(50), -- UNEMPLOYED, CASUAL, REGULAR, SELF_EMPLOYED, etc.
    employment_id INTEGER,
    occupation VARCHAR(100),
    sector VARCHAR(50), -- AGRICULTURE, MANUFACTURING, SERVICES, GOVERNMENT
    
    -- Assets (proxies)
    house_type VARCHAR(50), -- KUTCHA, SEMI_PUCCA, PUCCA
    house_type_id INTEGER,
    land_holding_class VARCHAR(50), -- NONE, SMALL, MEDIUM, LARGE
    
    -- Utility/tax proxies (where consent available)
    utility_bill_avg DECIMAL(10,2), -- Average monthly utility bill
    property_tax_bracket VARCHAR(50),
    
    -- Family context
    family_size INTEGER,
    dependents_count INTEGER,
    
    -- As of date
    as_of_date DATE NOT NULL,
    source VARCHAR(100), -- Where this data came from
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- One record per gr_id per as_of_date
    CONSTRAINT unique_gr_date UNIQUE (gr_id, as_of_date)
);

CREATE INDEX idx_socio_gr ON socio_economic_facts(gr_id);
CREATE INDEX idx_socio_date ON socio_economic_facts(as_of_date);
CREATE INDEX idx_socio_employment ON socio_economic_facts(employment_type);

COMMENT ON TABLE socio_economic_facts IS 'Socio-economic context for income band inference';

-- ============================================================
-- GOVERNANCE TABLES
-- ============================================================

-- 7. Consent Flags
CREATE TABLE IF NOT EXISTS consent_flags (
    consent_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    
    -- Consent types
    income_inference_consent BOOLEAN DEFAULT false,
    risk_analytics_consent BOOLEAN DEFAULT false,
    relationship_inference_consent BOOLEAN DEFAULT false,
    benefit_analytics_consent BOOLEAN DEFAULT false,
    
    -- Consent metadata
    consent_date DATE,
    consent_version VARCHAR(20), -- Version of consent terms
    withdrawn_date DATE,
    
    -- Source
    source VARCHAR(100), -- CITIZEN_PORTAL, FIELD_OFFICER, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- One consent record per GR
    CONSTRAINT unique_gr_consent UNIQUE (gr_id)
);

CREATE INDEX idx_consent_gr ON consent_flags(gr_id);
CREATE INDEX idx_consent_income ON consent_flags(income_inference_consent);
CREATE INDEX idx_consent_risk ON consent_flags(risk_analytics_consent);

COMMENT ON TABLE consent_flags IS 'DPDP Act 2023 consent tracking for analytic processing';

-- 8. Data Quality Flags (from Golden Record system)
CREATE TABLE IF NOT EXISTS data_quality_flags (
    quality_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    
    -- Quality scores (0-1)
    overall_confidence DECIMAL(5,4),
    completeness_score DECIMAL(5,4), -- How complete the record is
    consistency_score DECIMAL(5,4), -- Consistency across sources
    
    -- Missing data flags
    missing_critical_fields TEXT[], -- List of missing critical fields
    missing_count INTEGER DEFAULT 0,
    
    -- Conflict flags
    has_conflicts BOOLEAN DEFAULT false,
    conflict_count INTEGER DEFAULT 0,
    conflict_fields TEXT[], -- Fields with conflicting values
    
    -- Source attribution
    source_count INTEGER, -- Number of sources contributing
    primary_source VARCHAR(100), -- Most authoritative source
    
    -- As of date
    as_of_date DATE NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- One quality record per GR per date
    CONSTRAINT unique_gr_quality_date UNIQUE (gr_id, as_of_date)
);

CREATE INDEX idx_quality_gr ON data_quality_flags(gr_id);
CREATE INDEX idx_quality_date ON data_quality_flags(as_of_date);
CREATE INDEX idx_quality_confidence ON data_quality_flags(overall_confidence);

COMMENT ON TABLE data_quality_flags IS 'Data quality indicators from Golden Record system';

-- ============================================================
-- ANALYTICS OUTPUTS
-- ============================================================

-- 9. Profile 360 (main 360° profile table)
CREATE TABLE IF NOT EXISTS profile_360 (
    profile_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL UNIQUE REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    family_id UUID,
    
    -- 360° Profile JSON (complete profile document)
    profile_data JSONB NOT NULL,
    /* Structure:
    {
      "identity": {...},
      "relationships": [...],
      "socio_economic": {
        "inferred_income_band": "LOW",
        "income_band_confidence": 0.85,
        "education": "...",
        "employment": "..."
      },
      "benefits": {
        "lifetime_total": 50000,
        "last_1y": 20000,
        "last_3y": 45000,
        "by_category": {...}
      },
      "cluster": {
        "cluster_id": "cluster_123",
        "cluster_type": "FAMILY"
      },
      "risk_flags": [
        {"type": "UNDER_COVERAGE", "score": 0.9, "explanation": "..."}
      ],
      "metadata": {
        "last_updated": "...",
        "model_version": "...",
        "data_sources": [...]
      }
    }
    */
    
    -- Quick access fields (indexed)
    inferred_income_band VARCHAR(20), -- VERY_LOW, LOW, MEDIUM, HIGH, UNCERTAIN
    income_band_confidence DECIMAL(5,4),
    cluster_id VARCHAR(100), -- Community/cluster membership
    cluster_type VARCHAR(50), -- FAMILY, BUSINESS, CO_RESIDENCE, etc.
    
    -- Risk flags (array)
    risk_flags TEXT[], -- OVER_CONCENTRATION, UNDER_COVERAGE, POSSIBLE_LEAKAGE, PRIORITY_VULNERABLE
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_recomputed_at TIMESTAMP,
    
    -- Computed metadata
    recompute_priority INTEGER DEFAULT 5, -- 1-10, higher = more urgent
    recompute_reason TEXT -- Why it needs recomputation
);

CREATE INDEX idx_profile_360_gr ON profile_360(gr_id);
CREATE INDEX idx_profile_360_family ON profile_360(family_id);
CREATE INDEX idx_profile_360_income ON profile_360(inferred_income_band);
CREATE INDEX idx_profile_360_cluster ON profile_360(cluster_id);
CREATE INDEX idx_profile_360_flags ON profile_360 USING GIN(risk_flags);
CREATE INDEX idx_profile_360_data ON profile_360 USING GIN(profile_data);
CREATE INDEX idx_profile_360_updated ON profile_360(updated_at);
CREATE INDEX idx_profile_360_priority ON profile_360(recompute_priority DESC);

COMMENT ON TABLE profile_360 IS 'Complete 360° profiles with inferred features and analytics';

-- 10. Analytics: Benefit Summary
CREATE TABLE IF NOT EXISTS analytics_benefit_summary (
    summary_id BIGSERIAL PRIMARY KEY,
    gr_id UUID REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    family_id UUID,
    cluster_id VARCHAR(100),
    
    -- Time windows
    time_window VARCHAR(20) NOT NULL, -- LIFETIME, LAST_1Y, LAST_3Y, LAST_5Y
    
    -- Aggregations
    total_benefit_amount DECIMAL(15,2) DEFAULT 0,
    benefit_count INTEGER DEFAULT 0,
    scheme_count INTEGER DEFAULT 0,
    
    -- By category
    health_benefits DECIMAL(15,2) DEFAULT 0,
    food_benefits DECIMAL(15,2) DEFAULT 0,
    education_benefits DECIMAL(15,2) DEFAULT 0,
    housing_benefits DECIMAL(15,2) DEFAULT 0,
    social_security_benefits DECIMAL(15,2) DEFAULT 0,
    livelihood_benefits DECIMAL(15,2) DEFAULT 0,
    
    -- Per capita (for families/clusters)
    benefit_per_capita DECIMAL(12,2),
    
    -- Comparison metrics
    district_average DECIMAL(12,2), -- Average for district
    cluster_average DECIMAL(12,2), -- Average for cluster
    percentile_rank INTEGER, -- 0-100 percentile rank
    
    -- As of date
    as_of_date DATE NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- One summary per entity per time window per date
    CONSTRAINT unique_summary UNIQUE (COALESCE(gr_id::text, 'NULL'), 
                                      COALESCE(family_id::text, 'NULL'), 
                                      COALESCE(cluster_id, 'NULL'),
                                      time_window, as_of_date)
);

CREATE INDEX idx_benefit_summary_gr ON analytics_benefit_summary(gr_id);
CREATE INDEX idx_benefit_summary_family ON analytics_benefit_summary(family_id);
CREATE INDEX idx_benefit_summary_cluster ON analytics_benefit_summary(cluster_id);
CREATE INDEX idx_benefit_summary_date ON analytics_benefit_summary(as_of_date);
CREATE INDEX idx_benefit_summary_window ON analytics_benefit_summary(time_window);

COMMENT ON TABLE analytics_benefit_summary IS 'Aggregated benefit summaries by time window for individuals, families, and clusters';

-- 11. Analytics: Flags (risk and under-coverage alerts)
CREATE TABLE IF NOT EXISTS analytics_flags (
    flag_id BIGSERIAL PRIMARY KEY,
    gr_id UUID REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    family_id UUID,
    cluster_id VARCHAR(100),
    
    -- Flag type
    flag_type VARCHAR(50) NOT NULL, 
    -- OVER_CONCENTRATION, POSSIBLE_LEAKAGE, UNDER_COVERAGE, PRIORITY_VULNERABLE
    
    -- Flag details
    flag_severity VARCHAR(20) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
    flag_score DECIMAL(5,4), -- 0-1 confidence in flag
    flag_explanation TEXT, -- Human-readable explanation
    
    -- Context
    scheme_category VARCHAR(50), -- If flag is scheme-specific
    scheme_id INTEGER,
    district_id INTEGER,
    
    -- Metrics that triggered flag
    trigger_metrics JSONB, -- {"benefit_amount": 50000, "local_avg": 15000, ...}
    
    -- Status
    flag_status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, REVIEWED, RESOLVED, FALSE_POSITIVE
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    resolution_notes TEXT,
    
    -- Metadata
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flags_gr ON analytics_flags(gr_id);
CREATE INDEX idx_flags_family ON analytics_flags(family_id);
CREATE INDEX idx_flags_cluster ON analytics_flags(cluster_id);
CREATE INDEX idx_flags_type ON analytics_flags(flag_type);
CREATE INDEX idx_flags_status ON analytics_flags(flag_status);
CREATE INDEX idx_flags_severity ON analytics_flags(flag_severity);
CREATE INDEX idx_flags_scheme ON analytics_flags(scheme_category);

COMMENT ON TABLE analytics_flags IS 'Risk flags and alerts: over-concentration, under-coverage, anomalies';

-- 12. Profile Recompute Queue (for orchestrator)
CREATE TABLE IF NOT EXISTS profile_recompute_queue (
    queue_id BIGSERIAL PRIMARY KEY,
    gr_id UUID NOT NULL REFERENCES golden_records(gr_id) ON DELETE CASCADE,
    
    -- Priority
    priority INTEGER DEFAULT 5, -- 1-10, higher = more urgent
    priority_reason TEXT,
    
    -- Trigger
    trigger_type VARCHAR(50), -- NEW_BENEFIT, RELATIONSHIP_CHANGE, GOLDEN_RECORD_UPDATE, SCHEDULED, MANUAL
    trigger_reference VARCHAR(200), -- Reference to event that triggered
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
    processing_started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    
    -- Retry
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recompute_queue_status ON profile_recompute_queue(status);
CREATE INDEX idx_recompute_queue_priority ON profile_recompute_queue(priority DESC, created_at);
CREATE INDEX idx_recompute_queue_gr ON profile_recompute_queue(gr_id);
CREATE INDEX idx_recompute_queue_trigger ON profile_recompute_queue(trigger_type);

COMMENT ON TABLE profile_recompute_queue IS 'Queue for orchestrator to recompute 360° profiles';

-- ============================================================
-- VIEWS (for common queries)
-- ============================================================

-- View: Current 360° profiles (latest for each GR)
CREATE OR REPLACE VIEW v_current_profiles_360 AS
SELECT 
    p.*,
    gr.family_id as gr_family_id,
    gr.full_name,
    gr.district_id,
    gr.is_urban
FROM profile_360 p
JOIN golden_records gr ON p.gr_id = gr.gr_id
WHERE gr.status = 'active';

-- View: Active risk flags
CREATE OR REPLACE VIEW v_active_flags AS
SELECT 
    f.*,
    gr.full_name,
    gr.district_id
FROM analytics_flags f
LEFT JOIN golden_records gr ON f.gr_id = gr.gr_id
WHERE f.flag_status = 'ACTIVE'
ORDER BY f.flag_severity DESC, f.flag_score DESC, f.flagged_at DESC;

-- View: Family benefit summary
CREATE OR REPLACE VIEW v_family_benefit_summary AS
SELECT 
    gr.family_id,
    COUNT(DISTINCT gr.gr_id) as family_members,
    COUNT(DISTINCT be.scheme_id) as schemes_enrolled,
    SUM(be.amount) as total_benefits,
    AVG(be.amount) as avg_benefit_per_member
FROM golden_records gr
LEFT JOIN benefit_events be ON gr.gr_id = be.gr_id
WHERE gr.status = 'active' AND gr.family_id IS NOT NULL
GROUP BY gr.family_id;

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- Function: Get 360° profile JSON
CREATE OR REPLACE FUNCTION get_profile_360(p_gr_id UUID)
RETURNS JSONB AS $$
BEGIN
    RETURN (SELECT profile_data FROM profile_360 WHERE gr_id = p_gr_id);
END;
$$ LANGUAGE plpgsql;

-- Function: Check if recompute needed
CREATE OR REPLACE FUNCTION needs_recompute(p_gr_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    last_update TIMESTAMP;
    has_new_benefits BOOLEAN;
BEGIN
    -- Get last profile update
    SELECT updated_at INTO last_update 
    FROM profile_360 
    WHERE gr_id = p_gr_id;
    
    -- Check for new benefits since last update
    SELECT EXISTS(
        SELECT 1 FROM benefit_events 
        WHERE gr_id = p_gr_id 
        AND txn_date > COALESCE(last_update::DATE, '1900-01-01')
    ) INTO has_new_benefits;
    
    RETURN (last_update IS NULL OR has_new_benefits OR 
            last_update < NOW() - INTERVAL '24 hours');
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger: Auto-update updated_at on golden_records
CREATE OR REPLACE FUNCTION update_golden_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_golden_records_updated_at
BEFORE UPDATE ON golden_records
FOR EACH ROW
EXECUTE FUNCTION update_golden_records_updated_at();

-- Trigger: Queue recompute on new benefit
CREATE OR REPLACE FUNCTION queue_recompute_on_benefit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profile_recompute_queue (gr_id, priority, trigger_type, trigger_reference)
    VALUES (
        NEW.gr_id,
        7, -- High priority for new benefits
        'NEW_BENEFIT',
        'benefit_' || NEW.benefit_id
    )
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_queue_recompute_benefit
AFTER INSERT ON benefit_events
FOR EACH ROW
EXECUTE FUNCTION queue_recompute_on_benefit();

-- Trigger: Queue recompute on relationship change
CREATE OR REPLACE FUNCTION queue_recompute_on_relationship()
RETURNS TRIGGER AS $$
BEGIN
    -- Queue recompute for both GRs in relationship
    INSERT INTO profile_recompute_queue (gr_id, priority, trigger_type, trigger_reference)
    VALUES 
        (NEW.from_gr_id, 6, 'RELATIONSHIP_CHANGE', 'rel_' || NEW.relationship_id),
        (NEW.to_gr_id, 6, 'RELATIONSHIP_CHANGE', 'rel_' || NEW.relationship_id)
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_queue_recompute_relationship
AFTER INSERT OR UPDATE ON gr_relationships
FOR EACH ROW
EXECUTE FUNCTION queue_recompute_on_relationship();

-- ============================================================
-- INITIAL DATA (Reference data)
-- ============================================================

-- Insert 12 Rajasthan schemes (if not exists)
INSERT INTO scheme_master (scheme_code, scheme_name, category, min_age, max_age, max_income, target_caste, bpl_required, farmer_required) VALUES
('CHIRANJEEVI', 'Mukhyamantri Chiranjeevi Yojana', 'HEALTH', 0, NULL, NULL, 'ALL', false, false),
('VISHESH_LABH', 'Mukhyamantri Vishesh Labh Yojana', 'EDUCATION', 6, 18, NULL, 'ALL', false, false),
('GRAMIN_AWAS', 'Mukhyamantri Gramin Awas Yojana', 'HOUSING', 18, NULL, 300000, 'ALL', true, false),
('SC_ST_SCHOLARSHIP', 'SC/ST Post Matric Scholarship', 'EDUCATION', 16, 25, NULL, 'SC,ST', false, false),
('KISAN_CREDIT', 'Kisan Credit Card Scheme', 'LIVELIHOOD', 18, NULL, NULL, 'ALL', false, true),
('MAHILA_SHAKTI', 'Mukhyamantri Mahila Shakti Nidhi', 'SOCIAL_SECURITY', 18, 60, NULL, 'ALL', false, false),
('DISABILITY_PENSION', 'Disability Pension Scheme', 'SOCIAL_SECURITY', 0, NULL, 50000, 'ALL', false, false),
('OLD_AGE_PENSION', 'Old Age Pension', 'SOCIAL_SECURITY', 60, NULL, 30000, 'ALL', false, false),
('NREGA', 'Mahatma Gandhi NREGA', 'LIVELIHOOD', 18, NULL, NULL, 'ALL', false, false),
('BPL_ASSISTANCE', 'BPL Family Assistance', 'SOCIAL_SECURITY', 0, NULL, NULL, 'ALL', true, false),
('TRIBAL_WELFARE', 'Tribal Welfare Scheme', 'SOCIAL_SECURITY', 0, NULL, NULL, 'ST', false, false),
('OBC_SCHOLARSHIP', 'OBC Post Matric Scholarship', 'EDUCATION', 16, 25, NULL, 'OBC', false, false)
ON CONFLICT (scheme_code) DO NOTHING;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON SCHEMA public IS 'AI-PLATFORM-02: 360° Profiles database schema for smart_warehouse';

COMMENT ON TABLE golden_records IS 'Core Golden Records with family linking';
COMMENT ON TABLE gr_relationships IS 'Graph relationships: verified and inferred';
COMMENT ON TABLE scheme_master IS 'Government schemes master data';
COMMENT ON TABLE benefit_events IS 'Benefit disbursements and transactions';
COMMENT ON TABLE application_events IS 'Application history with eligibility scores';
COMMENT ON TABLE socio_economic_facts IS 'Socio-economic context for ML inference';
COMMENT ON TABLE consent_flags IS 'DPDP Act 2023 consent tracking';
COMMENT ON TABLE data_quality_flags IS 'Data quality from Golden Record system';
COMMENT ON TABLE profile_360 IS 'Complete 360° profiles with inferred features';
COMMENT ON TABLE analytics_benefit_summary IS 'Benefit aggregations by time window';
COMMENT ON TABLE analytics_flags IS 'Risk flags and anomaly alerts';
COMMENT ON TABLE profile_recompute_queue IS 'Queue for profile recomputation';

-- ============================================================
-- GRANTS (if needed for separate users)
-- ============================================================

-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO aiml_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aiml_user;

