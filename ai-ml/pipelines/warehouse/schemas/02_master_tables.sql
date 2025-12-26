-- SMART Rajasthan Master Data Foundation
-- Master Tables for AIML Warehouse
-- Database: smart_warehouse

-- ============================================================
-- CORE MASTER TABLES
-- ============================================================

-- 1. Districts (33 Rajasthan districts)
CREATE TABLE IF NOT EXISTS districts (
    district_id SERIAL PRIMARY KEY,
    district_code VARCHAR(10) UNIQUE NOT NULL,
    district_name VARCHAR(100) NOT NULL,
    population BIGINT,
    area_sqkm DECIMAL(10,2),
    is_urban BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE districts IS 'Rajasthan districts master data (33 districts)';

-- 2. Castes (GEN/OBC/SC/ST with sub-categories)
CREATE TABLE IF NOT EXISTS castes (
    caste_id SERIAL PRIMARY KEY,
    caste_code VARCHAR(20) UNIQUE NOT NULL,
    caste_name VARCHAR(100) NOT NULL,
    category VARCHAR(10) NOT NULL CHECK (category IN ('GEN', 'OBC', 'SC', 'ST')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE castes IS 'Caste master data with categories (GEN/OBC/SC/ST)';

-- 3. Scheme Categories
CREATE TABLE IF NOT EXISTS scheme_categories (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE scheme_categories IS 'Scheme categories (Health/Education/Housing/etc.)';

-- 4. Education Levels
CREATE TABLE IF NOT EXISTS education_levels (
    level_id SERIAL PRIMARY KEY,
    level_code VARCHAR(20) UNIQUE NOT NULL,
    level_name VARCHAR(100) NOT NULL,
    level_order INTEGER NOT NULL, -- For sorting: 1=Illiterate, 2=Primary, etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE education_levels IS 'Education level master (Illiterate/Primary/Graduate/etc.)';

-- 5. Employment Types
CREATE TABLE IF NOT EXISTS employment_types (
    type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE employment_types IS 'Employment type master (Unemployed/Casual/Regular/etc.)';

-- 6. House Types (Eligibility Scoring Specific)
CREATE TABLE IF NOT EXISTS house_types (
    type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE house_types IS 'House type master (Kutcha/Pucca/Semi)';

-- ============================================================
-- SCHEMES & ELIGIBILITY
-- ============================================================

-- 7. Schemes (12 Rajasthan schemes)
CREATE TABLE IF NOT EXISTS schemes (
    scheme_id SERIAL PRIMARY KEY,
    scheme_code VARCHAR(50) UNIQUE NOT NULL,
    scheme_name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES scheme_categories(category_id),
    description TEXT,
    
    -- Eligibility Criteria
    min_age INTEGER,
    max_age INTEGER,
    max_income DECIMAL(12,2), -- Annual family income limit
    min_marks DECIMAL(5,2), -- Minimum marks/score if applicable
    target_caste VARCHAR(10), -- NULL = all, or specific category
    bpl_required BOOLEAN DEFAULT false,
    farmer_required BOOLEAN DEFAULT false,
    house_type_required INTEGER REFERENCES house_types(type_id), -- NULL = not required
    
    -- Scheme Details
    benefit_amount DECIMAL(12,2), -- Annual benefit amount
    benefit_type VARCHAR(50), -- Cash/Scholarship/Housing/etc.
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_schemes_category ON schemes(category_id);
CREATE INDEX idx_schemes_status ON schemes(status);
CREATE INDEX idx_schemes_target_caste ON schemes(target_caste);

COMMENT ON TABLE schemes IS 'Rajasthan government schemes with eligibility criteria';

-- 8. Scheme Eligibility Criteria (Detailed rules)
CREATE TABLE IF NOT EXISTS scheme_eligibility_criteria (
    criteria_id SERIAL PRIMARY KEY,
    scheme_id INTEGER NOT NULL REFERENCES schemes(scheme_id),
    criteria_type VARCHAR(50) NOT NULL, -- age_range, income_limit, caste_list, education, etc.
    criteria_value TEXT NOT NULL, -- JSON or specific value
    criteria_description TEXT,
    is_mandatory BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_eligibility_scheme ON scheme_eligibility_criteria(scheme_id);
CREATE INDEX idx_eligibility_type ON scheme_eligibility_criteria(criteria_type);

COMMENT ON TABLE scheme_eligibility_criteria IS 'Detailed eligibility criteria for schemes';

-- ============================================================
-- TRANSACTIONAL TABLES
-- ============================================================

-- 9. Citizens (100K synthetic Rajasthan citizens)
CREATE TABLE IF NOT EXISTS citizens (
    citizen_id BIGSERIAL PRIMARY KEY,
    jan_aadhaar VARCHAR(12) UNIQUE, -- Jan Aadhaar number (Rajasthan specific)
    aadhaar_number VARCHAR(12), -- Regular Aadhaar
    
    -- Basic Information
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(300) GENERATED ALWAYS AS (
        CASE 
            WHEN middle_name IS NOT NULL THEN first_name || ' ' || middle_name || ' ' || COALESCE(last_name, '')
            ELSE first_name || ' ' || COALESCE(last_name, '')
        END
    ) STORED,
    
    date_of_birth DATE NOT NULL,
    age INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(date_of_birth))) STORED,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    
    -- Location
    district_id INTEGER NOT NULL REFERENCES districts(district_id),
    city_village VARCHAR(100),
    pincode VARCHAR(6),
    is_urban BOOLEAN DEFAULT false,
    
    -- Demographic & Socio-economic
    caste_id INTEGER NOT NULL REFERENCES castes(caste_id),
    family_income DECIMAL(12,2), -- Annual family income
    family_size INTEGER DEFAULT 4,
    
    -- Education & Employment
    education_id INTEGER REFERENCES education_levels(level_id),
    employment_id INTEGER REFERENCES employment_types(type_id),
    
    -- Eligibility Flags
    bpl_card BOOLEAN DEFAULT false, -- BPL (Below Poverty Line) card holder
    house_type_id INTEGER REFERENCES house_types(type_id),
    farmer BOOLEAN DEFAULT false,
    disabled BOOLEAN DEFAULT false,
    
    -- Contact
    mobile_number VARCHAR(10),
    email VARCHAR(255),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, deceased
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_citizens_district ON citizens(district_id);
CREATE INDEX idx_citizens_caste ON citizens(caste_id);
CREATE INDEX idx_citizens_age ON citizens(age);
CREATE INDEX idx_citizens_income ON citizens(family_income);
CREATE INDEX idx_citizens_jan_aadhaar ON citizens(jan_aadhaar);
CREATE INDEX idx_citizens_bpl ON citizens(bpl_card);
CREATE INDEX idx_citizens_farmer ON citizens(farmer);

COMMENT ON TABLE citizens IS '100K synthetic Rajasthan citizens with realistic demographics';

-- 10. Applications (50K citizen-scheme pairs)
CREATE TABLE IF NOT EXISTS applications (
    app_id BIGSERIAL PRIMARY KEY,
    application_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- References
    citizen_id BIGINT NOT NULL REFERENCES citizens(citizen_id),
    scheme_id INTEGER NOT NULL REFERENCES schemes(scheme_id),
    
    -- Application Details
    application_date DATE NOT NULL,
    application_status VARCHAR(50) NOT NULL DEFAULT 'pending', 
    -- pending, under_review, approved, rejected, disbursed, closed
    
    -- Eligibility Check Results
    eligibility_score DECIMAL(5,2), -- ML model score (0-100)
    eligibility_status VARCHAR(20), -- eligible, not_eligible, conditional
    eligibility_notes TEXT,
    
    -- Processing
    assigned_to_dept INTEGER, -- Department ID
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    approval_date DATE,
    
    -- Financial
    approved_amount DECIMAL(12,2),
    disbursed_amount DECIMAL(12,2),
    disbursement_date DATE,
    
    -- Documents
    documents_verified BOOLEAN DEFAULT false,
    documents_count INTEGER DEFAULT 0,
    
    -- Rejection Details (if rejected)
    rejection_reason TEXT,
    
    -- Status History
    status_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_changed_by VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_citizen ON applications(citizen_id);
CREATE INDEX idx_applications_scheme ON applications(scheme_id);
CREATE INDEX idx_applications_status ON applications(application_status);
CREATE INDEX idx_applications_date ON applications(application_date);
CREATE INDEX idx_applications_eligibility ON applications(eligibility_status, eligibility_score);
CREATE INDEX idx_applications_number ON applications(application_number);

COMMENT ON TABLE applications IS '50K citizen-scheme application pairs with eligibility scoring';

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_schemes_updated_at BEFORE UPDATE ON schemes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_citizens_updated_at BEFORE UPDATE ON citizens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON COLUMN citizens.jan_aadhaar IS 'Jan Aadhaar - Rajasthan specific citizen ID';
COMMENT ON COLUMN citizens.age IS 'Calculated age from date_of_birth';
COMMENT ON COLUMN applications.eligibility_score IS 'ML model eligibility score (0-100)';
COMMENT ON COLUMN applications.eligibility_status IS 'Automated eligibility determination';

