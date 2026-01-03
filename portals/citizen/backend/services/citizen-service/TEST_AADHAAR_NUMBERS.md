# Test Aadhaar Numbers with Maximum Data

## Instructions

1. **Run the SQL script** to get Aadhaar numbers with maximum data:
   ```sql
   -- Connect to smart_citizen database in pgAdmin
   -- Execute: scripts/get_test_aadhaar_numbers.sql
   ```

2. **OTP for all test accounts**: `123456`

3. **Login Process**:
   - Enter any Aadhaar number from the list below
   - Enter OTP: `123456`
   - Click "Login"

## How to Get the List

Execute this SQL query in pgAdmin (connected to `smart_citizen` database):

```sql
-- Find top 25 citizens with maximum data
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
        -- Calculate completeness score
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
        -- Count related data
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
        -- Total score = profile score + bonus for documents and applications
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
    email,
    district,
    profile_score,
    document_count,
    application_count,
    total_score
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
```

## Expected Output Format

After running the query, you'll get a list like:

| Rank | Aadhaar Number | Mobile Number | Full Name | District | Profile Score | Documents | Applications |
|------|----------------|---------------|-----------|----------|---------------|-----------|--------------|
| 1 | 123456789012 | 9876543210 | John Doe | Jaipur | 10 | 5 | 3 |
| 2 | 234567890123 | 9876543211 | Jane Smith | Udaipur | 10 | 4 | 2 |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Notes

- All these Aadhaar numbers will accept OTP: `123456`
- The OTP validation is hardcoded in the backend for testing
- These accounts have the most complete data in the system
- Use these for comprehensive testing of all features

