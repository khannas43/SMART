package com.smart.platform.aiml.eligibility.dto;

import java.util.Map;
import java.util.UUID;

/**
 * DTO for candidate in departmental worklist
 */
public class Candidate {
    private UUID familyId;
    private String schemeCode;
    private Double eligibilityScore;
    private Double priorityScore;
    private String eligibilityStatus;
    private String district;
    private String block;
    private String village;
    private String name;
    private String mobile;

    // Static factory method
    public static Candidate fromMap(Map<String, Object> map) {
        Candidate candidate = new Candidate();
        
        Object familyId = map.get("family_id");
        if (familyId != null) {
            candidate.setFamilyId(UUID.fromString(familyId.toString()));
        }
        
        candidate.setSchemeCode((String) map.get("scheme_code"));
        
        Object eligibilityScore = map.get("eligibility_score");
        if (eligibilityScore != null) {
            candidate.setEligibilityScore(eligibilityScore instanceof Number ? 
                ((Number) eligibilityScore).doubleValue() : Double.parseDouble(eligibilityScore.toString()));
        }
        
        Object priorityScore = map.get("priority_score");
        if (priorityScore != null) {
            candidate.setPriorityScore(priorityScore instanceof Number ? 
                ((Number) priorityScore).doubleValue() : Double.parseDouble(priorityScore.toString()));
        }
        
        candidate.setEligibilityStatus((String) map.get("eligibility_status"));
        candidate.setDistrict((String) map.get("district"));
        candidate.setBlock((String) map.get("block"));
        candidate.setVillage((String) map.get("village"));
        candidate.setName((String) map.get("name"));
        candidate.setMobile((String) map.get("mobile"));
        
        return candidate;
    }

    // Getters and Setters
    public UUID getFamilyId() {
        return familyId;
    }

    public void setFamilyId(UUID familyId) {
        this.familyId = familyId;
    }

    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public Double getEligibilityScore() {
        return eligibilityScore;
    }

    public void setEligibilityScore(Double eligibilityScore) {
        this.eligibilityScore = eligibilityScore;
    }

    public Double getPriorityScore() {
        return priorityScore;
    }

    public void setPriorityScore(Double priorityScore) {
        this.priorityScore = priorityScore;
    }

    public String getEligibilityStatus() {
        return eligibilityStatus;
    }

    public void setEligibilityStatus(String eligibilityStatus) {
        this.eligibilityStatus = eligibilityStatus;
    }

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public String getBlock() {
        return block;
    }

    public void setBlock(String block) {
        this.block = block;
    }

    public String getVillage() {
        return village;
    }

    public void setVillage(String village) {
        this.village = village;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getMobile() {
        return mobile;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }
}

