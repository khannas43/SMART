-- STRICT Query: Get exactly 8 family members (matching backend logic)
-- This query replicates the backend's filtering to show realistic family relationships
-- Replace '387193279353' with your seed Aadhaar number

WITH seed_citizen AS (
    SELECT id, aadhaar_number, full_name, address_line1, city, district, date_of_birth, gender,
           EXTRACT(YEAR FROM AGE(date_of_birth)) AS age
    FROM citizens
    WHERE aadhaar_number = '387193279353'
      AND status = 'ACTIVE'
),
-- Step 1: Get candidates with exact address match (backend's primary strategy)
exact_address_candidates AS (
    SELECT 
        sc.id AS seed_id,
        sc.aadhaar_number AS seed_aadhaar,
        sc.full_name AS seed_name,
        sc.age AS seed_age,
        sc.gender AS seed_gender,
        rc.id AS member_id,
        rc.aadhaar_number AS family_member_aadhaar,
        rc.full_name AS family_member_name,
        rc.date_of_birth AS member_dob,
        rc.gender AS member_gender,
        EXTRACT(YEAR FROM AGE(rc.date_of_birth)) AS member_age,
        ABS(EXTRACT(YEAR FROM AGE(sc.date_of_birth, rc.date_of_birth))) AS age_diff
    FROM seed_citizen sc
    INNER JOIN citizens rc ON sc.address_line1 = rc.address_line1
    WHERE rc.id != sc.id
      AND rc.status = 'ACTIVE'
      AND rc.gender IS NOT NULL  -- Backend requires gender
      AND rc.date_of_birth IS NOT NULL  -- Backend requires DOB
    LIMIT 15  -- Backend limits to 15 candidates
),
-- Step 2: Identify spouse (opposite gender, age diff <= 15 years)
spouse_ids AS (
    SELECT member_id
    FROM exact_address_candidates
    WHERE seed_gender != member_gender
      AND age_diff <= 15
    LIMIT 1  -- Only one spouse
),
-- Step 3: Identify children (at least 15 years younger, exact address only)
children_ids AS (
    SELECT member_id
    FROM exact_address_candidates
    WHERE member_age < seed_age - 15
      AND member_id NOT IN (SELECT member_id FROM spouse_ids)
    LIMIT 6  -- Max 6 children
),
-- Step 4: Get other family members (if no spouse, or to fill up to 8 total)
other_family_ids AS (
    SELECT member_id
    FROM exact_address_candidates
    WHERE member_id NOT IN (SELECT member_id FROM spouse_ids)
      AND member_id NOT IN (SELECT member_id FROM children_ids)
    LIMIT 7  -- Fill remaining slots up to 8 total
),
-- Step 5: Combine all family members with their relationship types
family_members AS (
    SELECT 
        seed_aadhaar,
        seed_name,
        family_member_aadhaar,
        family_member_name,
        member_id,
        CASE 
            WHEN member_id IN (SELECT member_id FROM spouse_ids) THEN 'Spouse'
            WHEN member_id IN (SELECT member_id FROM children_ids) THEN 'Child'
            WHEN member_id IN (SELECT member_id FROM other_family_ids) THEN 'Family Member'
        END AS relationship_type,
        CASE 
            WHEN member_id IN (SELECT member_id FROM spouse_ids) THEN 85
            WHEN member_id IN (SELECT member_id FROM children_ids) THEN 80
            WHEN member_id IN (SELECT member_id FROM other_family_ids) THEN 75
        END AS confidence,
        'Exact Address Match' AS match_type
    FROM exact_address_candidates
    WHERE member_id IN (SELECT member_id FROM spouse_ids)
       OR member_id IN (SELECT member_id FROM children_ids)
       OR member_id IN (SELECT member_id FROM other_family_ids)
)
-- Final selection: limit to 8 members, ordered by priority
SELECT 
    seed_aadhaar,
    seed_name,
    family_member_aadhaar,
    family_member_name,
    relationship_type,
    confidence,
    match_type
FROM family_members
ORDER BY 
    CASE relationship_type
        WHEN 'Spouse' THEN 1
        WHEN 'Child' THEN 2
        ELSE 3
    END,
    confidence DESC
LIMIT 8;
