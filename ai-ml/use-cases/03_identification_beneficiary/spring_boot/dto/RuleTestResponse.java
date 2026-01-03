package com.smart.platform.aiml.eligibility.dto;

/**
 * Response DTO for rule test result
 */
public class RuleTestResponse {
    private Boolean success;
    private Boolean rulePassed;
    private String result; // PASSED, FAILED, ERROR
    private String errorMessage;
    private String evaluationDetails;

    // Static factory methods
    public static RuleTestResponse error(String errorMessage) {
        RuleTestResponse response = new RuleTestResponse();
        response.setSuccess(false);
        response.setResult("ERROR");
        response.setErrorMessage(errorMessage);
        return response;
    }

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Boolean getRulePassed() {
        return rulePassed;
    }

    public void setRulePassed(Boolean rulePassed) {
        this.rulePassed = rulePassed;
    }

    public String getResult() {
        return result;
    }

    public void setResult(String result) {
        this.result = result;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public String getEvaluationDetails() {
        return evaluationDetails;
    }

    public void setEvaluationDetails(String evaluationDetails) {
        this.evaluationDetails = evaluationDetails;
    }
}

