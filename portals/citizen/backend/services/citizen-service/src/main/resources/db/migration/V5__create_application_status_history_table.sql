-- Track status changes and workflow
CREATE TABLE application_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES service_applications(id) ON DELETE CASCADE,
    
    -- Status change details
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    stage VARCHAR(100),
    comments TEXT,
    
    -- Actor information
    changed_by UUID,
    changed_by_type VARCHAR(20),
    
    -- Timestamps
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status_history_application ON application_status_history(application_id);
CREATE INDEX idx_status_history_changed_at ON application_status_history(changed_at);

