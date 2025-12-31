package com.smart.platform.decision.dto;

import java.util.List;

/**
 * Response DTO for decision history
 */
public class DecisionHistoryResponse {
    private Boolean success;
    private Integer applicationId;
    private List<DecisionHistoryEntry> history;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getApplicationId() {
        return applicationId;
    }

    public void setApplicationId(Integer applicationId) {
        this.applicationId = applicationId;
    }

    public List<DecisionHistoryEntry> getHistory() {
        return history;
    }

    public void setHistory(List<DecisionHistoryEntry> history) {
        this.history = history;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public static class DecisionHistoryEntry {
        private Integer historyId;
        private String fromStatus;
        private String toStatus;
        private String fromDecisionType;
        private String toDecisionType;
        private String changeReason;
        private String changedBy;
        private String changedByType;
        private String changedAt;

        // Getters and Setters
        public Integer getHistoryId() {
            return historyId;
        }

        public void setHistoryId(Integer historyId) {
            this.historyId = historyId;
        }

        public String getFromStatus() {
            return fromStatus;
        }

        public void setFromStatus(String fromStatus) {
            this.fromStatus = fromStatus;
        }

        public String getToStatus() {
            return toStatus;
        }

        public void setToStatus(String toStatus) {
            this.toStatus = toStatus;
        }

        public String getFromDecisionType() {
            return fromDecisionType;
        }

        public void setFromDecisionType(String fromDecisionType) {
            this.fromDecisionType = fromDecisionType;
        }

        public String getToDecisionType() {
            return toDecisionType;
        }

        public void setToDecisionType(String toDecisionType) {
            this.toDecisionType = toDecisionType;
        }

        public String getChangeReason() {
            return changeReason;
        }

        public void setChangeReason(String changeReason) {
            this.changeReason = changeReason;
        }

        public String getChangedBy() {
            return changedBy;
        }

        public void setChangedBy(String changedBy) {
            this.changedBy = changedBy;
        }

        public String getChangedByType() {
            return changedByType;
        }

        public void setChangedByType(String changedByType) {
            this.changedByType = changedByType;
        }

        public String getChangedAt() {
            return changedAt;
        }

        public void setChangedAt(String changedAt) {
            this.changedAt = changedAt;
        }
    }
}

