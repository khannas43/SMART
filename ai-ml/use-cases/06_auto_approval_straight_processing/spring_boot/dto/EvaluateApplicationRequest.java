package com.smart.platform.decision.dto;

/**
 * Request DTO for evaluating an application
 */
public class EvaluateApplicationRequest {
    private Integer applicationId;
    private String familyId;  // Optional, will be fetched if not provided
    private String schemeCode;  // Optional, will be fetched if not provided

    public Integer getApplicationId() {
        return applicationId;
    }

    public void setApplicationId(Integer applicationId) {
        this.applicationId = applicationId;
    }

    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }
}

