package com.smart.platform.detection.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for detection run
 */
public class DetectionRunResponse {
    private Boolean success;
    private Integer runId;
    private String runType;
    private String runStatus;  // RUNNING, COMPLETED, FAILED, CANCELLED
    private Integer totalBeneficiariesScanned;
    private Integer totalCasesFlagged;
    private Map<String, Integer> casesByClassification;
    private String startedBy;
    private String error;
    private List<Integer> flaggedCaseIds;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getRunId() {
        return runId;
    }

    public void setRunId(Integer runId) {
        this.runId = runId;
    }

    public String getRunType() {
        return runType;
    }

    public void setRunType(String runType) {
        this.runType = runType;
    }

    public String getRunStatus() {
        return runStatus;
    }

    public void setRunStatus(String runStatus) {
        this.runStatus = runStatus;
    }

    public Integer getTotalBeneficiariesScanned() {
        return totalBeneficiariesScanned;
    }

    public void setTotalBeneficiariesScanned(Integer totalBeneficiariesScanned) {
        this.totalBeneficiariesScanned = totalBeneficiariesScanned;
    }

    public Integer getTotalCasesFlagged() {
        return totalCasesFlagged;
    }

    public void setTotalCasesFlagged(Integer totalCasesFlagged) {
        this.totalCasesFlagged = totalCasesFlagged;
    }

    public Map<String, Integer> getCasesByClassification() {
        return casesByClassification;
    }

    public void setCasesByClassification(Map<String, Integer> casesByClassification) {
        this.casesByClassification = casesByClassification;
    }

    public String getStartedBy() {
        return startedBy;
    }

    public void setStartedBy(String startedBy) {
        this.startedBy = startedBy;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public List<Integer> getFlaggedCaseIds() {
        return flaggedCaseIds;
    }

    public void setFlaggedCaseIds(List<Integer> flaggedCaseIds) {
        this.flaggedCaseIds = flaggedCaseIds;
    }
}

