package com.smart.platform.aiml.goldenrecord.dto;

import java.util.List;

/**
 * Response DTO for duplicate candidates
 */
public class DuplicateCandidatesResponse {
    private Boolean success;
    private String janAadhaar;
    private List<DuplicateCandidate> candidates;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getJanAadhaar() {
        return janAadhaar;
    }

    public void setJanAadhaar(String janAadhaar) {
        this.janAadhaar = janAadhaar;
    }

    public List<DuplicateCandidate> getCandidates() {
        return candidates;
    }

    public void setCandidates(List<DuplicateCandidate> candidates) {
        this.candidates = candidates;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    /**
     * Nested DTO for duplicate candidate
     */
    public static class DuplicateCandidate {
        private Integer recordId;
        private String janAadhaar;
        private String name;
        private String mobile;
        private Double matchScore;

        // Getters and Setters
        public Integer getRecordId() {
            return recordId;
        }

        public void setRecordId(Integer recordId) {
            this.recordId = recordId;
        }

        public String getJanAadhaar() {
            return janAadhaar;
        }

        public void setJanAadhaar(String janAadhaar) {
            this.janAadhaar = janAadhaar;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getMobile() {
            return mobile;
        }

        public void setMobile(String mobile) {
            this.mobile = mobile;
        }

        public Double getMatchScore() {
            return matchScore;
        }

        public void setMatchScore(Double matchScore) {
            this.matchScore = matchScore;
        }
    }
}

