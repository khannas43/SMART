package com.smart.platform.aiml.eligibility.dto;

/**
 * Request DTO for creating a rule set snapshot
 */
public class CreateSnapshotRequest {
    private String snapshotVersion;
    private String snapshotName;
    private String description;
    private String createdBy;

    // Getters and Setters
    public String getSnapshotVersion() {
        return snapshotVersion;
    }

    public void setSnapshotVersion(String snapshotVersion) {
        this.snapshotVersion = snapshotVersion;
    }

    public String getSnapshotName() {
        return snapshotName;
    }

    public void setSnapshotName(String snapshotName) {
        this.snapshotName = snapshotName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }
}

