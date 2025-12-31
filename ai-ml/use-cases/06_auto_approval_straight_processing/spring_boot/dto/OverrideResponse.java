package com.smart.platform.decision.dto;

/**
 * Response DTO for decision override
 */
public class OverrideResponse {
    private Boolean success;
    private Integer overrideId;
    private Integer decisionId;
    private String originalDecisionType;
    private String overrideDecisionType;
    private String message;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getOverrideId() {
        return overrideId;
    }

    public void setOverrideId(Integer overrideId) {
        this.overrideId = overrideId;
    }

    public Integer getDecisionId() {
        return decisionId;
    }

    public void setDecisionId(Integer decisionId) {
        this.decisionId = decisionId;
    }

    public String getOriginalDecisionType() {
        return originalDecisionType;
    }

    public void setOriginalDecisionType(String originalDecisionType) {
        this.originalDecisionType = originalDecisionType;
    }

    public String getOverrideDecisionType() {
        return overrideDecisionType;
    }

    public void setOverrideDecisionType(String overrideDecisionType) {
        this.overrideDecisionType = overrideDecisionType;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

