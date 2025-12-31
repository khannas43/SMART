# Rule Management & Version Control

**Use Case ID:** AI-PLATFORM-03  
**Status:** Implementation Guide

---

## 1. Current Rule Storage (Not Hard-Coded)

### ✅ Rules are Database-Driven

**Rules are NOT hard-coded** - they are stored in PostgreSQL database tables:

- **Table**: `eligibility.scheme_eligibility_rules`
- **Table**: `eligibility.scheme_exclusion_rules`
- **Location**: `database/eligibility_schema.sql`

### Current Implementation

```sql
CREATE TABLE eligibility.scheme_eligibility_rules (
    rule_id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50), -- AGE, INCOME, GENDER, etc.
    rule_expression TEXT NOT NULL,
    rule_operator VARCHAR(20),
    rule_value TEXT,
    is_mandatory BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Rule Loading

Rules are loaded dynamically from database:
- **Caching**: Rules cached for 24 hours (configurable)
- **Versioning**: Each rule has a version number
- **Temporal**: Rules have `effective_from` and `effective_to` dates

---

## 2. Frontend Rule Management Interface (To Be Implemented)

### 2.1 UI Components Required

#### 2.1.1 Rule Management Dashboard
- **Screen**: Admin Portal → Scheme Configuration → Rule Management
- **Features**:
  - List all schemes
  - View rules per scheme
  - Add/Edit/Delete rules
  - Enable/Disable rules
  - Rule validation

#### 2.1.2 Rule Editor
- **Screen**: Rule Editor Modal/Dialog
- **Features**:
  - Dropdown: Rule Type (AGE, INCOME, GENDER, etc.)
  - Input: Rule Name
  - Dropdown: Operator (>=, <=, =, IN, NOT_IN, etc.)
  - Input: Rule Value
  - Checkbox: Is Mandatory
  - Input: Priority
  - Date Picker: Effective From/To
  - Rule Expression Preview
  - Validation: Test rule with sample data

#### 2.1.3 Rule Version History
- **Screen**: Rule Version History View
- **Features**:
  - View all versions of a rule
  - Compare versions
  - Rollback to previous version
  - See changes between versions

### 2.2 Backend APIs Needed

```java
// Rule Management APIs
GET    /api/v1/admin/rules/schemes                    // List schemes
GET    /api/v1/admin/rules/scheme/{scheme_id}         // Get rules for scheme
GET    /api/v1/admin/rules/{rule_id}                  // Get specific rule
POST   /api/v1/admin/rules                            // Create new rule
PUT    /api/v1/admin/rules/{rule_id}                  // Update rule
DELETE /api/v1/admin/rules/{rule_id}                  // Delete rule
POST   /api/v1/admin/rules/{rule_id}/clone            // Clone rule
POST   /api/v1/admin/rules/{rule_id}/activate         // Activate rule
POST   /api/v1/admin/rules/{rule_id}/deactivate       // Deactivate rule

// Version Management
GET    /api/v1/admin/rules/{rule_id}/versions         // Get version history
GET    /api/v1/admin/rules/{rule_id}/versions/{version_id}  // Get specific version
POST   /api/v1/admin/rules/{rule_id}/rollback         // Rollback to version

// Rule Testing
POST   /api/v1/admin/rules/test                       // Test rule expression
POST   /api/v1/admin/rules/validate                   // Validate rule syntax
```

---

## 3. Historical Tracking & Version Control (Enhanced)

### 3.1 Current Versioning

✅ **Already Implemented**:
- `version` field in rules table
- `effective_from` and `effective_to` dates
- `rule_change_history` table
- Timestamps for created/updated

### 3.2 Enhanced Versioning Required

#### 3.2.1 Rule Set Snapshots

Store complete rule set snapshots at specific points in time:

```sql
CREATE TABLE eligibility.rule_set_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(50) NOT NULL,
    snapshot_name VARCHAR(200),
    snapshot_date DATE NOT NULL,
    rule_ids INTEGER[], -- Array of rule IDs at this snapshot
    rule_data JSONB,    -- Complete rule data (denormalized)
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

#### 3.2.2 Evaluation Result Versioning

Link evaluation results to rule set versions:

```sql
-- Enhance eligibility_snapshots table
ALTER TABLE eligibility.eligibility_snapshots
ADD COLUMN rule_set_version VARCHAR(50),
ADD COLUMN rule_set_snapshot_id INTEGER REFERENCES eligibility.rule_set_snapshots(snapshot_id),
ADD COLUMN dataset_version VARCHAR(50); -- Track which dataset was used
```

#### 3.2.3 Dataset Versioning

Track which dataset version was used for evaluation:

```sql
CREATE TABLE eligibility.dataset_versions (
    dataset_version_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100), -- 'golden_records', 'profile_360', etc.
    version VARCHAR(50) NOT NULL,
    version_date DATE NOT NULL,
    description TEXT,
    metadata JSONB, -- Counts, schema changes, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dataset_name, version)
);
```

### 3.3 Historical Query Examples

**Query evaluations before rule change:**
```sql
SELECT * FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v1.0'
  AND evaluation_timestamp < '2024-12-01'
  AND dataset_version = 'golden_records_v2.1'
```

**Query evaluations after rule change:**
```sql
SELECT * FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v2.0'
  AND evaluation_timestamp >= '2024-12-01'
  AND dataset_version = 'golden_records_v2.2'
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Enhanced Database Schema

1. ✅ Create `rule_set_snapshots` table
2. ✅ Enhance `eligibility_snapshots` with version columns
3. ✅ Create `dataset_versions` table
4. ✅ Update evaluation service to record versions

### 4.2 Phase 2: Backend APIs

1. ⏳ Create Rule Management Service
2. ⏳ Create Rule Version Service
3. ⏳ Create Rule Testing Service
4. ⏳ Add version tracking to evaluation service

### 4.3 Phase 3: Frontend UI

1. ⏳ Rule Management Dashboard
2. ⏳ Rule Editor Component
3. ⏳ Rule Version History View
4. ⏳ Rule Testing Interface
5. ⏳ Dataset Version Selector

### 4.4 Phase 4: Version Tracking

1. ⏳ Automatic rule set snapshots on rule changes
2. ⏳ Dataset version tracking on evaluation
3. ⏳ Historical query APIs
4. ⏳ Comparison tools (before/after rule changes)

---

## 5. Enhanced Schema for Version Control

See `database/eligibility_schema_versioning.sql` for complete implementation.

---

**Status**: Design complete. Ready for implementation.

