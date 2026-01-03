package com.smart.platform.aiml.goldenrecord.dto;

import java.util.List;

/**
 * Response DTO for Golden Record search
 */
public class GoldenRecordSearchResponse {
    private Boolean success;
    private List<GoldenRecordResponse> records;
    private Integer total;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public List<GoldenRecordResponse> getRecords() {
        return records;
    }

    public void setRecords(List<GoldenRecordResponse> records) {
        this.records = records;
    }

    public Integer getTotal() {
        return total;
    }

    public void setTotal(Integer total) {
        this.total = total;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

