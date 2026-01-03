package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Response DTO for scheme configuration
 */
public class SchemeConfigResponse {
    private Boolean success;
    private String schemeId;
    private String schemeName;
    private List<RuleDto> rules;
    private Boolean mlModelAvailable;
    private String mlModelVersion;
    private String error;

    // Builder pattern
    public static SchemeConfigResponseBuilder builder() {
        return new SchemeConfigResponseBuilder();
    }

    // Static factory methods
    public static SchemeConfigResponse error(String errorMessage) {
        SchemeConfigResponse response = new SchemeConfigResponse();
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

    public String getSchemeId() {
        return schemeId;
    }

    public void setSchemeId(String schemeId) {
        this.schemeId = schemeId;
    }

    public String getSchemeName() {
        return schemeName;
    }

    public void setSchemeName(String schemeName) {
        this.schemeName = schemeName;
    }

    public List<RuleDto> getRules() {
        return rules;
    }

    public void setRules(List<RuleDto> rules) {
        this.rules = rules;
    }

    public Boolean getMlModelAvailable() {
        return mlModelAvailable;
    }

    public void setMlModelAvailable(Boolean mlModelAvailable) {
        this.mlModelAvailable = mlModelAvailable;
    }

    public String getMlModelVersion() {
        return mlModelVersion;
    }

    public void setMlModelVersion(String mlModelVersion) {
        this.mlModelVersion = mlModelVersion;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Builder class
    public static class SchemeConfigResponseBuilder {
        private SchemeConfigResponse response = new SchemeConfigResponse();

        public SchemeConfigResponseBuilder schemeId(String schemeId) {
            response.setSchemeId(schemeId);
            return this;
        }

        public SchemeConfigResponseBuilder schemeName(String schemeName) {
            response.setSchemeName(schemeName);
            return this;
        }

        public SchemeConfigResponseBuilder rules(List<RuleDto> rules) {
            response.setRules(rules);
            return this;
        }

        public SchemeConfigResponseBuilder mlModelAvailable(Boolean mlModelAvailable) {
            response.setMlModelAvailable(mlModelAvailable);
            return this;
        }

        public SchemeConfigResponse build() {
            return response;
        }
    }
}

