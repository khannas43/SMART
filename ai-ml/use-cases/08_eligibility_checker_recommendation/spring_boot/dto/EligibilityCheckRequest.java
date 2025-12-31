package com.smart.platform.eligibility.dto;

import java.util.List;
import java.util.Map;

/**
 * Request DTO for eligibility check
 */
public class EligibilityCheckRequest {
    private String familyId;
    private String beneficiaryId;
    private String sessionId;
    private String checkType;  // FULL_CHECK, SCHEME_SPECIFIC, QUICK_CHECK
    private String checkMode;  // WEB, MOBILE_APP, CHATBOT, ASSISTED
    private List<String> schemeCodes;
    private Map<String, Object> questionnaireResponses;  // For guest users
    private String language;  // en, hi, etc.

    // Getters and Setters
    public String getFamilyId() {
        return familyId;
    }

    public void setFamilyId(String familyId) {
        this.familyId = familyId;
    }

    public String getBeneficiaryId() {
        return beneficiaryId;
    }

    public void setBeneficiaryId(String beneficiaryId) {
        this.beneficiaryId = beneficiaryId;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getCheckType() {
        return checkType;
    }

    public void setCheckType(String checkType) {
        this.checkType = checkType;
    }

    public String getCheckMode() {
        return checkMode;
    }

    public void setCheckMode(String checkMode) {
        this.checkMode = checkMode;
    }

    public List<String> getSchemeCodes() {
        return schemeCodes;
    }

    public void setSchemeCodes(List<String> schemeCodes) {
        this.schemeCodes = schemeCodes;
    }

    public Map<String, Object> getQuestionnaireResponses() {
        return questionnaireResponses;
    }

    public void setQuestionnaireResponses(Map<String, Object> questionnaireResponses) {
        this.questionnaireResponses = questionnaireResponses;
    }

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }
}

