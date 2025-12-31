-- AIML Portal Database Schema
-- Database: smart_aiml
-- Purpose: Store ML models, experiments, predictions, training data, and analytics

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ML MODELS
-- ============================================================

-- ML Use Cases (27 use cases) - Create first as it's referenced
CREATE TABLE ml_use_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- eligibility_scoring, fraud_detection, recommendation, etc.
    
    -- Use case details
    business_objective TEXT,
    success_metrics JSONB,
    data_sources JSONB, -- Which portal databases feed this use case
    
    -- Status
    status VARCHAR(20) DEFAULT 'planning', -- planning, development, testing, production, retired
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_use_cases_code ON ml_use_cases(code);
CREATE INDEX idx_use_cases_category ON ml_use_cases(category);
CREATE INDEX idx_use_cases_status ON ml_use_cases(status);

-- ML Model registry
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    use_case_id UUID REFERENCES ml_use_cases(id),
    
    -- Model details
    model_type VARCHAR(50) NOT NULL, -- classification, regression, clustering, nlp, etc.
    algorithm VARCHAR(100), -- random_forest, neural_network, etc.
    framework VARCHAR(50), -- scikit-learn, tensorflow, pytorch, etc.
    
    -- Model artifacts
    model_path TEXT NOT NULL, -- Path to saved model file
    model_size BIGINT, -- Size in bytes
    artifact_uri TEXT, -- MLflow artifact URI
    
    -- Model metrics
    training_metrics JSONB, -- accuracy, precision, recall, F1, etc.
    validation_metrics JSONB,
    test_metrics JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'development', -- development, staging, production, deprecated
    is_active BOOLEAN DEFAULT false,
    
    -- Training info
    trained_by VARCHAR(255),
    training_date TIMESTAMP,
    training_duration_seconds INTEGER,
    
    -- Deployment
    deployed_at TIMESTAMP,
    deployment_endpoint TEXT,
    
    -- Metadata
    hyperparameters JSONB,
    feature_list JSONB,
    metadata JSONB,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_models_name_version ON ml_models(model_name, model_version);
CREATE INDEX idx_models_use_case ON ml_models(use_case_id);
CREATE INDEX idx_models_status ON ml_models(status);
CREATE INDEX idx_models_active ON ml_models(is_active);

-- ============================================================
-- EXPERIMENTS & RUNS
-- ============================================================

-- MLflow experiments sync (local cache)
CREATE TABLE mlflow_experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id VARCHAR(255) UNIQUE NOT NULL, -- MLflow experiment ID
    name VARCHAR(255) NOT NULL,
    artifact_location TEXT,
    
    -- Experiment details
    lifecycle_stage VARCHAR(20), -- active, deleted
    tags JSONB,
    
    -- Sync info
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mlflow_experiments_name ON mlflow_experiments(name);
CREATE INDEX idx_mlflow_experiments_lifecycle ON mlflow_experiments(lifecycle_stage);

-- MLflow runs sync
CREATE TABLE mlflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(255) UNIQUE NOT NULL, -- MLflow run ID
    experiment_id VARCHAR(255) NOT NULL,
    mlflow_experiment_id UUID REFERENCES mlflow_experiments(id),
    
    -- Run details
    run_name VARCHAR(255),
    status VARCHAR(20), -- RUNNING, SCHEDULED, FINISHED, FAILED, KILLED
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Metrics and parameters
    metrics JSONB,
    parameters JSONB,
    tags JSONB,
    
    -- Artifacts
    artifact_uri TEXT,
    
    -- Sync info
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mlflow_runs_experiment ON mlflow_runs(mlflow_experiment_id);
CREATE INDEX idx_mlflow_runs_status ON mlflow_runs(status);
CREATE INDEX idx_mlflow_runs_start_time ON mlflow_runs(start_time);

-- ============================================================
-- PREDICTIONS & INFERENCE
-- ============================================================

-- Model predictions/inferences
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES ml_models(id),
    use_case_id UUID REFERENCES ml_use_cases(id),
    
    -- Input data
    input_data JSONB NOT NULL,
    entity_id VARCHAR(100), -- Reference to citizen, application, etc.
    entity_type VARCHAR(50), -- citizen, application, scheme, etc.
    
    -- Prediction results
    prediction JSONB NOT NULL, -- Actual prediction results
    prediction_proba JSONB, -- Prediction probabilities
    confidence_score DECIMAL(5, 2), -- 0-100
    
    -- Metadata
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    inference_time_ms INTEGER,
    
    -- Ground truth (if available later)
    actual_value JSONB,
    is_correct BOOLEAN,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_model ON predictions(model_id);
CREATE INDEX idx_predictions_use_case ON predictions(use_case_id);
CREATE INDEX idx_predictions_entity ON predictions(entity_type, entity_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_predictions_confidence ON predictions(confidence_score);

-- Batch prediction jobs
CREATE TABLE batch_prediction_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_name VARCHAR(255) NOT NULL,
    model_id UUID NOT NULL REFERENCES ml_models(id),
    use_case_id UUID REFERENCES ml_use_cases(id),
    
    -- Job configuration
    input_source_type VARCHAR(50), -- database, file, api
    input_source_config JSONB,
    output_destination_type VARCHAR(50), -- database, file, api
    output_destination_config JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress_percentage DECIMAL(5, 2) DEFAULT 0,
    
    -- Results
    total_records INTEGER,
    processed_records INTEGER,
    failed_records INTEGER,
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_batch_jobs_status ON batch_prediction_jobs(status);
CREATE INDEX idx_batch_jobs_model ON batch_prediction_jobs(model_id);
CREATE INDEX idx_batch_jobs_created_at ON batch_prediction_jobs(created_at);

-- ============================================================
-- DATA PIPELINES
-- ============================================================

-- ETL pipeline runs
CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_name VARCHAR(255) NOT NULL,
    pipeline_type VARCHAR(50) NOT NULL, -- etl, feature_engineering, data_quality, etc.
    
    -- Configuration
    source_type VARCHAR(50), -- citizen_db, dept_db, warehouse, file
    source_config JSONB,
    destination_type VARCHAR(50),
    destination_config JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    progress_percentage DECIMAL(5, 2) DEFAULT 0,
    
    -- Results
    records_processed BIGINT,
    records_failed BIGINT,
    error_message TEXT,
    logs_path TEXT,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_runs_name ON pipeline_runs(pipeline_name);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX idx_pipeline_runs_type ON pipeline_runs(pipeline_type);
CREATE INDEX idx_pipeline_runs_started_at ON pipeline_runs(started_at);

-- ============================================================
-- MODEL MONITORING
-- ============================================================

-- Model performance monitoring
CREATE TABLE model_monitoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES ml_models(id),
    use_case_id UUID REFERENCES ml_use_cases(id),
    
    -- Monitoring period
    monitoring_date DATE NOT NULL,
    monitoring_window VARCHAR(20), -- hourly, daily, weekly, monthly
    
    -- Performance metrics
    prediction_count INTEGER,
    avg_confidence_score DECIMAL(5, 2),
    accuracy DECIMAL(5, 2),
    precision_score DECIMAL(5, 2),
    recall_score DECIMAL(5, 2),
    f1_score DECIMAL(5, 2),
    
    -- Data drift metrics
    data_drift_score DECIMAL(5, 2),
    feature_drift_scores JSONB,
    
    -- Model health
    health_status VARCHAR(20), -- healthy, degraded, critical
    alerts JSONB,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_monitoring_model ON model_monitoring(model_id);
CREATE INDEX idx_model_monitoring_date ON model_monitoring(monitoring_date);
CREATE INDEX idx_model_monitoring_health ON model_monitoring(health_status);

-- ============================================================
-- ANALYTICS & INSIGHTS
-- ============================================================

-- Analytics dashboards cache
CREATE TABLE analytics_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dashboard_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    
    -- Metric values
    metric_value JSONB NOT NULL,
    metric_date DATE,
    period_type VARCHAR(20), -- daily, weekly, monthly, yearly
    
    -- Cache metadata
    cache_key VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP,
    
    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_cache_type ON analytics_cache(dashboard_type);
CREATE INDEX idx_analytics_cache_date ON analytics_cache(metric_date);
CREATE INDEX idx_analytics_cache_expires ON analytics_cache(expires_at);

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_ml_models_updated_at BEFORE UPDATE ON ml_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_use_cases_updated_at BEFORE UPDATE ON ml_use_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mlflow_experiments_updated_at BEFORE UPDATE ON mlflow_experiments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mlflow_runs_updated_at BEFORE UPDATE ON mlflow_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_prediction_jobs_updated_at BEFORE UPDATE ON batch_prediction_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_runs_updated_at BEFORE UPDATE ON pipeline_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE ml_models IS 'ML model registry and metadata';
COMMENT ON TABLE ml_use_cases IS 'ML use cases (27 use cases)';
COMMENT ON TABLE mlflow_experiments IS 'MLflow experiments synchronization cache';
COMMENT ON TABLE mlflow_runs IS 'MLflow runs synchronization cache';
COMMENT ON TABLE predictions IS 'Model predictions and inference results';
COMMENT ON TABLE batch_prediction_jobs IS 'Batch prediction job tracking';
COMMENT ON TABLE pipeline_runs IS 'ETL and data pipeline run tracking';
COMMENT ON TABLE model_monitoring IS 'Model performance and health monitoring';
COMMENT ON TABLE analytics_cache IS 'Cached analytics dashboard data';

