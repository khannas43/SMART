-- Script to update family relationships for seed Aadhaar: 387193279353 (Sulekha Rajput)
-- This script inserts/updates relationships in family_relationships_cache table
-- Source: MANUAL (user-verified), is_verified: true

-- Step 1: Get UUIDs for all citizens by Aadhaar number
WITH citizen_ids AS (
    SELECT 
        aadhaar_number,
        id AS citizen_uuid,
        full_name
    FROM citizens
    WHERE aadhaar_number IN (
        '387193279353',  -- Seed: Sulekha Rajput
        '859689643743',  -- Shyam Rajput (Spouse)
        '859689643991',  -- Bali Rajput (Child)
        '237694608901',  -- Babita Rajput (Child)
        '875205246823',  -- Jugnu Rajput (Child)
        '411886224383',  -- Choteram Gujjar (Family Member)
        '888205246823',  -- Savita Gujjar (Family Member)
        '859548833425',  -- Bholaram Gujjar (Child)
        '876205246823'   -- Chiku Rajput (Family Member)
    )
    AND status = 'ACTIVE'
),
-- Step 2: Map relationship types to database format
relationships AS (
    SELECT 
        '387193279353' AS seed_aadhaar,
        '859689643743' AS family_aadhaar,
        'SPOUSE' AS relationship_type,
        'Spouse' AS relationship_label,
        85 AS confidence
    UNION ALL
    SELECT '387193279353', '859689643991', 'CHILD', 'Child', 80
    UNION ALL
    SELECT '387193279353', '237694608901', 'CHILD', 'Child', 80
    UNION ALL
    SELECT '387193279353', '875205246823', 'CHILD', 'Child', 80
    UNION ALL
    SELECT '387193279353', '411886224383', 'FAMILY_MEMBER', 'Family Member', 80
    UNION ALL
    SELECT '387193279353', '888205246823', 'FAMILY_MEMBER', 'Family Member', 80
    UNION ALL
    SELECT '387193279353', '859548833425', 'CHILD', 'Child', 80
    UNION ALL
    SELECT '387193279353', '876205246823', 'FAMILY_MEMBER', 'Family Member', 75
)
-- Step 3: Insert/Update relationships
-- First, delete existing relationships for this seed citizen (to avoid duplicates)
-- Note: Run this DELETE separately if needed, or use the INSERT with ON CONFLICT below

-- Step 4: Insert new relationships (with ON CONFLICT to handle updates)
INSERT INTO family_relationships_cache (
    citizen_id,
    related_citizen_id,
    relationship_type,
    relationship_label,
    confidence,
    is_verified,
    source,
    depth,
    synced_at,
    created_at,
    updated_at
)
SELECT 
    seed.citizen_uuid AS citizen_id,
    family.citizen_uuid AS related_citizen_id,
    rel.relationship_type,
    rel.relationship_label,
    rel.confidence,
    true AS is_verified,  -- Mark as verified since it's manual entry
    'MANUAL' AS source,   -- Source is manual/user-verified
    1 AS depth,           -- Direct relationships (depth 1)
    CURRENT_TIMESTAMP AS synced_at,
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at
FROM relationships rel
INNER JOIN citizen_ids seed ON seed.aadhaar_number = rel.seed_aadhaar
INNER JOIN citizen_ids family ON family.aadhaar_number = rel.family_aadhaar
WHERE seed.citizen_uuid IS NOT NULL
  AND family.citizen_uuid IS NOT NULL
  AND seed.citizen_uuid != family.citizen_uuid  -- Ensure no self-relationships
ON CONFLICT (citizen_id, related_citizen_id, relationship_type) 
DO UPDATE SET
    relationship_label = EXCLUDED.relationship_label,
    confidence = EXCLUDED.confidence,
    is_verified = EXCLUDED.is_verified,
    source = EXCLUDED.source,
    synced_at = EXCLUDED.synced_at,
    updated_at = EXCLUDED.updated_at;

-- Step 5: Verify the inserted relationships
SELECT 
    c1.aadhaar_number AS seed_aadhaar,
    c1.full_name AS seed_name,
    c2.aadhaar_number AS family_member_aadhaar,
    c2.full_name AS family_member_name,
    frc.relationship_type,
    frc.relationship_label,
    frc.confidence,
    frc.is_verified,
    frc.source,
    frc.created_at
FROM family_relationships_cache frc
INNER JOIN citizens c1 ON c1.id = frc.citizen_id
INNER JOIN citizens c2 ON c2.id = frc.related_citizen_id
WHERE c1.aadhaar_number = '387193279353'
ORDER BY 
    CASE frc.relationship_type
        WHEN 'SPOUSE' THEN 1
        WHEN 'CHILD' THEN 2
        ELSE 3
    END,
    frc.confidence DESC;

