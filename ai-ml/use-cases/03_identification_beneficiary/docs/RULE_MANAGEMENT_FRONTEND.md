# Rule Management Frontend Implementation Guide

**Use Case ID:** AI-PLATFORM-03  
**Component:** Frontend Rule Management Interface

---

## Overview

Frontend interface for administrators to manage eligibility rules through a web UI without needing database access.

## Component: RuleManagement.tsx

**Location**: `portals/admin/frontend/src/components/features/eligibility/RuleManagement.tsx`

### Features

1. **Scheme Selection**
   - Dropdown to select scheme
   - Loads rules for selected scheme

2. **Rule List**
   - Table view of all rules
   - Columns: Name, Type, Expression, Mandatory, Version, Actions
   - Pagination support

3. **Rule Editor Modal**
   - Add new rule
   - Edit existing rule
   - Form fields:
     - Rule Name
     - Rule Type (dropdown)
     - Operator (dropdown)
     - Rule Value
     - Rule Expression
     - Mandatory flag
     - Priority
     - Effective dates

4. **Rule Actions**
   - Edit rule
   - Test rule (with sample data)
   - View version history
   - Delete rule

## API Integration

All operations use REST APIs:
- `GET /api/v1/admin/rules/schemes` - List schemes
- `GET /api/v1/admin/rules/scheme/{scheme_id}` - Get rules
- `POST /api/v1/admin/rules` - Create rule
- `PUT /api/v1/admin/rules/{rule_id}` - Update rule
- `DELETE /api/v1/admin/rules/{rule_id}` - Delete rule
- `POST /api/v1/admin/rules/test` - Test rule

## Additional Components Needed

### 1. Rule Version History Component

**File**: `RuleVersionHistory.tsx`

Displays version history for a rule with:
- Version timeline
- Side-by-side comparison
- Rollback functionality

### 2. Rule Set Snapshot Component

**File**: `RuleSetSnapshot.tsx`

Manages rule set snapshots:
- Create snapshot before rule changes
- View all snapshots
- Compare snapshots
- Restore from snapshot

### 3. Dataset Version Selector

**File**: `DatasetVersionSelector.tsx`

Select dataset versions for evaluation:
- List available dataset versions
- Select version for evaluation
- View dataset metadata

### 4. Evaluation Comparison Component

**File**: `EvaluationComparison.tsx`

Compare evaluations across rule versions:
- Select two rule set versions
- View before/after comparison
- See affected families
- Generate comparison report

## Implementation Status

- ✅ **RuleManagement.tsx** - Created (basic component)
- ⏳ **RuleVersionHistory.tsx** - To be implemented
- ⏳ **RuleSetSnapshot.tsx** - To be implemented
- ⏳ **DatasetVersionSelector.tsx** - To be implemented
- ⏳ **EvaluationComparison.tsx** - To be implemented

---

**Next Steps**: Implement remaining components and integrate with backend APIs.

