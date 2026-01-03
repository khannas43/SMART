-- SIMPLIFIED: Get Top 25 Aadhaar Numbers
-- This version explicitly lists all columns to avoid any issues
-- Run this in pgAdmin Query Tool connected to smart_citizen database

WITH citizen_scores AS (
    SELECT 
        c.aadhaar_number,
        c.mobile_number,
        c.full_name,
        c.email,
        c.city,
        c.district,
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
        (SELECT COUNT(*) FROM documents d WHERE d.citizen_id = c.id) AS doc_count,
        (SELECT COUNT(*) FROM service_applications sa WHERE sa.citizen_id = c.id) AS app_count
    FROM citizens c
    WHERE c.aadhaar_number IS NOT NULL 
      AND c.aadhaar_number != ''
      AND c.mobile_number IS NOT NULL
      AND c.status = 'ACTIVE'
),
ranked AS (
    SELECT 
        aadhaar_number,
        mobile_number,
        full_name,
        email,
        city,
        district,
        profile_score,
        doc_count,
        app_count,
        (profile_score + 
         CASE WHEN doc_count > 0 THEN 2 ELSE 0 END +
         CASE WHEN app_count > 0 THEN 2 ELSE 0 END
        ) AS total_score,
        ROW_NUMBER() OVER (ORDER BY 
            (profile_score + 
             CASE WHEN doc_count > 0 THEN 2 ELSE 0 END +
             CASE WHEN app_count > 0 THEN 2 ELSE 0 END
            ) DESC
        ) AS rank
    FROM citizen_scores
)
SELECT 
    rank,
    aadhaar_number,
    mobile_number,
    full_name,
    COALESCE(email, 'N/A') AS email,
    COALESCE(city, 'N/A') AS city,
    COALESCE(district, 'N/A') AS district,
    profile_score,
    doc_count AS documents,
    app_count AS applications,
    total_score
FROM ranked
WHERE rank <= 25
ORDER BY rank;

