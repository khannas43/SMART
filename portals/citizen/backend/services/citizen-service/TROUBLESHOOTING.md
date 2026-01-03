# Troubleshooting Guide - Citizen Service

## Getting Full Error Details

If you see a BUILD FAILURE, run with verbose output:

```bash
mvn spring-boot:run -e
```

Or with full debug:

```bash
mvn spring-boot:run -X
```

This will show the actual error message.

---

## Common Errors and Solutions

### 1. Database Connection Error

**Error:**
```
Failed to configure a DataSource: 'url' attribute is not specified
```

**Solution:**
- Verify PostgreSQL is running
- Check database credentials in `application.yml`
- Verify database `smart_citizen` exists

**Check:**
```sql
-- In pgAdmin4 or psql
SELECT datname FROM pg_database WHERE datname = 'smart_citizen';
```

---

### 2. Flyway Migration Error - Table Already Exists

**Error:**
```
ERROR: relation "schemes" already exists
```

**Solution:**
Clean the database (see `CLEANUP_PGADMIN.md`):

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO sameer;
GRANT ALL ON SCHEMA public TO public;
```

---

### 3. Permission Denied Error

**Error:**
```
ERROR: permission denied for schema public
```

**Solution:**
Grant permissions in pgAdmin4:

```sql
GRANT ALL ON SCHEMA public TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sameer;
```

---

### 4. Port Already in Use

**Error:**
```
Port 8080 is already in use
```

**Solution:**
- Find and stop the process using port 8080:
  ```powershell
  netstat -ano | findstr :8080
  taskkill /PID <PID> /F
  ```
- Or change port in `application.yml`:
  ```yaml
  server:
    port: 8081
  ```

---

### 5. Flyway Schema History Error

**Error:**
```
FlywayException: Validate failed: Detected resolved migration not applied
```

**Solution:**
If you've modified migration files, you may need to repair:

```sql
-- Drop Flyway history table
DROP TABLE IF EXISTS flyway_schema_history CASCADE;
```

Then restart the application.

---

### 6. Missing Extension Error

**Error:**
```
ERROR: extension "uuid-ossp" does not exist
```

**Solution:**
Create the extension in pgAdmin4:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Verification Steps

### 1. Check Database Connection

```sql
-- In pgAdmin4, connect to smart_citizen and run:
SELECT current_database(), current_user;
```

Should return:
- `current_database`: `smart_citizen`
- `current_user`: `sameer`

### 2. Check Schema Exists

```sql
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name = 'public';
```

Should return one row with `public`.

### 3. Check Tables (After Cleanup)

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should return empty (or only `flyway_schema_history`).

### 4. Check PostgreSQL is Running

**Windows:**
```powershell
Get-Service -Name postgresql*
```

Should show `Running` status.

---

## Quick Diagnostic Commands

### Check Application Configuration

```bash
# Verify application.yml exists
cat src/main/resources/application.yml

# Check database URL format
grep -i "jdbc:postgresql" src/main/resources/application.yml
```

### Test Database Connection

```powershell
# Test connection (Windows)
$env:PGPASSWORD='anjali143'
psql -U sameer -d smart_citizen -c "SELECT version();"
```

---

## Still Having Issues?

1. **Share the full error message** (run with `-e` flag)
2. **Check the logs** - Look for lines starting with `ERROR` or `Exception`
3. **Verify prerequisites:**
   - ✅ Java 17+ installed
   - ✅ Maven installed
   - ✅ PostgreSQL running
   - ✅ Database `smart_citizen` exists
   - ✅ User `sameer` has permissions

---

## Getting Help

When asking for help, please provide:

1. **Full error message** (run `mvn spring-boot:run -e`)
2. **Last 20-30 lines** of console output
3. **Database status** (is PostgreSQL running?)
4. **What you've tried** (cleanup, permissions, etc.)

