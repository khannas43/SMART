# Fix Database Schema Issues

## Issue 1: application_events table syntax error

The `application_events` table creation failed due to a trailing comma syntax error.

### Fix

Run this SQL script to fix the table:

```bash
psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/fix_schema.sql
```

Or execute directly in PgAdmin:

```sql
-- Drop and recreate application_events table
DROP TABLE IF EXISTS application.application_events CASCADE;

CREATE TABLE application.application_events (
    event_id BIGSERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES application.applications(application_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    event_status VARCHAR(50) DEFAULT 'pending',
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    consumed_by TEXT[]
);

CREATE INDEX idx_app_events_type ON application.application_events(event_type);
CREATE INDEX idx_app_events_application ON application.application_events(application_id);
CREATE INDEX idx_app_events_timestamp ON application.application_events(event_timestamp);
CREATE INDEX idx_app_events_status ON application.application_events(event_status) WHERE event_status = 'pending';

COMMENT ON TABLE application.application_events IS 'Event log for downstream integration';
```

## Issue 2: Scripts using wrong column name

The initialization scripts were looking for `is_active` column in `scheme_master`, but it uses `status` instead.

### Fix

The scripts have been updated to use `status = 'active'` instead of `is_active = true`. Simply re-run the initialization scripts:

```bash
python scripts/init_scheme_form_schemas.py
python scripts/init_submission_modes_config.py
```

## Complete Fix Steps

1. **Fix application_events table:**
   ```bash
   psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f scripts/fix_schema.sql
   ```

2. **Re-run initialization scripts:**
   ```bash
   python scripts/init_scheme_form_schemas.py
   python scripts/init_submission_modes_config.py
   ```

3. **Verify:**
   ```bash
   python scripts/check_config.py
   ```

---

All fixes have been applied. The schema should now be complete and initialization scripts should work correctly.

