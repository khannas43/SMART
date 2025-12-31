# Database Consolidation: smart_warehouse

**Use Case ID:** AI-PLATFORM-03  
**Status**: ✅ Consolidated with AI-PLATFORM-02

---

## Architecture Decision

**All AI/ML use cases use the same `smart_warehouse` database** with different schemas for organization:

- **Database**: `smart_warehouse`
- **Schema**: `smart_warehouse` - 360° Profiles tables (AI-PLATFORM-02)
- **Schema**: `eligibility` - Eligibility tables (AI-PLATFORM-03)

---

## Benefits

1. **Simplified Management**: Single database to backup, monitor, manage
2. **Shared Connections**: Reuse database connections
3. **Data Co-location**: Related data in one place
4. **Easier Queries**: Can join across schemas when needed
5. **Consistent Configuration**: Single database configuration

---

## Database Structure

```
smart_warehouse (database)
├── smart_warehouse (schema)
│   ├── golden_records
│   ├── gr_relationships
│   ├── profile_360
│   ├── benefit_events
│   ├── application_events
│   └── ... (AI-PLATFORM-02 tables)
│
└── eligibility (schema)
    ├── scheme_master
    ├── scheme_eligibility_rules
    ├── eligibility_snapshots
    ├── candidate_lists
    ├── ml_model_registry
    └── ... (AI-PLATFORM-03 tables)
```

---

## Configuration

### db_config.yaml

```yaml
database:
  host: 172.17.16.1
  port: 5432
  name: smart_warehouse  # Consolidated database
  user: sameer
  password: anjali143
  schema: eligibility  # Schema within smart_warehouse
```

---

## Setup

### Create Schema (not database!)

```bash
# Connect to smart_warehouse (not create new database)
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f database/eligibility_schema.sql
```

### Verify

```sql
-- Check schemas in smart_warehouse
SELECT schema_name 
FROM information_schema.schemata 
WHERE catalog_name = 'smart_warehouse'
ORDER BY schema_name;

-- Should show:
-- - smart_warehouse (for AI-PLATFORM-02)
-- - eligibility (for AI-PLATFORM-03)
```

---

## Cross-Schema Queries (If Needed)

Since both schemas are in the same database, you can query across them:

```sql
-- Join eligibility with 360° profiles
SELECT 
    e.family_id,
    e.evaluation_status,
    p.income_band,
    p.vulnerability_level
FROM eligibility.eligibility_snapshots e
JOIN smart_warehouse.profile_360 p ON e.family_id = p.family_id
WHERE e.scheme_id = 'SCHEME_001';
```

---

## Migration Notes

If you already created `smart_eligibility` database:

1. **Option A**: Migrate data to `smart_warehouse`
2. **Option B**: Drop `smart_eligibility` and recreate in `smart_warehouse`
3. **Option C**: Keep existing, update config to point to `smart_warehouse` for new setup

---

**Status**: ✅ All configuration updated to use `smart_warehouse` database with `eligibility` schema.

