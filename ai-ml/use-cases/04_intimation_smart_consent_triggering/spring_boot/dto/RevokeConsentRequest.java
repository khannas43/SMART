package com.smart.platform.aiml.intimation.dto;

/**
 * Request DTO for revoking consent
 */
public class RevokeConsentRequest {
    private Integer consentId;
    private String revocationReason;  // user_request, expired, policy_change, etc.

    // Getters and Setters
    public Integer getConsentId() {
        return consentId;
    }

    public void setConsentId(Integer consentId) {
        this.consentId = consentId;
    }

    public String getRevocationReason() {
        return revocationReason;
    }

    public void setRevocationReason(String revocationReason) {
        this.revocationReason = revocationReason;
    }
}

