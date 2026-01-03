package com.smart.platform.aiml.intimation.dto;

import java.util.List;

/**
 * Response DTO for intimation status
 */
public class IntimationStatusResponse {
    private Boolean success;
    private String familyId;
    private List<IntimationRecord> intimations;
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

    public List<IntimationRecord> getIntimations() {
        return intimations;
    }

    public void setIntimations(List<IntimationRecord> intimations) {
        this.intimations = intimations;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    /**
     * Nested DTO for intimation record
     */
    public static class IntimationRecord {
        private Integer campaignId;
        private String campaignName;
        private String schemeCode;
        private String messageStatus;
        private String consentStatus;
        private String channel;
        private String deliveryStatus;
        private String sentAt;

        // Getters and Setters
        public Integer getCampaignId() {
            return campaignId;
        }

        public void setCampaignId(Integer campaignId) {
            this.campaignId = campaignId;
        }

        public String getCampaignName() {
            return campaignName;
        }

        public void setCampaignName(String campaignName) {
            this.campaignName = campaignName;
        }

        public String getSchemeCode() {
            return schemeCode;
        }

        public void setSchemeCode(String schemeCode) {
            this.schemeCode = schemeCode;
        }

        public String getMessageStatus() {
            return messageStatus;
        }

        public void setMessageStatus(String messageStatus) {
            this.messageStatus = messageStatus;
        }

        public String getConsentStatus() {
            return consentStatus;
        }

        public void setConsentStatus(String consentStatus) {
            this.consentStatus = consentStatus;
        }

        public String getChannel() {
            return channel;
        }

        public void setChannel(String channel) {
            this.channel = channel;
        }

        public String getDeliveryStatus() {
            return deliveryStatus;
        }

        public void setDeliveryStatus(String deliveryStatus) {
            this.deliveryStatus = deliveryStatus;
        }

        public String getSentAt() {
            return sentAt;
        }

        public void setSentAt(String sentAt) {
            this.sentAt = sentAt;
        }
    }
}

