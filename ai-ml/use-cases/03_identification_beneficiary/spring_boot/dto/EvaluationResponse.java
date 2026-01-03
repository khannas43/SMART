package com.smart.platform.aiml.eligibility.dto;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Response DTO for eligibility evaluation
 */
public class EvaluationResponse {
    private Boolean success;
    private UUID familyId;
    private Integer evaluationId;
    private List<SchemeEvaluation> schemes;
    private Integer totalSchemes;
    private Integer eligibleCount;
    private Integer possibleEligibleCount;
    private Integer notEligibleCount;
    private String evaluationTimestamp;
    private String error;

    // Static factory methods
    public static EvaluationResponse error(String errorMessage) {
        EvaluationResponse response = new EvaluationResponse();
        response.setSuccess(false);
        response.setError(errorMessage);
        return response;
    }

    public static EvaluationResponse fromMap(Map<String, Object> map) {
        EvaluationResponse response = new EvaluationResponse();
        
        Object success = map.get("success");
        if (success != null) {
            response.setSuccess(Boolean.parseBoolean(success.toString()));
        }
        
        Object familyId = map.get("family_id");
        if (familyId != null) {
            response.setFamilyId(UUID.fromString(familyId.toString()));
        }
        
        Object evaluationId = map.get("evaluation_id");
        if (evaluationId != null) {
            response.setEvaluationId(evaluationId instanceof Number ? 
                ((Number) evaluationId).intValue() : Integer.parseInt(evaluationId.toString()));
        }
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> schemesData = (List<Map<String, Object>>) map.get("schemes");
        if (schemesData != null) {
            List<SchemeEvaluation> schemes = new java.util.ArrayList<>();
            for (Map<String, Object> schemeData : schemesData) {
                schemes.add(SchemeEvaluation.fromMap(schemeData));
            }
            response.setSchemes(schemes);
        }
        
        Object totalSchemes = map.get("total_schemes");
        if (totalSchemes != null) {
            response.setTotalSchemes(totalSchemes instanceof Number ? 
                ((Number) totalSchemes).intValue() : Integer.parseInt(totalSchemes.toString()));
        }
        
        Object eligibleCount = map.get("eligible_count");
        if (eligibleCount != null) {
            response.setEligibleCount(eligibleCount instanceof Number ? 
                ((Number) eligibleCount).intValue() : Integer.parseInt(eligibleCount.toString()));
        }
        
        Object possibleEligibleCount = map.get("possible_eligible_count");
        if (possibleEligibleCount != null) {
            response.setPossibleEligibleCount(possibleEligibleCount instanceof Number ? 
                ((Number) possibleEligibleCount).intValue() : Integer.parseInt(possibleEligibleCount.toString()));
        }
        
        Object notEligibleCount = map.get("not_eligible_count");
        if (notEligibleCount != null) {
            response.setNotEligibleCount(notEligibleCount instanceof Number ? 
                ((Number) notEligibleCount).intValue() : Integer.parseInt(notEligibleCount.toString()));
        }
        
        response.setEvaluationTimestamp((String) map.get("evaluation_timestamp"));
        response.setError((String) map.get("error"));
        
        return response;
    }

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public UUID getFamilyId() {
        return familyId;
    }

    public void setFamilyId(UUID familyId) {
        this.familyId = familyId;
    }

    public Integer getEvaluationId() {
        return evaluationId;
    }

    public void setEvaluationId(Integer evaluationId) {
        this.evaluationId = evaluationId;
    }

    public List<SchemeEvaluation> getSchemes() {
        return schemes;
    }

    public void setSchemes(List<SchemeEvaluation> schemes) {
        this.schemes = schemes;
    }

    public Integer getTotalSchemes() {
        return totalSchemes;
    }

    public void setTotalSchemes(Integer totalSchemes) {
        this.totalSchemes = totalSchemes;
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

    public String getEvaluationTimestamp() {
        return evaluationTimestamp;
    }

    public void setEvaluationTimestamp(String evaluationTimestamp) {
        this.evaluationTimestamp = evaluationTimestamp;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    /**
     * Nested DTO for scheme evaluation result
     */
    public static class SchemeEvaluation {
        private String schemeCode;
        private String schemeName;
        private String eligibilityStatus; // RULE_ELIGIBLE, POSSIBLE_ELIGIBLE, NOT_ELIGIBLE
        private Double eligibilityScore;
        private Double priorityScore;
        private String confidenceLevel; // HIGH, MEDIUM, LOW
        private List<String> metRules;
        private List<String> failedRules;
        private String explanation;

        public static SchemeEvaluation fromMap(Map<String, Object> map) {
            SchemeEvaluation eval = new SchemeEvaluation();
            eval.setSchemeCode((String) map.get("scheme_code"));
            eval.setSchemeName((String) map.get("scheme_name"));
            eval.setEligibilityStatus((String) map.get("eligibility_status"));
            
            Object score = map.get("eligibility_score");
            if (score != null) {
                eval.setEligibilityScore(score instanceof Number ? 
                    ((Number) score).doubleValue() : Double.parseDouble(score.toString()));
            }
            
            Object priorityScore = map.get("priority_score");
            if (priorityScore != null) {
                eval.setPriorityScore(priorityScore instanceof Number ? 
                    ((Number) priorityScore).doubleValue() : Double.parseDouble(priorityScore.toString()));
            }
            
            eval.setConfidenceLevel((String) map.get("confidence_level"));
            
            @SuppressWarnings("unchecked")
            List<String> metRules = (List<String>) map.get("met_rules");
            eval.setMetRules(metRules);
            
            @SuppressWarnings("unchecked")
            List<String> failedRules = (List<String>) map.get("failed_rules");
            eval.setFailedRules(failedRules);
            
            eval.setExplanation((String) map.get("explanation"));
            
            return eval;
        }

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

        public Double getPriorityScore() {
            return priorityScore;
        }

        public void setPriorityScore(Double priorityScore) {
            this.priorityScore = priorityScore;
        }

        public String getConfidenceLevel() {
            return confidenceLevel;
        }

        public void setConfidenceLevel(String confidenceLevel) {
            this.confidenceLevel = confidenceLevel;
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

        public String getExplanation() {
            return explanation;
        }

        public void setExplanation(String explanation) {
            this.explanation = explanation;
        }
    }
}

