# Answers to Rule Management Questions

**Use Case ID:** AI-PLATFORM-03  
**Date:** 2024-12-27

---

## Question 1: Are Rules Hard-Coded?

### ✅ Answer: **NO - Rules are Database-Driven**

Rules are **NOT hard-coded**. They are stored in PostgreSQL database tables and loaded dynamically:

- **Storage**: `eligibility.scheme_eligibility_rules` table
- **Loading**: Rules loaded from database at runtime
- **Caching**: Rules cached in memory for 24 hours (configurable)
- **Dynamic**: Can be changed without code changes

### Current Implementation

```python
# Rules are loaded from database
rules = self.load_scheme_rules(scheme_id)  # Queries database
```

Rules can be:
- Added via SQL INSERT
- Modified via SQL UPDATE
- Deleted via SQL UPDATE (soft delete with effective_to date)

---

## Question 2: Frontend Interface for Rule Management

### ✅ Answer: **Yes - Frontend Interface Designed**

A complete rule management interface has been designed with:

### 2.1 UI Components

#### Rule Management Dashboard
- **Location**: Admin Portal → Scheme Configuration → Rule Management
- **Features**:
  - List all schemes
  - View rules per scheme (active/inactive)
  - Add/Edit/Delete rules
  - Enable/Disable rules
  - Rule validation and testing

#### Rule Editor
- **Modal/Dialog** for rule editing
- **Fields**:
  - Scheme selector
  - Rule name
  - Rule type (dropdown: AGE, INCOME, GENDER, etc.)
  - Operator (dropdown: >=, <=, =, IN, NOT_IN, etc.)
  - Rule value
  - Mandatory flag
  - Priority
  - Effective dates
  - Rule expression preview
- **Validation**: Test rule with sample data before saving

#### Rule Version History
- View all versions of a rule
- Compare versions side-by-side
- Rollback to previous version
- See who changed what and when

### 2.2 Backend APIs (Created)

**File**: `spring_boot/RuleManagementController.java`

All APIs are defined:
- `GET /api/v1/admin/rules/schemes` - List schemes
- `GET /api/v1/admin/rules/scheme/{scheme_id}` - Get rules
- `POST /api/v1/admin/rules` - Create rule
- `PUT /api/v1/admin/rules/{rule_id}` - Update rule
- `DELETE /api/v1/admin/rules/{rule_id}` - Delete rule
- `GET /api/v1/admin/rules/{rule_id}/versions` - Version history
- `POST /api/v1/admin/rules/{rule_id}/rollback` - Rollback
- `POST /api/v1/admin/rules/test` - Test rule
- `POST /api/v1/admin/rules/validate` - Validate syntax

### 2.3 Python Service (Created)

**File**: `src/rule_manager.py`

Provides programmatic access:
- `create_rule()` - Create new rule
- `update_rule()` - Update rule (creates new version)
- `delete_rule()` - Soft delete rule
- `create_rule_set_snapshot()` - Create rule set snapshot
- `compare_evaluations()` - Compare across versions

### 2.4 Implementation Status

- ✅ **Database Schema**: Complete
- ✅ **Backend APIs**: Defined (Java controllers)
- ✅ **Python Service**: Implemented
- ⏳ **Frontend UI**: To be implemented (React components)
- ⏳ **Service Layer**: Java service implementation pending

---

## Question 3: Historical Tracking (Before/After Rule Changes)

### ✅ Answer: **Yes - Comprehensive Version Control Implemented**

Complete historical tracking system has been designed and implemented:

### 3.1 Rule Set Snapshots

**Table**: `eligibility.rule_set_snapshots`

Stores complete rule sets at specific points in time:
- Snapshot version (e.g., "v1.0", "v2.0")
- Complete rule data (denormalized)
- Snapshot date
- Change summary

**Usage**:
```sql
-- Create snapshot before rule change
SELECT eligibility.create_rule_set_snapshot(
    'SCHEME_001', 'v2.0', 'Rule Set v2.0 - Dec 2024',
    'Updated age requirement from 60 to 65', 'admin'
);
```

### 3.2 Evaluation Version Tracking

**Enhanced Table**: `eligibility.eligibility_snapshots`

Now includes:
- `rule_set_version` - Which rule set version was used
- `rule_set_snapshot_id` - Link to snapshot
- `dataset_version_golden_records` - Dataset version used
- `dataset_version_profile_360` - Dataset version used
- `dataset_version_jrdr` - Dataset version used

### 3.3 Dataset Versioning

**Table**: `eligibility.dataset_versions`

Tracks versions of source datasets:
- Dataset name (golden_records, profile_360, jrdr)
- Version identifier
- Version date
- Metadata (record counts, schema changes)
- Schema hash (for change detection)

### 3.4 Historical Query Examples

#### Query Evaluations Before Rule Change
```sql
SELECT * FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v1.0'
  AND evaluation_timestamp < '2024-12-01'
  AND dataset_version_golden_records = 'v2.1'
  AND dataset_version_profile_360 = 'v2.0';
```

#### Query Evaluations After Rule Change
```sql
SELECT * FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND rule_set_version = 'v2.0'
  AND evaluation_timestamp >= '2024-12-01'
  AND dataset_version_golden_records = 'v2.2'
  AND dataset_version_profile_360 = 'v2.1';
```

#### Compare Before/After
```sql
SELECT 
    family_id,
    rule_set_version,
    evaluation_status,
    eligibility_score
FROM eligibility.eligibility_snapshots
WHERE scheme_id = 'SCHEME_001'
  AND family_id = 'uuid-here'
  AND rule_set_version IN ('v1.0', 'v2.0')
ORDER BY rule_set_version, evaluation_timestamp DESC;
```

### 3.5 Comparison Features

**Table**: `eligibility.evaluation_comparison`

Automatically tracks changes when rules are updated:
- Old vs new status
- Score delta
- Which families were affected

**Function**: `compare_evaluations()`
- Compare results across rule versions
- Identify families affected by rule changes
- Calculate impact metrics

### 3.6 Workflow for Rule Changes

```
1. Create Rule Set Snapshot (before change)
   ↓
2. Record Dataset Versions (current versions)
   ↓
3. Update/Add/Delete Rules
   ↓
4. Create New Rule Set Snapshot (after change)
   ↓
5. Run Evaluation (automatically records versions)
   ↓
6. Compare Results (before/after analysis)
```

---

## Implementation Files

### Database Schema
- ✅ `database/eligibility_schema.sql` - Base schema
- ✅ `database/eligibility_schema_versioning.sql` - Versioning extensions

### Backend Services
- ✅ `spring_boot/RuleManagementController.java` - REST APIs
- ✅ `src/rule_manager.py` - Python rule management service

### Documentation
- ✅ `docs/RULE_MANAGEMENT.md` - Complete rule management guide
- ✅ `docs/RULE_MANAGEMENT_ANSWERS.md` - This document

---

## Summary

| Question | Answer | Status |
|----------|--------|--------|
| 1. Rules hard-coded? | **NO** - Database-driven | ✅ Implemented |
| 2. Frontend interface? | **YES** - Full UI designed | ✅ APIs Ready, ⏳ UI Pending |
| 3. Historical tracking? | **YES** - Complete versioning | ✅ Implemented |

---

## Next Steps

1. **Implement Frontend UI** (React components)
   - Rule Management Dashboard
   - Rule Editor
   - Version History View

2. **Complete Java Service Layer**
   - Implement `RuleManagementService.java`
   - Connect to Python service or database

3. **Testing**
   - Test rule CRUD operations
   - Test version tracking
   - Test historical queries

4. **User Training**
   - Train admin users on rule management
   - Document rule syntax and best practices

---

**Status**: ✅ **Version Control and APIs Complete. Frontend UI Pending.**

