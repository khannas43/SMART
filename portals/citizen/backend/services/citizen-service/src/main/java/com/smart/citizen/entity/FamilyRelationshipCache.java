package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "family_relationships_cache", 
       uniqueConstraints = @UniqueConstraint(
           columnNames = {"citizen_id", "related_citizen_id", "relationship_type"}
       ),
       indexes = {
           @Index(name = "idx_family_cache_citizen", columnList = "citizen_id"),
           @Index(name = "idx_family_cache_related", columnList = "related_citizen_id"),
           @Index(name = "idx_family_cache_type", columnList = "relationship_type"),
           @Index(name = "idx_family_cache_synced", columnList = "synced_at"),
           @Index(name = "idx_family_cache_citizen_type", columnList = "citizen_id, relationship_type"),
           @Index(name = "idx_family_cache_citizen_depth", columnList = "citizen_id, depth")
       })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FamilyRelationshipCache extends BaseEntity {
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false)
    private Citizen citizen;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "related_citizen_id", nullable = false)
    private Citizen relatedCitizen;
    
    @Column(name = "relationship_type", nullable = false, length = 50)
    private String relationshipType;
    
    @Column(name = "relationship_label", length = 50)
    private String relationshipLabel;
    
    @Column(name = "confidence")
    private Integer confidence;
    
    @Column(name = "is_verified")
    @Builder.Default
    private Boolean isVerified = false;
    
    @Column(name = "source", length = 50)
    @Builder.Default
    private String source = "NEO4J";
    
    @Column(name = "depth")
    @Builder.Default
    private Integer depth = 1;
    
    @Column(name = "path_length")
    private Integer pathLength;
    
    @Column(name = "synced_at")
    private LocalDateTime syncedAt;
    
    @Column(name = "expires_at")
    private LocalDateTime expiresAt;
    
    @Column(name = "last_verified_at")
    private LocalDateTime lastVerifiedAt;
}

