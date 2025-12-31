package com.smart.platform.inclusion.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for priority household list
 */
public class PriorityListResponse {
    private Boolean success;
    private Integer totalCount;
    private List<PriorityHouseholdItem> households;
    private Map<String, Object> filters;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
    }

    public List<PriorityHouseholdItem> getHouseholds() {
        return households;
    }

    public void setHouseholds(List<PriorityHouseholdItem> households) {
        this.households = households;
    }

    public Map<String, Object> getFilters() {
        return filters;
    }

    public void setFilters(Map<String, Object> filters) {
        this.filters = filters;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTO
    public static class PriorityHouseholdItem {
        private Integer priorityId;
        private String familyId;
        private String householdHeadId;
        private String blockId;
        private String district;
        private String gramPanchayat;
        private Double inclusionGapScore;
        private Double vulnerabilityScore;
        private String priorityLevel;
        private List<String> prioritySegments;
        private Integer predictedEligibleCount;
        private Integer actualEnrolledCount;
        private Integer eligibilityGapCount;
        private String detectedAt;

        // Getters and Setters
        public Integer getPriorityId() {
            return priorityId;
        }

        public void setPriorityId(Integer priorityId) {
            this.priorityId = priorityId;
        }

        public String getFamilyId() {
            return familyId;
        }

        public void setFamilyId(String familyId) {
            this.familyId = familyId;
        }

        public String getHouseholdHeadId() {
            return householdHeadId;
        }

        public void setHouseholdHeadId(String householdHeadId) {
            this.householdHeadId = householdHeadId;
        }

        public String getBlockId() {
            return blockId;
        }

        public void setBlockId(String blockId) {
            this.blockId = blockId;
        }

        public String getDistrict() {
            return district;
        }

        public void setDistrict(String district) {
            this.district = district;
        }

        public String getGramPanchayat() {
            return gramPanchayat;
        }

        public void setGramPanchayat(String gramPanchayat) {
            this.gramPanchayat = gramPanchayat;
        }

        public Double getInclusionGapScore() {
            return inclusionGapScore;
        }

        public void setInclusionGapScore(Double inclusionGapScore) {
            this.inclusionGapScore = inclusionGapScore;
        }

        public Double getVulnerabilityScore() {
            return vulnerabilityScore;
        }

        public void setVulnerabilityScore(Double vulnerabilityScore) {
            this.vulnerabilityScore = vulnerabilityScore;
        }

        public String getPriorityLevel() {
            return priorityLevel;
        }

        public void setPriorityLevel(String priorityLevel) {
            this.priorityLevel = priorityLevel;
        }

        public List<String> getPrioritySegments() {
            return prioritySegments;
        }

        public void setPrioritySegments(List<String> prioritySegments) {
            this.prioritySegments = prioritySegments;
        }

        public Integer getPredictedEligibleCount() {
            return predictedEligibleCount;
        }

        public void setPredictedEligibleCount(Integer predictedEligibleCount) {
            this.predictedEligibleCount = predictedEligibleCount;
        }

        public Integer getActualEnrolledCount() {
            return actualEnrolledCount;
        }

        public void setActualEnrolledCount(Integer actualEnrolledCount) {
            this.actualEnrolledCount = actualEnrolledCount;
        }

        public Integer getEligibilityGapCount() {
            return eligibilityGapCount;
        }

        public void setEligibilityGapCount(Integer eligibilityGapCount) {
            this.eligibilityGapCount = eligibilityGapCount;
        }

        public String getDetectedAt() {
            return detectedAt;
        }

        public void setDetectedAt(String detectedAt) {
            this.detectedAt = detectedAt;
        }
    }
}

