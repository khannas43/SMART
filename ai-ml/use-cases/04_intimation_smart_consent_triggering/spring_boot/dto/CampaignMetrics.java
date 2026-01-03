package com.smart.platform.aiml.intimation.dto;

/**
 * DTO for campaign metrics
 */
public class CampaignMetrics {
    private Integer campaignId;
    private Integer totalCandidates;
    private Integer messagesSent;
    private Integer messagesDelivered;
    private Integer messagesFailed;
    private Integer consentsGiven;
    private Integer consentsRejected;
    private Double responseRate;
    private Double deliveryRate;
    private String error;

    // Getters and Setters
    public Integer getCampaignId() {
        return campaignId;
    }

    public void setCampaignId(Integer campaignId) {
        this.campaignId = campaignId;
    }

    public Integer getTotalCandidates() {
        return totalCandidates;
    }

    public void setTotalCandidates(Integer totalCandidates) {
        this.totalCandidates = totalCandidates;
    }

    public Integer getMessagesSent() {
        return messagesSent;
    }

    public void setMessagesSent(Integer messagesSent) {
        this.messagesSent = messagesSent;
    }

    public Integer getMessagesDelivered() {
        return messagesDelivered;
    }

    public void setMessagesDelivered(Integer messagesDelivered) {
        this.messagesDelivered = messagesDelivered;
    }

    public Integer getMessagesFailed() {
        return messagesFailed;
    }

    public void setMessagesFailed(Integer messagesFailed) {
        this.messagesFailed = messagesFailed;
    }

    public Integer getConsentsGiven() {
        return consentsGiven;
    }

    public void setConsentsGiven(Integer consentsGiven) {
        this.consentsGiven = consentsGiven;
    }

    public Integer getConsentsRejected() {
        return consentsRejected;
    }

    public void setConsentsRejected(Integer consentsRejected) {
        this.consentsRejected = consentsRejected;
    }

    public Double getResponseRate() {
        return responseRate;
    }

    public void setResponseRate(Double responseRate) {
        this.responseRate = responseRate;
    }

    public Double getDeliveryRate() {
        return deliveryRate;
    }

    public void setDeliveryRate(Double deliveryRate) {
        this.deliveryRate = deliveryRate;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

