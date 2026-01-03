package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Response DTO for rule validation
 */
public class RuleValidationResponse {
    private Boolean success;
    private Boolean isValid;
    private List<String> errors;
    private List<String> warnings;
    private String syntaxCheck;
    private String semanticCheck;

    // Static factory methods
    public static RuleValidationResponse error(String errorMessage) {
        RuleValidationResponse response = new RuleValidationResponse();
        response.setSuccess(false);
        response.setIsValid(false);
        response.getErrors().add(errorMessage);
        return response;
    }

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Boolean getIsValid() {
        return isValid;
    }

    public void setIsValid(Boolean isValid) {
        this.isValid = isValid;
    }

    public List<String> getErrors() {
        if (errors == null) {
            errors = new java.util.ArrayList<>();
        }
        return errors;
    }

    public void setErrors(List<String> errors) {
        this.errors = errors;
    }

    public List<String> getWarnings() {
        if (warnings == null) {
            warnings = new java.util.ArrayList<>();
        }
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public String getSyntaxCheck() {
        return syntaxCheck;
    }

    public void setSyntaxCheck(String syntaxCheck) {
        this.syntaxCheck = syntaxCheck;
    }

    public String getSemanticCheck() {
        return semanticCheck;
    }

    public void setSemanticCheck(String semanticCheck) {
        this.semanticCheck = semanticCheck;
    }
}

