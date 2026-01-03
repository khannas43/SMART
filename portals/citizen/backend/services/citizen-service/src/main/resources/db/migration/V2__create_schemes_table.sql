-- Government schemes available for citizens
CREATE TABLE schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    department VARCHAR(255),
    
    -- Eligibility criteria (JSON)
    eligibility_criteria JSONB,
    
    -- Scheme details
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_schemes_code ON schemes(code);
CREATE INDEX idx_schemes_category ON schemes(category);
CREATE INDEX idx_schemes_status ON schemes(status);

