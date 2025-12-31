package com.smart.platform.nudging.dto;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * DTO for nudge scheduling response
 */
public class NudgeResponse {
    private boolean success;
    private String nudgeId;
    private String familyId;
    private String actionType;
    private String urgency;
    private String scheduledChannel;
    private LocalDateTime scheduledTime;
    private String timeWindow;
    private String templateId;
    private String personalizedContent;
    private Double channelConfidence;
    private Double timeConfidence;
    private String contentStrategy;
    private Map<String, Object> fatigueStatus;
    private String reason;
    private String error;

    // Getters and Setters
    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getNudgeId() {
        return nudgeId;
    }

    public void setNudgeId(String nudgeId) {
        this.nudgeId = nudgeId;
    }

    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getActionType() {
        return actionType;
    }

    public void setActionType(String actionType) {
        this.actionType = actionType;
    }

    public String getUrgency() {
        return urgency;
    }

    public void setUrgency(String urgency) {
        this.urgency = urgency;
    }

    public String getScheduledChannel() {
        return scheduledChannel;
    }

    public void setScheduledChannel(String scheduledChannel) {
        this.scheduledChannel = scheduledChannel;
    }

    public LocalDateTime getScheduledTime() {
        return scheduledTime;
    }

    public void setScheduledTime(LocalDateTime scheduledTime) {
        this.scheduledTime = scheduledTime;
    }

    public String getTimeWindow() {
        return timeWindow;
    }

    public void setTimeWindow(String timeWindow) {
        this.timeWindow = timeWindow;
    }

    public String getTemplateId() {
        return templateId;
    }

    public void setTemplateId(String templateId) {
        this.templateId = templateId;
    }

    public String getPersonalizedContent() {
        return personalizedContent;
    }

    public void setPersonalizedContent(String personalizedContent) {
        this.personalizedContent = personalizedContent;
    }

    public Double getChannelConfidence() {
        return channelConfidence;
    }

    public void setChannelConfidence(Double channelConfidence) {
        this.channelConfidence = channelConfidence;
    }

    public Double getTimeConfidence() {
        return timeConfidence;
    }

    public void setTimeConfidence(Double timeConfidence) {
        this.timeConfidence = timeConfidence;
    }

    public String getContentStrategy() {
        return contentStrategy;
    }

    public void setContentStrategy(String contentStrategy) {
        this.contentStrategy = contentStrategy;
    }

    public Map<String, Object> getFatigueStatus() {
        return fatigueStatus;
    }

    public void setFatigueStatus(Map<String, Object> fatigueStatus) {
        this.fatigueStatus = fatigueStatus;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

