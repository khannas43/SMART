package com.smart.citizen.repository;

import com.smart.citizen.entity.FamilyRelationshipCache;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface FamilyRelationshipCacheRepository extends JpaRepository<FamilyRelationshipCache, UUID> {
    
    /**
     * Find all relationships for a citizen, ordered by depth
     */
    List<FamilyRelationshipCache> findByCitizenIdOrderByDepthAsc(UUID citizenId);
    
    /**
     * Find relationships up to a certain depth
     */
    List<FamilyRelationshipCache> findByCitizenIdAndDepthLessThanEqualOrderByDepthAsc(
        UUID citizenId, int maxDepth);
    
    /**
     * Find relationships by type
     */
    List<FamilyRelationshipCache> findByCitizenIdAndRelationshipType(
        UUID citizenId, String relationshipType);
    
    /**
     * Find expired cache entries
     */
    List<FamilyRelationshipCache> findByExpiresAtBefore(LocalDateTime now);
    
    /**
     * Find non-expired cache entries for a citizen
     */
    @Query("SELECT f FROM FamilyRelationshipCache f " +
           "WHERE f.citizen.id = :citizenId " +
           "AND (f.expiresAt IS NULL OR f.expiresAt > :now) " +
           "ORDER BY f.depth ASC")
    List<FamilyRelationshipCache> findFreshByCitizenId(
        @Param("citizenId") UUID citizenId, 
        @Param("now") LocalDateTime now);
    
    /**
     * Delete old cache entries for a citizen (refresh)
     */
    @Modifying
    @Query("DELETE FROM FamilyRelationshipCache f WHERE f.citizen.id = :citizenId")
    void deleteByCitizenId(@Param("citizenId") UUID citizenId);
    
    /**
     * Check if cache exists and is fresh
     */
    @Query("SELECT COUNT(f) > 0 FROM FamilyRelationshipCache f " +
           "WHERE f.citizen.id = :citizenId " +
           "AND (f.expiresAt IS NULL OR f.expiresAt > :now)")
    boolean existsFreshCache(@Param("citizenId") UUID citizenId, @Param("now") LocalDateTime now);
    
    /**
     * Count relationships for a citizen
     */
    long countByCitizenId(UUID citizenId);
}

