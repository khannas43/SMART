package com.smart.platform.inclusion.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for priority status
 */
public class PriorityStatusResponse {
    private Boolean success;
    private String familyId;
    private Boolean isPriority;
    private PriorityHousehold priorityHousehold;
    private List<ExceptionFlag> exceptionFlags;
    private List<Nudge> nudges;
    private String timestamp;
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

    public Boolean getIsPriority() {
        return isPriority;
    }

    public void setIsPriority(Boolean isPriority) {
        this.isPriority = isPriority;
    }

    public PriorityHousehold getPriorityHousehold() {
        return priorityHousehold;
    }

    public void setPriorityHousehold(PriorityHousehold priorityHousehold) {
        this.priorityHousehold = priorityHousehold;
    }

    public List<ExceptionFlag> getExceptionFlags() {
        return exceptionFlags;
    }

    public void setExceptionFlags(List<ExceptionFlag> exceptionFlags) {
        this.exceptionFlags = exceptionFlags;
    }

    public List<Nudge> getNudges() {
        return nudges;
    }

    public void setNudges(List<Nudge> nudges) {
        this.nudges = nudges;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTOs
    public static class PriorityHousehold {
        private Integer priorityId;
        private String familyId;
        private Double inclusionGapScore;
        private Double vulnerabilityScore;
        private Double coverageGapScore;
        private String priorityLevel;
        private List<String> prioritySegments;
        private Integer predictedEligibleCount;
        private Integer actualEnrolledCount;
        private Integer eligibilityGapCount;

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

        public Double getCoverageGapScore() {
            return coverageGapScore;
        }

        public void setCoverageGapScore(Double coverageGapScore) {
            this.coverageGapScore = coverageGapScore;
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
    }

    public static class ExceptionFlag {
        private Integer exceptionId;
        private String familyId;
        private String beneficiaryId;
        private String exceptionCategory;
        private String exceptionDescription;
        private Double anomalyScore;
        private String reviewStatus;

        // Getters and Setters
        public Integer getExceptionId() {
            return exceptionId;
        }

        public void setExceptionId(Integer exceptionId) {
            this.exceptionId = exceptionId;
        }

        public String getFamilyId() {
            return familyId;
        }

        public void setFamilyId(String familyId) {
            this.familyId = familyId;
        }

        public String getBeneficiaryId() {
            return beneficiaryId;
        }

        public void setBeneficiaryId(String beneficiaryId) {
            this.beneficiaryId = beneficiaryId;
        }

        public String getExceptionCategory() {
            return exceptionCategory;
        }

        public void setExceptionCategory(String exceptionCategory) {
            this.exceptionCategory = exceptionCategory;
        }

        public String getExceptionDescription() {
            return exceptionDescription;
        }

        public void setExceptionDescription(String exceptionDescription) {
            this.exceptionDescription = exceptionDescription;
        }

        public Double getAnomalyScore() {
            return anomalyScore;
        }

        public void setAnomalyScore(Double anomalyScore) {
            this.anomalyScore = anomalyScore;
        }

        public String getReviewStatus() {
            return reviewStatus;
        }

        public void setReviewStatus(String reviewStatus) {
            this.reviewStatus = reviewStatus;
        }
    }

    public static class Nudge {
        private Integer nudgeId;
        private String nudgeType;
        private String nudgeMessage;
        private List<String> recommendedActions;
        private List<String> schemeCodes;
        private String channel;
        private String priorityLevel;
        private String deliveryStatus;

        // Getters and Setters
        public Integer getNudgeId() {
            return nudgeId;
        }

        public void setNudgeId(Integer nudgeId) {
            this.nudgeId = nudgeId;
        }

        public String getNudgeType() {
            return nudgeType;
        }

        public void setNudgeType(String nudgeType) {
            this.nudgeType = nudgeType;
        }

        public String getNudgeMessage() {
            return nudgeMessage;
        }

        public void setNudgeMessage(String nudgeMessage) {
            this.nudgeMessage = nudgeMessage;
        }

        public List<String> getRecommendedActions() {
            return recommendedActions;
        }

        public void setRecommendedActions(List<String> recommendedActions) {
            this.recommendedActions = recommendedActions;
        }

        public List<String> getSchemeCodes() {
            return schemeCodes;
        }

        public void setSchemeCodes(List<String> schemeCodes) {
            this.schemeCodes = schemeCodes;
        }

        public String getChannel() {
            return channel;
        }

        public void setChannel(String channel) {
            this.channel = channel;
        }

        public String getPriorityLevel() {
            return priorityLevel;
        }

        public void setPriorityLevel(String priorityLevel) {
            this.priorityLevel = priorityLevel;
        }

        public String getDeliveryStatus() {
            return deliveryStatus;
        }

        public void setDeliveryStatus(String deliveryStatus) {
            this.deliveryStatus = deliveryStatus;
        }
    }
}

