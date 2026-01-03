-- Audit trail for all important actions
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Action details
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    action_details JSONB,
    
    -- Actor
    performed_by UUID,
    performed_by_type VARCHAR(20),
    
    -- IP and location
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Timestamp
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_performed_by ON audit_log(performed_by);
CREATE INDEX idx_audit_log_performed_at ON audit_log(performed_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);

