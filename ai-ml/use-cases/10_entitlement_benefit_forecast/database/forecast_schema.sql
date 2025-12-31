-- ============================================================================
-- Entitlement & Benefit Forecast Schema
-- Use Case ID: AI-PLATFORM-10
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS forecast;
GRANT USAGE ON SCHEMA forecast TO sameer;
ALTER SCHEMA forecast OWNER TO sameer;

SET search_path TO forecast;

-- Forecast records (main forecast runs)
CREATE TABLE IF NOT EXISTS forecast_records (
    forecast_id SERIAL PRIMARY KEY,
    
    -- Household identification
    family_id UUID NOT NULL,
    household_head_id VARCHAR(255),
    
    -- Forecast parameters
    horizon_months INTEGER NOT NULL DEFAULT 12,  -- Forecast horizon in months
    forecast_date DATE NOT NULL DEFAULT CURRENT_DATE,
    forecast_type VARCHAR(50) NOT NULL DEFAULT 'BASELINE',  -- BASELINE, SCENARIO, AGGREGATE
    scenario_name VARCHAR(100),  -- STATUS_QUO, ACT_ON_RECOMMENDATIONS, POLICY_CHANGE
    
    -- Forecast status
    status VARCHAR(50) DEFAULT 'COMPLETED',  -- IN_PROGRESS, COMPLETED, FAILED
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(50) DEFAULT 'SYSTEM',
    
    -- Summary metrics
    total_annual_value DECIMAL(15,2),  -- Total annual benefit value
    total_forecast_value DECIMAL(15,2),  -- Total value over horizon
    scheme_count INTEGER DEFAULT 0,  -- Number of schemes in forecast
    
    -- Metadata
    assumptions JSONB,  -- List of assumptions used
    uncertainty_level VARCHAR(20),  -- LOW, MEDIUM, HIGH
    metadata JSONB
);

CREATE INDEX idx_forecast_records_family_id ON forecast_records(family_id);
CREATE INDEX idx_forecast_records_forecast_date ON forecast_records(forecast_date DESC);
CREATE INDEX idx_forecast_records_scenario ON forecast_records(scenario_name) WHERE scenario_name IS NOT NULL;
CREATE INDEX idx_forecast_records_type ON forecast_records(forecast_type, status);

-- Forecast projections (detailed breakdown by scheme and time period)
CREATE TABLE IF NOT EXISTS forecast_projections (
    projection_id SERIAL PRIMARY KEY,
    
    -- Related forecast
    forecast_id INTEGER NOT NULL REFERENCES forecast_records(forecast_id) ON DELETE CASCADE,
    
    -- Scheme details
    scheme_code VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(255),
    
    -- Projection details
    projection_type VARCHAR(50) NOT NULL,  -- CURRENT_ENROLMENT, FUTURE_ENROLMENT, POLICY_CHANGE
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL,  -- MONTHLY, QUARTERLY, ANNUAL
    
    -- Benefit amounts
    benefit_amount DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    benefit_count INTEGER DEFAULT 1,  -- Number of benefits in period
    benefit_frequency VARCHAR(50),  -- MONTHLY, ANNUAL, SEASONAL, CONDITIONAL
    
    -- Probability and confidence
    probability DECIMAL(5,4) DEFAULT 1.0,  -- Probability of this benefit (0-1)
    confidence_level VARCHAR(20) DEFAULT 'MEDIUM',  -- HIGH, MEDIUM, LOW
    
    -- Assumptions
    assumptions TEXT[],  -- Array of assumptions for this projection
    eligibility_based_on VARCHAR(100),  -- What eligibility assumption this is based on
    
    -- Life stage events (if applicable)
    life_stage_event VARCHAR(100),  -- e.g., "CHILD_REACHING_SCHOOL_AGE", "APPROACHING_PENSION_AGE"
    event_date DATE,
    
    metadata JSONB
);

CREATE INDEX idx_forecast_projections_forecast_id ON forecast_projections(forecast_id);
CREATE INDEX idx_forecast_projections_scheme_code ON forecast_projections(scheme_code);
CREATE INDEX idx_forecast_projections_period ON forecast_projections(period_start, period_end);
CREATE INDEX idx_forecast_projections_type ON forecast_projections(projection_type);

-- Scenario configurations
CREATE TABLE IF NOT EXISTS forecast_scenarios (
    scenario_id SERIAL PRIMARY KEY,
    
    scenario_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    scenario_type VARCHAR(50) NOT NULL,  -- CITIZEN_FACING, PLANNER_FACING
    
    -- Scenario parameters
    include_recommendations BOOLEAN DEFAULT FALSE,
    recommendation_horizon_months INTEGER,
    recommendation_probability DECIMAL(5,4) DEFAULT 1.0,
    
    include_policy_changes BOOLEAN DEFAULT FALSE,
    policy_change_ids INTEGER[],  -- References to policy_changes table
    
    -- Assumptions
    assumptions JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_forecast_scenarios_name ON forecast_scenarios(scenario_name);
CREATE INDEX idx_forecast_scenarios_type ON forecast_scenarios(scenario_type, is_active);

-- Policy changes (announced rate changes, new schemes, sunsetting)
CREATE TABLE IF NOT EXISTS policy_changes (
    change_id SERIAL PRIMARY KEY,
    
    change_type VARCHAR(50) NOT NULL,  -- RATE_CHANGE, NEW_SCHEME, SCHEME_SUNSET, BENEFIT_FORMULA_CHANGE
    
    -- Scheme affected
    scheme_code VARCHAR(100),
    scheme_name VARCHAR(255),
    
    -- Change details
    change_description TEXT NOT NULL,
    effective_date DATE NOT NULL,
    announced_date DATE,
    
    -- Change parameters
    old_value DECIMAL(15,2),  -- Old rate/amount
    new_value DECIMAL(15,2),  -- New rate/amount
    change_formula TEXT,  -- Formula for rate changes
    
    -- Source
    announced_by VARCHAR(100),  -- Department, policy document
    source_reference VARCHAR(255),  -- URL, document reference
    
    -- Status
    is_confirmed BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_policy_changes_scheme_code ON policy_changes(scheme_code) WHERE scheme_code IS NOT NULL;
CREATE INDEX idx_policy_changes_effective_date ON policy_changes(effective_date);
CREATE INDEX idx_policy_changes_type ON policy_changes(change_type, is_confirmed);

-- Benefit schedules (scheme benefit patterns)
CREATE TABLE IF NOT EXISTS benefit_schedules (
    schedule_id SERIAL PRIMARY KEY,
    
    scheme_code VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(255),
    
    -- Schedule type
    schedule_type VARCHAR(50) NOT NULL,  -- FIXED, SLAB_BASED, CONDITIONAL, SEASONAL
    frequency VARCHAR(50) NOT NULL,  -- MONTHLY, ANNUAL, QUARTERLY, SEASONAL, CONDITIONAL
    
    -- Benefit amount/formula
    fixed_amount DECIMAL(15,2),  -- For fixed benefits
    formula_expression TEXT,  -- For formula-based benefits
    slab_config JSONB,  -- For slab-based benefits
    
    -- Conditional requirements
    conditional_on VARCHAR(100),  -- ATTENDANCE, HEALTH_VISITS, PERFORMANCE, etc.
    
    -- Seasonal patterns
    seasonal_months INTEGER[],  -- Months when benefit is active (1-12)
    crop_season VARCHAR(50),  -- Kharif, Rabi, etc.
    
    -- Effective dates
    effective_from DATE,
    effective_to DATE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    metadata JSONB
);

CREATE INDEX idx_benefit_schedules_scheme_code ON benefit_schedules(scheme_code);
CREATE INDEX idx_benefit_schedules_active ON benefit_schedules(is_active, effective_from, effective_to) WHERE is_active = TRUE;

-- Aggregate forecasts (for planning/analytics)
CREATE TABLE IF NOT EXISTS aggregate_forecasts (
    aggregate_id SERIAL PRIMARY KEY,
    
    -- Aggregation level
    aggregation_level VARCHAR(50) NOT NULL,  -- BLOCK, DISTRICT, STATE
    block_id VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    
    -- Forecast parameters
    forecast_date DATE NOT NULL,
    horizon_months INTEGER NOT NULL,
    scenario_name VARCHAR(100),
    
    -- Scheme aggregation
    scheme_code VARCHAR(100),
    scheme_name VARCHAR(255),
    
    -- Aggregate metrics
    total_households INTEGER DEFAULT 0,
    eligible_households INTEGER DEFAULT 0,
    enrolled_households INTEGER DEFAULT 0,
    
    total_annual_value DECIMAL(15,2),
    total_forecast_value DECIMAL(15,2),
    per_household_avg DECIMAL(15,2),
    
    -- Period breakdown
    period_start DATE,
    period_end DATE,
    period_type VARCHAR(20),  -- MONTHLY, QUARTERLY, ANNUAL
    
    -- Generated metadata
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(50) DEFAULT 'SYSTEM',
    
    metadata JSONB
);

CREATE INDEX idx_aggregate_forecasts_level ON aggregate_forecasts(aggregation_level, block_id, district);
CREATE INDEX idx_aggregate_forecasts_date ON aggregate_forecasts(forecast_date DESC);
CREATE INDEX idx_aggregate_forecasts_scheme ON aggregate_forecasts(scheme_code) WHERE scheme_code IS NOT NULL;

-- Life stage events tracking (for forecast triggers)
CREATE TABLE IF NOT EXISTS life_stage_events (
    event_id SERIAL PRIMARY KEY,
    
    -- Household/Beneficiary
    family_id UUID NOT NULL,
    beneficiary_id VARCHAR(255),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,  -- CHILD_REACHING_SCHOOL_AGE, APPROACHING_PENSION_AGE, etc.
    event_date DATE NOT NULL,
    event_description TEXT,
    
    -- Related scheme eligibility
    eligible_scheme_codes TEXT[],  -- Schemes that become eligible due to this event
    eligibility_trigger_date DATE,  -- When eligibility starts
    
    -- Status
    is_processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_life_stage_events_family_id ON life_stage_events(family_id);
CREATE INDEX idx_life_stage_events_date ON life_stage_events(event_date);
CREATE INDEX idx_life_stage_events_type ON life_stage_events(event_type, is_processed) WHERE is_processed = FALSE;

-- Forecast assumptions log
CREATE TABLE IF NOT EXISTS forecast_assumptions (
    assumption_id SERIAL PRIMARY KEY,
    
    forecast_id INTEGER REFERENCES forecast_records(forecast_id) ON DELETE CASCADE,
    
    assumption_category VARCHAR(100),  -- ELIGIBILITY, BENEFIT_SCHEDULE, POLICY, ENROLMENT
    assumption_text TEXT NOT NULL,
    assumption_source VARCHAR(100),  -- CURRENT_DATA, POLICY_DOCUMENT, ESTIMATE
    
    confidence_level VARCHAR(20),  -- HIGH, MEDIUM, LOW
    uncertainty_description TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_forecast_assumptions_forecast_id ON forecast_assumptions(forecast_id);

-- Forecast audit logs
CREATE TABLE IF NOT EXISTS forecast_audit_logs (
    audit_id SERIAL PRIMARY KEY,
    
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL,  -- SYSTEM, USER, PLANNER
    actor_id VARCHAR(100),
    
    -- Event details
    forecast_id INTEGER REFERENCES forecast_records(forecast_id) ON DELETE SET NULL,
    family_id UUID,
    event_description TEXT NOT NULL,
    event_data JSONB,
    
    metadata JSONB
);

CREATE INDEX idx_forecast_audit_logs_event_type ON forecast_audit_logs(event_type);
CREATE INDEX idx_forecast_audit_logs_timestamp ON forecast_audit_logs(event_timestamp DESC);
CREATE INDEX idx_forecast_audit_logs_family_id ON forecast_audit_logs(family_id) WHERE family_id IS NOT NULL;

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update last_updated_at timestamp
CREATE OR REPLACE FUNCTION update_forecast_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_forecast_scenarios_updated_at BEFORE UPDATE ON forecast_scenarios
    FOR EACH ROW EXECUTE FUNCTION update_forecast_updated_at_column();

CREATE TRIGGER update_benefit_schedules_updated_at BEFORE UPDATE ON benefit_schedules
    FOR EACH ROW EXECUTE FUNCTION update_forecast_updated_at_column();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON SCHEMA forecast IS 'Schema for Entitlement & Benefit Forecast (AI-PLATFORM-10)';
COMMENT ON TABLE forecast_records IS 'Main forecast records for households';
COMMENT ON TABLE forecast_projections IS 'Detailed benefit projections by scheme and time period';
COMMENT ON TABLE forecast_scenarios IS 'Forecast scenario configurations';
COMMENT ON TABLE policy_changes IS 'Policy changes affecting forecasts (rate changes, new schemes, etc.)';
COMMENT ON TABLE benefit_schedules IS 'Benefit schedules and patterns for schemes';
COMMENT ON TABLE aggregate_forecasts IS 'Aggregate forecasts for planning/analytics';
COMMENT ON TABLE life_stage_events IS 'Life stage events that trigger forecast updates';
COMMENT ON TABLE forecast_assumptions IS 'Assumptions used in forecasts';
COMMENT ON TABLE forecast_audit_logs IS 'Audit logs for forecast operations';

