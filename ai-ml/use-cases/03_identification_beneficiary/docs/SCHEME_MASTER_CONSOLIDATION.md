# Scheme Master Table Consolidation

**Use Case ID:** AI-PLATFORM-03  
**Issue**: Duplicate `scheme_master` tables in different schemas  
**Solution**: Use single `scheme_master` in `public` schema, reference via `scheme_code`

---

## Problem

Currently, there are two `scheme_master` tables:

1. **`public.scheme_master`** (AI-PLATFORM-02)
   - `scheme_id` SERIAL (INTEGER)
   - `scheme_code` VARCHAR(50) UNIQUE
   - Summary eligibility criteria fields
   - Used by 360° Profiles

2. **`eligibility.scheme_master`** (AI-PLATFORM-03)
   - `scheme_id` VARCHAR(50) PRIMARY KEY
   - `is_auto_id_enabled` BOOLEAN
   - Used by Auto Identification

**Issues:**
- ❌ Data duplication
- ❌ Synchronization problems
- ❌ Update conflicts
- ❌ Maintenance overhead

---

## Solution: Single Source of Truth

**Use `public.scheme_master` as the single source** and extend it for eligibility needs.

### Option 1: Extend Existing Table (Recommended)

Add eligibility-specific columns to `public.scheme_master`:

```sql
-- Add eligibility columns to existing scheme_master
ALTER TABLE scheme_master 
ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20); -- CASH, NON_CASH
```

### Option 2: Use scheme_code as Link

Reference `public.scheme_master` via `scheme_code` in eligibility tables:

```sql
-- Eligibility tables reference via scheme_code
scheme_eligibility_rules.scheme_code → scheme_master.scheme_code
eligibility_snapshots.scheme_code → scheme_master.scheme_code
```

---

## Recommended Approach

**Extend `public.scheme_master`** and remove `eligibility.scheme_master`:

1. **Add columns to `public.scheme_master`**:
   ```sql
   ALTER TABLE scheme_master 
   ADD COLUMN IF NOT EXISTS is_auto_id_enabled BOOLEAN DEFAULT true,
   ADD COLUMN IF NOT EXISTS scheme_type VARCHAR(20);
   ```

2. **Update eligibility tables** to use `scheme_code` (VARCHAR) instead of `scheme_id` (INTEGER)

3. **Remove `eligibility.scheme_master`** table

4. **Update Python code** to use `scheme_code` for lookups

---

## Migration Script

See: `database/migrate_scheme_master.sql`

---

**Status**: Design complete. Ready for implementation.

