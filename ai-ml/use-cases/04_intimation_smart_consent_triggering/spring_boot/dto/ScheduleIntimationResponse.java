package com.smart.platform.aiml.intimation.dto;

import java.util.List;

/**
 * Response DTO for scheduling intimation
 */
public class ScheduleIntimationResponse {
    private Boolean success;
    private String message;
    private List<CampaignSummary> campaigns;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<CampaignSummary> getCampaigns() {
        return campaigns;
    }

    public void setCampaigns(List<CampaignSummary> campaigns) {
        this.campaigns = campaigns;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

