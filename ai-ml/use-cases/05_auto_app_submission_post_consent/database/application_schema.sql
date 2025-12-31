-- Auto Application Submission Post-Consent Database Schema
-- Use Case ID: AI-PLATFORM-05
-- Database: smart_warehouse (consolidated with other AI/ML use cases)
-- Schema: application

-- Note: This schema is part of smart_warehouse database
-- All AI/ML use cases use the same smart_warehouse database with different schemas for organization

CREATE SCHEMA IF NOT EXISTS application;

-- Grant permissions to sameer user
GRANT USAGE ON SCHEMA application TO sameer;
GRANT CREATE ON SCHEMA application TO sameer;
ALTER SCHEMA application OWNER TO sameer;

-- ============================================================================
-- APPLICATION MANAGEMENT
-- ============================================================================

-- Applications
-- Main application records created after consent
CREATE TABLE IF NOT EXISTS application.applications (
    application_id SERIAL PRIMARY KEY,
    
    -- Identifiers
    application_number VARCHAR(100) UNIQUE, -- Generated or from department
    family_id UUID NOT NULL,
    member_id UUID, -- NULL for family-level schemes, specific member for individual schemes
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Consent & Eligibility Context
    consent_id INTEGER, -- FK to intimation.consent_records (nullable, can reference consent)
    eligibility_snapshot_id INTEGER, -- FK to eligibility.eligibility_snapshots
    eligibility_score DECIMAL(5,4),
    eligibility_status VARCHAR(50), -- RULE_ELIGIBLE, POSSIBLE_ELIGIBLE
    
    -- Status
    status VARCHAR(50) DEFAULT 'creating', 
    -- creating, draft, pending_review, pending_citizen_input, pending_assisted,
    -- pending_submission, submitted, submission_failed, rejected, accepted, withdrawn
    
    -- Submission Mode
    submission_mode VARCHAR(50), -- auto, review, assisted
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    draft_created_at TIMESTAMP,
    submitted_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    
    -- Department Response
    department_application_number VARCHAR(100), -- Application number from department
    department_response JSONB, -- Full response from department
    department_error_message TEXT,
    
    -- Metadata
    created_by VARCHAR(255) DEFAULT 'application_orchestrator',
    updated_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT unique_active_application UNIQUE (family_id, scheme_code, status) 
        DEFERRABLE INITIALLY DEFERRED -- Allow multiple if status allows
);

CREATE INDEX idx_applications_family_scheme ON application.applications(family_id, scheme_code);
CREATE INDEX idx_applications_status ON application.applications(status);
CREATE INDEX idx_applications_scheme ON application.applications(scheme_code);
CREATE INDEX idx_applications_consent ON application.applications(consent_id) WHERE consent_id IS NOT NULL;
CREATE INDEX idx_applications_created ON application.applications(created_at);

-- Application Fields
-- Field-level data with source tracking for compliance
CREATE TABLE IF NOT EXISTS application.application_fields (
    field_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Field Information
    field_name VARCHAR(255) NOT NULL, -- Form field name (e.g., "full_name", "dob")
    field_path VARCHAR(500), -- JSON path if nested (e.g., "beneficiary.address.district")
    field_type VARCHAR(50), -- string, number, date, boolean, array, object
    field_value JSONB, -- Actual field value (supports all types via JSONB)
    
    -- Source Tracking (for audit and compliance)
    source_type VARCHAR(50) NOT NULL, -- GR (Golden Record), PROFILE_360, CITIZEN, SYSTEM, DERIVED
    source_detail TEXT, -- Additional source info (e.g., "GR.golden_records.first_name")
    
    -- Mapping Information
    mapping_type VARCHAR(50), -- direct, derived, concatenated, conditional, relationship
    mapping_rule_id INTEGER, -- FK to scheme_field_mappings if applicable
    
    -- Validation
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB, -- Array of validation errors if invalid
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_app_fields_application ON application.application_fields(application_id);
CREATE INDEX idx_app_fields_name ON application.application_fields(application_id, field_name);
CREATE INDEX idx_app_fields_source ON application.application_fields(source_type);

-- Application Documents
-- Document attachments with references to document store
CREATE TABLE IF NOT EXISTS application.application_documents (
    document_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Document Information
    document_type VARCHAR(100) NOT NULL, -- AADHAAR, DISABILITY_CERT, INCOME_CERT, etc.
    document_name VARCHAR(255),
    document_category VARCHAR(50), -- IDENTITY, INCOME, DISABILITY, ADDRESS, OTHER
    
    -- Document Reference (to Raj eVault or document store)
    document_store VARCHAR(50), -- RAJ_EVAULT, S3, AZURE_BLOB, etc.
    document_reference VARCHAR(500), -- Document ID or URL in document store
    document_url TEXT, -- Direct URL if available
    
    -- Status
    status VARCHAR(50) DEFAULT 'attached', -- attached, missing, invalid, verified
    is_mandatory BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    
    -- Metadata
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP,
    verified_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_app_docs_application ON application.application_documents(application_id);
CREATE INDEX idx_app_docs_type ON application.application_documents(document_type);
CREATE INDEX idx_app_docs_status ON application.application_documents(status);
CREATE INDEX idx_app_docs_mandatory ON application.application_documents(application_id, is_mandatory) WHERE is_mandatory = true;

-- Application Validation Results
-- Comprehensive validation results and errors
CREATE TABLE IF NOT EXISTS application.application_validation_results (
    validation_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Validation Type
    validation_type VARCHAR(50) NOT NULL, -- syntactic, semantic, completeness, fraud_check
    validation_category VARCHAR(100), -- type_check, format_check, business_rule, etc.
    
    -- Results
    is_valid BOOLEAN NOT NULL,
    severity VARCHAR(20), -- error, warning, info
    field_name VARCHAR(255), -- Specific field if applicable, NULL for application-level
    error_code VARCHAR(100), -- Error code for programmatic handling
    error_message TEXT NOT NULL, -- Human-readable error message
    error_details JSONB, -- Additional error context
    
    -- Timestamps
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_app_validation_application ON application.application_validation_results(application_id);
CREATE INDEX idx_app_validation_type ON application.application_validation_results(validation_type);
CREATE INDEX idx_app_validation_valid ON application.application_validation_results(application_id, is_valid) WHERE is_valid = false;

-- Application Submissions
-- Submission records and department responses
CREATE TABLE IF NOT EXISTS application.application_submissions (
    submission_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Submission Details
    submission_mode VARCHAR(50) NOT NULL, -- auto, review, assisted
    connector_type VARCHAR(50) NOT NULL, -- REST, SOAP, API_SETU
    connector_name VARCHAR(100), -- Specific connector identifier
    
    -- Payload
    submission_payload JSONB NOT NULL, -- Full payload sent to department
    payload_format VARCHAR(50), -- JSON, XML, FORM_DATA
    
    -- Department Response
    department_response JSONB, -- Full response from department
    department_application_number VARCHAR(100), -- Application number assigned by department
    response_status_code INTEGER, -- HTTP status code or equivalent
    response_status VARCHAR(50), -- success, error, validation_error, etc.
    response_message TEXT,
    
    -- Retry Tracking
    attempt_number INTEGER DEFAULT 1,
    is_retry BOOLEAN DEFAULT false,
    previous_submission_id INTEGER, -- FK to previous submission if retry
    
    -- Timestamps
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    
    -- Metadata
    submitted_by VARCHAR(255) DEFAULT 'application_orchestrator',
    processing_time_ms INTEGER -- Time taken for submission
);

CREATE INDEX idx_app_submissions_application ON application.application_submissions(application_id);
CREATE INDEX idx_app_submissions_status ON application.application_submissions(response_status);
CREATE INDEX idx_app_submissions_submitted ON application.application_submissions(submitted_at);

-- Application Audit Logs
-- Immutable audit trail for compliance and transparency
CREATE TABLE IF NOT EXISTS application.application_audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Audit Event
    event_type VARCHAR(100) NOT NULL, 
    -- CREATED, FIELD_UPDATED, STATUS_CHANGED, VALIDATED, SUBMITTED, REJECTED, etc.
    event_description TEXT,
    
    -- Changes (for field updates)
    field_name VARCHAR(255),
    old_value JSONB,
    new_value JSONB,
    source_type VARCHAR(50), -- GR, PROFILE_360, CITIZEN, SYSTEM
    
    -- Context
    triggered_by VARCHAR(50), -- consent_event, citizen_action, system, manual
    trigger_details JSONB, -- Additional context about what triggered the change
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Actor
    actor_type VARCHAR(50), -- system, citizen, officer, admin
    actor_id VARCHAR(255), -- User ID if applicable
    actor_name VARCHAR(255) -- Human-readable actor name
);

CREATE INDEX idx_app_audit_application ON application.application_audit_logs(application_id);
CREATE INDEX idx_app_audit_event ON application.application_audit_logs(event_type);
CREATE INDEX idx_app_audit_timestamp ON application.application_audit_logs(event_timestamp);
CREATE INDEX idx_app_audit_field ON application.application_audit_logs(application_id, field_name) WHERE field_name IS NOT NULL;

-- ============================================================================
-- SCHEME FORM SCHEMAS & MAPPINGS
-- ============================================================================

-- Scheme Form Schemas
-- Canonical form schemas per scheme
CREATE TABLE IF NOT EXISTS application.scheme_form_schemas (
    schema_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Schema Definition
    schema_definition JSONB NOT NULL, -- JSON Schema for the form
    schema_version VARCHAR(20) DEFAULT '1.0',
    
    -- Field Definitions (extracted from schema_definition for easy querying)
    fields JSONB, -- Array of field definitions with types, constraints, etc.
    mandatory_fields TEXT[], -- List of mandatory field names
    optional_fields TEXT[],
    
    -- Validation Rules
    validation_rules JSONB, -- Business rules and validation logic
    semantic_rules JSONB, -- Semantic validation rules
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_until TIMESTAMP, -- NULL = indefinitely
    
    -- Metadata
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    -- Constraints
    UNIQUE(scheme_code, schema_version)
);

CREATE INDEX idx_form_schemas_scheme ON application.scheme_form_schemas(scheme_code);
CREATE INDEX idx_form_schemas_active ON application.scheme_form_schemas(scheme_code, is_active) WHERE is_active = true;

-- Scheme Field Mappings
-- Mapping rules from GR/360° to form fields
CREATE TABLE IF NOT EXISTS application.scheme_field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Target Field
    target_field_name VARCHAR(255) NOT NULL, -- Form field name
    target_field_path VARCHAR(500), -- JSON path if nested
    
    -- Mapping Type
    mapping_type VARCHAR(50) NOT NULL, -- direct, derived, concatenated, conditional, relationship
    priority INTEGER DEFAULT 100, -- Lower = higher priority if multiple mappings for same field
    
    -- Source Definition
    source_type VARCHAR(50) NOT NULL, -- GR, PROFILE_360, ELIGIBILITY, SYSTEM, CONSTANT
    source_field VARCHAR(500), -- Source field path (e.g., "GR.first_name", "360.income_band")
    source_fields TEXT[], -- Multiple source fields for concatenated mappings
    
    -- Transformation
    transformation_expression TEXT, -- Jinja2 template or Python expression for transformation
    transformation_type VARCHAR(50), -- jinja2, python, sql, constant
    
    -- Conditional Mapping
    condition_expression TEXT, -- Condition to evaluate before applying mapping
    condition_type VARCHAR(50), -- jinja2, python
    
    -- Default Value
    default_value JSONB, -- Default if source not available
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_mandatory BOOLEAN DEFAULT false, -- If mapping is required for form completeness
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    description TEXT,
    created_by VARCHAR(255)
);

CREATE INDEX idx_field_mappings_scheme ON application.scheme_field_mappings(scheme_code);
CREATE INDEX idx_field_mappings_target ON application.scheme_field_mappings(scheme_code, target_field_name);
CREATE INDEX idx_field_mappings_active ON application.scheme_field_mappings(scheme_code, is_active) WHERE is_active = true;
CREATE INDEX idx_field_mappings_priority ON application.scheme_field_mappings(scheme_code, priority);

-- Submission Modes Configuration
-- Per-scheme submission mode configuration
CREATE TABLE IF NOT EXISTS application.submission_modes_config (
    config_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) NOT NULL REFERENCES public.scheme_master(scheme_code) ON DELETE CASCADE,
    
    -- Submission Mode
    default_mode VARCHAR(50) NOT NULL, -- auto, review, assisted
    
    -- Auto Submission Rules
    allow_auto_submission BOOLEAN DEFAULT false,
    auto_submission_conditions JSONB, -- Conditions for auto submission (e.g., score > 0.9, all docs present)
    
    -- Review Mode Rules
    require_citizen_review BOOLEAN DEFAULT true,
    editable_fields TEXT[], -- Fields citizen can edit during review
    read_only_fields TEXT[], -- Fields that are read-only
    
    -- Assisted Mode Rules
    route_to_assisted_on_missing_data BOOLEAN DEFAULT true,
    missing_data_threshold INTEGER, -- Number of missing fields before routing
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    UNIQUE(scheme_code)
);

CREATE INDEX idx_submission_modes_scheme ON application.submission_modes_config(scheme_code);
CREATE INDEX idx_submission_modes_active ON application.submission_modes_config(scheme_code, is_active) WHERE is_active = true;

-- Department Connectors
-- Department API configurations
CREATE TABLE IF NOT EXISTS application.department_connectors (
    connector_id SERIAL PRIMARY KEY,
    
    -- Connector Identification
    connector_name VARCHAR(100) NOT NULL UNIQUE,
    department_name VARCHAR(255),
    scheme_code VARCHAR(50) REFERENCES public.scheme_master(scheme_code) ON DELETE SET NULL,
    
    -- Connector Type
    connector_type VARCHAR(50) NOT NULL, -- REST, SOAP, API_SETU
    connector_version VARCHAR(20),
    
    -- Configuration
    base_url TEXT, -- Base URL for REST/SOAP endpoints
    endpoint_path TEXT, -- API endpoint path
    wsdl_url TEXT, -- WSDL URL for SOAP
    api_setu_config JSONB, -- API Setu specific configuration
    
    -- Authentication
    auth_type VARCHAR(50), -- NONE, API_KEY, OAUTH2, BASIC, WSS
    auth_config JSONB, -- Authentication configuration (encrypted)
    
    -- Payload Configuration
    payload_format VARCHAR(50), -- JSON, XML, FORM_DATA
    payload_template JSONB, -- Template for payload construction
    response_schema JSONB, -- Expected response schema
    
    -- Retry Configuration
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 5,
    retry_on_status_codes INTEGER[], -- HTTP status codes to retry on
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_test_mode BOOLEAN DEFAULT false, -- Use test endpoint
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested_at TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    description TEXT
);

CREATE INDEX idx_connectors_name ON application.department_connectors(connector_name);
CREATE INDEX idx_connectors_scheme ON application.department_connectors(scheme_code);
CREATE INDEX idx_connectors_active ON application.department_connectors(is_active) WHERE is_active = true;
CREATE INDEX idx_connectors_type ON application.department_connectors(connector_type);

-- Application Events
-- Event log for downstream integration
CREATE TABLE IF NOT EXISTS application.application_events (
    event_id BIGSERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES application.applications(application_id) ON DELETE CASCADE,
    
    -- Event Details
    event_type VARCHAR(100) NOT NULL,
    -- APPLICATION_DRAFT_CREATED, APPLICATION_SUBMITTED, APPLICATION_REJECTED_BY_DEPT_VALIDATION,
    -- APPLICATION_ACCEPTED_BY_DEPT, APPLICATION_STATUS_UPDATED, etc.
    
    event_data JSONB NOT NULL, -- Event payload
    event_status VARCHAR(50) DEFAULT 'pending', -- pending, published, failed
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    
    -- Consumer Tracking (optional, for event streaming)
    consumed_by TEXT[] -- List of consumer IDs that have processed this event
);

CREATE INDEX idx_app_events_type ON application.application_events(event_type);
CREATE INDEX idx_app_events_application ON application.application_events(application_id);
CREATE INDEX idx_app_events_timestamp ON application.application_events(event_timestamp);
CREATE INDEX idx_app_events_status ON application.application_events(event_status) WHERE event_status = 'pending';

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION application.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER trigger_applications_updated_at
    BEFORE UPDATE ON application.applications
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_application_fields_updated_at
    BEFORE UPDATE ON application.application_fields
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_application_documents_updated_at
    BEFORE UPDATE ON application.application_documents
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_scheme_form_schemas_updated_at
    BEFORE UPDATE ON application.scheme_form_schemas
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_scheme_field_mappings_updated_at
    BEFORE UPDATE ON application.scheme_field_mappings
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_submission_modes_config_updated_at
    BEFORE UPDATE ON application.submission_modes_config
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

CREATE TRIGGER trigger_department_connectors_updated_at
    BEFORE UPDATE ON application.department_connectors
    FOR EACH ROW EXECUTE FUNCTION application.update_updated_at();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON SCHEMA application IS 'Schema for Auto Application Submission Post-Consent (AI-PLATFORM-05)';
COMMENT ON TABLE application.applications IS 'Main application records created after consent';
COMMENT ON TABLE application.application_fields IS 'Field-level data with source tracking for compliance';
COMMENT ON TABLE application.application_documents IS 'Document attachments with references to document store';
COMMENT ON TABLE application.application_validation_results IS 'Validation results and errors';
COMMENT ON TABLE application.application_submissions IS 'Submission records and department responses';
COMMENT ON TABLE application.application_audit_logs IS 'Immutable audit trail for compliance';
COMMENT ON TABLE application.scheme_form_schemas IS 'Canonical form schemas per scheme';
COMMENT ON TABLE application.scheme_field_mappings IS 'Mapping rules from GR/360° to form fields';
COMMENT ON TABLE application.submission_modes_config IS 'Per-scheme submission mode configuration';
COMMENT ON TABLE application.department_connectors IS 'Department API configurations';
COMMENT ON TABLE application.application_events IS 'Event log for downstream integration';

