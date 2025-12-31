package com.smart.platform.inclusion.dto;

/**
 * Response DTO for nudge delivery
 */
public class NudgeDeliveryResponse {
    private Boolean success;
    private Integer nudgeId;
    private String deliveryStatus;  // SCHEDULED, DELIVERED, FAILED
    private String scheduledAt;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getNudgeId() {
        return nudgeId;
    }

    public void setNudgeId(Integer nudgeId) {
        this.nudgeId = nudgeId;
    }

    public String getDeliveryStatus() {
        return deliveryStatus;
    }

    public void setDeliveryStatus(String deliveryStatus) {
        this.deliveryStatus = deliveryStatus;
    }

    public String getScheduledAt() {
        return scheduledAt;
    }

    public void setScheduledAt(String scheduledAt) {
        this.scheduledAt = scheduledAt;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

