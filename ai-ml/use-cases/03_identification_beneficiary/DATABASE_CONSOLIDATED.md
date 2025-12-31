# ✅ Database Consolidated: Using smart_warehouse

**Use Case ID:** AI-PLATFORM-03  
**Status**: ✅ All configurations updated

---

## Architecture Decision

**All AI/ML use cases now use the same `smart_warehouse` database** with different schemas:

```
smart_warehouse (database)
├── public schema (or smart_warehouse schema)
│   ├── golden_records
│   ├── gr_relationships
│   ├── profile_360
│   ├── benefit_events
│   ├── application_events
│   └── ... (AI-PLATFORM-02 tables)
│
└── eligibility schema
    ├── scheme_master
    ├── scheme_eligibility_rules
    ├── eligibility_snapshots
    ├── candidate_lists
    ├── ml_model_registry
    └── ... (AI-PLATFORM-03 tables)
```

---

## What Changed

### ✅ Updated Files

1. **`config/db_config.yaml`** - Changed database name to `smart_warehouse`
2. **`database/eligibility_schema.sql`** - Updated comments
3. **`scripts/setup_database.sh`** - Updated to use `smart_warehouse`
4. **Documentation** - All references updated

### ✅ Benefits

- ✅ Single database to manage
- ✅ Shared connections
- ✅ Data co-location
- ✅ Easier cross-schema queries
- ✅ Consistent configuration

---

## Setup Instructions

### In pgAdmin4:

1. **Connect to `smart_warehouse` database** (should already exist from AI-PLATFORM-02)

2. **Create eligibility schema**:
   ```sql
   -- Run the schema file
   -- File: database/eligibility_schema.sql
   ```

3. **Load initial schemes**:
   ```sql
   -- Run: scripts/load_initial_schemes.sql
   ```

### Verify:

```sql
-- Check schemas in smart_warehouse
SELECT schema_name 
FROM information_schema.schemata 
WHERE catalog_name = 'smart_warehouse'
ORDER BY schema_name;

-- Should show both schemas:
-- - public (or smart_warehouse) - for AI-PLATFORM-02
-- - eligibility - for AI-PLATFORM-03
```

---

## Configuration

**`config/db_config.yaml`**:
```yaml
database:
  name: smart_warehouse  # Consolidated database
  schema: eligibility     # Schema within smart_warehouse
```

---

**Status**: ✅ All configurations updated to use `smart_warehouse` database.

