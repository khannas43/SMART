package com.smart.platform.detection.dto;

import java.util.Map;

/**
 * Response DTO for leakage analytics
 */
public class LeakageAnalyticsResponse {
    private Boolean success;
    private String periodStart;
    private String periodEnd;
    private String schemeCode;
    private Integer totalBeneficiariesScanned;
    private Integer totalCasesFlagged;
    private Map<String, Integer> casesByType;
    private Double totalFinancialExposure;
    private Double estimatedSavings;
    private Integer confirmedIneligibleCount;
    private Integer falsePositiveCount;
    private Double confirmationRate;
    private Double falsePositiveRate;
    private Map<String, Integer> ineligibilityReasons;
    private Map<String, Integer> overlapTypes;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
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

    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public Integer getTotalBeneficiariesScanned() {
        return totalBeneficiariesScanned;
    }

    public void setTotalBeneficiariesScanned(Integer totalBeneficiariesScanned) {
        this.totalBeneficiariesScanned = totalBeneficiariesScanned;
    }

    public Integer getTotalCasesFlagged() {
        return totalCasesFlagged;
    }

    public void setTotalCasesFlagged(Integer totalCasesFlagged) {
        this.totalCasesFlagged = totalCasesFlagged;
    }

    public Map<String, Integer> getCasesByType() {
        return casesByType;
    }

    public void setCasesByType(Map<String, Integer> casesByType) {
        this.casesByType = casesByType;
    }

    public Double getTotalFinancialExposure() {
        return totalFinancialExposure;
    }

    public void setTotalFinancialExposure(Double totalFinancialExposure) {
        this.totalFinancialExposure = totalFinancialExposure;
    }

    public Double getEstimatedSavings() {
        return estimatedSavings;
    }

    public void setEstimatedSavings(Double estimatedSavings) {
        this.estimatedSavings = estimatedSavings;
    }

    public Integer getConfirmedIneligibleCount() {
        return confirmedIneligibleCount;
    }

    public void setConfirmedIneligibleCount(Integer confirmedIneligibleCount) {
        this.confirmedIneligibleCount = confirmedIneligibleCount;
    }

    public Integer getFalsePositiveCount() {
        return falsePositiveCount;
    }

    public void setFalsePositiveCount(Integer falsePositiveCount) {
        this.falsePositiveCount = falsePositiveCount;
    }

    public Double getConfirmationRate() {
        return confirmationRate;
    }

    public void setConfirmationRate(Double confirmationRate) {
        this.confirmationRate = confirmationRate;
    }

    public Double getFalsePositiveRate() {
        return falsePositiveRate;
    }

    public void setFalsePositiveRate(Double falsePositiveRate) {
        this.falsePositiveRate = falsePositiveRate;
    }

    public Map<String, Integer> getIneligibilityReasons() {
        return ineligibilityReasons;
    }

    public void setIneligibilityReasons(Map<String, Integer> ineligibilityReasons) {
        this.ineligibilityReasons = ineligibilityReasons;
    }

    public Map<String, Integer> getOverlapTypes() {
        return overlapTypes;
    }

    public void setOverlapTypes(Map<String, Integer> overlapTypes) {
        this.overlapTypes = overlapTypes;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

