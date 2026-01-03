package com.smart.platform.aiml.eligibility.dto;

import java.util.Map;

/**
 * Response DTO for batch evaluation status
 */
public class BatchStatusResponse {
    private Boolean success;
    private String batchId;
    private String status; // RUNNING, COMPLETED, FAILED, CANCELLED
    private Integer totalFamilies;
    private Integer processedFamilies;
    private Integer eligibleCount;
    private Double progressPercentage;
    private String startedAt;
    private String completedAt;
    private String error;

    // Static factory methods
    public static BatchStatusResponse error(String errorMessage) {
        BatchStatusResponse response = new BatchStatusResponse();
        response.setSuccess(false);
        response.setError(errorMessage);
        return response;
    }

    public static BatchStatusResponse fromMap(Map<String, Object> map) {
        BatchStatusResponse response = new BatchStatusResponse();
        
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
        
        Object progressPercentage = map.get("progress_percentage");
        if (progressPercentage != null) {
            response.setProgressPercentage(progressPercentage instanceof Number ? 
                ((Number) progressPercentage).doubleValue() : Double.parseDouble(progressPercentage.toString()));
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

    public Double getProgressPercentage() {
        return progressPercentage;
    }

    public void setProgressPercentage(Double progressPercentage) {
        this.progressPercentage = progressPercentage;
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

