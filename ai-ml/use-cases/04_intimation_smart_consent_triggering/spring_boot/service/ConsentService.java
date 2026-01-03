package com.smart.platform.aiml.intimation.service;

import com.smart.platform.aiml.intimation.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

/**
 * Service layer for Consent Management
 * Use Case ID: AI-PLATFORM-04
 */
@Service
public class ConsentService {

    @Autowired
    private PythonIntimationClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Capture consent from user
     */
    public ConsentResponse captureConsent(
            String familyId,
            String schemeCode,
            Boolean consentValue,
            String consentMethod,
            String channel,
            String sessionId,
            String deviceId,
            String ipAddress) {
        
        ConsentResponse response = new ConsentResponse();
        
        try {
            Map<String, Object> result = pythonClient.createConsent(
                    familyId, schemeCode, consentValue, consentMethod, channel,
                    sessionId, deviceId, ipAddress);
            
            response.setSuccess(true);
            
            Object consentId = result.get("consent_id");
            if (consentId != null) {
                response.setConsentId(consentId instanceof Number ? 
                    ((Number) consentId).intValue() : Integer.parseInt(consentId.toString()));
            }
            
            response.setStatus((String) result.get("status"));
            response.setConsentType((String) result.get("consent_type"));
            
            Object validUntil = result.get("valid_until");
            if (validUntil != null) {
                response.setValidUntil(validUntil.toString());
            }
            
            response.setMessage("Consent captured successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to capture consent: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get consent status
     */
    public ConsentStatusResponse getConsentStatus(String familyId, String schemeCode) {
        ConsentStatusResponse response = new ConsentStatusResponse();
        
        try {
            Map<String, Object> result = pythonClient.getConsentStatus(familyId, schemeCode);
            
            if (result == null || result.isEmpty()) {
                response.setSuccess(false);
                response.setMessage("No consent found");
                return response;
            }
            
            response.setSuccess(true);
            
            Object consentId = result.get("consent_id");
            if (consentId != null) {
                response.setConsentId(consentId instanceof Number ? 
                    ((Number) consentId).intValue() : Integer.parseInt(consentId.toString()));
            }
            
            response.setFamilyId((String) result.get("family_id"));
            response.setSchemeCode((String) result.get("scheme_code"));
            response.setStatus((String) result.get("status"));
            response.setConsentType((String) result.get("consent_type"));
            
            Object consentDate = result.get("consent_date");
            if (consentDate != null) {
                response.setConsentDate(consentDate.toString());
            }
            
            Object validUntil = result.get("valid_until");
            if (validUntil != null) {
                response.setValidUntil(validUntil.toString());
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get consent status: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Revoke consent
     */
    public RevokeConsentResponse revokeConsent(Integer consentId, String revocationReason) {
        RevokeConsentResponse response = new RevokeConsentResponse();
        
        try {
            Map<String, Object> result = pythonClient.revokeConsent(consentId, revocationReason);
            
            response.setSuccess(true);
            response.setConsentId(consentId);
            response.setStatus((String) result.get("status"));
            response.setMessage("Consent revoked successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to revoke consent: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get consent history for a family
     */
    public ConsentHistoryResponse getConsentHistory(String familyId, String schemeCode) {
        ConsentHistoryResponse response = new ConsentHistoryResponse();
        
        try {
            Map<String, Object> result = pythonClient.getConsentHistory(familyId, schemeCode);
            
            response.setSuccess(true);
            response.setFamilyId(familyId);
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> history = (List<Map<String, Object>>) result.get("history");
            if (history != null) {
                List<ConsentHistoryResponse.ConsentRecord> records = new ArrayList<>();
                for (Map<String, Object> record : history) {
                    ConsentHistoryResponse.ConsentRecord consentRecord = 
                        new ConsentHistoryResponse.ConsentRecord();
                    
                    Object consentId = record.get("consent_id");
                    if (consentId != null) {
                        consentRecord.setConsentId(consentId instanceof Number ? 
                            ((Number) consentId).intValue() : Integer.parseInt(consentId.toString()));
                    }
                    
                    consentRecord.setSchemeCode((String) record.get("scheme_code"));
                    consentRecord.setStatus((String) record.get("status"));
                    consentRecord.setConsentType((String) record.get("consent_type"));
                    consentRecord.setConsentMethod((String) record.get("consent_method"));
                    consentRecord.setChannel((String) record.get("consent_channel"));
                    
                    Object consentDate = record.get("created_at");
                    if (consentDate != null) {
                        consentRecord.setConsentDate(consentDate.toString());
                    }
                    
                    Object validUntil = record.get("valid_until");
                    if (validUntil != null) {
                        consentRecord.setValidUntil(validUntil.toString());
                    }
                    
                    records.add(consentRecord);
                }
                response.setHistory(records);
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get consent history: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Verify OTP for strong consent
     */
    public VerifyOtpResponse verifyOtp(Integer consentId, String otp) {
        VerifyOtpResponse response = new VerifyOtpResponse();
        
        try {
            Map<String, Object> result = pythonClient.verifyOtp(consentId, otp);
            
            Object verified = result.get("verified");
            if (verified != null && Boolean.parseBoolean(verified.toString())) {
                response.setSuccess(true);
                response.setVerified(true);
                response.setMessage("OTP verified successfully");
                
                @SuppressWarnings("unchecked")
                Map<String, Object> consent = (Map<String, Object>) result.get("consent");
                if (consent != null) {
                    response.setConsentId(consentId);
                    response.setStatus((String) consent.get("status"));
                }
            } else {
                response.setSuccess(false);
                response.setVerified(false);
                response.setMessage("OTP verification failed");
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setVerified(false);
            response.setError("Failed to verify OTP: " + e.getMessage());
        }
        
        return response;
    }
}

