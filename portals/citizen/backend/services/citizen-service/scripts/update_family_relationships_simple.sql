-- Simple script to update family relationships for seed Aadhaar: 387193279353 (Sulekha Rajput)
-- Run this script in pgAdmin or psql

-- Step 1: Delete existing relationships for this seed citizen
DELETE FROM family_relationships_cache
WHERE citizen_id IN (
    SELECT id FROM citizens WHERE aadhaar_number = '387193279353' AND status = 'ACTIVE'
);

-- Step 2: Insert new relationships
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
    seed.id AS citizen_id,
    family.id AS related_citizen_id,
    rel.relationship_type,
    rel.relationship_label,
    rel.confidence,
    true AS is_verified,
    'MANUAL' AS source,
    1 AS depth,
    CURRENT_TIMESTAMP AS synced_at,
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at
FROM (
    VALUES
        ('387193279353', '859689643743', 'SPOUSE', 'Spouse', 85),
        ('387193279353', '859689643991', 'CHILD', 'Child', 80),
        ('387193279353', '237694608901', 'CHILD', 'Child', 80),
        ('387193279353', '875205246823', 'CHILD', 'Child', 80),
        ('387193279353', '411886224383', 'FAMILY_MEMBER', 'Family Member', 80),
        ('387193279353', '888205246823', 'FAMILY_MEMBER', 'Family Member', 80),
        ('387193279353', '859548833425', 'CHILD', 'Child', 80),
        ('387193279353', '876205246823', 'FAMILY_MEMBER', 'Family Member', 75)
) AS rel(seed_aadhaar, family_aadhaar, relationship_type, relationship_label, confidence)
INNER JOIN citizens seed ON seed.aadhaar_number = rel.seed_aadhaar AND seed.status = 'ACTIVE'
INNER JOIN citizens family ON family.aadhaar_number = rel.family_aadhaar AND family.status = 'ACTIVE'
WHERE seed.id != family.id  -- Ensure no self-relationships
ON CONFLICT (citizen_id, related_citizen_id, relationship_type) 
DO UPDATE SET
    relationship_label = EXCLUDED.relationship_label,
    confidence = EXCLUDED.confidence,
    is_verified = EXCLUDED.is_verified,
    source = EXCLUDED.source,
    synced_at = EXCLUDED.synced_at,
    updated_at = EXCLUDED.updated_at;

-- Step 3: Verify the inserted relationships
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

