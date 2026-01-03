package com.smart.platform.aiml.intimation.dto;

import java.util.List;
import java.util.Map;

/**
 * Request DTO for scheduling intimation
 */
public class ScheduleIntimationRequest {
    private String schemeCode;
    private List<String> familyIds;
    private String priority;
    private Map<String, Object> eligibilityMeta;

    // Getters and Setters
    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public List<String> getFamilyIds() {
        return familyIds;
    }

    public void setFamilyIds(List<String> familyIds) {
        this.familyIds = familyIds;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public Map<String, Object> getEligibilityMeta() {
        return eligibilityMeta;
    }

    public void setEligibilityMeta(Map<String, Object> eligibilityMeta) {
        this.eligibilityMeta = eligibilityMeta;
    }
}

