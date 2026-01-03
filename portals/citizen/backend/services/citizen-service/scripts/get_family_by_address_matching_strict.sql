-- STRICT Query: Get family members with same filtering logic as backend (max 8 members)
-- This matches the backend's stricter filtering to show realistic family relationships
-- Replace '387193279353' with your seed Aadhaar number

WITH seed_citizen AS (
    SELECT id, aadhaar_number, full_name, address_line1, city, district, date_of_birth, gender
    FROM citizens
    WHERE aadhaar_number = '387193279353'
      AND status = 'ACTIVE'
),
-- Step 1: Find candidates with exact address match (most strict)
exact_address_matches AS (
    SELECT 
        sc.id AS seed_id,
        sc.aadhaar_number AS seed_aadhaar,
        sc.full_name AS seed_name,
        rc.id AS member_id,
        rc.aadhaar_number AS family_member_aadhaar,
        rc.full_name AS family_member_name,
        rc.date_of_birth AS member_dob,
        rc.gender AS member_gender,
        EXTRACT(YEAR FROM AGE(rc.date_of_birth)) AS member_age,
        EXTRACT(YEAR FROM AGE(sc.date_of_birth)) AS seed_age,
        ABS(EXTRACT(YEAR FROM AGE(sc.date_of_birth, rc.date_of_birth))) AS age_diff,
        'Exact Address' AS match_type,
        85 AS base_confidence
    FROM seed_citizen sc
    INNER JOIN citizens rc ON sc.address_line1 = rc.address_line1
    WHERE rc.id != sc.id
      AND rc.status = 'ACTIVE'
      AND rc.gender IS NOT NULL  -- Must have gender (backend requirement)
      AND rc.date_of_birth IS NOT NULL  -- Must have DOB (backend requirement)
    LIMIT 15  -- Backend limits to 15 candidates
),
-- Step 2: Find spouse (opposite gender, similar age within 15 years)
spouse_candidates AS (
    SELECT *,
        CASE 
            WHEN seed_citizen.gender != member_gender 
                 AND age_diff <= 15
            THEN 'Spouse'
            ELSE NULL
        END AS relationship_type,
        base_confidence AS confidence
    FROM exact_address_matches
    CROSS JOIN seed_citizen
    WHERE seed_citizen.id = seed_id
),
-- Step 3: Find children (at least 15 years younger, exact address only)
child_candidates AS (
    SELECT *,
        'Child' AS relationship_type,
        80 AS confidence
    FROM exact_address_matches
    WHERE member_age < seed_age - 15
),
-- Step 4: Combine and limit to 8 total members (including self)
ranked_members AS (
    -- Spouse (if found)
    SELECT 
        seed_aadhaar,
        seed_name,
        family_member_aadhaar,
        family_member_name,
        relationship_type,
        confidence,
        match_type,
        1 AS priority  -- Spouse has highest priority
    FROM spouse_candidates
    WHERE relationship_type = 'Spouse'
    LIMIT 1  -- Only one spouse
    
    UNION ALL
    
    -- Children (max 6 to keep total under 8)
    SELECT 
        seed_aadhaar,
        seed_name,
        family_member_aadhaar,
        family_member_name,
        relationship_type,
        confidence,
        match_type,
        2 AS priority  -- Children second priority
    FROM child_candidates
    LIMIT 6  -- Max 6 children
    
    UNION ALL
    
    -- Other family members (if no spouse found, fill up to 8 total)
    SELECT 
        seed_aadhaar,
        seed_name,
        family_member_aadhaar,
        family_member_name,
        'Family Member' AS relationship_type,
        base_confidence AS confidence,
        match_type,
        3 AS priority  -- Other family members lowest priority
    FROM exact_address_matches
    WHERE member_id NOT IN (
        SELECT member_id FROM spouse_candidates WHERE relationship_type = 'Spouse'
        UNION
        SELECT member_id FROM child_candidates LIMIT 6
    )
    LIMIT 7  -- Max 7 to keep total under 8 (1 self + 7 others)
)
SELECT 
    seed_aadhaar,
    seed_name,
    family_member_aadhaar,
    family_member_name,
    relationship_type,
    confidence,
    match_type
FROM ranked_members
ORDER BY priority ASC, confidence DESC
LIMIT 8;  -- Final limit: max 8 members (including self would be 9, but we exclude self in results)

