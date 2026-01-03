package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Response DTO for scheme rules
 */
public class SchemeRulesResponse {
    private Boolean success;
    private String schemeCode;
    private List<RuleDto> rules;
    private Integer totalRules;
    private Integer activeRules;
    private String error;

    // Static factory methods
    public static SchemeRulesResponse error(String errorMessage) {
        SchemeRulesResponse response = new SchemeRulesResponse();
        response.setSuccess(false);
        response.setError(errorMessage);
        return response;
    }

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

    public List<RuleDto> getRules() {
        return rules;
    }

    public void setRules(List<RuleDto> rules) {
        this.rules = rules;
        this.totalRules = rules != null ? rules.size() : 0;
        if (rules != null) {
            this.activeRules = (int) rules.stream()
                .filter(rule -> rule.getActive() != null && rule.getActive())
                .count();
        }
    }

    public Integer getTotalRules() {
        return totalRules;
    }

    public void setTotalRules(Integer totalRules) {
        this.totalRules = totalRules;
    }

    public Integer getActiveRules() {
        return activeRules;
    }

    public void setActiveRules(Integer activeRules) {
        this.activeRules = activeRules;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

