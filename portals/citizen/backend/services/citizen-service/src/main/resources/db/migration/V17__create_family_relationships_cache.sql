-- Migration: Create family relationships cache table
-- Purpose: Cache Neo4j relationship queries in PostgreSQL for fast access and fallback
-- This enables hybrid approach: Neo4j (primary) -> PostgreSQL Cache -> Address Matching (fallback)

CREATE TABLE IF NOT EXISTS family_relationships_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Citizen identifiers
    citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    
    -- Relationship details
    related_citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- SPOUSE, CHILD, PARENT, SIBLING, etc.
    relationship_label VARCHAR(50), -- Human-readable: "Spouse", "Child", etc.
    
    -- Metadata
    confidence INTEGER, -- 0-100
    is_verified BOOLEAN DEFAULT false,
    source VARCHAR(50) DEFAULT 'NEO4J', -- NEO4J, POSTGRESQL, MANUAL
    
    -- Graph metadata
    depth INTEGER DEFAULT 1, -- How many hops from root citizen
    path_length INTEGER, -- Shortest path length
    
    -- Cache metadata
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Optional: TTL for cache
    last_verified_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_relationship UNIQUE (citizen_id, related_citizen_id, relationship_type),
    CONSTRAINT no_self_relationship CHECK (citizen_id != related_citizen_id)
);

-- Indexes for performance
CREATE INDEX idx_family_cache_citizen ON family_relationships_cache(citizen_id);
CREATE INDEX idx_family_cache_related ON family_relationships_cache(related_citizen_id);
CREATE INDEX idx_family_cache_type ON family_relationships_cache(relationship_type);
CREATE INDEX idx_family_cache_synced ON family_relationships_cache(synced_at);
CREATE INDEX idx_family_cache_expires ON family_relationships_cache(expires_at) WHERE expires_at IS NOT NULL;

-- Composite index for common queries
CREATE INDEX idx_family_cache_citizen_type ON family_relationships_cache(citizen_id, relationship_type);
CREATE INDEX idx_family_cache_citizen_depth ON family_relationships_cache(citizen_id, depth);

COMMENT ON TABLE family_relationships_cache IS 'Cached family relationships synced from Neo4j for fast PostgreSQL queries and fallback when Neo4j is unavailable';
COMMENT ON COLUMN family_relationships_cache.source IS 'Source of relationship: NEO4J (from graph DB), POSTGRESQL (from address matching), MANUAL (user verified)';
COMMENT ON COLUMN family_relationships_cache.expires_at IS 'Cache expiration time. NULL means never expires. Used for TTL-based cache invalidation';

