-- Department Portal Database Schema
-- Database: smart_dept
-- Purpose: Store department user data, workflow management, processing, and approvals

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- DEPARTMENT & ORGANIZATION STRUCTURE
-- ============================================================

-- Departments
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(100),
    parent_department_id UUID REFERENCES departments(id),
    level INTEGER DEFAULT 1, -- hierarchy level
    
    -- Department details
    description TEXT,
    head_officer_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_code ON departments(code);
CREATE INDEX idx_departments_parent ON departments(parent_department_id);
CREATE INDEX idx_departments_status ON departments(status);

-- ============================================================
-- DEPARTMENT USERS
-- ============================================================

-- Department officers and staff
CREATE TABLE dept_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    department_id UUID NOT NULL REFERENCES departments(id),
    designation_id UUID REFERENCES designations(id),
    
    -- Personal information
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    mobile_number VARCHAR(10),
    office_phone VARCHAR(20),
    
    -- Authentication
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    last_password_change TIMESTAMP,
    
    -- Role and permissions
    role VARCHAR(50) NOT NULL, -- admin, officer, clerk, supervisor, viewer
    permissions JSONB, -- fine-grained permissions
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended, terminated
    last_login_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_dept_users_employee_id ON dept_users(employee_id);
CREATE INDEX idx_dept_users_department ON dept_users(department_id);
CREATE INDEX idx_dept_users_username ON dept_users(username);
CREATE INDEX idx_dept_users_status ON dept_users(status);
CREATE INDEX idx_dept_users_role ON dept_users(role);

-- Designations/Positions
CREATE TABLE designations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    department_id UUID REFERENCES departments(id),
    level INTEGER, -- hierarchy level
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_designations_code ON designations(code);
CREATE INDEX idx_designations_department ON designations(department_id);

-- ============================================================
-- WORKFLOW MANAGEMENT
-- ============================================================

-- Workflow definitions
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    service_type VARCHAR(100),
    
    -- Workflow configuration
    workflow_steps JSONB NOT NULL, -- JSON array of steps with conditions
    auto_assign BOOLEAN DEFAULT false,
    sla_days INTEGER, -- Service Level Agreement in days
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, draft
    version INTEGER DEFAULT 1,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_code ON workflows(code);
CREATE INDEX idx_workflows_service_type ON workflows(service_type);
CREATE INDEX idx_workflows_status ON workflows(status);

-- Application processing assignments
CREATE TABLE application_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id VARCHAR(100) NOT NULL, -- Reference to citizen portal application
    application_number VARCHAR(50) NOT NULL,
    
    -- Assignment details
    department_id UUID NOT NULL REFERENCES departments(id),
    assigned_to_user_id UUID REFERENCES dept_users(id),
    assigned_by_user_id UUID REFERENCES dept_users(id),
    current_stage VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'assigned', -- assigned, in_progress, completed, transferred
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Timestamps
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date DATE,
    
    -- Additional data
    notes TEXT,
    metadata JSONB,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assignments_application_number ON application_assignments(application_number);
CREATE INDEX idx_assignments_department ON application_assignments(department_id);
CREATE INDEX idx_assignments_assigned_to ON application_assignments(assigned_to_user_id);
CREATE INDEX idx_assignments_status ON application_assignments(status);
CREATE INDEX idx_assignments_due_date ON application_assignments(due_date);

-- ============================================================
-- PROCESSING & APPROVALS
-- ============================================================

-- Processing actions and decisions
CREATE TABLE processing_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assignment_id UUID NOT NULL REFERENCES application_assignments(id) ON DELETE CASCADE,
    application_number VARCHAR(50) NOT NULL,
    
    -- Action details
    action_type VARCHAR(50) NOT NULL, -- approve, reject, request_info, forward, return
    action_by_user_id UUID NOT NULL REFERENCES dept_users(id),
    action_by_department_id UUID REFERENCES departments(id),
    
    -- Decision details
    decision VARCHAR(50), -- approved, rejected, pending, returned
    comments TEXT,
    next_stage VARCHAR(100),
    next_assigned_to UUID REFERENCES dept_users(id),
    
    -- Additional data
    action_data JSONB,
    
    -- Timestamps
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_processing_actions_assignment ON processing_actions(assignment_id);
CREATE INDEX idx_processing_actions_application ON processing_actions(application_number);
CREATE INDEX idx_processing_actions_user ON processing_actions(action_by_user_id);
CREATE INDEX idx_processing_actions_decision ON processing_actions(decision);
CREATE INDEX idx_processing_actions_date ON processing_actions(action_date);

-- Approval chains
CREATE TABLE approval_chains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_number VARCHAR(50) NOT NULL,
    workflow_id UUID REFERENCES workflows(id),
    
    -- Approval sequence
    approval_level INTEGER NOT NULL,
    approver_user_id UUID REFERENCES dept_users(id),
    approver_department_id UUID REFERENCES departments(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, skipped
    approved_at TIMESTAMP,
    comments TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_chains_application ON approval_chains(application_number);
CREATE INDEX idx_approval_chains_approver ON approval_chains(approver_user_id);
CREATE INDEX idx_approval_chains_status ON approval_chains(status);

-- ============================================================
-- DOCUMENTS & VERIFICATION
-- ============================================================

-- Document verification by department
CREATE TABLE document_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(100) NOT NULL, -- Reference to citizen portal document
    application_number VARCHAR(50) NOT NULL,
    
    -- Verification details
    verified_by_user_id UUID NOT NULL REFERENCES dept_users(id),
    verification_status VARCHAR(20) NOT NULL, -- verified, rejected, pending, requires_review
    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_notes TEXT,
    
    -- Verification result
    verification_result JSONB, -- detailed verification data
    confidence_score DECIMAL(5, 2), -- 0-100
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_verifications_document ON document_verifications(document_id);
CREATE INDEX idx_doc_verifications_application ON document_verifications(application_number);
CREATE INDEX idx_doc_verifications_status ON document_verifications(verification_status);
CREATE INDEX idx_doc_verifications_verifier ON document_verifications(verified_by_user_id);

-- ============================================================
-- REPORTS & ANALYTICS
-- ============================================================

-- Dashboard metrics cache
CREATE TABLE dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department_id UUID REFERENCES departments(id),
    user_id UUID REFERENCES dept_users(id),
    
    -- Metric details
    metric_type VARCHAR(50) NOT NULL, -- pending_applications, completed_today, sla_breached, etc.
    metric_value DECIMAL(15, 2),
    metric_date DATE NOT NULL,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dashboard_metrics_dept ON dashboard_metrics(department_id);
CREATE INDEX idx_dashboard_metrics_user ON dashboard_metrics(user_id);
CREATE INDEX idx_dashboard_metrics_type ON dashboard_metrics(metric_type);
CREATE INDEX idx_dashboard_metrics_date ON dashboard_metrics(metric_date);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

-- Internal notifications for department users
CREATE TABLE dept_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES dept_users(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES application_assignments(id) ON DELETE SET NULL,
    
    -- Notification details
    type VARCHAR(50) NOT NULL, -- assignment, reminder, alert, system
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    subject VARCHAR(255),
    message TEXT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'unread', -- unread, read, archived
    read_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dept_notifications_user ON dept_notifications(user_id);
CREATE INDEX idx_dept_notifications_status ON dept_notifications(status);
CREATE INDEX idx_dept_notifications_created_at ON dept_notifications(created_at);

-- ============================================================
-- AUDIT LOG
-- ============================================================

-- Audit trail for department actions
CREATE TABLE dept_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Action details
    entity_type VARCHAR(50) NOT NULL, -- application, document, user, etc.
    entity_id UUID,
    entity_reference VARCHAR(100), -- application_number, etc.
    action VARCHAR(50) NOT NULL, -- create, update, delete, approve, reject, assign
    
    -- Actor
    performed_by_user_id UUID REFERENCES dept_users(id),
    performed_by_department_id UUID REFERENCES departments(id),
    
    -- Action details
    action_details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Timestamp
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dept_audit_log_entity ON dept_audit_log(entity_type, entity_reference);
CREATE INDEX idx_dept_audit_log_user ON dept_audit_log(performed_by_user_id);
CREATE INDEX idx_dept_audit_log_date ON dept_audit_log(performed_at);
CREATE INDEX idx_dept_audit_log_action ON dept_audit_log(action);

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
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dept_users_updated_at BEFORE UPDATE ON dept_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_application_assignments_updated_at BEFORE UPDATE ON application_assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_chains_updated_at BEFORE UPDATE ON approval_chains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_verifications_updated_at BEFORE UPDATE ON document_verifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE departments IS 'Government departments and organizational structure';
COMMENT ON TABLE dept_users IS 'Department officers and staff members';
COMMENT ON TABLE workflows IS 'Workflow definitions for service processing';
COMMENT ON TABLE application_assignments IS 'Assignments of citizen applications to department users';
COMMENT ON TABLE processing_actions IS 'Processing actions and decisions on applications';
COMMENT ON TABLE approval_chains IS 'Multi-level approval chains for applications';
COMMENT ON TABLE document_verifications IS 'Document verification records by department';
COMMENT ON TABLE dashboard_metrics IS 'Cached dashboard metrics for performance';
COMMENT ON TABLE dept_notifications IS 'Internal notifications for department users';
COMMENT ON TABLE dept_audit_log IS 'Audit trail for all department actions';

