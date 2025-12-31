package com.smart.platform.detection.dto;

import java.util.List;

/**
 * Response DTO for case list
 */
public class CaseListResponse {
    private Boolean success;
    private List<DetectedCaseSummary> cases;
    private Integer totalCount;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public List<DetectedCaseSummary> getCases() {
        return cases;
    }

    public void setCases(List<DetectedCaseSummary> cases) {
        this.cases = cases;
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

    // Nested DTO
    public static class DetectedCaseSummary {
        private Integer caseId;
        private String beneficiaryId;
        private String schemeCode;
        private String caseType;
        private String confidenceLevel;
        private String caseStatus;
        private Integer priority;
        private Double financialExposure;
        private String detectionTimestamp;

        // Getters and Setters
        public Integer getCaseId() {
            return caseId;
        }

        public void setCaseId(Integer caseId) {
            this.caseId = caseId;
        }

        public String getBeneficiaryId() {
            return beneficiaryId;
        }

        public void setBeneficiaryId(String beneficiaryId) {
            this.beneficiaryId = beneficiaryId;
        }

        public String getSchemeCode() {
            return schemeCode;
        }

        public void setSchemeCode(String schemeCode) {
            this.schemeCode = schemeCode;
        }

        public String getCaseType() {
            return caseType;
        }

        public void setCaseType(String caseType) {
            this.caseType = caseType;
        }

        public String getConfidenceLevel() {
            return confidenceLevel;
        }

        public void setConfidenceLevel(String confidenceLevel) {
            this.confidenceLevel = confidenceLevel;
        }

        public String getCaseStatus() {
            return caseStatus;
        }

        public void setCaseStatus(String caseStatus) {
            this.caseStatus = caseStatus;
        }

        public Integer getPriority() {
            return priority;
        }

        public void setPriority(Integer priority) {
            this.priority = priority;
        }

        public Double getFinancialExposure() {
            return financialExposure;
        }

        public void setFinancialExposure(Double financialExposure) {
            this.financialExposure = financialExposure;
        }

        public String getDetectionTimestamp() {
            return detectionTimestamp;
        }

        public void setDetectionTimestamp(String detectionTimestamp) {
            this.detectionTimestamp = detectionTimestamp;
        }
    }
}

