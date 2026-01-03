-- Payment transactions for services
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    
    -- Payment details
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50),
    payment_gateway VARCHAR(50),
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING',
    gateway_response JSONB,
    gateway_transaction_id VARCHAR(100),
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_application ON payments(application_id);
CREATE INDEX idx_payments_citizen ON payments(citizen_id);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_date ON payments(initiated_at);

