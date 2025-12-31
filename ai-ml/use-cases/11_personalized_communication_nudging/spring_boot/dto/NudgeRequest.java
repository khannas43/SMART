package com.smart.platform.nudging.dto;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * DTO for nudge scheduling request
 */
public class NudgeRequest {
    private String actionType;
    private String familyId;
    private String urgency;
    private LocalDateTime expiryDate;
    private Map<String, Object> actionContext;
    private String scheduledBy;

    // Getters and Setters
    public String getActionType() {
        return actionType;
    }

    public void setActionType(String actionType) {
        this.actionType = actionType;
    }

    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getUrgency() {
        return urgency;
    }

    public void setUrgency(String urgency) {
        this.urgency = urgency;
    }

    public LocalDateTime getExpiryDate() {
        return expiryDate;
    }

    public void setExpiryDate(LocalDateTime expiryDate) {
        this.expiryDate = expiryDate;
    }

    public Map<String, Object> getActionContext() {
        return actionContext;
    }

    public void setActionContext(Map<String, Object> actionContext) {
        this.actionContext = actionContext;
    }

    public String getScheduledBy() {
        return scheduledBy;
    }

    public void setScheduledBy(String scheduledBy) {
        this.scheduledBy = scheduledBy;
    }
}

