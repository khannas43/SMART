package com.smart.platform.aiml.intimation.dto;

/**
 * Request DTO for capturing consent
 */
public class CaptureConsentRequest {
    private String familyId;
    private String schemeCode;
    private Boolean consentValue;
    private String consentMethod;  // click, tap, otp, e_sign, offline
    private String channel;  // sms, mobile_app, web, whatsapp, ivr, offline
    private String sessionId;
    private String deviceId;
    private String ipAddress;

    // Getters and Setters
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

    public Boolean getConsentValue() {
        return consentValue;
    }

    public void setConsentValue(Boolean consentValue) {
        this.consentValue = consentValue;
    }

    public String getConsentMethod() {
        return consentMethod;
    }

    public void setConsentMethod(String consentMethod) {
        this.consentMethod = consentMethod;
    }

    public String getChannel() {
        return channel;
    }

    public void setChannel(String channel) {
        this.channel = channel;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getIpAddress() {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }
}

