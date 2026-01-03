package com.smart.platform.aiml.eligibility.dto;

/**
 * Request DTO for rolling back a rule to a previous version
 */
public class RollbackRequest {
    private Integer versionId;

    // Getters and Setters
    public Integer getVersionId() {
        return versionId;
    }

    public void setVersionId(Integer versionId) {
        this.versionId = versionId;
    }
}

