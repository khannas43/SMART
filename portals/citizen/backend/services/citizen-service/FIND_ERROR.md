# How to Find the Actual Error

## Problem

You're seeing a Maven stack trace, but the **actual Spring Boot error** appears earlier in the console output.

## Solution: Scroll Up in Your Terminal

The error sequence usually looks like this:

```
1. Spring Boot starts
   "Starting CitizenServiceApplication..."
   
2. Connection attempts
   "HikariPool-1 - Starting..."
   
3. Flyway runs
   "Flyway Community Edition..."
   
4. ⚠️ ACTUAL ERROR HERE ⚠️
   "ERROR: ..." or "Exception: ..."
   
5. Application fails
   "Application run failed"
   
6. Maven stack trace (what you're seeing)
   "Caused by: org.apache.maven.plugin..."
```

## What to Look For

Scroll up in your terminal and look for these patterns:

### Common Error Patterns:

1. **Database/Flyway Errors:**
   ```
   ERROR: relation "schemes" already exists
   ERROR: extension "uuid-ossp" does not exist
   Migration V2__create_schemes_table.sql failed
   ```

2. **Connection Errors:**
   ```
   Connection to localhost:5432 refused
   FATAL: password authentication failed
   Failed to configure a DataSource
   ```

3. **Permission Errors:**
   ```
   ERROR: permission denied for schema public
   ERROR: must be owner of table
   ```

4. **Port Errors:**
   ```
   Port 8080 is already in use
   Address already in use
   ```

## Quick Command to Find Errors

### PowerShell:
```powershell
mvn spring-boot:run 2>&1 | Select-String -Pattern 'ERROR|Exception|Failed' -Context 3,10
```

### Or capture full output to file:
```powershell
mvn spring-boot:run > startup.log 2>&1
# Then check startup.log for errors
Get-Content startup.log | Select-String -Pattern 'ERROR|Exception'
```

## What to Share

When you find the actual error, share:
1. **The error line** (starts with ERROR or Exception)
2. **The 5-10 lines BEFORE it** (context)
3. **The 5-10 lines AFTER it** (if any additional details)

Example of what we need:
```
ERROR: relation "schemes" already exists
Location: db/migration/V2__create_schemes_table.sql
Statement: CREATE TABLE schemes (
```

This tells us exactly what's wrong!

