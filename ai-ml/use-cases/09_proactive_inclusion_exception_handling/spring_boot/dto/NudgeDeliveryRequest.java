package com.smart.platform.inclusion.dto;

import java.util.List;

/**
 * Request DTO for nudge delivery
 */
public class NudgeDeliveryRequest {
    private String familyId;
    private String nudgeType;  // SCHEME_SUGGESTION, ACTION_REMINDER, UPDATE_REQUEST
    private String nudgeMessage;
    private List<String> recommendedActions;
    private List<String> schemeCodes;
    private String channel;  // PORTAL, MOBILE_APP, SMS, FIELD_WORKER, EMAIL
    private String priorityLevel;  // HIGH, MEDIUM, LOW
    private String scheduledAt;  // ISO timestamp

    // Getters and Setters
    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getNudgeType() {
        return nudgeType;
    }

    public void setNudgeType(String nudgeType) {
        this.nudgeType = nudgeType;
    }

    public String getNudgeMessage() {
        return nudgeMessage;
    }

    public void setNudgeMessage(String nudgeMessage) {
        this.nudgeMessage = nudgeMessage;
    }

    public List<String> getRecommendedActions() {
        return recommendedActions;
    }

    public void setRecommendedActions(List<String> recommendedActions) {
        this.recommendedActions = recommendedActions;
    }

    public List<String> getSchemeCodes() {
        return schemeCodes;
    }

    public void setSchemeCodes(List<String> schemeCodes) {
        this.schemeCodes = schemeCodes;
    }

    public String getChannel() {
        return channel;
    }

    public void setChannel(String channel) {
        this.channel = channel;
    }

    public String getPriorityLevel() {
        return priorityLevel;
    }

    public void setPriorityLevel(String priorityLevel) {
        this.priorityLevel = priorityLevel;
    }

    public String getScheduledAt() {
        return scheduledAt;
    }

    public void setScheduledAt(String scheduledAt) {
        this.scheduledAt = scheduledAt;
    }
}

