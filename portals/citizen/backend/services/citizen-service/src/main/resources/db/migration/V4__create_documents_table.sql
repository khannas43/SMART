-- Documents uploaded by citizens or departments
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES service_applications(id) ON DELETE CASCADE,
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE SET NULL,
    
    -- Document details
    document_type VARCHAR(100) NOT NULL,
    document_name VARCHAR(255),
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),
    
    -- Verification
    verification_status VARCHAR(20) DEFAULT 'PENDING',
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

