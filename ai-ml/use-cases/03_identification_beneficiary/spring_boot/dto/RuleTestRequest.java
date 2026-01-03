package com.smart.platform.aiml.eligibility.dto;

import java.util.Map;

/**
 * Request DTO for testing a rule expression
 */
public class RuleTestRequest {
    private String ruleExpression;
    private Map<String, Object> testData; // Family data to test against

    // Getters and Setters
    public String getRuleExpression() {
        return ruleExpression;
    }

    public void setRuleExpression(String ruleExpression) {
        this.ruleExpression = ruleExpression;
    }

    public Map<String, Object> getTestData() {
        return testData;
    }

    public void setTestData(Map<String, Object> testData) {
        this.testData = testData;
    }
}

