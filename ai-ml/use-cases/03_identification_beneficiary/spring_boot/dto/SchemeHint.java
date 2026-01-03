package com.smart.platform.aiml.eligibility.dto;

import java.util.Map;

/**
 * DTO for citizen-facing scheme hint
 */
public class SchemeHint {
    private String schemeCode;
    private String schemeName;
    private String hintText;
    private String actionText;
    private String actionUrl;
    private Double confidenceScore;

    // Static factory method
    public static SchemeHint fromMap(Map<String, Object> map) {
        SchemeHint hint = new SchemeHint();
        hint.setSchemeCode((String) map.get("scheme_code"));
        hint.setSchemeName((String) map.get("scheme_name"));
        hint.setHintText((String) map.get("hint_text"));
        hint.setActionText((String) map.get("action_text"));
        hint.setActionUrl((String) map.get("action_url"));
        
        Object confidenceScore = map.get("confidence_score");
        if (confidenceScore != null) {
            hint.setConfidenceScore(confidenceScore instanceof Number ? 
                ((Number) confidenceScore).doubleValue() : Double.parseDouble(confidenceScore.toString()));
        }
        
        return hint;
    }

    // Getters and Setters
    public String getSchemeCode() {
        return schemeCode;
    }

    public void setSchemeCode(String schemeCode) {
        this.schemeCode = schemeCode;
    }

    public String getSchemeName() {
        return schemeName;
    }

    public void setSchemeName(String schemeName) {
        this.schemeName = schemeName;
    }

    public String getHintText() {
        return hintText;
    }

    public void setHintText(String hintText) {
        this.hintText = hintText;
    }

    public String getActionText() {
        return actionText;
    }

    public void setActionText(String actionText) {
        this.actionText = actionText;
    }

    public String getActionUrl() {
        return actionUrl;
    }

    public void setActionUrl(String actionUrl) {
        this.actionUrl = actionUrl;
    }

    public Double getConfidenceScore() {
        return confidenceScore;
    }

    public void setConfidenceScore(Double confidenceScore) {
        this.confidenceScore = confidenceScore;
    }
}

