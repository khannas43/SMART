package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Response DTO for citizen-facing eligibility hints
 */
public class CitizenHintsResponse {
    private Boolean success;
    private List<SchemeHint> hints;
    private String error;

    public CitizenHintsResponse() {
    }

    public CitizenHintsResponse(List<SchemeHint> hints) {
        this.success = true;
        this.hints = hints;
    }

    // Static factory methods
    public static CitizenHintsResponse error(String errorMessage) {
        CitizenHintsResponse response = new CitizenHintsResponse();
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

    public List<SchemeHint> getHints() {
        return hints;
    }

    public void setHints(List<SchemeHint> hints) {
        this.hints = hints;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

