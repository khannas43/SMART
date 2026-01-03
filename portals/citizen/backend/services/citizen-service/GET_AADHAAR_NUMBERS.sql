-- Get Top 25 Aadhaar Numbers with Maximum Data
-- Run this query in pgAdmin (Query Tool) connected to smart_citizen database
-- Copy the aadhaar_number column from the results

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
        id,
        aadhaar_number,
        mobile_number,
        full_name,
        email,
        date_of_birth,
        gender,
        address_line1,
        city,
        district,
        pincode,
        profile_score,
        document_count,
        application_count,
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
    aadhaar_number AS "Aadhaar Number",
    mobile_number AS "Mobile Number",
    full_name AS "Full Name",
    COALESCE(email, 'N/A') AS "Email",
    COALESCE(district, 'N/A') AS "District",
    profile_score AS "Profile Score",
    document_count AS "Documents",
    application_count AS "Applications",
    total_score AS "Total Score"
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;

-- ============================================
-- SIMPLIFIED VERSION - Just Aadhaar Numbers
-- ============================================
-- Uncomment below to get just the Aadhaar numbers in a simple list:

/*
SELECT 
    aadhaar_number
FROM ranked_citizens
WHERE rank <= 25
ORDER BY rank;
*/

