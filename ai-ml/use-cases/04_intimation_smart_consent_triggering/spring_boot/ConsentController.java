package com.smart.platform.aiml.intimation.controller;

import com.smart.platform.aiml.intimation.dto.*;
import com.smart.platform.aiml.intimation.service.ConsentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST Controller for Consent Management
 * Handles consent capture, status queries, and revocation
 */
@RestController
@RequestMapping("/api/v1/consent")
@CrossOrigin(origins = "*")
public class ConsentController {

    @Autowired
    private ConsentService consentService;

    /**
     * Capture consent from user
     * POST /api/v1/consent/capture
     */
    @PostMapping("/capture")
    public ResponseEntity<ConsentResponse> captureConsent(
            @RequestBody CaptureConsentRequest request) {
        
        ConsentResponse response = consentService.captureConsent(
            request.getFamilyId(),
            request.getSchemeCode(),
            request.getConsentValue(),
            request.getConsentMethod(),
            request.getChannel(),
            request.getSessionId(),
            request.getDeviceId(),
            request.getIpAddress()
        );
        
        return ResponseEntity.ok(response);
    }

    /**
     * Get consent status
     * GET /api/v1/consent/status?family_id={uuid}&scheme_code={code}
     */
    @GetMapping("/status")
    public ResponseEntity<ConsentStatusResponse> getConsentStatus(
            @RequestParam("family_id") String familyId,
            @RequestParam(value = "scheme_code", required = false) String schemeCode) {
        
        ConsentStatusResponse response = consentService.getConsentStatus(familyId, schemeCode);
        return ResponseEntity.ok(response);
    }

    /**
     * Revoke consent
     * POST /api/v1/consent/revoke
     */
    @PostMapping("/revoke")
    public ResponseEntity<RevokeConsentResponse> revokeConsent(
            @RequestBody RevokeConsentRequest request) {
        
        RevokeConsentResponse response = consentService.revokeConsent(
            request.getConsentId(),
            request.getRevocationReason()
        );
        
        return ResponseEntity.ok(response);
    }

    /**
     * Get consent history for a family
     * GET /api/v1/consent/history?family_id={uuid}
     */
    @GetMapping("/history")
    public ResponseEntity<ConsentHistoryResponse> getConsentHistory(
            @RequestParam("family_id") String familyId,
            @RequestParam(value = "scheme_code", required = false) String schemeCode) {
        
        ConsentHistoryResponse response = consentService.getConsentHistory(familyId, schemeCode);
        return ResponseEntity.ok(response);
    }

    /**
     * Verify OTP for strong consent
     * POST /api/v1/consent/verify-otp
     */
    @PostMapping("/verify-otp")
    public ResponseEntity<VerifyOtpResponse> verifyOtp(
            @RequestBody VerifyOtpRequest request) {
        
        VerifyOtpResponse response = consentService.verifyOtp(
            request.getConsentId(),
            request.getOtp()
        );
        
        return ResponseEntity.ok(response);
    }
}

