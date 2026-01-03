-- Feedback and complaints from citizens
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE SET NULL,
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    
    -- Feedback details
    type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    -- Status
    status VARCHAR(20) DEFAULT 'OPEN',
    resolution TEXT,
    resolved_at TIMESTAMP,
    resolved_by UUID,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_citizen ON feedback(citizen_id);
CREATE INDEX idx_feedback_application ON feedback(application_id);
CREATE INDEX idx_feedback_type ON feedback(type);
CREATE INDEX idx_feedback_status ON feedback(status);
CREATE INDEX idx_feedback_created ON feedback(created_at);

