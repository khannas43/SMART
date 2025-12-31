package com.smart.platform.decision.controller;

import com.smart.platform.decision.dto.*;
import com.smart.platform.decision.service.DecisionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Decision Evaluation APIs
 * Use Case ID: AI-PLATFORM-06
 */
@RestController
@RequestMapping("/decision")
@CrossOrigin(origins = "*")
public class DecisionController {

    @Autowired
    private DecisionService decisionService;

    /**
     * Evaluate an application and make a decision
     * POST /decision/evaluateApplication
     */
    @PostMapping("/evaluateApplication")
    public ResponseEntity<DecisionResponse> evaluateApplication(
            @RequestBody EvaluateApplicationRequest request) {
        try {
            DecisionResponse response = decisionService.evaluateApplication(
                    request.getApplicationId(),
                    request.getFamilyId(),
                    request.getSchemeCode()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DecisionResponse errorResponse = new DecisionResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get decision history for an application
     * GET /decision/history?application_id={id}
     */
    @GetMapping("/history")
    public ResponseEntity<DecisionHistoryResponse> getDecisionHistory(
            @RequestParam Integer applicationId) {
        try {
            DecisionHistoryResponse response = decisionService.getDecisionHistory(applicationId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DecisionHistoryResponse errorResponse = new DecisionHistoryResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get decision details by decision ID
     * GET /decision/{decisionId}
     */
    @GetMapping("/{decisionId}")
    public ResponseEntity<DecisionDetailResponse> getDecision(
            @PathVariable Integer decisionId) {
        try {
            DecisionDetailResponse response = decisionService.getDecision(decisionId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DecisionDetailResponse errorResponse = new DecisionDetailResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Override a decision (officer override)
     * POST /decision/override
     */
    @PostMapping("/override")
    public ResponseEntity<OverrideResponse> overrideDecision(
            @RequestBody OverrideRequest request) {
        try {
            OverrideResponse response = decisionService.overrideDecision(
                    request.getDecisionId(),
                    request.getOverrideDecisionType(),
                    request.getOverrideReason(),
                    request.getOfficerId(),
                    request.getOfficerName()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            OverrideResponse errorResponse = new OverrideResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get decisions by family ID
     * GET /decision/family/{familyId}
     */
    @GetMapping("/family/{familyId}")
    public ResponseEntity<DecisionListResponse> getDecisionsByFamily(
            @PathVariable String familyId) {
        try {
            DecisionListResponse response = decisionService.getDecisionsByFamily(familyId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DecisionListResponse errorResponse = new DecisionListResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get decisions by scheme code
     * GET /decision/scheme/{schemeCode}
     */
    @GetMapping("/scheme/{schemeCode}")
    public ResponseEntity<DecisionListResponse> getDecisionsByScheme(
            @PathVariable String schemeCode) {
        try {
            DecisionListResponse response = decisionService.getDecisionsByScheme(schemeCode);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DecisionListResponse errorResponse = new DecisionListResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get STP (Straight-Through Processing) metrics
     * GET /decision/metrics/stp
     */
    @GetMapping("/metrics/stp")
    public ResponseEntity<STPMetricsResponse> getSTPMetrics(
            @RequestParam(required = false) String schemeCode,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        try {
            STPMetricsResponse response = decisionService.getSTPMetrics(
                    schemeCode, startDate, endDate);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            STPMetricsResponse errorResponse = new STPMetricsResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}

