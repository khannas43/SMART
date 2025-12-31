package com.smart.platform.aiml.eligibility.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.smart.platform.aiml.eligibility.service.EligibilityEvaluationService;
import com.smart.platform.aiml.eligibility.dto.*;

import java.util.List;
import java.util.UUID;

/**
 * REST Controller for Eligibility Evaluation
 * Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries
 */
@RestController
@RequestMapping("/api/v1/eligibility")
@CrossOrigin(origins = "*")
public class EligibilityEvaluationController {

    @Autowired
    private EligibilityEvaluationService evaluationService;

    /**
     * Evaluate eligibility for a family (on-demand)
     * POST /eligibility/evaluate?family_id={family_id}
     */
    @PostMapping("/evaluate")
    public ResponseEntity<EvaluationResponse> evaluateFamily(
            @RequestParam("family_id") String familyId,
            @RequestParam(value = "scheme_ids", required = false) List<String> schemeIds,
            @RequestParam(value = "use_ml", defaultValue = "true") boolean useMl
    ) {
        try {
            EvaluationResponse response = evaluationService.evaluateFamily(
                    UUID.fromString(familyId),
                    schemeIds,
                    useMl
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(EvaluationResponse.error(e.getMessage()));
        }
    }

    /**
     * Get precomputed eligibility results for a family
     * GET /eligibility/precomputed?family_id={family_id}
     */
    @GetMapping("/precomputed")
    public ResponseEntity<PrecomputedResultsResponse> getPrecomputedResults(
            @RequestParam("family_id") String familyId,
            @RequestParam(value = "scheme_ids", required = false) List<String> schemeIds
    ) {
        try {
            PrecomputedResultsResponse response = evaluationService.getPrecomputedResults(
                    UUID.fromString(familyId),
                    schemeIds
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(PrecomputedResultsResponse.error(e.getMessage()));
        }
    }

    /**
     * Get citizen-facing eligibility hints
     * GET /eligibility/citizen-hints?family_id={family_id}
     */
    @GetMapping("/citizen-hints")
    public ResponseEntity<CitizenHintsResponse> getCitizenHints(
            @RequestParam("family_id") String familyId
    ) {
        try {
            List<SchemeHint> hints = evaluationService.generateCitizenHints(
                    UUID.fromString(familyId)
            );
            return ResponseEntity.ok(new CitizenHintsResponse(hints));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(CitizenHintsResponse.error(e.getMessage()));
        }
    }

    /**
     * Get scheme configuration and rules
     * GET /eligibility/config/scheme/{scheme_id}
     */
    @GetMapping("/config/scheme/{scheme_id}")
    public ResponseEntity<SchemeConfigResponse> getSchemeConfig(
            @PathVariable("scheme_id") String schemeId
    ) {
        try {
            SchemeConfigResponse response = evaluationService.getSchemeConfig(schemeId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(SchemeConfigResponse.error(e.getMessage()));
        }
    }
}

