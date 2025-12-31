package com.smart.platform.decision.dto;

/**
 * Request DTO for overriding a decision
 */
public class OverrideRequest {
    private Integer decisionId;
    private String overrideDecisionType;  // OFFICER_APPROVED, OFFICER_REJECTED
    private String overrideReason;  // Mandatory justification
    private String officerId;
    private String officerName;
    private String officerRole;

    // Getters and Setters
    public Integer getDecisionId() {
        return decisionId;
    }

    public void setDecisionId(Integer decisionId) {
        this.decisionId = decisionId;
    }

    public String getOverrideDecisionType() {
        return overrideDecisionType;
    }

    public void setOverrideDecisionType(String overrideDecisionType) {
        this.overrideDecisionType = overrideDecisionType;
    }

    public String getOverrideReason() {
        return overrideReason;
    }

    public void setOverrideReason(String overrideReason) {
        this.overrideReason = overrideReason;
    }

    public String getOfficerId() {
        return officerId;
    }

    public void setOfficerId(String officerId) {
        this.officerId = officerId;
    }

    public String getOfficerName() {
        return officerName;
    }

    public void setOfficerName(String officerName) {
        this.officerName = officerName;
    }

    public String getOfficerRole() {
        return officerRole;
    }

    public void setOfficerRole(String officerRole) {
        this.officerRole = officerRole;
    }
}

