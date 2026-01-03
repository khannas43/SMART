-- Notifications sent to citizens
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    
    -- Notification details
    type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    -- Read status (for in-app notifications)
    is_read BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_citizen ON notifications(citizen_id);
CREATE INDEX idx_notifications_application ON notifications(application_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

