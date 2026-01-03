package com.smart.platform.aiml.intimation.dto;

/**
 * DTO for campaign details
 */
public class CampaignDetails {
    private Integer campaignId;
    private String campaignName;
    private String schemeCode;
    private String campaignType;  // INITIAL, RETRY, REMINDER
    private String status;  // DRAFT, ACTIVE, PAUSED, COMPLETED, CANCELLED
    private Double eligibilityScoreThreshold;
    private Integer totalCandidates;
    private String scheduledAt;
    private String createdAt;
    private String error;

    // Getters and Setters
    public Integer getCampaignId() {
        return campaignId;
    }

    public void setCampaignId(Integer campaignId) {
        this.campaignId = campaignId;
    }

    public String getCampaignName() {
        return campaignName;
    }

    public void setCampaignName(String campaignName) {
        this.campaignName = campaignName;
    }

    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public String getCampaignType() {
        return campaignType;
    }

    public void setCampaignType(String campaignType) {
        this.campaignType = campaignType;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Double getEligibilityScoreThreshold() {
        return eligibilityScoreThreshold;
    }

    public void setEligibilityScoreThreshold(Double eligibilityScoreThreshold) {
        this.eligibilityScoreThreshold = eligibilityScoreThreshold;
    }

    public Integer getTotalCandidates() {
        return totalCandidates;
    }

    public void setTotalCandidates(Integer totalCandidates) {
        this.totalCandidates = totalCandidates;
    }

    public String getScheduledAt() {
        return scheduledAt;
    }

    public void setScheduledAt(String scheduledAt) {
        this.scheduledAt = scheduledAt;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

