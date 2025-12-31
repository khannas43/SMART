package com.smart.platform.eligibility.controller;

import com.smart.platform.eligibility.dto.*;
import com.smart.platform.eligibility.service.EligibilityService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Eligibility Checker & Recommendations
 * Use Case ID: AI-PLATFORM-08
 */
@RestController
@RequestMapping("/eligibility")
@CrossOrigin(origins = "*")
public class EligibilityController {

    @Autowired
    private EligibilityService eligibilityService;

    /**
     * Perform eligibility check
     * POST /eligibility/check
     */
    @PostMapping("/check")
    public ResponseEntity<EligibilityCheckResponse> checkEligibility(
            @RequestBody EligibilityCheckRequest request) {
        try {
            EligibilityCheckResponse response = eligibilityService.checkEligibility(
                    request.getFamilyId(),
                    request.getBeneficiaryId(),
                    request.getQuestionnaireResponses(),
                    request.getSessionId(),
                    request.getSchemeCodes(),
                    request.getCheckType() != null ? request.getCheckType() : "FULL_CHECK",
                    request.getCheckMode() != null ? request.getCheckMode() : "WEB",
                    request.getLanguage() != null ? request.getLanguage() : "en"
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            EligibilityCheckResponse errorResponse = new EligibilityCheckResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get recommendations for logged-in user
     * GET /eligibility/recommendations?family_id={id}&beneficiary_id={id}&refresh={bool}&language={lang}
     */
    @GetMapping("/recommendations")
    public ResponseEntity<EligibilityCheckResponse> getRecommendations(
            @RequestParam String familyId,
            @RequestParam(required = false) String beneficiaryId,
            @RequestParam(required = false, defaultValue = "false") Boolean refresh,
            @RequestParam(required = false, defaultValue = "en") String language) {
        try {
            EligibilityCheckResponse response = eligibilityService.getRecommendations(
                    familyId, beneficiaryId, refresh, language);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            EligibilityCheckResponse errorResponse = new EligibilityCheckResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get questionnaire template
     * GET /eligibility/questionnaire?template_name={name}
     */
    @GetMapping("/questionnaire")
    public ResponseEntity<QuestionnaireResponse> getQuestionnaire(
            @RequestParam(required = false, defaultValue = "default_guest_questionnaire") String templateName) {
        try {
            QuestionnaireResponse response = eligibilityService.getQuestionnaire(templateName);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            QuestionnaireResponse errorResponse = new QuestionnaireResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get eligibility for specific scheme
     * GET /eligibility/schemes/{schemeCode}?family_id={id}&session_id={id}&questionnaire={json}
     */
    @GetMapping("/schemes/{schemeCode}")
    public ResponseEntity<EligibilityCheckResponse> getSchemeEligibility(
            @PathVariable String schemeCode,
            @RequestParam(required = false) String familyId,
            @RequestParam(required = false) String sessionId,
            @RequestParam(required = false) String questionnaire,
            @RequestParam(required = false, defaultValue = "en") String language) {
        try {
            EligibilityCheckResponse response = eligibilityService.getSchemeEligibility(
                    schemeCode, familyId, sessionId, questionnaire, language);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            EligibilityCheckResponse errorResponse = new EligibilityCheckResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get check history
     * GET /eligibility/history?family_id={id}&session_id={id}&limit={limit}
     */
    @GetMapping("/history")
    public ResponseEntity<List<EligibilityCheckResponse>> getCheckHistory(
            @RequestParam(required = false) String familyId,
            @RequestParam(required = false) String sessionId,
            @RequestParam(required = false, defaultValue = "10") Integer limit) {
        try {
            List<EligibilityCheckResponse> response = eligibilityService.getCheckHistory(
                    familyId, sessionId, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}

