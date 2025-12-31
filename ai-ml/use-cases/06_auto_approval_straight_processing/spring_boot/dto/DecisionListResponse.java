package com.smart.platform.decision.dto;

import java.util.List;

/**
 * Response DTO for list of decisions
 */
public class DecisionListResponse {
    private Boolean success;
    private List<DecisionSummary> decisions;
    private Integer totalCount;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public List<DecisionSummary> getDecisions() {
        return decisions;
    }

    public void setDecisions(List<DecisionSummary> decisions) {
        this.decisions = decisions;
    }

    public Integer getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public static class DecisionSummary {
        private Integer decisionId;
        private Integer applicationId;
        private String familyId;
        private String schemeCode;
        private String decisionType;
        private String decisionStatus;
        private Double riskScore;
        private String riskBand;
        private String decisionTimestamp;

        // Getters and Setters
        public Integer getDecisionId() {
            return decisionId;
        }

        public void setDecisionId(Integer decisionId) {
            this.decisionId = decisionId;
        }

        public Integer getApplicationId() {
            return applicationId;
        }

        public void setApplicationId(Integer applicationId) {
            this.applicationId = applicationId;
        }

        public String getFamilyId() {
            return familyId;
        }

        public void setFamilyId(String familyId) {
            this.familyId = familyId;
        }

        public String getSchemeCode() {
            return schemeCode;
        }

        public void setSchemeCode(String schemeCode) {
            this.schemeCode = schemeCode;
        }

        public String getDecisionType() {
            return decisionType;
        }

        public void setDecisionType(String decisionType) {
            this.decisionType = decisionType;
        }

        public String getDecisionStatus() {
            return decisionStatus;
        }

        public void setDecisionStatus(String decisionStatus) {
            this.decisionStatus = decisionStatus;
        }

        public Double getRiskScore() {
            return riskScore;
        }

        public void setRiskScore(Double riskScore) {
            this.riskScore = riskScore;
        }

        public String getRiskBand() {
            return riskBand;
        }

        public void setRiskBand(String riskBand) {
            this.riskBand = riskBand;
        }

        public String getDecisionTimestamp() {
            return decisionTimestamp;
        }

        public void setDecisionTimestamp(String decisionTimestamp) {
            this.decisionTimestamp = decisionTimestamp;
        }
    }
}

