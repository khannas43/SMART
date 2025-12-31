package com.smart.platform.eligibility.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for eligibility check
 */
public class EligibilityCheckResponse {
    private Boolean success;
    private Integer checkId;
    private String sessionId;
    private String userType;  // LOGGED_IN, GUEST, ANONYMOUS
    private Boolean isApproximate;
    private Integer totalSchemesChecked;
    private Integer eligibleCount;
    private Integer possibleEligibleCount;
    private Integer notEligibleCount;
    private Integer processingTimeMs;
    private List<SchemeEvaluationResult> topRecommendations;
    private List<SchemeEvaluationResult> otherSchemes;
    private List<SchemeEvaluationResult> allEvaluations;
    private Integer recommendationId;
    private String familyId;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getCheckId() {
        return checkId;
    }

    public void setCheckId(Integer checkId) {
        this.checkId = checkId;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getUserType() {
        return userType;
    }

    public void setUserType(String userType) {
        this.userType = userType;
    }

    public Boolean getIsApproximate() {
        return isApproximate;
    }

    public void setIsApproximate(Boolean isApproximate) {
        this.isApproximate = isApproximate;
    }

    public Integer getTotalSchemesChecked() {
        return totalSchemesChecked;
    }

    public void setTotalSchemesChecked(Integer totalSchemesChecked) {
        this.totalSchemesChecked = totalSchemesChecked;
    }

    public Integer getEligibleCount() {
        return eligibleCount;
    }

    public void setEligibleCount(Integer eligibleCount) {
        this.eligibleCount = eligibleCount;
    }

    public Integer getPossibleEligibleCount() {
        return possibleEligibleCount;
    }

    public void setPossibleEligibleCount(Integer possibleEligibleCount) {
        this.possibleEligibleCount = possibleEligibleCount;
    }

    public Integer getNotEligibleCount() {
        return notEligibleCount;
    }

    public void setNotEligibleCount(Integer notEligibleCount) {
        this.notEligibleCount = notEligibleCount;
    }

    public Integer getProcessingTimeMs() {
        return processingTimeMs;
    }

    public void setProcessingTimeMs(Integer processingTimeMs) {
        this.processingTimeMs = processingTimeMs;
    }

    public List<SchemeEvaluationResult> getTopRecommendations() {
        return topRecommendations;
    }

    public void setTopRecommendations(List<SchemeEvaluationResult> topRecommendations) {
        this.topRecommendations = topRecommendations;
    }

    public List<SchemeEvaluationResult> getOtherSchemes() {
        return otherSchemes;
    }

    public void setOtherSchemes(List<SchemeEvaluationResult> otherSchemes) {
        this.otherSchemes = otherSchemes;
    }

    public List<SchemeEvaluationResult> getAllEvaluations() {
        return allEvaluations;
    }

    public void setAllEvaluations(List<SchemeEvaluationResult> allEvaluations) {
        this.allEvaluations = allEvaluations;
    }

    public Integer getRecommendationId() {
        return recommendationId;
    }

    public void setRecommendationId(Integer recommendationId) {
        this.recommendationId = recommendationId;
    }

    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTO
    public static class SchemeEvaluationResult {
        private String schemeCode;
        private String schemeName;
        private String eligibilityStatus;  // ELIGIBLE, POSSIBLE_ELIGIBLE, NOT_ELIGIBLE
        private Double eligibilityScore;
        private String confidenceLevel;  // HIGH, MEDIUM, LOW
        private Integer recommendationRank;
        private Double priorityScore;
        private Double impactScore;
        private Double underCoverageBoost;
        private String explanationText;
        private List<String> nextSteps;
        private List<String> metRules;
        private List<String> failedRules;

        // Getters and Setters
        public String getSchemeCode() {
            return schemeCode;
        }

        public void setSchemeCode(String schemeCode) {
            this.schemeCode = schemeCode;
        }

        public String getSchemeName() {
            return schemeName;
        }

        public void setSchemeName(String schemeName) {
            this.schemeName = schemeName;
        }

        public String getEligibilityStatus() {
            return eligibilityStatus;
        }

        public void setEligibilityStatus(String eligibilityStatus) {
            this.eligibilityStatus = eligibilityStatus;
        }

        public Double getEligibilityScore() {
            return eligibilityScore;
        }

        public void setEligibilityScore(Double eligibilityScore) {
            this.eligibilityScore = eligibilityScore;
        }

        public String getConfidenceLevel() {
            return confidenceLevel;
        }

        public void setConfidenceLevel(String confidenceLevel) {
            this.confidenceLevel = confidenceLevel;
        }

        public Integer getRecommendationRank() {
            return recommendationRank;
        }

        public void setRecommendationRank(Integer recommendationRank) {
            this.recommendationRank = recommendationRank;
        }

        public Double getPriorityScore() {
            return priorityScore;
        }

        public void setPriorityScore(Double priorityScore) {
            this.priorityScore = priorityScore;
        }

        public Double getImpactScore() {
            return impactScore;
        }

        public void setImpactScore(Double impactScore) {
            this.impactScore = impactScore;
        }

        public Double getUnderCoverageBoost() {
            return underCoverageBoost;
        }

        public void setUnderCoverageBoost(Double underCoverageBoost) {
            this.underCoverageBoost = underCoverageBoost;
        }

        public String getExplanationText() {
            return explanationText;
        }

        public void setExplanationText(String explanationText) {
            this.explanationText = explanationText;
        }

        public List<String> getNextSteps() {
            return nextSteps;
        }

        public void setNextSteps(List<String> nextSteps) {
            this.nextSteps = nextSteps;
        }

        public List<String> getMetRules() {
            return metRules;
        }

        public void setMetRules(List<String> metRules) {
            this.metRules = metRules;
        }

        public List<String> getFailedRules() {
            return failedRules;
        }

        public void setFailedRules(List<String> failedRules) {
            this.failedRules = failedRules;
        }
    }
}

