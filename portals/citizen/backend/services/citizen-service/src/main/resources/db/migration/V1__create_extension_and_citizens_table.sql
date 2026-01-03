-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    status VARCHAR(20) DEFAULT 'ACTIVE',
    verification_status VARCHAR(20) DEFAULT 'PENDING',
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

