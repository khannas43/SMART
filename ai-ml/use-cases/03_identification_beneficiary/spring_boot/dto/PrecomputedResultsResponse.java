package com.smart.platform.aiml.eligibility.dto;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Response DTO for precomputed eligibility results
 */
public class PrecomputedResultsResponse {
    private Boolean success;
    private UUID familyId;
    private List<EvaluationResponse.SchemeEvaluation> schemes;
    private String snapshotTimestamp;
    private String error;

    // Static factory methods
    public static PrecomputedResultsResponse error(String errorMessage) {
        PrecomputedResultsResponse response = new PrecomputedResultsResponse();
        response.setSuccess(false);
        response.setError(errorMessage);
        return response;
    }

    public static PrecomputedResultsResponse fromMap(Map<String, Object> map) {
        PrecomputedResultsResponse response = new PrecomputedResultsResponse();
        
        Object success = map.get("success");
        if (success != null) {
            response.setSuccess(Boolean.parseBoolean(success.toString()));
        }
        
        Object familyId = map.get("family_id");
        if (familyId != null) {
            response.setFamilyId(UUID.fromString(familyId.toString()));
        }
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> schemesData = (List<Map<String, Object>>) map.get("schemes");
        if (schemesData != null) {
            List<EvaluationResponse.SchemeEvaluation> schemes = new java.util.ArrayList<>();
            for (Map<String, Object> schemeData : schemesData) {
                schemes.add(EvaluationResponse.SchemeEvaluation.fromMap(schemeData));
            }
            response.setSchemes(schemes);
        }
        
        response.setSnapshotTimestamp((String) map.get("snapshot_timestamp"));
        response.setError((String) map.get("error"));
        
        return response;
    }

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public UUID getFamilyId() {
        return familyId;
    }

    public void setFamilyId(UUID familyId) {
        this.familyId = familyId;
    }

    public List<EvaluationResponse.SchemeEvaluation> getSchemes() {
        return schemes;
    }

    public void setSchemes(List<EvaluationResponse.SchemeEvaluation> schemes) {
        this.schemes = schemes;
    }

    public String getSnapshotTimestamp() {
        return snapshotTimestamp;
    }

    public void setSnapshotTimestamp(String snapshotTimestamp) {
        this.snapshotTimestamp = snapshotTimestamp;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

