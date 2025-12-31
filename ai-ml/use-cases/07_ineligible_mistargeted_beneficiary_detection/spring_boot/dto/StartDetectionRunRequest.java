package com.smart.platform.detection.dto;

import java.util.List;

/**
 * Request DTO for starting a detection run
 */
public class StartDetectionRunRequest {
    private String runType;  // FULL, INCREMENTAL, SCHEME_SPECIFIC, PRIORITY_BATCH
    private List<String> schemeCodes;
    private List<String> beneficiaryIds;
    private String startedBy;

    // Getters and Setters
    public String getRunType() {
        return runType;
    }

    public void setRunType(String runType) {
        this.runType = runType;
    }

    public List<String> getSchemeCodes() {
        return schemeCodes;
    }

    public void setSchemeCodes(List<String> schemeCodes) {
        this.schemeCodes = schemeCodes;
    }

    public List<String> getBeneficiaryIds() {
        return beneficiaryIds;
    }

    public void setBeneficiaryIds(List<String> beneficiaryIds) {
        this.beneficiaryIds = beneficiaryIds;
    }

    public String getStartedBy() {
        return startedBy;
    }

    public void setStartedBy(String startedBy) {
        this.startedBy = startedBy;
    }
}

