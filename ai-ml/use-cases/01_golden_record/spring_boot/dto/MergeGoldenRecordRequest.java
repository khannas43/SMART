package com.smart.platform.aiml.goldenrecord.dto;

import java.util.List;

/**
 * Request DTO for merging Golden Records
 */
public class MergeGoldenRecordRequest {
    private List<Integer> sourceRecordIds;
    private String targetJanAadhaar;
    private String approvedBy;

    // Getters and Setters
    public List<Integer> getSourceRecordIds() {
        return sourceRecordIds;
    }

    public void setSourceRecordIds(List<Integer> sourceRecordIds) {
        this.sourceRecordIds = sourceRecordIds;
    }

    public String getTargetJanAadhaar() {
        return targetJanAadhaar;
    }

    public void setTargetJanAadhaar(String targetJanAadhaar) {
        this.targetJanAadhaar = targetJanAadhaar;
    }

    public String getApprovedBy() {
        return approvedBy;
    }

    public void setApprovedBy(String approvedBy) {
        this.approvedBy = approvedBy;
    }
}

