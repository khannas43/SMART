package com.smart.platform.decision.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for decision details
 */
public class DecisionDetailResponse {
    private Boolean success;
    private Integer decisionId;
    private Integer applicationId;
    private String familyId;
    private String schemeCode;
    private String decisionType;
    private String decisionStatus;
    private Double riskScore;
    private String riskBand;
    private String routingReason;
    private String decisionTimestamp;
    private DecisionResponse.RuleEvaluationResult ruleResults;
    private DecisionResponse.RiskScoreResult riskResults;
    private DecisionResponse.RoutingResult routing;
    private List<RuleEvaluationDetail> ruleEvaluations;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

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

    public String getRoutingReason() {
        return routingReason;
    }

    public void setRoutingReason(String routingReason) {
        this.routingReason = routingReason;
    }

    public String getDecisionTimestamp() {
        return decisionTimestamp;
    }

    public void setDecisionTimestamp(String decisionTimestamp) {
        this.decisionTimestamp = decisionTimestamp;
    }

    public DecisionResponse.RuleEvaluationResult getRuleResults() {
        return ruleResults;
    }

    public void setRuleResults(DecisionResponse.RuleEvaluationResult ruleResults) {
        this.ruleResults = ruleResults;
    }

    public DecisionResponse.RiskScoreResult getRiskResults() {
        return riskResults;
    }

    public void setRiskResults(DecisionResponse.RiskScoreResult riskResults) {
        this.riskResults = riskResults;
    }

    public DecisionResponse.RoutingResult getRouting() {
        return routing;
    }

    public void setRouting(DecisionResponse.RoutingResult routing) {
        this.routing = routing;
    }

    public List<RuleEvaluationDetail> getRuleEvaluations() {
        return ruleEvaluations;
    }

    public void setRuleEvaluations(List<RuleEvaluationDetail> ruleEvaluations) {
        this.ruleEvaluations = ruleEvaluations;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public static class RuleEvaluationDetail {
        private String ruleCategory;
        private String ruleName;
        private Boolean passed;
        private String severity;
        private String resultMessage;
        private Map<String, Object> resultDetails;

        // Getters and Setters
        public String getRuleCategory() {
            return ruleCategory;
        }

        public void setRuleCategory(String ruleCategory) {
            this.ruleCategory = ruleCategory;
        }

        public String getRuleName() {
            return ruleName;
        }

        public void setRuleName(String ruleName) {
            this.ruleName = ruleName;
        }

        public Boolean getPassed() {
            return passed;
        }

        public void setPassed(Boolean passed) {
            this.passed = passed;
        }

        public String getSeverity() {
            return severity;
        }

        public void setSeverity(String severity) {
            this.severity = severity;
        }

        public String getResultMessage() {
            return resultMessage;
        }

        public void setResultMessage(String resultMessage) {
            this.resultMessage = resultMessage;
        }

        public Map<String, Object> getResultDetails() {
            return resultDetails;
        }

        public void setResultDetails(Map<String, Object> resultDetails) {
            this.resultDetails = resultDetails;
        }
    }
}

