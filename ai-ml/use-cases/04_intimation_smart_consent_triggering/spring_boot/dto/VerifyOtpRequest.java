package com.smart.platform.aiml.intimation.dto;

/**
 * Request DTO for verifying OTP
 */
public class VerifyOtpRequest {
    private Integer consentId;
    private String otp;

    // Getters and Setters
    public Integer getConsentId() {
        return consentId;
    }

    public void setConsentId(Integer consentId) {
        this.consentId = consentId;
    }

    public String getOtp() {
        return otp;
    }

    public void setOtp(String otp) {
        this.otp = otp;
    }
}

