package com.smart.platform.detection.controller;

import com.smart.platform.detection.dto.*;
import com.smart.platform.detection.service.DetectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Beneficiary Detection APIs
 * Use Case ID: AI-PLATFORM-07
 */
@RestController
@RequestMapping("/detection")
@CrossOrigin(origins = "*")
public class DetectionController {

    @Autowired
    private DetectionService detectionService;

    /**
     * Start a detection run
     * POST /detection/run
     */
    @PostMapping("/run")
    public ResponseEntity<DetectionRunResponse> startDetectionRun(
            @RequestBody StartDetectionRunRequest request) {
        try {
            DetectionRunResponse response = detectionService.startDetectionRun(
                    request.getRunType(),
                    request.getSchemeCodes(),
                    request.getBeneficiaryIds(),
                    request.getStartedBy()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DetectionRunResponse errorResponse = new DetectionRunResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get detection run details
     * GET /detection/run/{runId}
     */
    @GetMapping("/run/{runId}")
    public ResponseEntity<DetectionRunResponse> getDetectionRun(
            @PathVariable Integer runId) {
        try {
            DetectionRunResponse response = detectionService.getDetectionRun(runId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DetectionRunResponse errorResponse = new DetectionRunResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * List detection runs
     * GET /detection/runs?status={status}&limit={limit}
     */
    @GetMapping("/runs")
    public ResponseEntity<List<DetectionRunResponse>> listDetectionRuns(
            @RequestParam(required = false) String status,
            @RequestParam(required = false, defaultValue = "50") Integer limit) {
        try {
            List<DetectionRunResponse> response = detectionService.listDetectionRuns(status, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get detected case details
     * GET /detection/case/{caseId}
     */
    @GetMapping("/case/{caseId}")
    public ResponseEntity<DetectedCaseResponse> getCase(
            @PathVariable Integer caseId) {
        try {
            DetectedCaseResponse response = detectionService.getCase(caseId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DetectedCaseResponse errorResponse = new DetectedCaseResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * List detected cases
     * GET /detection/cases?schemeCode={code}&caseType={type}&status={status}&priority={priority}&limit={limit}
     */
    @GetMapping("/cases")
    public ResponseEntity<CaseListResponse> listCases(
            @RequestParam(required = false) String schemeCode,
            @RequestParam(required = false) String caseType,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) Integer priority,
            @RequestParam(required = false, defaultValue = "100") Integer limit) {
        try {
            CaseListResponse response = detectionService.listCases(
                    schemeCode, caseType, status, priority, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            CaseListResponse errorResponse = new CaseListResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Verify a detected case
     * POST /detection/case/{caseId}/verify
     */
    @PostMapping("/case/{caseId}/verify")
    public ResponseEntity<DetectedCaseResponse> verifyCase(
            @PathVariable Integer caseId,
            @RequestBody VerifyCaseRequest request) {
        try {
            DetectedCaseResponse response = detectionService.verifyCase(
                    caseId,
                    request.getVerificationMethod(),
                    request.getVerificationResult(),
                    request.getDecisionType(),
                    request.getDecisionRationale(),
                    request.getVerifiedBy(),
                    request.getVerifiedByName()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DetectedCaseResponse errorResponse = new DetectedCaseResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get worklist for an officer
     * GET /detection/worklist?officerId={id}&queue={queue}&status={status}
     */
    @GetMapping("/worklist")
    public ResponseEntity<WorklistResponse> getWorklist(
            @RequestParam(required = false) String officerId,
            @RequestParam(required = false) String queue,
            @RequestParam(required = false) String status) {
        try {
            WorklistResponse response = detectionService.getWorklist(officerId, queue, status);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            WorklistResponse errorResponse = new WorklistResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Assign case to officer
     * POST /detection/worklist/assign
     */
    @PostMapping("/worklist/assign")
    public ResponseEntity<WorklistResponse> assignCase(
            @RequestParam Integer caseId,
            @RequestParam String officerId,
            @RequestParam(required = false) String queue,
            @RequestParam(required = false) String assignedBy) {
        try {
            WorklistResponse response = detectionService.assignCase(
                    caseId, officerId, queue, assignedBy);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            WorklistResponse errorResponse = new WorklistResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get leakage analytics
     * GET /detection/analytics?schemeCode={code}&startDate={date}&endDate={date}
     */
    @GetMapping("/analytics")
    public ResponseEntity<LeakageAnalyticsResponse> getLeakageAnalytics(
            @RequestParam(required = false) String schemeCode,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        try {
            LeakageAnalyticsResponse response = detectionService.getLeakageAnalytics(
                    schemeCode, startDate, endDate);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            LeakageAnalyticsResponse errorResponse = new LeakageAnalyticsResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Detect single beneficiary (on-demand)
     * POST /detection/detect
     */
    @PostMapping("/detect")
    public ResponseEntity<DetectedCaseResponse> detectBeneficiary(
            @RequestParam String beneficiaryId,
            @RequestParam(required = false) String familyId,
            @RequestParam String schemeCode) {
        try {
            DetectedCaseResponse response = detectionService.detectBeneficiary(
                    beneficiaryId, familyId, schemeCode);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DetectedCaseResponse errorResponse = new DetectedCaseResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}

