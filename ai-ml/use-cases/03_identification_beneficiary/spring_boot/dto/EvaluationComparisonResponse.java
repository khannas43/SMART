package com.smart.platform.aiml.eligibility.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for comparing evaluations across rule versions
 */
public class EvaluationComparisonResponse {
    private Boolean success;
    private String schemeCode;
    private String versionOld;
    private String versionNew;
    private Integer totalFamiliesCompared;
    private Integer familiesWithDifferentResults;
    private List<FamilyComparisonResult> familyComparisons;
    private Map<String, Integer> statusChanges; // Status change counts
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

    public String getVersionOld() {
        return versionOld;
    }

    public void setVersionOld(String versionOld) {
        this.versionOld = versionOld;
    }

    public String getVersionNew() {
        return versionNew;
    }

    public void setVersionNew(String versionNew) {
        this.versionNew = versionNew;
    }

    public Integer getTotalFamiliesCompared() {
        return totalFamiliesCompared;
    }

    public void setTotalFamiliesCompared(Integer totalFamiliesCompared) {
        this.totalFamiliesCompared = totalFamiliesCompared;
    }

    public Integer getFamiliesWithDifferentResults() {
        return familiesWithDifferentResults;
    }

    public void setFamiliesWithDifferentResults(Integer familiesWithDifferentResults) {
        this.familiesWithDifferentResults = familiesWithDifferentResults;
    }

    public List<FamilyComparisonResult> getFamilyComparisons() {
        return familyComparisons;
    }

    public void setFamilyComparisons(List<FamilyComparisonResult> familyComparisons) {
        this.familyComparisons = familyComparisons;
    }

    public Map<String, Integer> getStatusChanges() {
        return statusChanges;
    }

    public void setStatusChanges(Map<String, Integer> statusChanges) {
        this.statusChanges = statusChanges;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    /**
     * Nested DTO for family comparison result
     */
    public static class FamilyComparisonResult {
        private String familyId;
        private String statusOld;
        private String statusNew;
        private Double scoreOld;
        private Double scoreNew;
        private Boolean hasChanged;

        // Getters and Setters
        public String getFamilyId() {
            return familyId;
        }

        public void setFamilyId(String familyId) {
            this.familyId = familyId;
        }

        public String getStatusOld() {
            return statusOld;
        }

        public void setStatusOld(String statusOld) {
            this.statusOld = statusOld;
        }

        public String getStatusNew() {
            return statusNew;
        }

        public void setStatusNew(String statusNew) {
            this.statusNew = statusNew;
        }

        public Double getScoreOld() {
            return scoreOld;
        }

        public void setScoreOld(Double scoreOld) {
            this.scoreOld = scoreOld;
        }

        public Double getScoreNew() {
            return scoreNew;
        }

        public void setScoreNew(Double scoreNew) {
            this.scoreNew = scoreNew;
        }

        public Boolean getHasChanged() {
            return hasChanged;
        }

        public void setHasChanged(Boolean hasChanged) {
            this.hasChanged = hasChanged;
        }
    }
}

