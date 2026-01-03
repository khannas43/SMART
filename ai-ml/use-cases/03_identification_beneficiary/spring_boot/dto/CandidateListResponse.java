package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Response DTO for candidate list
 */
public class CandidateListResponse {
    private Boolean success;
    private List<Candidate> candidates;
    private Integer totalCount;
    private String error;

    public CandidateListResponse() {
    }

    public CandidateListResponse(List<Candidate> candidates) {
        this.success = true;
        this.candidates = candidates;
        this.totalCount = candidates != null ? candidates.size() : 0;
    }

    // Static factory methods
    public static CandidateListResponse error(String errorMessage) {
        CandidateListResponse response = new CandidateListResponse();
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

    public List<Candidate> getCandidates() {
        return candidates;
    }

    public void setCandidates(List<Candidate> candidates) {
        this.candidates = candidates;
        this.totalCount = candidates != null ? candidates.size() : 0;
    }

    public Integer getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

