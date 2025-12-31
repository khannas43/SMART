-- Monitor Portal Database Schema
-- Database: smart_monitor
-- Purpose: System monitoring, logs, metrics, health checks, and administration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- SYSTEM COMPONENTS
-- ============================================================

-- Registered system components (portals, services, databases)
CREATE TABLE system_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_name VARCHAR(255) UNIQUE NOT NULL,
    component_type VARCHAR(50) NOT NULL, -- portal, service, database, cache, queue
    category VARCHAR(50), -- citizen_portal, dept_portal, aiml_portal, monitor_portal, shared_service
    
    -- Component details
    description TEXT,
    host VARCHAR(255),
    port INTEGER,
    endpoint_url TEXT,
    health_check_url TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'unknown', -- healthy, degraded, down, unknown
    is_critical BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_components_name ON system_components(component_name);
CREATE INDEX idx_components_type ON system_components(component_type);
CREATE INDEX idx_components_status ON system_components(status);
CREATE INDEX idx_components_category ON system_components(category);

-- ============================================================
-- HEALTH CHECKS
-- ============================================================

-- Component health check results
CREATE TABLE health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    
    -- Health check details
    check_type VARCHAR(50) NOT NULL, -- ping, http, database, custom
    status VARCHAR(20) NOT NULL, -- success, failure, timeout
    response_time_ms INTEGER,
    status_code INTEGER,
    
    -- Response details
    response_message TEXT,
    error_message TEXT,
    
    -- Timestamps
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_checks_component ON health_checks(component_id);
CREATE INDEX idx_health_checks_status ON health_checks(status);
CREATE INDEX idx_health_checks_checked_at ON health_checks(checked_at);

-- ============================================================
-- METRICS & PERFORMANCE
-- ============================================================

-- System metrics collection
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    
    -- Metric details
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50), -- counter, gauge, histogram, summary
    metric_value DECIMAL(15, 4),
    metric_unit VARCHAR(20), -- bytes, seconds, requests, percentage
    
    -- Tags/labels
    tags JSONB,
    
    -- Timestamp
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_component ON system_metrics(component_id);
CREATE INDEX idx_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_metrics_collected_at ON system_metrics(collected_at);

-- Performance metrics (CPU, Memory, Disk, Network)
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    host_name VARCHAR(255),
    
    -- Resource metrics
    cpu_usage_percent DECIMAL(5, 2),
    memory_used_bytes BIGINT,
    memory_total_bytes BIGINT,
    memory_usage_percent DECIMAL(5, 2),
    disk_used_bytes BIGINT,
    disk_total_bytes BIGINT,
    disk_usage_percent DECIMAL(5, 2),
    network_rx_bytes BIGINT,
    network_tx_bytes BIGINT,
    
    -- Application metrics
    active_connections INTEGER,
    requests_per_second DECIMAL(10, 2),
    error_rate DECIMAL(5, 2),
    
    -- Timestamp
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_component ON performance_metrics(component_id);
CREATE INDEX idx_performance_collected_at ON performance_metrics(collected_at);

-- ============================================================
-- LOGS
-- ============================================================

-- System logs aggregation
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    
    -- Log details
    log_level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARN, ERROR, FATAL
    logger_name VARCHAR(255),
    message TEXT NOT NULL,
    stack_trace TEXT,
    
    -- Context
    thread_name VARCHAR(255),
    class_name VARCHAR(255),
    method_name VARCHAR(255),
    line_number INTEGER,
    
    -- Metadata
    mdc_data JSONB, -- Mapped Diagnostic Context
    exception_type VARCHAR(255),
    
    -- Timestamp
    logged_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_logs_component ON system_logs(component_id);
CREATE INDEX idx_logs_level ON system_logs(log_level);
CREATE INDEX idx_logs_logged_at ON system_logs(logged_at);
CREATE INDEX idx_logs_logger ON system_logs(logger_name);

-- Log aggregations (pre-aggregated for faster queries)
CREATE TABLE log_aggregations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    
    -- Aggregation period
    aggregation_date DATE NOT NULL,
    aggregation_hour INTEGER, -- 0-23
    log_level VARCHAR(20) NOT NULL,
    
    -- Counts
    log_count BIGINT NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_log_agg_component ON log_aggregations(component_id);
CREATE INDEX idx_log_agg_date ON log_aggregations(aggregation_date);
CREATE INDEX idx_log_agg_level ON log_aggregations(log_level);

-- ============================================================
-- ALERTS & INCIDENTS
-- ============================================================

-- Alert definitions
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(255) UNIQUE NOT NULL,
    component_id UUID REFERENCES system_components(id) ON DELETE CASCADE,
    
    -- Rule configuration
    metric_name VARCHAR(100),
    condition_type VARCHAR(50), -- threshold, rate_change, anomaly
    condition_config JSONB NOT NULL,
    
    -- Alert settings
    severity VARCHAR(20) NOT NULL, -- info, warning, critical
    enabled BOOLEAN DEFAULT true,
    notification_channels JSONB, -- email, sms, webhook, etc.
    
    -- Metadata
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alert_rules_component ON alert_rules(component_id);
CREATE INDEX idx_alert_rules_enabled ON alert_rules(enabled);
CREATE INDEX idx_alert_rules_severity ON alert_rules(severity);

-- Alert incidents
CREATE TABLE alert_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_rule_id UUID NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    
    -- Incident details
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open', -- open, acknowledged, resolved, closed
    
    -- Resolution
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    
    -- Metadata
    metric_value DECIMAL(15, 4),
    threshold_value DECIMAL(15, 4),
    metadata JSONB,
    
    -- Timestamps
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidents_alert_rule ON alert_incidents(alert_rule_id);
CREATE INDEX idx_incidents_component ON alert_incidents(component_id);
CREATE INDEX idx_incidents_status ON alert_incidents(status);
CREATE INDEX idx_incidents_severity ON alert_incidents(severity);
CREATE INDEX idx_incidents_triggered_at ON alert_incidents(triggered_at);

-- ============================================================
-- USERS & PERMISSIONS
-- ============================================================

-- Monitor portal admin users
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    
    -- Authentication
    password_hash VARCHAR(255),
    last_password_change TIMESTAMP,
    
    -- Role and permissions
    role VARCHAR(50) NOT NULL, -- super_admin, admin, operator, viewer
    permissions JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
    last_login_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_admin_users_status ON admin_users(status);

-- ============================================================
-- AUDIT LOG
-- ============================================================

-- Comprehensive audit log
CREATE TABLE monitor_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Action details
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    action VARCHAR(50) NOT NULL, -- create, update, delete, view, configure
    
    -- Actor
    performed_by_user_id UUID REFERENCES admin_users(id),
    performed_by_type VARCHAR(20), -- admin, system
    
    -- Action details
    action_details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Timestamp
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_monitor_audit_log_entity ON monitor_audit_log(entity_type, entity_id);
CREATE INDEX idx_monitor_audit_log_user ON monitor_audit_log(performed_by_user_id);
CREATE INDEX idx_monitor_audit_log_date ON monitor_audit_log(performed_at);
CREATE INDEX idx_monitor_audit_log_action ON monitor_audit_log(action);

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
CREATE TRIGGER update_components_updated_at BEFORE UPDATE ON system_components
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_rules_updated_at BEFORE UPDATE ON alert_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_incidents_updated_at BEFORE UPDATE ON alert_incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE system_components IS 'Registered system components for monitoring';
COMMENT ON TABLE health_checks IS 'Health check results for system components';
COMMENT ON TABLE system_metrics IS 'System metrics collection';
COMMENT ON TABLE performance_metrics IS 'Performance metrics (CPU, Memory, Disk, Network)';
COMMENT ON TABLE system_logs IS 'Aggregated system logs';
COMMENT ON TABLE log_aggregations IS 'Pre-aggregated log statistics';
COMMENT ON TABLE alert_rules IS 'Alert rule definitions';
COMMENT ON TABLE alert_incidents IS 'Alert incidents and their resolution';
COMMENT ON TABLE admin_users IS 'Monitor portal administrator users';
COMMENT ON TABLE monitor_audit_log IS 'Comprehensive audit trail for monitor portal';

