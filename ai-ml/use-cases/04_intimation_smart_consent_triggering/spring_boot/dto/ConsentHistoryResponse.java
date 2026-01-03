package com.smart.platform.aiml.intimation.dto;

import java.util.List;

/**
 * Response DTO for consent history
 */
public class ConsentHistoryResponse {
    private Boolean success;
    private String familyId;
    private List<ConsentRecord> history;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public List<ConsentRecord> getHistory() {
        return history;
    }

    public void setHistory(List<ConsentRecord> history) {
        this.history = history;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    /**
     * Nested DTO for consent record
     */
    public static class ConsentRecord {
        private Integer consentId;
        private String schemeCode;
        private String status;  // given, rejected, revoked, expired, pending
        private String consentType;  // soft, strong
        private String consentMethod;  // click, tap, otp, e_sign, offline
        private String channel;  // sms, mobile_app, web, whatsapp, ivr, offline
        private String consentDate;
        private String validUntil;

        // Getters and Setters
        public Integer getConsentId() {
            return consentId;
        }

        public void setConsentId(Integer consentId) {
            this.consentId = consentId;
        }

        public String getSchemeCode() {
            return schemeCode;
        }

        public void setSchemeCode(String schemeCode) {
            this.schemeCode = schemeCode;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public String getConsentType() {
            return consentType;
        }

        public void setConsentType(String consentType) {
            this.consentType = consentType;
        }

        public String getConsentMethod() {
            return consentMethod;
        }

        public void setConsentMethod(String consentMethod) {
            this.consentMethod = consentMethod;
        }

        public String getChannel() {
            return channel;
        }

        public void setChannel(String channel) {
            this.channel = channel;
        }

        public String getConsentDate() {
            return consentDate;
        }

        public void setConsentDate(String consentDate) {
            this.consentDate = consentDate;
        }

        public String getValidUntil() {
            return validUntil;
        }

        public void setValidUntil(String validUntil) {
            this.validUntil = validUntil;
        }
    }
}

