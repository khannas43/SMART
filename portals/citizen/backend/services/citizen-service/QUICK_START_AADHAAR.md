# Quick Start: Get Test Aadhaar Numbers

## Method 1: Using pgAdmin (Easiest - Recommended)

1. **Open pgAdmin4**
2. **Connect to PostgreSQL server** (localhost:5432)
3. **Select `smart_citizen` database**
4. **Right-click on `smart_citizen` → Query Tool**
5. **Open the SQL file**: `GET_AADHAAR_NUMBERS.sql`
6. **Click Execute (F5)**
7. **Copy the Aadhaar numbers from the results**

## Method 2: Enable PowerShell Script Execution

If you want to use the PowerShell script, run this command first:

```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy for current user (allows scripts)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script
.\scripts\get_test_aadhaar_numbers.ps1
```

**Note**: You may need to run PowerShell as Administrator for this.

## Method 3: Bypass Execution Policy (One-time)

Run the script with bypass flag:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\get_test_aadhaar_numbers.ps1"
```

## Quick SQL Query (Copy-Paste)

If you just want to run the query directly in pgAdmin:

```sql
WITH citizen_scores AS (
    SELECT 
        c.id,
        c.aadhaar_number,
        c.mobile_number,
        c.full_name,
        (SELECT COUNT(*) FROM documents d WHERE d.citizen_id = c.id) AS document_count,
        (SELECT COUNT(*) FROM service_applications sa WHERE sa.citizen_id = c.id) AS application_count,
        (
            CASE WHEN c.aadhaar_number IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.mobile_number IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.email IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.full_name IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.date_of_birth IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.gender IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.address_line1 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.city IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.district IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN c.pincode IS NOT NULL THEN 1 ELSE 0 END
        ) AS profile_score
    FROM citizens c
    WHERE c.aadhaar_number IS NOT NULL 
      AND c.aadhaar_number != ''
      AND c.mobile_number IS NOT NULL
      AND c.status = 'ACTIVE'
),
ranked_citizens AS (
    SELECT 
        *,
        (profile_score + 
         CASE WHEN document_count > 0 THEN 2 ELSE 0 END +
         CASE WHEN application_count > 0 THEN 2 ELSE 0 END
        ) AS total_score,
        ROW_NUMBER() OVER (ORDER BY 
            (profile_score + 
             CASE WHEN document_count > 0 THEN 2 ELSE 0 END +
             CASE WHEN application_count > 0 THEN 2 ELSE 0 END
            ) DESC
        ) AS rank
    FROM citizen_scores
)
SELECT 
    rank,
    aadhaar_number,
    mobile_number,
    full_name,
    district,
    profile_score,
    document_count,
    application_count
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
```

## Important Notes

- **OTP for ALL accounts**: `123456`
- **Aadhaar numbers are 12 digits**
- **All accounts are ACTIVE status**
- **Ranked by data completeness** (profile + documents + applications)

## After Getting the List

1. Copy the Aadhaar numbers
2. Use them to login with OTP: `123456`
3. Test all features of the application

