-- Citizen Portal Database Schema
-- Database: smart_citizen
-- Purpose: Store citizen-facing data including service requests, applications, documents

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USER & AUTHENTICATION
-- ============================================================

-- Citizens table (user accounts)
CREATE TABLE citizens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aadhaar_number VARCHAR(12) UNIQUE,
    mobile_number VARCHAR(10) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    address_line1 TEXT,
    address_line2 TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100) DEFAULT 'Rajasthan',
    pincode VARCHAR(6),
    
    -- Account status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended, verified
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    last_login_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_citizens_mobile ON citizens(mobile_number);
CREATE INDEX idx_citizens_aadhaar ON citizens(aadhaar_number);
CREATE INDEX idx_citizens_status ON citizens(status);

-- ============================================================
-- SERVICES & SCHEMES
-- ============================================================

-- Government schemes available for citizens
CREATE TABLE schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- social_welfare, education, health, financial, etc.
    department VARCHAR(255),
    
    -- Eligibility criteria (JSON or text)
    eligibility_criteria JSONB,
    
    -- Scheme details
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, closed
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_schemes_code ON schemes(code);
CREATE INDEX idx_schemes_category ON schemes(category);
CREATE INDEX idx_schemes_status ON schemes(status);

-- ============================================================
-- SERVICE APPLICATIONS
-- ============================================================

-- Service applications submitted by citizens
CREATE TABLE service_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_number VARCHAR(50) UNIQUE NOT NULL,
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    scheme_id UUID REFERENCES schemes(id),
    
    -- Application details
    service_type VARCHAR(100) NOT NULL,
    application_type VARCHAR(100), -- new, renewal, modification, cancellation
    subject TEXT,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, under_review, approved, rejected, completed, cancelled
    current_stage VARCHAR(100),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Processing details
    assigned_to_dept VARCHAR(255),
    assigned_to_officer UUID,
    expected_completion_date DATE,
    actual_completion_date TIMESTAMP,
    
    -- Additional data (JSON for flexible schema)
    application_data JSONB,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_applications_citizen ON service_applications(citizen_id);
CREATE INDEX idx_applications_scheme ON service_applications(scheme_id);
CREATE INDEX idx_applications_status ON service_applications(status);
CREATE INDEX idx_applications_number ON service_applications(application_number);
CREATE INDEX idx_applications_submission_date ON service_applications(submission_date);

-- ============================================================
-- DOCUMENTS
-- ============================================================

-- Documents uploaded by citizens or departments
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES service_applications(id) ON DELETE CASCADE,
    citizen_id UUID REFERENCES citizens(id) ON DELETE SET NULL,
    
    -- Document details
    document_type VARCHAR(100) NOT NULL, -- aadhaar, pan, photo, certificate, etc.
    document_name VARCHAR(255),
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64), -- SHA-256 hash for integrity
    
    -- Verification
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    verified_by UUID,
    verified_at TIMESTAMP,
    verification_notes TEXT,
    
    -- Audit fields
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_documents_citizen ON documents(citizen_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_verification ON documents(verification_status);

-- ============================================================
-- APPLICATION STATUS HISTORY
-- ============================================================

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
    changed_by UUID, -- citizen_id or officer_id
    changed_by_type VARCHAR(20), -- citizen, officer, system
    
    -- Timestamps
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status_history_application ON application_status_history(application_id);
CREATE INDEX idx_status_history_changed_at ON application_status_history(changed_at);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

-- Notifications sent to citizens
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_id UUID REFERENCES citizens(id) ON DELETE CASCADE,
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    
    -- Notification details
    type VARCHAR(50) NOT NULL, -- email, sms, push, in_app
    channel VARCHAR(20) NOT NULL, -- email, sms, push
    subject VARCHAR(255),
    message TEXT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, delivered, failed, read
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_citizen ON notifications(citizen_id);
CREATE INDEX idx_notifications_application ON notifications(application_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- ============================================================
-- PAYMENTS
-- ============================================================

-- Payment transactions for services
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    
    -- Payment details
    transaction_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50), -- online, cash, cheque, upi
    payment_gateway VARCHAR(50),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, success, failed, refunded
    gateway_response JSONB,
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_application ON payments(application_id);
CREATE INDEX idx_payments_citizen ON payments(citizen_id);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(status);

-- ============================================================
-- FEEDBACK & COMPLAINTS
-- ============================================================

-- Feedback and complaints from citizens
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citizen_id UUID REFERENCES citizens(id) ON DELETE SET NULL,
    application_id UUID REFERENCES service_applications(id) ON DELETE SET NULL,
    
    -- Feedback details
    type VARCHAR(50) NOT NULL, -- feedback, complaint, suggestion, rating
    category VARCHAR(100),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open', -- open, in_progress, resolved, closed
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

-- ============================================================
-- AUDIT LOG
-- ============================================================

-- Audit trail for all important actions
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Action details
    entity_type VARCHAR(50) NOT NULL, -- citizen, application, document, etc.
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- create, update, delete, view, approve, reject
    action_details JSONB,
    
    -- Actor
    performed_by UUID,
    performed_by_type VARCHAR(20), -- citizen, officer, system
    
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

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_citizens_updated_at BEFORE UPDATE ON citizens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_applications_updated_at BEFORE UPDATE ON service_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate application number
CREATE OR REPLACE FUNCTION generate_application_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.application_number IS NULL THEN
        NEW.application_number := 'APP-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') || '-' || 
                                  LPAD(NEXTVAL('application_number_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create sequence for application numbers
CREATE SEQUENCE IF NOT EXISTS application_number_seq START 1;

-- Trigger for application number generation
CREATE TRIGGER generate_application_number_trigger BEFORE INSERT ON service_applications
    FOR EACH ROW EXECUTE FUNCTION generate_application_number();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE citizens IS 'Citizen user accounts and profile information';
COMMENT ON TABLE schemes IS 'Government schemes available for citizens to apply';
COMMENT ON TABLE service_applications IS 'Service applications submitted by citizens';
COMMENT ON TABLE documents IS 'Documents uploaded by citizens or departments';
COMMENT ON TABLE application_status_history IS 'Status change history for applications';
COMMENT ON TABLE notifications IS 'Notifications sent to citizens';
COMMENT ON TABLE payments IS 'Payment transactions for services';
COMMENT ON TABLE feedback IS 'Feedback and complaints from citizens';
COMMENT ON TABLE audit_log IS 'Audit trail for all important actions';

