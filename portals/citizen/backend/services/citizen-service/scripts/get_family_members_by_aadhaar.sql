-- Query to get Aadhaar numbers of linked family members for a seed Aadhaar number
-- Usage: Replace '387193279353' with the desired seed Aadhaar number

-- Option 1: Get family members from family_relationships_cache (cached relationships)
SELECT 
    seed_citizen.aadhaar_number AS seed_aadhaar,
    seed_citizen.full_name AS seed_name,
    related_citizen.aadhaar_number AS family_member_aadhaar,
    related_citizen.full_name AS family_member_name,
    frc.relationship_label AS relationship_type,
    frc.relationship_type AS relationship_code,
    frc.confidence,
    frc.source,
    frc.depth,
    frc.is_verified,
    frc.synced_at
FROM citizens seed_citizen
INNER JOIN family_relationships_cache frc ON seed_citizen.id = frc.citizen_id
INNER JOIN citizens related_citizen ON frc.related_citizen_id = related_citizen.id
WHERE seed_citizen.aadhaar_number = '387193279353'
  AND (frc.expires_at IS NULL OR frc.expires_at > CURRENT_TIMESTAMP)
ORDER BY frc.depth ASC, frc.confidence DESC;

-- Option 2: Also check reverse relationships (where the seed is the related citizen)
-- This finds relationships where the seed citizen is listed as a related member
SELECT 
    seed_citizen.aadhaar_number AS seed_aadhaar,
    seed_citizen.full_name AS seed_name,
    related_citizen.aadhaar_number AS family_member_aadhaar,
    related_citizen.full_name AS family_member_name,
    CASE 
        WHEN frc.relationship_type = 'PARENT' THEN 'CHILD'
        WHEN frc.relationship_type = 'CHILD' THEN 'PARENT'
        ELSE frc.relationship_label
    END AS relationship_type,
    CASE 
        WHEN frc.relationship_type = 'PARENT' THEN 'CHILD'
        WHEN frc.relationship_type = 'CHILD' THEN 'PARENT'
        ELSE frc.relationship_type
    END AS relationship_code,
    frc.confidence,
    frc.source,
    frc.depth,
    frc.is_verified,
    frc.synced_at
FROM citizens seed_citizen
INNER JOIN family_relationships_cache frc ON seed_citizen.id = frc.related_citizen_id
INNER JOIN citizens related_citizen ON frc.citizen_id = related_citizen.id
WHERE seed_citizen.aadhaar_number = '387193279353'
  AND (frc.expires_at IS NULL OR frc.expires_at > CURRENT_TIMESTAMP)
ORDER BY frc.depth ASC, frc.confidence DESC;

-- Option 3: Combined query (both directions) - RECOMMENDED
SELECT 
    seed_citizen.aadhaar_number AS seed_aadhaar,
    seed_citizen.full_name AS seed_name,
    related_citizen.aadhaar_number AS family_member_aadhaar,
    related_citizen.full_name AS family_member_name,
    frc.relationship_label AS relationship_type,
    frc.relationship_type AS relationship_code,
    frc.confidence,
    frc.source,
    frc.depth,
    frc.is_verified,
    frc.synced_at
FROM citizens seed_citizen
INNER JOIN family_relationships_cache frc ON seed_citizen.id = frc.citizen_id
INNER JOIN citizens related_citizen ON frc.related_citizen_id = related_citizen.id
WHERE seed_citizen.aadhaar_number = '387193279353'
  AND (frc.expires_at IS NULL OR frc.expires_at > CURRENT_TIMESTAMP)

UNION ALL

SELECT 
    seed_citizen.aadhaar_number AS seed_aadhaar,
    seed_citizen.full_name AS seed_name,
    related_citizen.aadhaar_number AS family_member_aadhaar,
    related_citizen.full_name AS family_member_name,
    CASE 
        WHEN frc.relationship_type = 'PARENT' THEN 'CHILD'
        WHEN frc.relationship_type = 'CHILD' THEN 'PARENT'
        ELSE frc.relationship_label
    END AS relationship_type,
    CASE 
        WHEN frc.relationship_type = 'PARENT' THEN 'CHILD'
        WHEN frc.relationship_type = 'CHILD' THEN 'PARENT'
        ELSE frc.relationship_type
    END AS relationship_code,
    frc.confidence,
    frc.source,
    frc.depth,
    frc.is_verified,
    frc.synced_at
FROM citizens seed_citizen
INNER JOIN family_relationships_cache frc ON seed_citizen.id = frc.related_citizen_id
INNER JOIN citizens related_citizen ON frc.citizen_id = related_citizen.id
WHERE seed_citizen.aadhaar_number = '387193279353'
  AND (frc.expires_at IS NULL OR frc.expires_at > CURRENT_TIMESTAMP)

ORDER BY depth ASC, confidence DESC;

-- Option 4: Simple query - Just Aadhaar numbers (if cache is empty, use address matching)
-- This query also includes potential family members based on address matching
WITH seed_citizen AS (
    SELECT id, aadhaar_number, full_name, address_line1, city, district, date_of_birth, gender
    FROM citizens
    WHERE aadhaar_number = '387193279353'
),
cached_relationships AS (
    -- From cache
    SELECT 
        sc.aadhaar_number AS seed_aadhaar,
        rc.aadhaar_number AS family_member_aadhaar,
        rc.full_name AS family_member_name,
        frc.relationship_label AS relationship_type,
        frc.confidence,
        'CACHED' AS source
    FROM seed_citizen sc
    INNER JOIN family_relationships_cache frc ON sc.id = frc.citizen_id
    INNER JOIN citizens rc ON frc.related_citizen_id = rc.id
    WHERE (frc.expires_at IS NULL OR frc.expires_at > CURRENT_TIMESTAMP)
)
SELECT 
    seed_aadhaar,
    family_member_aadhaar,
    family_member_name,
    relationship_type,
    confidence,
    source
FROM cached_relationships

UNION ALL

-- Address-based matches (fallback if cache is empty)
SELECT 
    sc.aadhaar_number AS seed_aadhaar,
    rc.aadhaar_number AS family_member_aadhaar,
    rc.full_name AS family_member_name,
    CASE 
        WHEN sc.gender != rc.gender AND ABS(EXTRACT(YEAR FROM AGE(sc.date_of_birth, rc.date_of_birth))) <= 15 
        THEN 'Spouse'
        WHEN rc.date_of_birth IS NOT NULL AND sc.date_of_birth IS NOT NULL 
             AND EXTRACT(YEAR FROM AGE(sc.date_of_birth, rc.date_of_birth)) > 15
        THEN 'Child'
        ELSE 'Family Member'
    END AS relationship_type,
    CASE 
        WHEN sc.address_line1 = rc.address_line1 THEN 85
        WHEN sc.city = rc.city THEN 70
        WHEN sc.district = rc.district THEN 60
        ELSE 50
    END AS confidence,
    'ADDRESS_MATCH' AS source
FROM seed_citizen sc
INNER JOIN citizens rc ON (
    (sc.address_line1 IS NOT NULL AND sc.address_line1 = rc.address_line1)
    OR (sc.city IS NOT NULL AND sc.city = rc.city)
    OR (sc.district IS NOT NULL AND sc.district = rc.district)
)
WHERE rc.id != sc.id
  AND rc.status = 'ACTIVE'
  AND NOT EXISTS (
      SELECT 1 FROM cached_relationships cr 
      WHERE cr.family_member_aadhaar = rc.aadhaar_number
  )

ORDER BY confidence DESC, relationship_type;

