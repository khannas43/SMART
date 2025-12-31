package com.smart.platform.decision.dto;

import java.util.Map;

/**
 * Response DTO for STP (Straight-Through Processing) metrics
 */
public class STPMetricsResponse {
    private Boolean success;
    private String schemeCode;
    private String periodStart;
    private String periodEnd;
    private Integer totalDecisions;
    private Integer autoApprovedCount;
    private Integer officerReviewedCount;
    private Integer rejectedCount;
    private Double autoApprovalRate;
    private Double averageProcessingTimeMinutes;
    private Map<String, Integer> decisionsByType;
    private Map<String, Integer> decisionsByRiskBand;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public String getPeriodStart() {
        return periodStart;
    }

    public void setPeriodStart(String periodStart) {
        this.periodStart = periodStart;
    }

    public String getPeriodEnd() {
        return periodEnd;
    }

    public void setPeriodEnd(String periodEnd) {
        this.periodEnd = periodEnd;
    }

    public Integer getTotalDecisions() {
        return totalDecisions;
    }

    public void setTotalDecisions(Integer totalDecisions) {
        this.totalDecisions = totalDecisions;
    }

    public Integer getAutoApprovedCount() {
        return autoApprovedCount;
    }

    public void setAutoApprovedCount(Integer autoApprovedCount) {
        this.autoApprovedCount = autoApprovedCount;
    }

    public Integer getOfficerReviewedCount() {
        return officerReviewedCount;
    }

    public void setOfficerReviewedCount(Integer officerReviewedCount) {
        this.officerReviewedCount = officerReviewedCount;
    }

    public Integer getRejectedCount() {
        return rejectedCount;
    }

    public void setRejectedCount(Integer rejectedCount) {
        this.rejectedCount = rejectedCount;
    }

    public Double getAutoApprovalRate() {
        return autoApprovalRate;
    }

    public void setAutoApprovalRate(Double autoApprovalRate) {
        this.autoApprovalRate = autoApprovalRate;
    }

    public Double getAverageProcessingTimeMinutes() {
        return averageProcessingTimeMinutes;
    }

    public void setAverageProcessingTimeMinutes(Double averageProcessingTimeMinutes) {
        this.averageProcessingTimeMinutes = averageProcessingTimeMinutes;
    }

    public Map<String, Integer> getDecisionsByType() {
        return decisionsByType;
    }

    public void setDecisionsByType(Map<String, Integer> decisionsByType) {
        this.decisionsByType = decisionsByType;
    }

    public Map<String, Integer> getDecisionsByRiskBand() {
        return decisionsByRiskBand;
    }

    public void setDecisionsByRiskBand(Map<String, Integer> decisionsByRiskBand) {
        this.decisionsByRiskBand = decisionsByRiskBand;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

