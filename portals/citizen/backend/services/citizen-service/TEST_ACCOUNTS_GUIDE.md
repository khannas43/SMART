# Test Accounts Guide - 25 Aadhaar Numbers with Maximum Data

## Quick Start

1. **Run the PowerShell script** to get the list of Aadhaar numbers:
   ```powershell
   cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
   .\scripts\get_test_aadhaar_numbers.ps1
   ```

2. **OTP for ALL accounts**: `123456`

3. **Login Process**:
   - Enter any Aadhaar number from the list
   - Enter OTP: `123456`
   - Click "Login"

## What Was Implemented

### Backend Changes

1. **New OTP Verification Endpoint**:
   - `POST /citizen/api/v1/auth/verify-otp?janAadhaarId={aadhaar}&otp={otp}`
   - Validates OTP format (6 digits)
   - Accepts hardcoded OTP: `123456` for any Aadhaar number
   - Returns JWT token on successful verification

2. **Hardcoded OTP**: `123456` is accepted for all test accounts

### Frontend Changes

1. **Updated Login Flow**:
   - Now uses OTP verification endpoint
   - Validates OTP before sending to backend
   - Shows appropriate error messages

## Getting the Aadhaar Numbers

### Option 1: PowerShell Script (Recommended)

```powershell
cd C:\Projects\SMART\portals\citizen\backend\services\citizen-service
.\scripts\get_test_aadhaar_numbers.ps1
```

This will display:
- Top 25 Aadhaar numbers ranked by data completeness
- Mobile numbers, names, districts
- Profile scores, document counts, application counts
- Easy-to-copy list of Aadhaar numbers

### Option 2: SQL Query in pgAdmin

1. Connect to `smart_citizen` database in pgAdmin
2. Open Query Tool
3. Execute: `scripts/get_test_aadhaar_numbers.sql`
4. Copy the Aadhaar numbers from the results

### Option 3: Direct SQL

Run this query in pgAdmin:

```sql
WITH citizen_scores AS (
    SELECT 
        c.id,
        c.aadhaar_number,
        c.mobile_number,
        c.full_name,
        c.email,
        c.date_of_birth,
        c.gender,
        c.address_line1,
        c.city,
        c.district,
        c.pincode,
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
        ) AS profile_score,
        (SELECT COUNT(*) FROM documents d WHERE d.citizen_id = c.id) AS document_count,
        (SELECT COUNT(*) FROM service_applications sa WHERE sa.citizen_id = c.id) AS application_count
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
            ) DESC,
            document_count DESC,
            application_count DESC
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
    application_count,
    total_score
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
```

## Testing Checklist

- [ ] Run the script to get Aadhaar numbers
- [ ] Restart backend service (to load new OTP endpoint)
- [ ] Test login with first Aadhaar number + OTP: 123456
- [ ] Verify profile loads correctly
- [ ] Test with different Aadhaar numbers
- [ ] Verify error handling for wrong OTP

## Notes

- **OTP is hardcoded**: `123456` works for ALL test accounts
- **Data completeness**: Accounts are ranked by:
  - Profile completeness (name, email, DOB, address, etc.)
  - Number of documents
  - Number of applications
- **All accounts are ACTIVE**: Only active citizens are included
- **Aadhaar required**: Only citizens with valid Aadhaar numbers are included

## Troubleshooting

### Script doesn't run
- Check PostgreSQL is running
- Verify database connection settings
- Ensure `psql` is in PATH or use full path

### No results
- Verify data migration completed (V11 migration)
- Check if `smart_citizen` database has data
- Verify citizens have Aadhaar numbers

### OTP not working
- Restart backend service
- Check backend logs for errors
- Verify endpoint: `POST /citizen/api/v1/auth/verify-otp`
- Ensure OTP is exactly: `123456`

