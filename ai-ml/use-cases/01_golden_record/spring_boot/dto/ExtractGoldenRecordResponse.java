package com.smart.platform.aiml.goldenrecord.dto;

/**
 * Response DTO for extracting Golden Record
 */
public class ExtractGoldenRecordResponse {
    private Boolean success;
    private String janAadhaar;
    private Boolean extracted;
    private Boolean recordExtracted;
    private String message;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getJanAadhaar() {
        return janAadhaar;
    }

    public void setJanAadhaar(String janAadhaar) {
        this.janAadhaar = janAadhaar;
    }

    public Boolean getExtracted() {
        return extracted;
    }

    public void setExtracted(Boolean extracted) {
        this.extracted = extracted;
    }

    public Boolean getRecordExtracted() {
        return recordExtracted;
    }

    public void setRecordExtracted(Boolean recordExtracted) {
        this.recordExtracted = recordExtracted;
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

