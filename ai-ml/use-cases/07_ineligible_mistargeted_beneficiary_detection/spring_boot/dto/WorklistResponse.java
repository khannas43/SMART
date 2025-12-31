package com.smart.platform.detection.dto;

import java.util.List;

/**
 * Response DTO for worklist
 */
public class WorklistResponse {
    private Boolean success;
    private String officerId;
    private String worklistQueue;
    private List<WorklistCase> cases;
    private Integer totalCount;
    private Integer activeCount;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getOfficerId() {
        return officerId;
    }

    public void setOfficerId(String officerId) {
        this.officerId = officerId;
    }

    public String getWorklistQueue() {
        return worklistQueue;
    }

    public void setWorklistQueue(String worklistQueue) {
        this.worklistQueue = worklistQueue;
    }

    public List<WorklistCase> getCases() {
        return cases;
    }

    public void setCases(List<WorklistCase> cases) {
        this.cases = cases;
    }

    public Integer getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
    }

    public Integer getActiveCount() {
        return activeCount;
    }

    public void setActiveCount(Integer activeCount) {
        this.activeCount = activeCount;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTO
    public static class WorklistCase {
        private Integer caseId;
        private Integer assignmentId;
        private String beneficiaryId;
        private String schemeCode;
        private String caseType;
        private String caseStatus;
        private Integer priority;
        private Double financialExposure;
        private String detectionRationale;
        private String assignedAt;

        // Getters and Setters
        public Integer getCaseId() {
            return caseId;
        }

        public void setCaseId(Integer caseId) {
            this.caseId = caseId;
        }

        public Integer getAssignmentId() {
            return assignmentId;
        }

        public void setAssignmentId(Integer assignmentId) {
            this.assignmentId = assignmentId;
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

        public String getDetectionRationale() {
            return detectionRationale;
        }

        public void setDetectionRationale(String detectionRationale) {
            this.detectionRationale = detectionRationale;
        }

        public String getAssignedAt() {
            return assignedAt;
        }

        public void setAssignedAt(String assignedAt) {
            this.assignedAt = assignedAt;
        }
    }
}

