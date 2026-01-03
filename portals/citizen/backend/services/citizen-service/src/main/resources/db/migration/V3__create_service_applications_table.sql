-- Service applications submitted by citizens
CREATE TABLE service_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_number VARCHAR(50) UNIQUE NOT NULL,
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    scheme_id UUID REFERENCES schemes(id),
    
    -- Application details
    service_type VARCHAR(100) NOT NULL,
    application_type VARCHAR(100),
    subject TEXT,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'NORMAL',
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'SUBMITTED',
    current_stage VARCHAR(100),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
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

-- Sequence for application numbers
CREATE SEQUENCE IF NOT EXISTS application_number_seq START 1;

