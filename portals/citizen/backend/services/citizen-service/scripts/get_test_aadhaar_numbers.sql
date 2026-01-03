-- SQL Script to find citizens with maximum data available
-- This script finds citizens with the most complete profiles for testing
-- Run this in pgAdmin or psql connected to smart_citizen database

-- Find citizens with maximum data completeness
-- Scoring based on:
-- 1. Has Aadhaar number
-- 2. Has mobile number
-- 3. Has email
-- 4. Has full name
-- 5. Has date of birth
-- 6. Has gender
-- 7. Has address information
-- 8. Has documents
-- 9. Has applications

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
    date_of_birth,
    gender,
    district,
    profile_score,
    document_count,
    application_count,
    total_score
FROM ranked_citizens
WHERE rank <= 30  -- Get top 30 to have extra options
ORDER BY rank;

-- Alternative: Get exactly 25 with best data
-- Uncomment below and comment above if you want exactly 25

/*
SELECT 
    aadhaar_number,
    mobile_number,
    full_name,
    email,
    district,
    profile_score,
    document_count,
    application_count
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
*/

