# Database Cleanup Using pgAdmin4

## Step-by-Step Instructions

### 1. Open pgAdmin4

Launch pgAdmin4 from your Windows start menu.

### 2. Connect to PostgreSQL Server

- Expand your PostgreSQL server (usually "PostgreSQL 16" or similar)
- Enter your password if prompted (password: `anjali143`)

### 3. Navigate to smart_citizen Database

- Expand **Databases**
- Right-click on **smart_citizen**
- Select **Query Tool** from the context menu

### 4. Execute Cleanup SQL

In the Query Tool window, paste and execute this SQL:

```sql
-- Drop all tables and objects in public schema
DROP SCHEMA public CASCADE;

-- Recreate the public schema
CREATE SCHEMA public;

-- Grant necessary permissions
GRANT ALL ON SCHEMA public TO sameer;
GRANT ALL ON SCHEMA public TO public;
```

### 5. Execute the Query

- Click the **Execute** button (▶️) or press `F5`
- You should see "Query returned successfully" in the Messages tab

### 6. Verify Cleanup

To verify everything was cleaned, run:

```sql
-- List all tables (should return empty or only flyway_schema_history)
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see no tables (or only `flyway_schema_history` if it exists).

### 7. Close pgAdmin4 (Optional)

You can close pgAdmin4 now. The cleanup is complete.

### 8. Run Spring Boot Application

Go back to your terminal/command prompt and run:

```bash
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
mvn spring-boot:run
```

Flyway will now create all tables from migrations automatically!

---

## What This Does

- **DROP SCHEMA public CASCADE**: Removes all tables, sequences, functions, and other objects in the public schema
- **CREATE SCHEMA public**: Recreates the empty public schema
- **GRANT statements**: Ensures the `sameer` user has full permissions on the schema

## Important Notes

⚠️ **This will delete ALL data** in the `smart_citizen` database. Since you're in development and just starting, this is fine. In production, you would use Flyway's repair/baseline commands instead.

