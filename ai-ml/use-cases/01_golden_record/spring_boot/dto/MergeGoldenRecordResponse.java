package com.smart.platform.aiml.goldenrecord.dto;

/**
 * Response DTO for merging Golden Records
 */
public class MergeGoldenRecordResponse {
    private Boolean success;
    private String targetJanAadhaar;
    private Boolean merged;
    private String message;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getTargetJanAadhaar() {
        return targetJanAadhaar;
    }

    public void setTargetJanAadhaar(String targetJanAadhaar) {
        this.targetJanAadhaar = targetJanAadhaar;
    }

    public Boolean getMerged() {
        return merged;
    }

    public void setMerged(Boolean merged) {
        this.merged = merged;
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

