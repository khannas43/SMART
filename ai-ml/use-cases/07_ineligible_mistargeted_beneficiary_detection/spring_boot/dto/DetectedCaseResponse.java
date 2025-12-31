package com.smart.platform.detection.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for detected case
 */
public class DetectedCaseResponse {
    private Boolean success;
    private Integer caseId;
    private String beneficiaryId;
    private String familyId;
    private String schemeCode;
    private String caseType;  // HARD_INELIGIBLE, LIKELY_MIS_TARGETED, LOW_CONFIDENCE_FLAG
    private String confidenceLevel;  // HIGH, MEDIUM, LOW
    private String caseStatus;  // FLAGGED, UNDER_VERIFICATION, VERIFIED_INELIGIBLE, etc.
    private Double riskScore;
    private Double financialExposure;
    private Double vulnerabilityScore;
    private Integer priority;  // 1-10, lower = higher priority
    private String detectionRationale;
    private String recommendedAction;
    private String actionUrgency;  // IMMEDIATE, HIGH, MEDIUM, LOW
    private Map<String, Object> ruleEvaluations;
    private Map<String, Object> mlExplanations;
    private String assignedTo;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Integer getCaseId() {
        return caseId;
    }

    public void setCaseId(Integer caseId) {
        this.caseId = caseId;
    }

    public String getBeneficiaryId() {
        return beneficiaryId;
    }

    public void setBeneficiaryId(String beneficiaryId) {
        this.beneficiaryId = beneficiaryId;
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

    public String getCaseType() {
        return caseType;
    }

    public void setCaseType(String caseType) {
        this.caseType = caseType;
    }

    public String getConfidenceLevel() {
        return confidenceLevel;
    }

    public void setConfidenceLevel(String confidenceLevel) {
        this.confidenceLevel = confidenceLevel;
    }

    public String getCaseStatus() {
        return caseStatus;
    }

    public void setCaseStatus(String caseStatus) {
        this.caseStatus = caseStatus;
    }

    public Double getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(Double riskScore) {
        this.riskScore = riskScore;
    }

    public Double getFinancialExposure() {
        return financialExposure;
    }

    public void setFinancialExposure(Double financialExposure) {
        this.financialExposure = financialExposure;
    }

    public Double getVulnerabilityScore() {
        return vulnerabilityScore;
    }

    public void setVulnerabilityScore(Double vulnerabilityScore) {
        this.vulnerabilityScore = vulnerabilityScore;
    }

    public Integer getPriority() {
        return priority;
    }

    public void setPriority(Integer priority) {
        this.priority = priority;
    }

    public String getDetectionRationale() {
        return detectionRationale;
    }

    public void setDetectionRationale(String detectionRationale) {
        this.detectionRationale = detectionRationale;
    }

    public String getRecommendedAction() {
        return recommendedAction;
    }

    public void setRecommendedAction(String recommendedAction) {
        this.recommendedAction = recommendedAction;
    }

    public String getActionUrgency() {
        return actionUrgency;
    }

    public void setActionUrgency(String actionUrgency) {
        this.actionUrgency = actionUrgency;
    }

    public Map<String, Object> getRuleEvaluations() {
        return ruleEvaluations;
    }

    public void setRuleEvaluations(Map<String, Object> ruleEvaluations) {
        this.ruleEvaluations = ruleEvaluations;
    }

    public Map<String, Object> getMlExplanations() {
        return mlExplanations;
    }

    public void setMlExplanations(Map<String, Object> mlExplanations) {
        this.mlExplanations = mlExplanations;
    }

    public String getAssignedTo() {
        return assignedTo;
    }

    public void setAssignedTo(String assignedTo) {
        this.assignedTo = assignedTo;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}

