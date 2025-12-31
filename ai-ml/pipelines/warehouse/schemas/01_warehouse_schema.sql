-- AIML Data Warehouse Schema
-- Database: smart_warehouse
-- Purpose: Analytical database for ML training and analytics (star/snowflake schema)
-- Location: Restricted DC (same as AIML portal)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity searches

-- ============================================================
-- STAGING SCHEMA (for ETL)
-- ============================================================

CREATE SCHEMA IF NOT EXISTS staging;
COMMENT ON SCHEMA staging IS 'Staging area for ETL processes';

-- ============================================================
-- DIMENSIONS (Dimensional Model)
-- ============================================================

-- Time Dimension
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD format
    date_actual DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT false,
    holiday_name VARCHAR(100),
    
    -- Fiscal year (if different from calendar)
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate date dimension (can be done via ETL or function)
CREATE INDEX idx_dim_date_actual ON dim_date(date_actual);
CREATE INDEX idx_dim_date_year_month ON dim_date(year, month);

-- Citizen Dimension (Denormalized from Citizen Portal)
CREATE TABLE dim_citizen (
    citizen_key BIGSERIAL PRIMARY KEY,
    citizen_id VARCHAR(100) NOT NULL, -- Original ID from citizen portal
    
    -- Demographics
    aadhaar_number VARCHAR(12),
    mobile_number VARCHAR(10),
    email VARCHAR(255),
    full_name VARCHAR(255),
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(10),
    
    -- Location
    city VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100) DEFAULT 'Rajasthan',
    pincode VARCHAR(6),
    region VARCHAR(50), -- North, South, East, West, Central
    
    -- Status
    verification_status VARCHAR(20),
    account_status VARCHAR(20),
    
    -- SCD Type 2 fields (for historical tracking)
    is_current BOOLEAN DEFAULT true,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_citizen_id ON dim_citizen(citizen_id);
CREATE INDEX idx_dim_citizen_district ON dim_citizen(district);
CREATE INDEX idx_dim_citizen_current ON dim_citizen(is_current);

-- Scheme Dimension
CREATE TABLE dim_scheme (
    scheme_key BIGSERIAL PRIMARY KEY,
    scheme_id VARCHAR(100) NOT NULL, -- Original ID from citizen portal
    
    -- Scheme details
    scheme_code VARCHAR(50) NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    department VARCHAR(255),
    sub_category VARCHAR(100),
    
    -- Temporal
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN,
    
    -- SCD Type 2 fields
    is_current BOOLEAN DEFAULT true,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_scheme_code ON dim_scheme(scheme_code);
CREATE INDEX idx_dim_scheme_category ON dim_scheme(category);
CREATE INDEX idx_dim_scheme_current ON dim_scheme(is_current);

-- Department Dimension
CREATE TABLE dim_department (
    department_key BIGSERIAL PRIMARY KEY,
    department_id VARCHAR(100) NOT NULL,
    
    -- Department details
    department_code VARCHAR(50) NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    parent_department VARCHAR(255),
    level INTEGER,
    head_officer_name VARCHAR(255),
    
    -- SCD Type 2 fields
    is_current BOOLEAN DEFAULT true,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_department_code ON dim_department(department_code);
CREATE INDEX idx_dim_department_current ON dim_department(is_current);

-- ============================================================
-- FACTS (Fact Tables)
-- ============================================================

-- Service Applications Fact (Grain: One row per application)
CREATE TABLE fact_service_applications (
    -- Surrogate keys
    application_key BIGSERIAL PRIMARY KEY,
    
    -- Dimension keys
    citizen_key BIGINT NOT NULL REFERENCES dim_citizen(citizen_key),
    scheme_key BIGINT REFERENCES dim_scheme(scheme_key),
    department_key BIGINT REFERENCES dim_department(department_key),
    submission_date_key INTEGER REFERENCES dim_date(date_key),
    completion_date_key INTEGER REFERENCES dim_date(date_key),
    
    -- Natural keys (from source systems)
    application_id VARCHAR(100) NOT NULL,
    application_number VARCHAR(50) NOT NULL,
    source_system VARCHAR(50) DEFAULT 'citizen_portal',
    
    -- Measures
    application_count INTEGER DEFAULT 1,
    processing_days INTEGER, -- Days to process
    sla_days INTEGER, -- Expected SLA
    sla_breached BOOLEAN, -- Whether SLA was breached
    
    -- Status flags
    status VARCHAR(50),
    is_approved BOOLEAN,
    is_rejected BOOLEAN,
    is_completed BOOLEAN,
    
    -- Amounts (if applicable)
    amount_requested DECIMAL(15, 2),
    amount_approved DECIMAL(15, 2),
    
    -- Degenerate dimensions
    service_type VARCHAR(100),
    application_type VARCHAR(100),
    priority VARCHAR(20),
    
    -- ETL metadata
    etl_batch_id VARCHAR(100),
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE (application_id, source_system, etl_batch_id)
);

CREATE INDEX idx_fact_apps_citizen ON fact_service_applications(citizen_key);
CREATE INDEX idx_fact_apps_scheme ON fact_service_applications(scheme_key);
CREATE INDEX idx_fact_apps_department ON fact_service_applications(department_key);
CREATE INDEX idx_fact_apps_submission_date ON fact_service_applications(submission_date_key);
CREATE INDEX idx_fact_apps_completion_date ON fact_service_applications(completion_date_key);
CREATE INDEX idx_fact_apps_application_number ON fact_service_applications(application_number);
CREATE INDEX idx_fact_apps_status ON fact_service_applications(status);
CREATE INDEX idx_fact_apps_etl_batch ON fact_service_applications(etl_batch_id);

-- Application Processing Fact (Grain: One row per processing action)
CREATE TABLE fact_application_processing (
    -- Surrogate key
    processing_key BIGSERIAL PRIMARY KEY,
    
    -- Dimension keys
    application_key BIGINT REFERENCES fact_service_applications(application_key),
    department_key BIGINT REFERENCES dim_department(department_key),
    action_date_key INTEGER REFERENCES dim_date(date_key),
    
    -- Natural keys
    assignment_id VARCHAR(100),
    application_number VARCHAR(50) NOT NULL,
    
    -- Measures
    processing_count INTEGER DEFAULT 1,
    processing_time_hours DECIMAL(10, 2),
    
    -- Action details
    action_type VARCHAR(50), -- approve, reject, forward, etc.
    decision VARCHAR(50),
    stage VARCHAR(100),
    
    -- ETL metadata
    etl_batch_id VARCHAR(100),
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_processing_application ON fact_application_processing(application_key);
CREATE INDEX idx_fact_processing_department ON fact_application_processing(department_key);
CREATE INDEX idx_fact_processing_date ON fact_application_processing(action_date_key);
CREATE INDEX idx_fact_processing_application_number ON fact_application_processing(application_number);

-- Eligibility Scoring Fact (Grain: One row per eligibility prediction)
CREATE TABLE fact_eligibility_scoring (
    -- Surrogate key
    eligibility_key BIGSERIAL PRIMARY KEY,
    
    -- Dimension keys
    citizen_key BIGINT NOT NULL REFERENCES dim_citizen(citizen_key),
    scheme_key BIGINT REFERENCES dim_scheme(scheme_key),
    prediction_date_key INTEGER REFERENCES dim_date(date_key),
    
    -- Natural keys
    citizen_id VARCHAR(100),
    scheme_code VARCHAR(50),
    application_id VARCHAR(100),
    
    -- Prediction measures
    eligibility_score DECIMAL(5, 2) NOT NULL, -- 0-100
    confidence_score DECIMAL(5, 2),
    probability_approved DECIMAL(5, 4),
    
    -- Model info
    model_id VARCHAR(100),
    model_version VARCHAR(50),
    
    -- Actual outcome (for model evaluation)
    actual_approved BOOLEAN,
    prediction_correct BOOLEAN,
    
    -- ETL metadata
    etl_batch_id VARCHAR(100),
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_eligibility_citizen ON fact_eligibility_scoring(citizen_key);
CREATE INDEX idx_fact_eligibility_scheme ON fact_eligibility_scoring(scheme_key);
CREATE INDEX idx_fact_eligibility_date ON fact_eligibility_scoring(prediction_date_key);
CREATE INDEX idx_fact_eligibility_score ON fact_eligibility_scoring(eligibility_score);
CREATE INDEX idx_fact_eligibility_model ON fact_eligibility_scoring(model_id, model_version);

-- ============================================================
-- AGGREGATED TABLES (Pre-computed aggregations)
-- ============================================================

-- Daily application aggregations
CREATE TABLE agg_daily_applications (
    aggregation_key BIGSERIAL PRIMARY KEY,
    
    -- Dimensions
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    scheme_key BIGINT REFERENCES dim_scheme(scheme_key),
    department_key BIGINT REFERENCES dim_department(department_key),
    district VARCHAR(100),
    
    -- Measures
    total_applications INTEGER DEFAULT 0,
    approved_applications INTEGER DEFAULT 0,
    rejected_applications INTEGER DEFAULT 0,
    pending_applications INTEGER DEFAULT 0,
    avg_processing_days DECIMAL(10, 2),
    sla_compliance_rate DECIMAL(5, 2),
    
    -- Amounts
    total_amount_requested DECIMAL(15, 2),
    total_amount_approved DECIMAL(15, 2),
    
    -- ETL metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (date_key, scheme_key, department_key, district)
);

CREATE INDEX idx_agg_daily_apps_date ON agg_daily_applications(date_key);
CREATE INDEX idx_agg_daily_apps_scheme ON agg_daily_applications(scheme_key);
CREATE INDEX idx_agg_daily_apps_department ON agg_daily_applications(department_key);

-- ============================================================
-- ETL METADATA
-- ============================================================

-- ETL batch tracking
CREATE TABLE etl_batches (
    batch_id VARCHAR(100) PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL, -- full_load, incremental, delta
    source_system VARCHAR(50) NOT NULL, -- citizen_portal, dept_portal
    
    -- Status
    status VARCHAR(20) DEFAULT 'running', -- running, completed, failed
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Statistics
    records_processed BIGINT,
    records_inserted BIGINT,
    records_updated BIGINT,
    records_failed BIGINT,
    
    -- Error handling
    error_message TEXT,
    
    -- Metadata
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etl_batches_type ON etl_batches(batch_type);
CREATE INDEX idx_etl_batches_source ON etl_batches(source_system);
CREATE INDEX idx_etl_batches_status ON etl_batches(status);
CREATE INDEX idx_etl_batches_start_time ON etl_batches(start_time);

-- ETL data quality checks
CREATE TABLE etl_data_quality (
    id BIGSERIAL PRIMARY KEY,
    batch_id VARCHAR(100) REFERENCES etl_batches(batch_id),
    
    -- Quality check details
    check_type VARCHAR(50) NOT NULL, -- completeness, validity, consistency, uniqueness
    table_name VARCHAR(255),
    column_name VARCHAR(255),
    check_rule TEXT,
    
    -- Results
    passed BOOLEAN,
    expected_value BIGINT,
    actual_value BIGINT,
    error_message TEXT,
    
    -- Timestamp
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etl_quality_batch ON etl_data_quality(batch_id);
CREATE INDEX idx_etl_quality_type ON etl_data_quality(check_type);
CREATE INDEX idx_etl_quality_passed ON etl_data_quality(passed);

-- ============================================================
-- FUNCTIONS & HELPERS
-- ============================================================

-- Function to get date key from date
CREATE OR REPLACE FUNCTION get_date_key(p_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN TO_CHAR(p_date, 'YYYYMMDD')::INTEGER;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to populate date dimension (generate dates)
CREATE OR REPLACE FUNCTION populate_date_dimension(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    date_var DATE := start_date;
BEGIN
    WHILE date_var <= end_date LOOP
        INSERT INTO dim_date (
            date_key, date_actual, year, quarter, month, month_name,
            week, day_of_month, day_of_week, day_name, is_weekend,
            fiscal_year, fiscal_quarter
        )
        VALUES (
            get_date_key(date_var),
            date_var,
            EXTRACT(YEAR FROM date_var),
            EXTRACT(QUARTER FROM date_var),
            EXTRACT(MONTH FROM date_var),
            TO_CHAR(date_var, 'Month'),
            EXTRACT(WEEK FROM date_var),
            EXTRACT(DAY FROM date_var),
            EXTRACT(DOW FROM date_var),
            TO_CHAR(date_var, 'Day'),
            EXTRACT(DOW FROM date_var) IN (0, 6), -- Sunday=0, Saturday=6
            EXTRACT(YEAR FROM date_var), -- Same as calendar year for now
            EXTRACT(QUARTER FROM date_var)
        )
        ON CONFLICT (date_key) DO NOTHING;
        
        date_var := date_var + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON SCHEMA staging IS 'Staging area for ETL data loads';
COMMENT ON TABLE dim_date IS 'Time dimension table for date-based analytics';
COMMENT ON TABLE dim_citizen IS 'Citizen dimension (Type 2 SCD)';
COMMENT ON TABLE dim_scheme IS 'Scheme dimension (Type 2 SCD)';
COMMENT ON TABLE dim_department IS 'Department dimension (Type 2 SCD)';
COMMENT ON TABLE fact_service_applications IS 'Fact table for service applications (grain: one row per application)';
COMMENT ON TABLE fact_application_processing IS 'Fact table for application processing actions (grain: one row per action)';
COMMENT ON TABLE fact_eligibility_scoring IS 'Fact table for eligibility scoring predictions';
COMMENT ON TABLE agg_daily_applications IS 'Pre-aggregated daily application statistics';
COMMENT ON TABLE etl_batches IS 'ETL batch tracking and metadata';
COMMENT ON TABLE etl_data_quality IS 'ETL data quality check results';

-- Initial population of date dimension (last 5 years to next 2 years)
-- SELECT populate_date_dimension(CURRENT_DATE - INTERVAL '5 years', CURRENT_DATE + INTERVAL '2 years');

