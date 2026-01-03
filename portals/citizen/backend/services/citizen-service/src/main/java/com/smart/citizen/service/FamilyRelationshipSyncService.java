package com.smart.citizen.service;

import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.FamilyRelationshipCache;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.FamilyRelationshipCacheRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class FamilyRelationshipSyncService {
    
    private final ProfileGraphService profileGraphService;
    private final FamilyRelationshipCacheRepository cacheRepository;
    private final CitizenRepository citizenRepository;
    
    @Value("${family-relationships.cache.ttl-hours:1}")
    private int cacheTtlHours;
    
    @Value("${family-relationships.cache.auto-sync:true}")
    private boolean autoSyncEnabled;
    
    /**
     * Sync family relationships from Neo4j to PostgreSQL cache
     * 
     * @param citizenId Citizen to sync relationships for
     * @param depth Maximum depth to sync
     * @return Number of relationships synced
     */
    @Transactional
    public int syncFromNeo4j(UUID citizenId, int depth) {
        if (!autoSyncEnabled) {
            log.debug("Auto-sync is disabled, skipping sync for citizen: {}", citizenId);
            return 0;
        }
        
        try {
            Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new RuntimeException("Citizen not found: " + citizenId));
            
            // Query Neo4j
            String identifier = citizen.getAadhaarNumber() != null && !citizen.getAadhaarNumber().isEmpty()
                ? citizen.getAadhaarNumber()
                : citizenId.toString();
            
            Map<String, Object> neo4jGraph = profileGraphService.getFamilyNetwork(identifier, depth);
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> nodes = (List<Map<String, Object>>) neo4jGraph.get("nodes");
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> links = (List<Map<String, Object>>) neo4jGraph.get("links");
            
            if (nodes == null || nodes.isEmpty()) {
                log.debug("No relationships found in Neo4j for citizen: {}", citizenId);
                return 0;
            }
            
            // Delete existing cache for this citizen
            cacheRepository.deleteByCitizenId(citizenId);
            
            // Build mapping of Neo4j node IDs to citizen IDs
            Map<Long, UUID> nodeIdToCitizenId = buildNodeMapping(nodes, citizenId);
            
            // Calculate expiration time
            LocalDateTime expiresAt = LocalDateTime.now().plusHours(cacheTtlHours);
            LocalDateTime syncedAt = LocalDateTime.now();
            
            // Sync relationships
            int syncedCount = 0;
            Set<String> processedRelationships = new HashSet<>(); // Track duplicates
            
            for (Map<String, Object> link : links) {
                Long sourceId = ((Number) link.get("source")).longValue();
                Long targetId = ((Number) link.get("target")).longValue();
                String relType = (String) link.get("type");
                if (relType == null) {
                    relType = (String) link.get("relationship_type");
                }
                if (relType == null) {
                    relType = "RELATED";
                }
                
                UUID fromId = nodeIdToCitizenId.get(sourceId);
                UUID toId = nodeIdToCitizenId.get(targetId);
                
                // Only cache relationships where this citizen is the source
                if (fromId != null && toId != null && fromId.equals(citizenId)) {
                    // Create unique key to avoid duplicates
                    String relationshipKey = citizenId + ":" + toId + ":" + relType;
                    if (processedRelationships.contains(relationshipKey)) {
                        continue; // Skip duplicate
                    }
                    processedRelationships.add(relationshipKey);
                    
                    // Get related citizen
                    Optional<Citizen> relatedCitizenOpt = citizenRepository.findById(toId);
                    if (relatedCitizenOpt.isEmpty()) {
                        log.warn("Related citizen not found: {}, skipping relationship", toId);
                        continue;
                    }
                    
                    String relationshipLabel = mapRelationshipType(relType);
                    Integer confidence = link.get("weight") != null 
                        ? (int) (((Number) link.get("weight")).doubleValue() * 100)
                        : 85;
                    
                    FamilyRelationshipCache cache = FamilyRelationshipCache.builder()
                        .citizen(citizen)
                        .relatedCitizen(relatedCitizenOpt.get())
                        .relationshipType(relType)
                        .relationshipLabel(relationshipLabel)
                        .confidence(confidence)
                        .isVerified(false)
                        .source("NEO4J")
                        .depth(1) // Can be calculated from path if needed
                        .syncedAt(syncedAt)
                        .expiresAt(expiresAt)
                        .build();
                    
                    try {
                        cacheRepository.save(cache);
                        syncedCount++;
                    } catch (Exception e) {
                        log.warn("Failed to save cache entry for relationship {} -> {}: {}", 
                            citizenId, toId, e.getMessage());
                    }
                }
            }
            
            log.info("Synced {} relationships from Neo4j to PostgreSQL cache for citizen: {}", 
                syncedCount, citizenId);
            return syncedCount;
            
        } catch (Exception e) {
            log.error("Failed to sync relationships from Neo4j for citizen: {}", citizenId, e);
            throw new RuntimeException("Sync failed: " + e.getMessage(), e);
        }
    }
    
    /**
     * Build mapping from Neo4j node IDs to citizen UUIDs
     */
    private Map<Long, UUID> buildNodeMapping(List<Map<String, Object>> nodes, UUID rootCitizenId) {
        Map<Long, UUID> mapping = new HashMap<>();
        
        for (Map<String, Object> node : nodes) {
            Long nodeId = ((Number) node.get("id")).longValue();
            String grIdStr = (String) node.get("gr_id");
            String aadhaar = (String) node.get("jan_aadhaar");
            
            UUID citizenId = null;
            
            // Try to find by gr_id (UUID)
            if (grIdStr != null) {
                try {
                    citizenId = UUID.fromString(grIdStr);
                    // Verify citizen exists
                    if (citizenRepository.findById(citizenId).isEmpty()) {
                        citizenId = null;
                    }
                } catch (IllegalArgumentException e) {
                    // Not a UUID, try Aadhaar
                }
            }
            
            // Try to find by Aadhaar
            if (citizenId == null && aadhaar != null && !aadhaar.isEmpty()) {
                Optional<Citizen> citizenOpt = citizenRepository.findByAadhaarNumber(aadhaar);
                if (citizenOpt.isPresent()) {
                    citizenId = citizenOpt.get().getId();
                }
            }
            
            // Fallback to root citizen ID if this is the root node
            if (citizenId == null) {
                // Check if this node matches the root citizen by name or other attributes
                String name = (String) node.get("name");
                if (name != null && !name.equals("Unknown")) {
                    // Try to find by name (less reliable, but fallback)
                    Optional<Citizen> citizenOpt = citizenRepository.findById(rootCitizenId);
                    if (citizenOpt.isPresent() && name.equals(citizenOpt.get().getFullName())) {
                        citizenId = rootCitizenId;
                    }
                } else {
                    citizenId = rootCitizenId;
                }
            }
            
            if (citizenId != null) {
                mapping.put(nodeId, citizenId);
            } else {
                log.warn("Could not map Neo4j node {} to citizen ID (gr_id: {}, aadhaar: {})", 
                    nodeId, grIdStr, aadhaar);
            }
        }
        
        return mapping;
    }
    
    /**
     * Map Neo4j relationship type to human-readable label
     */
    private String mapRelationshipType(String relType) {
        if (relType == null) {
            return "Family Member";
        }
        
        return switch (relType.toUpperCase()) {
            case "SPOUSE" -> "Spouse";
            case "CHILD" -> "Child";
            case "PARENT" -> "Parent";
            case "SIBLING" -> "Sibling";
            case "CO_RESIDENT" -> "Co-Resident";
            case "CO_BENEFIT" -> "Co-Benefit";
            case "EMPLOYEE_OF" -> "Employee";
            case "BUSINESS_PARTNER" -> "Business Partner";
            case "SHG_MEMBER" -> "SHG Member";
            default -> "Family Member";
        };
    }
    
    /**
     * Clean up expired cache entries
     */
    @Transactional
    public int cleanupExpiredCache() {
        LocalDateTime now = LocalDateTime.now();
        List<FamilyRelationshipCache> expired = cacheRepository.findByExpiresAtBefore(now);
        if (!expired.isEmpty()) {
            int count = expired.size();
            cacheRepository.deleteAll(expired);
            log.info("Cleaned up {} expired cache entries", count);
            return count;
        }
        return 0;
    }
    
    /**
     * Get cache statistics
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        LocalDateTime now = LocalDateTime.now();
        
        long totalCacheEntries = cacheRepository.count();
        long expiredEntries = cacheRepository.findByExpiresAtBefore(now).size();
        long freshEntries = totalCacheEntries - expiredEntries;
        
        stats.put("totalEntries", totalCacheEntries);
        stats.put("expiredEntries", expiredEntries);
        stats.put("freshEntries", freshEntries);
        stats.put("cacheTtlHours", cacheTtlHours);
        stats.put("autoSyncEnabled", autoSyncEnabled);
        
        return stats;
    }
}

