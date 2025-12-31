# ✅ Final Solution: Single scheme_master Table

**Use Case ID:** AI-PLATFORM-03  
**Problem**: Duplicate `scheme_master` tables causing maintenance issues  
**Solution**: Use single `public.scheme_master`, extend with eligibility fields, reference via `scheme_code`

---

## ✅ Solution Summary

### Single Source of Truth: `public.scheme_master`

**Location**: `public` schema (shared between AI-PLATFORM-02 and AI-PLATFORM-03)

**Structure**:
```sql
CREATE TABLE scheme_master (
    scheme_id SERIAL PRIMARY KEY,           -- INTEGER (auto-increment)
    scheme_code VARCHAR(50) UNIQUE NOT NULL, -- VARCHAR (unique identifier) ⭐ USE THIS
    scheme_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- Eligibility criteria (from AI-PLATFORM-02)
    min_age INTEGER,
    max_age INTEGER,
    max_income DECIMAL(12,2),
    target_caste VARCHAR(50),
    bpl_required BOOLEAN,
    farmer_required BOOLEAN,
    
    -- NEW: Eligibility-specific fields (added for AI-PLATFORM-03)
    is_auto_id_enabled BOOLEAN DEFAULT true,  -- NEW
    scheme_type VARCHAR(20),                  -- NEW: CASH, NON_CASH
    
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Changes Made

### 1. ✅ Extended `public.scheme_master`

**Migration Script**: `database/migrate_scheme_master.sql`

```sql
-- Add eligibility columns
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20);

-- Update existing schemes
UPDATE scheme_master 
SET is_auto_id_enabled = true,
    scheme_type = CASE 
        WHEN category IN ('SOCIAL_SECURITY', 'LIVELIHOOD') THEN 'CASH'
        WHEN category IN ('HEALTH', 'EDUCATION', 'FOOD') THEN 'NON_CASH'
        ELSE 'CASH'
    END
WHERE is_auto_id_enabled IS NULL;
```

### 2. ✅ Updated Eligibility Schema

**File**: `database/eligibility_schema.sql`

- ❌ **Removed**: `eligibility.scheme_master` table
- ✅ **Updated**: All eligibility tables now use `scheme_code` (VARCHAR) instead of `scheme_id` (VARCHAR)
- ✅ **Foreign Keys**: All reference `scheme_master(scheme_code)`

**Tables Updated**:
- `eligibility.scheme_eligibility_rules` → uses `scheme_code`
- `eligibility.eligibility_snapshots` → uses `scheme_code`
- `eligibility.candidate_lists` → uses `scheme_code`
- `eligibility.ml_model_registry` → uses `scheme_code`

### 3. ⚠️ Python Code Updates Required

**Files to Update** (use `scheme_code` instead of `scheme_id`):

1. **`src/evaluator_service.py`**
   - `_get_active_schemes()` - Query `scheme_master` for `scheme_code`
   - `_get_schemes_for_event()` - Use `scheme_code`
   - All queries that use `scheme_id` → change to `scheme_code`

2. **`src/rule_engine.py`**
   - `load_scheme_rules()` - Query by `scheme_code` instead of `scheme_id`

3. **`src/ml_scorer.py`**
   - Model registry queries - Use `scheme_code`

4. **`src/prioritizer.py`**
   - Candidate list queries - Use `scheme_code`

5. **`src/train_eligibility_model.py`**
   - Training data queries - Use `scheme_code`

---

## Migration Steps

### Step 1: Extend Existing Table

```sql
-- Run in pgAdmin4 (connected to smart_warehouse)
-- File: database/migrate_scheme_master.sql
```

### Step 2: Update Eligibility Schema

```sql
-- Run updated eligibility_schema.sql
-- This removes eligibility.scheme_master and updates all tables
```

### Step 3: Update Python Code

**Change all `scheme_id` references to `scheme_code`** in:
- Queries to `eligibility.scheme_master` → change to `scheme_master` (public schema)
- Queries that use `scheme_id` → change to `scheme_code`
- Function parameters that accept `scheme_id` → change to `scheme_code`

---

## Key Differences

| Aspect | Before | After |
|--------|--------|-------|
| **scheme_master location** | `eligibility.scheme_master` | `public.scheme_master` |
| **scheme_master PK** | `scheme_id VARCHAR(50)` | `scheme_id SERIAL` (INTEGER) |
| **Link field** | `scheme_id VARCHAR(50)` | `scheme_code VARCHAR(50)` ⭐ |
| **Foreign keys** | `REFERENCES eligibility.scheme_master(scheme_id)` | `REFERENCES scheme_master(scheme_code)` |
| **Python queries** | `WHERE scheme_id = %s` | `WHERE scheme_code = %s` |

---

## Benefits

1. ✅ **Single Source of Truth**: One table to maintain
2. ✅ **No Duplication**: Data stored once
3. ✅ **Easy Updates**: Update once, affects both use cases
4. ✅ **Consistent Data**: No synchronization issues
5. ✅ **Proper Foreign Keys**: Referential integrity maintained
6. ✅ **Uses Existing Data**: Leverages `scheme_code` that already exists

---

## Verification

```sql
-- Check scheme_master has new columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'scheme_master'
AND column_name IN ('is_auto_id_enabled', 'scheme_type');

-- Check eligibility tables use scheme_code
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'eligibility' 
AND column_name = 'scheme_code'
ORDER BY table_name;

-- Verify no duplicate scheme_master
SELECT schema_name, table_name
FROM information_schema.tables
WHERE table_name = 'scheme_master';
-- Should only show: public.scheme_master

-- Check foreign keys
SELECT 
    tc.table_schema, 
    tc.table_name, 
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND ccu.table_name = 'scheme_master'
    AND tc.table_schema = 'eligibility';
```

---

## Next Steps

1. ✅ **Schema Updated** - `eligibility_schema.sql` updated
2. ✅ **Migration Script Created** - `migrate_scheme_master.sql`
3. ⚠️ **Python Code Updates** - Need to update all Python files to use `scheme_code`
4. ⚠️ **Testing** - Test with updated code

---

**Status**: ✅ Schema consolidation complete. ⚠️ Python code updates pending.

