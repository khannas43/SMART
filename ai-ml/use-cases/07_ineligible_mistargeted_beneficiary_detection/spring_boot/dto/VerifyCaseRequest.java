package com.smart.platform.detection.dto;

/**
 * Request DTO for verifying a case
 */
public class VerifyCaseRequest {
    private String verificationMethod;  // FIELD_VERIFICATION, DOCUMENT_REVIEW, CROSS_CHECK, APPEAL_REVIEW
    private String verificationResult;
    private String decisionType;  // CONFIRMED_INELIGIBLE, FALSE_POSITIVE, REQUIRES_RECALCULATION, APPEAL_GRANTED
    private String decisionRationale;
    private String verifiedBy;
    private String verifiedByName;

    // Getters and Setters
    public String getVerificationMethod() {
        return verificationMethod;
    }

    public void setVerificationMethod(String verificationMethod) {
        this.verificationMethod = verificationMethod;
    }

    public String getVerificationResult() {
        return verificationResult;
    }

    public void setVerificationResult(String verificationResult) {
        this.verificationResult = verificationResult;
    }

    public String getDecisionType() {
        return decisionType;
    }

    public void setDecisionType(String decisionType) {
        this.decisionType = decisionType;
    }

    public String getDecisionRationale() {
        return decisionRationale;
    }

    public void setDecisionRationale(String decisionRationale) {
        this.decisionRationale = decisionRationale;
    }

    public String getVerifiedBy() {
        return verifiedBy;
    }

    public void setVerifiedBy(String verifiedBy) {
        this.verifiedBy = verifiedBy;
    }

    public String getVerifiedByName() {
        return verifiedByName;
    }

    public void setVerifiedByName(String verifiedByName) {
        this.verifiedByName = verifiedByName;
    }
}

