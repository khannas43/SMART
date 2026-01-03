package com.smart.platform.aiml.goldenrecord.dto;

/**
 * Request DTO for extracting Golden Record
 */
public class ExtractGoldenRecordRequest {
    private String janAadhaar;
    private Boolean forceRefresh;

    // Getters and Setters
    public String getJanAadhaar() {
        return janAadhaar;
    }

    public void setJanAadhaar(String janAadhaar) {
        this.janAadhaar = janAadhaar;
    }

    public Boolean getForceRefresh() {
        return forceRefresh;
    }

    public void setForceRefresh(Boolean forceRefresh) {
        this.forceRefresh = forceRefresh;
    }
}

