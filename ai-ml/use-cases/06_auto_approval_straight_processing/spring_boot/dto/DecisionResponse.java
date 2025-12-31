package com.smart.platform.decision.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for decision evaluation
 */
public class DecisionResponse {
    private Boolean success;
    private Integer decisionId;
    private String decisionType;  // AUTO_APPROVE, ROUTE_TO_OFFICER, ROUTE_TO_FRAUD, AUTO_REJECT
    private String decisionStatus;  // approved, rejected, under_review
    private Double riskScore;
    private String riskBand;  // LOW, MEDIUM, HIGH
    private String reason;
    private RuleEvaluationResult ruleResults;
    private RiskScoreResult riskResults;
    private RoutingResult routing;
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

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public RuleEvaluationResult getRuleResults() {
        return ruleResults;
    }

    public void setRuleResults(RuleEvaluationResult ruleResults) {
        this.ruleResults = ruleResults;
    }

    public RiskScoreResult getRiskResults() {
        return riskResults;
    }

    public void setRiskResults(RiskScoreResult riskResults) {
        this.riskResults = riskResults;
    }

    public RoutingResult getRouting() {
        return routing;
    }

    public void setRouting(RoutingResult routing) {
        this.routing = routing;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTOs
    public static class RuleEvaluationResult {
        private Boolean allPassed;
        private Integer passedCount;
        private Integer failedCount;
        private List<String> criticalFailures;
        private List<RuleEvaluation> evaluations;

        // Getters and Setters
        public Boolean getAllPassed() {
            return allPassed;
        }

        public void setAllPassed(Boolean allPassed) {
            this.allPassed = allPassed;
        }

        public Integer getPassedCount() {
            return passedCount;
        }

        public void setPassedCount(Integer passedCount) {
            this.passedCount = passedCount;
        }

        public Integer getFailedCount() {
            return failedCount;
        }

        public void setFailedCount(Integer failedCount) {
            this.failedCount = failedCount;
        }

        public List<String> getCriticalFailures() {
            return criticalFailures;
        }

        public void setCriticalFailures(List<String> criticalFailures) {
            this.criticalFailures = criticalFailures;
        }

        public List<RuleEvaluation> getEvaluations() {
            return evaluations;
        }

        public void setEvaluations(List<RuleEvaluation> evaluations) {
            this.evaluations = evaluations;
        }
    }

    public static class RuleEvaluation {
        private String ruleCategory;
        private String ruleName;
        private Boolean passed;
        private String severity;
        private String resultMessage;

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
    }

    public static class RiskScoreResult {
        private Double riskScore;
        private String riskBand;
        private String modelVersion;
        private String modelType;
        private List<String> topFactors;

        // Getters and Setters
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

        public String getModelVersion() {
            return modelVersion;
        }

        public void setModelVersion(String modelVersion) {
            this.modelVersion = modelVersion;
        }

        public String getModelType() {
            return modelType;
        }

        public void setModelType(String modelType) {
            this.modelType = modelType;
        }

        public List<String> getTopFactors() {
            return topFactors;
        }

        public void setTopFactors(List<String> topFactors) {
            this.topFactors = topFactors;
        }
    }

    public static class RoutingResult {
        private String action;
        private String status;
        private String message;
        private String queue;
        private Integer triggerId;

        // Getters and Setters
        public String getAction() {
            return action;
        }

        public void setAction(String action) {
            this.action = action;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public String getQueue() {
            return queue;
        }

        public void setQueue(String queue) {
            this.queue = queue;
        }

        public Integer getTriggerId() {
            return triggerId;
        }

        public void setTriggerId(Integer triggerId) {
            this.triggerId = triggerId;
        }
    }
}

