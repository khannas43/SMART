# Solution: Single scheme_master Table

**Use Case ID:** AI-PLATFORM-03  
**Problem**: Duplicate `scheme_master` tables causing maintenance issues  
**Solution**: Use single `public.scheme_master`, extend with eligibility fields

---

## ✅ Final Solution

### Single Source of Truth: `public.scheme_master`

**Location**: `public` schema (shared between AI-PLATFORM-02 and AI-PLATFORM-03)

**Structure**:
```sql
CREATE TABLE scheme_master (
    scheme_id SERIAL PRIMARY KEY,           -- INTEGER (from AI-PLATFORM-02)
    scheme_code VARCHAR(50) UNIQUE NOT NULL, -- VARCHAR (unique identifier)
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

### 1. Extended `public.scheme_master`

Added columns:
- `is_auto_id_enabled` BOOLEAN - Whether scheme participates in auto-identification
- `scheme_type` VARCHAR(20) - CASH or NON_CASH

### 2. Updated Eligibility Tables

Changed from `scheme_id VARCHAR(50)` to `scheme_code VARCHAR(50)`:
- `eligibility.scheme_eligibility_rules` → uses `scheme_code`
- `eligibility.eligibility_snapshots` → uses `scheme_code`
- `eligibility.candidate_lists` → uses `scheme_code`
- `eligibility.ml_model_registry` → uses `scheme_code`

**Foreign Keys**: All reference `scheme_master(scheme_code)`

### 3. Removed Duplicate Table

- ❌ Removed: `eligibility.scheme_master`
- ✅ Using: `public.scheme_master` (extended)

---

## Migration Steps

### Step 1: Extend Existing Table

```sql
-- Add eligibility columns to public.scheme_master
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

### Step 2: Update Eligibility Schema

Run updated `eligibility_schema.sql` which:
- Removes `eligibility.scheme_master` table
- Updates all tables to use `scheme_code` instead of `scheme_id`
- Adds foreign keys to `public.scheme_master`

### Step 3: Update Python Code

Update queries to use `scheme_code`:
- `rule_engine.py` - Use `scheme_code` for lookups
- `evaluator_service.py` - Use `scheme_code` in queries
- `ml_scorer.py` - Use `scheme_code` for model registry
- `prioritizer.py` - Use `scheme_code` for candidate lists

---

## Benefits

1. ✅ **Single Source of Truth**: One table to maintain
2. ✅ **No Duplication**: Data stored once
3. ✅ **Easy Updates**: Update once, affects both use cases
4. ✅ **Consistent Data**: No synchronization issues
5. ✅ **Foreign Keys**: Proper referential integrity

---

## Usage

### Query Schemes

```sql
-- Get all schemes with auto-identification enabled
SELECT scheme_code, scheme_name, category, scheme_type
FROM scheme_master
WHERE is_auto_id_enabled = true
ORDER BY scheme_code;
```

### Add New Scheme

```sql
-- Add to public.scheme_master (affects both use cases)
INSERT INTO scheme_master (
    scheme_code, scheme_name, category, 
    is_auto_id_enabled, scheme_type, status
) VALUES (
    'NEW_SCHEME', 'New Scheme', 'CATEGORY',
    true, 'CASH', 'active'
);
```

### Update Scheme

```sql
-- Update once, affects both use cases
UPDATE scheme_master
SET is_auto_id_enabled = false
WHERE scheme_code = 'OLD_SCHEME';
```

---

## Code Updates Required

### Python Files to Update

1. **`src/rule_engine.py`**
   - Change queries from `scheme_id` to `scheme_code`
   - Update `load_scheme_rules()` method

2. **`src/evaluator_service.py`**
   - Change `scheme_id` to `scheme_code` in queries
   - Update `_get_active_schemes()` method

3. **`src/ml_scorer.py`**
   - Update model registry queries to use `scheme_code`

4. **`src/prioritizer.py`**
   - Update candidate list queries to use `scheme_code`

5. **`src/train_eligibility_model.py`**
   - Update training data queries to use `scheme_code`

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
```

---

**Status**: ✅ Schema updated. Python code updates pending.

