package com.smart.citizen.service.impl;

import com.smart.citizen.dto.citizen.BulkUpdateFamilyRelationshipsRequest;
import com.smart.citizen.dto.citizen.ConsentPreferenceDto;
import com.smart.citizen.dto.citizen.CitizenRequest;
import com.smart.citizen.dto.citizen.CitizenResponse;
import com.smart.citizen.dto.citizen.CitizenUpdateRequest;
import com.smart.citizen.dto.citizen.FamilyGraphResponse;
import com.smart.citizen.dto.citizen.FamilyMember;
import com.smart.citizen.dto.citizen.FamilyRelationship;
import com.smart.citizen.dto.citizen.UpdateFamilyRelationshipRequest;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.exception.BadRequestException;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.CitizenMapper;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.FamilyRelationshipCacheRepository;
import com.smart.citizen.service.CitizenService;
import com.smart.citizen.service.FamilyRelationshipSyncService;
import com.smart.citizen.service.ProfileGraphService;
import com.smart.citizen.service.TransliterationService;
import com.smart.citizen.entity.FamilyRelationshipCache;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class CitizenServiceImpl implements CitizenService {

    private final CitizenRepository citizenRepository;
    private final CitizenMapper citizenMapper;
    private final TransliterationService transliterationService;
    private final ProfileGraphService profileGraphService;
    private final FamilyRelationshipSyncService familyRelationshipSyncService;
    private final FamilyRelationshipCacheRepository cacheRepository;

    @Override
    public CitizenResponse createCitizen(CitizenRequest request) {
        // Check if mobile number already exists
        if (citizenRepository.existsByMobileNumber(request.getMobileNumber())) {
            throw new BadRequestException("Mobile number already exists: " + request.getMobileNumber());
        }

        // Check if Aadhaar number already exists (if provided)
        if (request.getAadhaarNumber() != null && !request.getAadhaarNumber().isEmpty()) {
            if (citizenRepository.existsByAadhaarNumber(request.getAadhaarNumber())) {
                throw new BadRequestException("Aadhaar number already exists: " + request.getAadhaarNumber());
            }
        }

        Citizen citizen = citizenMapper.toEntity(request);
        citizen.setStatus(Citizen.CitizenStatus.ACTIVE);
        
        // Auto-transliterate name to Hindi
        if (citizen.getFullName() != null && !citizen.getFullName().trim().isEmpty()) {
            String hindiName = transliterationService.transliterateName(citizen.getFullName());
            citizen.setFullNameHindi(hindiName);
        }
        citizen.setVerificationStatus(Citizen.VerificationStatus.PENDING);
        Citizen savedCitizen = citizenRepository.save(citizen);
        return citizenMapper.toResponse(savedCitizen);
    }

    @Override
    @Transactional(readOnly = true)
    public CitizenResponse getCitizenById(UUID id) {
        Citizen citizen = citizenRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", id));
        return citizenMapper.toResponse(citizen);
    }

    @Override
    @Transactional(readOnly = true)
    public CitizenResponse getCitizenByMobileNumber(String mobileNumber) {
        Citizen citizen = citizenRepository.findByMobileNumber(mobileNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "mobileNumber", mobileNumber));
        return citizenMapper.toResponse(citizen);
    }

    @Override
    @Transactional(readOnly = true)
    public CitizenResponse getCitizenByAadhaarNumber(String aadhaarNumber) {
        Citizen citizen = citizenRepository.findByAadhaarNumber(aadhaarNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "aadhaarNumber", aadhaarNumber));
        return citizenMapper.toResponse(citizen);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<CitizenResponse> getAllCitizens(Pageable pageable) {
        return citizenRepository.findAll(pageable)
                .map(citizenMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CitizenResponse> getCitizensByStatus(String status) {
        Citizen.CitizenStatus citizenStatus = Citizen.CitizenStatus.valueOf(status.toUpperCase());
        return citizenRepository.findByStatus(citizenStatus).stream()
                .map(citizenMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public CitizenResponse updateCitizen(UUID id, CitizenUpdateRequest request) {
        Citizen citizen = citizenRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", id));
        
        citizenMapper.updateEntityFromRequest(request, citizen);
        
        // Auto-transliterate name to Hindi if name was updated
        if (request.getFullName() != null && !request.getFullName().trim().isEmpty()) {
            String hindiName = transliterationService.transliterateName(request.getFullName());
            citizen.setFullNameHindi(hindiName);
        }
        
        Citizen updatedCitizen = citizenRepository.save(citizen);
        return citizenMapper.toResponse(updatedCitizen);
    }

    @Override
    public void deleteCitizen(UUID id) {
        Citizen citizen = citizenRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", id));
        citizenRepository.delete(citizen);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsByMobileNumber(String mobileNumber) {
        return citizenRepository.existsByMobileNumber(mobileNumber);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsByAadhaarNumber(String aadhaarNumber) {
        return citizenRepository.existsByAadhaarNumber(aadhaarNumber);
    }

    @Override
    @Transactional(readOnly = true)
    public FamilyGraphResponse getFamilyRelationships(UUID citizenId, int depth) {
        // Verify citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        List<FamilyMember> members = new ArrayList<>();
        List<FamilyRelationship> relationships = new ArrayList<>();

        // Try Neo4j first (preferred method for graph relationships)
        try {
            // Use citizen ID (UUID) or Aadhaar number to query Neo4j
            String identifier = citizen.getAadhaarNumber() != null && !citizen.getAadhaarNumber().isEmpty()
                    ? citizen.getAadhaarNumber()
                    : citizenId.toString();
            
            Map<String, Object> neo4jGraph = profileGraphService.getFamilyNetwork(identifier, depth);
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> nodes = (List<Map<String, Object>>) neo4jGraph.get("nodes");
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> links = (List<Map<String, Object>>) neo4jGraph.get("links");
            
            // Convert Neo4j nodes to FamilyMember DTOs
            if (nodes != null && !nodes.isEmpty()) {
                Map<Long, UUID> nodeIdToCitizenId = new HashMap<>();
                
                for (Map<String, Object> node : nodes) {
                    Long nodeId = ((Number) node.get("id")).longValue();
                    String grIdStr = (String) node.get("gr_id");
                    String name = (String) node.get("name");
                    Number ageNum = (Number) node.get("age");
                    String gender = (String) node.get("gender");
                    
                    // Try to find citizen by gr_id or by name/aadhaar
                    UUID memberCitizenId = null;
                    if (grIdStr != null) {
                        try {
                            memberCitizenId = UUID.fromString(grIdStr);
                        } catch (IllegalArgumentException e) {
                            // gr_id is not a UUID, try to find by other means
                        }
                    }
                    
                    // If gr_id matches citizenId, use it; otherwise try to find by name
                    if (memberCitizenId == null || !memberCitizenId.equals(citizenId)) {
                        // Try to find citizen by name (fallback)
                        if (name != null && !name.equals("Unknown")) {
                            // For now, use gr_id as UUID if available, otherwise generate a placeholder
                            // In production, you'd query PostgreSQL to map gr_id to citizen_id
                            if (grIdStr != null) {
                                try {
                                    memberCitizenId = UUID.fromString(grIdStr);
                                } catch (Exception e) {
                                    // If gr_id is not UUID, we'll need to look it up
                                    // For now, skip this node or use a placeholder
                                    continue;
                                }
                            } else {
                                continue; // Skip nodes without gr_id
                            }
                        }
                    }
                    
                    if (memberCitizenId == null) {
                        memberCitizenId = UUID.fromString(grIdStr); // Use gr_id as UUID
                    }
                    
                    nodeIdToCitizenId.put(nodeId, memberCitizenId);
                    
                    // Determine relationship type
                    String relationship = "Family Member";
                    if (memberCitizenId.equals(citizenId)) {
                        relationship = "Self";
                    }
                    
                    // Try to get Hindi name from database if available
                    String nameHindi = null;
                    try {
                        Optional<Citizen> memberCitizenOpt = citizenRepository.findById(memberCitizenId);
                        if (memberCitizenOpt.isPresent()) {
                            nameHindi = memberCitizenOpt.get().getFullNameHindi();
                        }
                    } catch (Exception e) {
                        // Ignore if can't fetch
                    }
                    
                    FamilyMember member = FamilyMember.builder()
                            .id(memberCitizenId)
                            .name(name != null ? name : "Unknown")
                            .nameHindi(nameHindi)
                            .relationship(relationship)
                            .age(ageNum != null ? ageNum.intValue() : null)
                            .gender(gender)
                            .confidence(85) // Default confidence for Neo4j relationships
                            .build();
                    members.add(member);
                }
                
                // Convert Neo4j links to FamilyRelationship DTOs
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
                    
                    if (fromId != null && toId != null) {
                        // Map Neo4j relationship types to our format
                        String relationship = relType;
                        if (relType.equals("CHILD")) {
                            relationship = "Child";
                        } else if (relType.equals("PARENT")) {
                            relationship = "Parent";
                        } else if (relType.equals("SPOUSE")) {
                            relationship = "Spouse";
                        } else if (relType.equals("SIBLING")) {
                            relationship = "Sibling";
                        }
                        
                        FamilyRelationship rel = FamilyRelationship.builder()
                                .from(fromId)
                                .to(toId)
                                .relationship(relationship)
                                .confidence(85) // Default confidence
                                .build();
                        relationships.add(rel);
                    }
                }
                
                // If Neo4j returned relationships or multiple members, sync to cache and return it
                // Only return early if we have actual relationships or more than just the user
                if (!relationships.isEmpty() || (members.size() > 1)) {
                    // Sync to PostgreSQL cache for future use (async, don't block)
                    try {
                        familyRelationshipSyncService.syncFromNeo4j(citizenId, depth);
                    } catch (Exception syncError) {
                        // Log but don't fail the request
                        System.err.println("Failed to sync Neo4j results to cache: " + syncError.getMessage());
                    }
                    
                    return FamilyGraphResponse.builder()
                            .members(members)
                            .relationships(relationships)
                            .build();
                } else {
                    // Neo4j returned only the user with no relationships, continue to fallback strategies
                    System.out.println("Neo4j returned only user with no relationships, trying fallback strategies");
                    members.clear(); // Clear to allow fallback to populate
                    relationships.clear();
                }
            }
        } catch (Exception e) {
            // Log error but continue to fallback
            System.err.println("Neo4j query failed, trying PostgreSQL cache: " + e.getMessage());
        }
        
        // Strategy 2: Try PostgreSQL cache (synced from Neo4j)
        try {
            LocalDateTime now = LocalDateTime.now();
            List<FamilyRelationshipCache> cached = cacheRepository.findFreshByCitizenId(citizenId, now);
            
            if (cached != null && !cached.isEmpty()) {
                // Convert cache to DTOs
                Set<UUID> memberIds = new HashSet<>();
                memberIds.add(citizenId); // Add self
                
                for (FamilyRelationshipCache cache : cached) {
                    if (cache.getRelatedCitizen() != null) {
                        memberIds.add(cache.getRelatedCitizen().getId());
                        
                        FamilyRelationship rel = FamilyRelationship.builder()
                            .from(citizenId)
                            .to(cache.getRelatedCitizen().getId())
                            .relationship(cache.getRelationshipLabel() != null ? 
                                cache.getRelationshipLabel() : cache.getRelationshipType())
                            .confidence(cache.getConfidence())
                            .build();
                        relationships.add(rel);
                    }
                }
                
                // Load member details
                for (UUID memberId : memberIds) {
                    Optional<Citizen> memberOpt = citizenRepository.findById(memberId);
                    if (memberOpt.isPresent()) {
                        Citizen c = memberOpt.get();
                        FamilyMember member = FamilyMember.builder()
                            .id(c.getId())
                            .name(c.getFullName() != null ? c.getFullName() : "Unknown")
                            .nameHindi(c.getFullNameHindi())
                            .relationship(memberId.equals(citizenId) ? "Self" : "Family Member")
                            .age(c.getDateOfBirth() != null ? 
                                Period.between(c.getDateOfBirth(), LocalDate.now()).getYears() : null)
                            .gender(c.getGender())
                            .confidence(100)
                            .aadhaarNumber(c.getAadhaarNumber())
                            .mobileNumber(c.getMobileNumber())
                            .dateOfBirth(c.getDateOfBirth())
                            .build();
                        members.add(member);
                    }
                }
                
                if (!members.isEmpty()) {
                    System.out.println("Loaded " + relationships.size() + 
                        " relationships from PostgreSQL cache for citizen: " + citizenId);
                    return FamilyGraphResponse.builder()
                        .members(members)
                        .relationships(relationships)
                        .build();
                }
            }
        } catch (Exception e) {
            // Log error but continue to fallback
            System.err.println("PostgreSQL cache query failed, falling back to address matching: " + e.getMessage());
        }
        
        // Strategy 3: Fallback to PostgreSQL-based address matching if Neo4j and cache fail
        System.out.println("Starting address matching fallback for citizen: " + citizenId);
        System.out.println("Citizen address: " + citizen.getAddressLine1() + ", city: " + citizen.getCity() + ", district: " + citizen.getDistrict());
        
        // Add the current citizen as the root
        FamilyMember self = FamilyMember.builder()
                .id(citizen.getId())
                .name(citizen.getFullName() != null ? citizen.getFullName() : "You")
                .nameHindi(citizen.getFullNameHindi())
                .relationship("Self")
                .age(citizen.getDateOfBirth() != null ? 
                     java.time.Period.between(citizen.getDateOfBirth(), LocalDate.now()).getYears() : null)
                .gender(citizen.getGender())
                .confidence(100)
                .aadhaarNumber(citizen.getAadhaarNumber())
                .mobileNumber(citizen.getMobileNumber())
                .dateOfBirth(citizen.getDateOfBirth())
                .build();
        members.add(self);

        // Try to find actual family members from database
        // Use strict criteria to find realistic family relationships (max 8 members)
        List<Citizen> potentialFamily = new ArrayList<>();
        if (depth >= 1) {
            // Strategy 1: Try exact address match (most strict) - ONLY use this for realistic results
            if (citizen.getAddressLine1() != null && !citizen.getAddressLine1().isEmpty()) {
                List<Citizen> addressMatches = citizenRepository.findByAddressLine1(citizen.getAddressLine1());
                System.out.println("Address match found " + addressMatches.size() + " citizens with same address");
                
                // Filter to only include realistic family members:
                // - Must have gender and date of birth for age/gender matching
                // - Limit to max 15 candidates for further filtering
                potentialFamily = addressMatches.stream()
                        .filter(c -> !c.getId().equals(citizen.getId()))
                        .filter(c -> c.getGender() != null) // Must have gender
                        .filter(c -> c.getDateOfBirth() != null) // Must have DOB for age calculation
                        .limit(15) // Limit candidates early
                        .collect(java.util.stream.Collectors.toList());
                
                System.out.println("After filtering (gender, DOB, limit 15): " + potentialFamily.size() + " candidates");
            }
            
            // Strategy 2: Only use city/district if exact address returns very few results (0-2)
            // This prevents matching hundreds of people from the same city
            if (potentialFamily.size() <= 2) {
                if (citizen.getCity() != null && !citizen.getCity().isEmpty()) {
                    List<Citizen> cityMatches = citizenRepository.findByCity(citizen.getCity());
                    // Filter out the current citizen and apply strict criteria
                    List<Citizen> filteredCity = cityMatches.stream()
                            .filter(c -> !c.getId().equals(citizen.getId()))
                            .filter(c -> c.getGender() != null)
                            .filter(c -> c.getDateOfBirth() != null)
                            .limit(10) // Limit city matches
                            .collect(java.util.stream.Collectors.toList());
                    
                    if (potentialFamily.isEmpty()) {
                        potentialFamily = filteredCity;
                        System.out.println("City match found " + filteredCity.size() + " citizens in same city (after filtering)");
                    }
                }
            }
            
            // Strategy 3: Only use district if we still have very few results (0-1)
            // This is the last resort and should rarely be used
            if (potentialFamily.size() <= 1 && citizen.getDistrict() != null && !citizen.getDistrict().isEmpty()) {
                List<Citizen> districtMatches = citizenRepository.findByDistrict(citizen.getDistrict());
                List<Citizen> filteredDistrict = districtMatches.stream()
                        .filter(c -> !c.getId().equals(citizen.getId()))
                        .filter(c -> c.getGender() != null)
                        .filter(c -> c.getDateOfBirth() != null)
                        .limit(8) // Very limited district matches
                        .collect(java.util.stream.Collectors.toList());
                
                if (potentialFamily.isEmpty()) {
                    potentialFamily = filteredDistrict;
                    System.out.println("District match found " + filteredDistrict.size() + " citizens in same district (after filtering)");
                }
            }
            
            // Final limit: Maximum 15 candidates for processing (will be further filtered)
            List<Citizen> limitedFamily = potentialFamily.stream()
                    .limit(15)
                    .collect(java.util.stream.Collectors.toList());
            
            // Filter to find potential spouse (similar age, opposite gender)
            // Use address matching with confidence levels: exact address = high, city = medium, district = low
            boolean spouseFound = false;
            System.out.println("Current citizen: " + citizen.getFullName() + ", Gender: " + citizen.getGender() + ", Age: " + 
                (citizen.getDateOfBirth() != null ? java.time.Period.between(citizen.getDateOfBirth(), LocalDate.now()).getYears() : "unknown"));
            
            for (Citizen potentialSpouse : limitedFamily) {
                if (potentialSpouse.getId().equals(citizen.getId())) {
                    System.out.println("Skipping self: " + potentialSpouse.getFullName());
                    continue;
                }
                
                // Check address match level for confidence scoring
                boolean exactSameAddress = citizen.getAddressLine1() != null && 
                                         !citizen.getAddressLine1().isEmpty() &&
                                         citizen.getAddressLine1().equals(potentialSpouse.getAddressLine1());
                boolean sameCity = citizen.getCity() != null && 
                                !citizen.getCity().isEmpty() &&
                                citizen.getCity().equals(potentialSpouse.getCity());
                boolean sameDistrict = citizen.getDistrict() != null && 
                                     !citizen.getDistrict().isEmpty() &&
                                     citizen.getDistrict().equals(potentialSpouse.getDistrict());
                
                // Only proceed if there's some location match
                if ((exactSameAddress || sameCity || sameDistrict) && 
                    potentialSpouse.getGender() != null && citizen.getGender() != null) {
                    // Potential spouse: opposite gender, similar age
                    boolean oppositeGender = (!citizen.getGender().equals(potentialSpouse.getGender()));
                    boolean similarAge = true;
                    int ageDiff = 0;
                    if (citizen.getDateOfBirth() != null && potentialSpouse.getDateOfBirth() != null) {
                        ageDiff = Math.abs(java.time.Period.between(citizen.getDateOfBirth(), potentialSpouse.getDateOfBirth()).getYears());
                        similarAge = ageDiff <= 15; // Within 15 years (relaxed from 10)
                    }
                    
                    System.out.println("Checking: " + potentialSpouse.getFullName() + 
                        ", Gender: " + potentialSpouse.getGender() + 
                        ", Age: " + (potentialSpouse.getDateOfBirth() != null ? 
                            java.time.Period.between(potentialSpouse.getDateOfBirth(), LocalDate.now()).getYears() : "unknown") +
                        ", Opposite gender: " + oppositeGender + 
                        ", Age diff: " + ageDiff + 
                        ", Similar age: " + similarAge);
                    
                    if (oppositeGender && similarAge) {
                        // Calculate confidence based on match level
                        int confidence = exactSameAddress ? 85 : (sameCity ? 70 : 60);
                        System.out.println("Found potential spouse: " + potentialSpouse.getFullName() + " (confidence: " + confidence + "%)");
                        spouseFound = true;
                        
                        FamilyMember spouse = FamilyMember.builder()
                                .id(potentialSpouse.getId())
                                .name(potentialSpouse.getFullName() != null ? potentialSpouse.getFullName() : "Family Member")
                                .nameHindi(potentialSpouse.getFullNameHindi())
                                .relationship("Spouse")
                                .age(potentialSpouse.getDateOfBirth() != null ? 
                                     java.time.Period.between(potentialSpouse.getDateOfBirth(), LocalDate.now()).getYears() : null)
                                .gender(potentialSpouse.getGender())
                                .confidence(confidence)
                                .aadhaarNumber(potentialSpouse.getAadhaarNumber())
                                .mobileNumber(potentialSpouse.getMobileNumber())
                                .dateOfBirth(potentialSpouse.getDateOfBirth())
                                .build();
                        members.add(spouse);
                        relationships.add(FamilyRelationship.builder()
                                .from(citizen.getId())
                                .to(potentialSpouse.getId())
                                .relationship("Spouse")
                                .confidence(confidence)
                                .build());
                        
                        // Look for children (younger than both parents)
                        // Use location matching with confidence levels
                        // Limit total family size to 8 (self + spouse + max 6 children)
                        if (depth >= 2) {
                            int childCount = 0;
                            int maxChildren = 6; // Max 6 children to keep total under 8 (self + spouse + 6 children)
                            for (Citizen potentialChild : limitedFamily) {
                                if (potentialChild.getId().equals(citizen.getId()) || 
                                    potentialChild.getId().equals(potentialSpouse.getId())) continue;
                                
                                // Check if we've reached the total member limit (8)
                                if (members.size() >= 8) {
                                    System.out.println("Reached maximum family members limit (8), stopping child detection");
                                    break;
                                }
                                
                                // Check location match for confidence - ONLY use exact address for children (more realistic)
                                boolean exactSameAddressChild = citizen.getAddressLine1() != null && 
                                                               !citizen.getAddressLine1().isEmpty() &&
                                                               citizen.getAddressLine1().equals(potentialChild.getAddressLine1());
                                
                                // Only proceed if exact address match (more realistic for children)
                                if (exactSameAddressChild && potentialChild.getDateOfBirth() != null) {
                                    int childAge = java.time.Period.between(potentialChild.getDateOfBirth(), LocalDate.now()).getYears();
                                    int parentAge = citizen.getDateOfBirth() != null ? 
                                                  java.time.Period.between(citizen.getDateOfBirth(), LocalDate.now()).getYears() : 0;
                                    
                                    // At least 15 years younger (relaxed from strict)
                                    if (childAge < parentAge - 15 && childCount < maxChildren) { // Limit to maxChildren
                                        // Calculate confidence - exact address match for children
                                        int childConfidence = 80;
                                        
                                        FamilyMember child = FamilyMember.builder()
                                                .id(potentialChild.getId())
                                                .name(potentialChild.getFullName() != null ? potentialChild.getFullName() : "Family Member")
                                                .nameHindi(potentialChild.getFullNameHindi())
                                                .relationship("Child")
                                                .age(childAge)
                                                .gender(potentialChild.getGender())
                                                .confidence(childConfidence)
                                                .aadhaarNumber(potentialChild.getAadhaarNumber())
                                                .mobileNumber(potentialChild.getMobileNumber())
                                                .dateOfBirth(potentialChild.getDateOfBirth())
                                                .build();
                                        members.add(child);
                                        relationships.add(FamilyRelationship.builder()
                                                .from(citizen.getId())
                                                .to(potentialChild.getId())
                                                .relationship("Parent")
                                                .confidence(childConfidence)
                                                .build());
                                        relationships.add(FamilyRelationship.builder()
                                                .from(potentialSpouse.getId())
                                                .to(potentialChild.getId())
                                                .relationship("Parent")
                                                .confidence(childConfidence)
                                                .build());
                                        childCount++;
                                    }
                                }
                            }
                        }
                        break; // Only add first potential spouse
                    } else {
                        System.out.println("Rejected as spouse: " + potentialSpouse.getFullName() + 
                            " (oppositeGender: " + oppositeGender + ", similarAge: " + similarAge + ")");
                    }
                } else {
                    System.out.println("Skipping (no location match or missing gender): " + potentialSpouse.getFullName());
                }
            }
            
            // If no spouse found, add family members as "Family Member" relationships
            // But limit total family members to 8 (including spouse and children)
            if (!spouseFound && !limitedFamily.isEmpty()) {
                System.out.println("No spouse found, adding family members as generic family (max 8 total)");
                int addedCount = members.size() - 1; // Current members (excluding self)
                int maxTotalMembers = 8; // Maximum total family members including self
                
                for (Citizen familyMember : limitedFamily) {
                    if (familyMember.getId().equals(citizen.getId())) continue;
                    if (addedCount >= maxTotalMembers - 1) { // -1 for self
                        System.out.println("Reached maximum family members limit (" + maxTotalMembers + "), stopping");
                        break;
                    }
                    
                    // Only add if exact address match (more realistic)
                    boolean exactSameAddress = citizen.getAddressLine1() != null && 
                                             !citizen.getAddressLine1().isEmpty() &&
                                             citizen.getAddressLine1().equals(familyMember.getAddressLine1());
                    
                    // For city/district matches, apply stricter age-based filtering
                    boolean sameCity = !exactSameAddress && citizen.getCity() != null && 
                                    !citizen.getCity().isEmpty() &&
                                    citizen.getCity().equals(familyMember.getCity());
                    boolean sameDistrict = !exactSameAddress && !sameCity && citizen.getDistrict() != null && 
                                         !citizen.getDistrict().isEmpty() &&
                                         citizen.getDistrict().equals(familyMember.getDistrict());
                    
                    // For city/district matches, require reasonable age difference (family-like)
                    boolean reasonableAgeDiff = true;
                    if ((sameCity || sameDistrict) && citizen.getDateOfBirth() != null && familyMember.getDateOfBirth() != null) {
                        int ageDiff = Math.abs(java.time.Period.between(citizen.getDateOfBirth(), familyMember.getDateOfBirth()).getYears());
                        // For city/district, require age difference to be reasonable (not random people)
                        // Either similar age (siblings/spouse) or significant difference (parent/child)
                        reasonableAgeDiff = ageDiff <= 20 || ageDiff >= 15;
                    }
                    
                    if ((exactSameAddress || (sameCity && reasonableAgeDiff) || (sameDistrict && reasonableAgeDiff))) {
                        int confidence = exactSameAddress ? 75 : (sameCity ? 60 : 50);
                        
                        FamilyMember member = FamilyMember.builder()
                                .id(familyMember.getId())
                                .name(familyMember.getFullName() != null ? familyMember.getFullName() : "Family Member")
                                .nameHindi(familyMember.getFullNameHindi())
                                .relationship("Family Member")
                                .age(familyMember.getDateOfBirth() != null ? 
                                     java.time.Period.between(familyMember.getDateOfBirth(), LocalDate.now()).getYears() : null)
                                .gender(familyMember.getGender())
                                .confidence(confidence)
                                .aadhaarNumber(familyMember.getAadhaarNumber())
                                .mobileNumber(familyMember.getMobileNumber())
                                .dateOfBirth(familyMember.getDateOfBirth())
                                .build();
                        members.add(member);
                        relationships.add(FamilyRelationship.builder()
                                .from(citizen.getId())
                                .to(familyMember.getId())
                                .relationship("Family Member")
                                .confidence(confidence)
                                .build());
                        addedCount++;
                        System.out.println("Added family member: " + familyMember.getFullName() + " (confidence: " + confidence + "%, total: " + (addedCount + 1) + ")");
                    }
                }
            }
            
            // Enforce maximum limit: If we have more than 8 members (including self), trim to 8
            if (members.size() > 8) {
                System.out.println("Warning: Found " + members.size() + " family members, limiting to 8");
                // Keep self and first 7 family members (sorted by confidence if possible)
                List<FamilyMember> sortedMembers = new ArrayList<>(members);
                sortedMembers.sort((a, b) -> {
                    // Keep self first
                    if (a.getId().equals(citizen.getId())) return -1;
                    if (b.getId().equals(citizen.getId())) return 1;
                    // Sort by confidence descending
                    int confA = a.getConfidence() != null ? a.getConfidence() : 0;
                    int confB = b.getConfidence() != null ? b.getConfidence() : 0;
                    return Integer.compare(confB, confA);
                });
                
                members.clear();
                members.addAll(sortedMembers.subList(0, Math.min(8, sortedMembers.size())));
                
                // Also trim relationships to match
                Set<UUID> keptMemberIds = members.stream()
                        .map(FamilyMember::getId)
                        .collect(java.util.stream.Collectors.toSet());
                relationships.removeIf(rel -> 
                    !keptMemberIds.contains(rel.getFrom()) || !keptMemberIds.contains(rel.getTo())
                );
            }
        }
        
        // If no real family members found, don't add mock data
        // Mock data with random UUIDs causes issues when users try to view profiles
        // Instead, return only real family members found in the database
        System.out.println("Final result: " + members.size() + " members, " + relationships.size() + " relationships");

        return FamilyGraphResponse.builder()
                .members(members)
                .relationships(relationships)
                .build();
    }

    @Override
    public int updateFamilyRelationships(UUID citizenId, BulkUpdateFamilyRelationshipsRequest request) {
        // Verify citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        // Delete existing relationships for this citizen (to replace with new ones)
        cacheRepository.deleteByCitizenId(citizenId);

        int savedCount = 0;
        LocalDateTime now = LocalDateTime.now();

        for (UpdateFamilyRelationshipRequest relRequest : request.getRelationships()) {
            // Find related citizen by Aadhaar number
            Optional<Citizen> relatedCitizenOpt = citizenRepository.findByAadhaarNumber(relRequest.getRelatedCitizenAadhaar());
            
            if (relatedCitizenOpt.isEmpty()) {
                // Skip if related citizen not found
                continue;
            }

            Citizen relatedCitizen = relatedCitizenOpt.get();

            // Skip self-relationships
            if (citizen.getId().equals(relatedCitizen.getId())) {
                continue;
            }

            // Create or update relationship cache entry
            FamilyRelationshipCache cache = FamilyRelationshipCache.builder()
                    .citizen(citizen)
                    .relatedCitizen(relatedCitizen)
                    .relationshipType(relRequest.getRelationshipType().toUpperCase())
                    .relationshipLabel(relRequest.getRelationshipLabel())
                    .confidence(relRequest.getConfidence())
                    .isVerified(true) // Mark as verified since it's manual entry
                    .source("MANUAL") // Source is manual/user-verified
                    .depth(1) // Direct relationships
                    .syncedAt(now)
                    .expiresAt(null) // Manual entries don't expire
                    .build();

            try {
                cacheRepository.save(cache);
                savedCount++;
            } catch (Exception e) {
                // Log error but continue with other relationships
                System.err.println("Failed to save relationship: " + e.getMessage());
            }
        }

        return savedCount;
    }

    @Override
    @Transactional(readOnly = true)
    public List<ConsentPreferenceDto> getConsentPreferences(UUID citizenId) {
        // Verify citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        // Return default consent preferences
        // In a real implementation, these would be stored in a database table
        List<ConsentPreferenceDto> preferences = new ArrayList<>();
        preferences.add(ConsentPreferenceDto.builder()
                .field("fullName")
                .fieldLabel("Full Name")
                .enabled(true)
                .source("UIDAI")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("dateOfBirth")
                .fieldLabel("Date of Birth")
                .enabled(true)
                .source("UIDAI")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("gender")
                .fieldLabel("Gender")
                .enabled(true)
                .source("UIDAI")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("addressLine1")
                .fieldLabel("Address")
                .enabled(false)
                .source("Manual")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("email")
                .fieldLabel("Email")
                .enabled(false)
                .source("Manual")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("mobileNumber")
                .fieldLabel("Mobile Number")
                .enabled(true)
                .source("UIDAI")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("incomeBand")
                .fieldLabel("Income Band")
                .enabled(false)
                .source("Inferred")
                .build());
        preferences.add(ConsentPreferenceDto.builder()
                .field("vulnerabilityCategory")
                .fieldLabel("Vulnerability Category")
                .enabled(false)
                .source("Inferred")
                .build());

        return preferences;
    }

    @Override
    @Transactional
    public List<ConsentPreferenceDto> updateConsentPreferences(UUID citizenId, List<ConsentPreferenceDto> preferences) {
        // Verify citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        // In a real implementation, these would be saved to a database table
        // For now, we just validate and return the preferences
        if (preferences == null || preferences.isEmpty()) {
            throw new BadRequestException("Consent preferences cannot be empty");
        }

        // Validate all preferences have required fields
        for (ConsentPreferenceDto pref : preferences) {
            if (pref.getField() == null || pref.getField().isEmpty()) {
                throw new BadRequestException("Consent preference field is required");
            }
            if (pref.getEnabled() == null) {
                throw new BadRequestException("Consent preference enabled status is required");
            }
        }

        // Return the updated preferences
        // In a real implementation, save to database and return saved preferences
        return preferences;
    }
}

