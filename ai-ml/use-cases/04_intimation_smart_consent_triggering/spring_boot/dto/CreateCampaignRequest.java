package com.smart.platform.aiml.intimation.dto;

import java.util.List;

/**
 * Request DTO for creating campaign
 */
public class CreateCampaignRequest {
    private String campaignName;
    private String schemeCode;
    private String campaignType;  // INITIAL, RETRY, REMINDER
    private Double eligibilityScoreThreshold;
    private List<String> targetDistricts;
    private String scheduledAt;  // ISO 8601 datetime string

    // Getters and Setters
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

    public Double getEligibilityScoreThreshold() {
        return eligibilityScoreThreshold;
    }

    public void setEligibilityScoreThreshold(Double eligibilityScoreThreshold) {
        this.eligibilityScoreThreshold = eligibilityScoreThreshold;
    }

    public List<String> getTargetDistricts() {
        return targetDistricts;
    }

    public void setTargetDistricts(List<String> targetDistricts) {
        this.targetDistricts = targetDistricts;
    }

    public String getScheduledAt() {
        return scheduledAt;
    }

    public void setScheduledAt(String scheduledAt) {
        this.scheduledAt = scheduledAt;
    }
}

