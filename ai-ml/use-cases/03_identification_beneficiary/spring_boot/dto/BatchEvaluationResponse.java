package com.smart.platform.aiml.eligibility.dto;

import java.util.Map;

/**
 * Response DTO for batch evaluation
 */
public class BatchEvaluationResponse {
    private Boolean success;
    private String batchId;
    private String status; // RUNNING, COMPLETED, FAILED
    private Integer totalFamilies;
    private Integer processedFamilies;
    private Integer eligibleCount;
    private String startedAt;
    private String completedAt;
    private String error;

    // Static factory methods
    public static BatchEvaluationResponse error(String errorMessage) {
        BatchEvaluationResponse response = new BatchEvaluationResponse();
        response.setSuccess(false);
        response.setError(errorMessage);
        return response;
    }

    public static BatchEvaluationResponse fromMap(Map<String, Object> map) {
        BatchEvaluationResponse response = new BatchEvaluationResponse();
        
        Object success = map.get("success");
        if (success != null) {
            response.setSuccess(Boolean.parseBoolean(success.toString()));
        }
        
        response.setBatchId((String) map.get("batch_id"));
        response.setStatus((String) map.get("status"));
        
        Object totalFamilies = map.get("total_families");
        if (totalFamilies != null) {
            response.setTotalFamilies(totalFamilies instanceof Number ? 
                ((Number) totalFamilies).intValue() : Integer.parseInt(totalFamilies.toString()));
        }
        
        Object processedFamilies = map.get("processed_families");
        if (processedFamilies != null) {
            response.setProcessedFamilies(processedFamilies instanceof Number ? 
                ((Number) processedFamilies).intValue() : Integer.parseInt(processedFamilies.toString()));
        }
        
        Object eligibleCount = map.get("eligible_count");
        if (eligibleCount != null) {
            response.setEligibleCount(eligibleCount instanceof Number ? 
                ((Number) eligibleCount).intValue() : Integer.parseInt(eligibleCount.toString()));
        }
        
        response.setStartedAt((String) map.get("started_at"));
        response.setCompletedAt((String) map.get("completed_at"));
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

    public String getBatchId() {
        return batchId;
    }

    public void setBatchId(String batchId) {
        this.batchId = batchId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getTotalFamilies() {
        return totalFamilies;
    }

    public void setTotalFamilies(Integer totalFamilies) {
        this.totalFamilies = totalFamilies;
    }

    public Integer getProcessedFamilies() {
        return processedFamilies;
    }

    public void setProcessedFamilies(Integer processedFamilies) {
        this.processedFamilies = processedFamilies;
    }

    public Integer getEligibleCount() {
        return eligibleCount;
    }

    public void setEligibleCount(Integer eligibleCount) {
        this.eligibleCount = eligibleCount;
    }

    public String getStartedAt() {
        return startedAt;
    }

    public void setStartedAt(String startedAt) {
        this.startedAt = startedAt;
    }

    public String getCompletedAt() {
        return completedAt;
    }

    public void setCompletedAt(String completedAt) {
        this.completedAt = completedAt;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

