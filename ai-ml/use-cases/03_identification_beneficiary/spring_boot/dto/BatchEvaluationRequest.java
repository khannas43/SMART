package com.smart.platform.aiml.eligibility.dto;

import java.util.List;

/**
 * Request DTO for batch evaluation
 */
public class BatchEvaluationRequest {
    private List<String> schemeIds;
    private List<Integer> districtIds;
    private Integer maxFamilies;

    // Getters and Setters
    public List<String> getSchemeIds() {
        return schemeIds;
    }

    public void setSchemeIds(List<String> schemeIds) {
        this.schemeIds = schemeIds;
    }

    public List<Integer> getDistrictIds() {
        return districtIds;
    }

    public void setDistrictIds(List<Integer> districtIds) {
        this.districtIds = districtIds;
    }

    public Integer getMaxFamilies() {
        return maxFamilies;
    }

    public void setMaxFamilies(Integer maxFamilies) {
        this.maxFamilies = maxFamilies;
    }
}

