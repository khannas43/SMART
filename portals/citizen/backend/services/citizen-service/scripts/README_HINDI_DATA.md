# Hindi Data Population Guide

## Quick Start

To test Hindi localization, you need to populate Hindi data in the database. Here are the easiest ways:

### Option 1: Run SQL Script in pgAdmin (Recommended)

1. Open **pgAdmin**
2. Connect to your database (`smart`)
3. Open **Query Tool** (Right-click database → Query Tool)
4. Open the file: `scripts/QUICK_TEST_HINDI.sql`
5. Execute the script (F5 or click Execute)
6. Refresh your frontend and switch to Hindi language

### Option 2: Use PowerShell Script

```powershell
cd portals/citizen/backend/services/citizen-service/scripts
.\populate_hindi_data.ps1
```

**Note:** This requires `psql` to be in your PATH. If not, use Option 1.

### Option 3: Manual SQL Updates

Run these SQL commands in pgAdmin:

```sql
-- Update one citizen
UPDATE citizens 
SET full_name_hindi = 'रानी ठाकुर'
WHERE id = (SELECT id FROM citizens LIMIT 1);

-- Update one scheme
UPDATE schemes 
SET 
    name_hindi = 'राजस्थान सरकार योजना',
    description_hindi = 'यह योजना राजस्थान के नागरिकों के लिए है।'
WHERE id = (SELECT id FROM schemes LIMIT 1);
```

## Verify Hindi Data

Run this query to check if Hindi data exists:

```sql
-- Check citizens with Hindi names
SELECT 
    aadhaar_number,
    full_name,
    full_name_hindi
FROM citizens
WHERE full_name_hindi IS NOT NULL
LIMIT 5;

-- Check schemes with Hindi names
SELECT 
    code,
    name,
    name_hindi
FROM schemes
WHERE name_hindi IS NOT NULL
LIMIT 5;
```

## Testing

1. **Backend**: Make sure backend is running and migrations (V14, V15) have been applied
2. **Frontend**: Refresh your browser
3. **Language**: Switch to Hindi (हिंदी) using the language switcher
4. **Check**:
   - Dashboard: User name should show in Hindi (if you updated that user)
   - Schemes page: Scheme names should show in Hindi (if you updated those schemes)
   - Scheme details: Descriptions should show in Hindi

## Troubleshooting

### Issue: Still showing English

**Possible causes:**
1. **No Hindi data**: The Hindi fields are NULL/empty. Run the SQL script to populate data.
2. **Wrong user**: You're logged in as a user that doesn't have a Hindi name. Update that specific user.
3. **Wrong scheme**: The schemes you're viewing don't have Hindi names. Update those specific schemes.
4. **Cache**: Hard refresh the browser (Ctrl+Shift+R or Cmd+Shift+R).

### Issue: Migrations not applied

Check if the columns exist:

```sql
-- Check citizens table
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'citizens' 
  AND column_name LIKE '%hindi%';

-- Check schemes table
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'schemes' 
  AND column_name LIKE '%hindi%';
```

If columns don't exist, restart the backend to apply migrations.

## Bulk Population

For production, you'll want to populate Hindi data for all records. See:
- `populate_hindi_names.sql` - Template for citizen names
- `populate_hindi_schemes.sql` - Template for scheme names/descriptions

These templates show different methods (manual mapping, bulk updates, etc.).

