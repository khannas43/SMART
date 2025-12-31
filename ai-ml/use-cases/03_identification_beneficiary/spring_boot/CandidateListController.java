package com.smart.platform.aiml.eligibility.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.smart.platform.aiml.eligibility.service.EligibilityEvaluationService;
import com.smart.platform.aiml.eligibility.dto.*;

import java.util.List;

/**
 * REST Controller for Candidate Lists (Departmental Worklists)
 * Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries
 */
@RestController
@RequestMapping("/api/v1/eligibility/candidate-list")
@CrossOrigin(origins = "*")
public class CandidateListController {

    @Autowired
    private EligibilityEvaluationService evaluationService;

    /**
     * Get candidate list for a scheme (departmental worklist)
     * GET /eligibility/candidate-list?scheme_id={scheme_id}&district={district_id}&score>={min_score}
     */
    @GetMapping
    public ResponseEntity<CandidateListResponse> getCandidateList(
            @RequestParam("scheme_id") String schemeId,
            @RequestParam(value = "district", required = false) Integer districtId,
            @RequestParam(value = "score", defaultValue = "0.5") double minScore,
            @RequestParam(value = "limit", defaultValue = "100") int limit
    ) {
        try {
            List<Candidate> candidates = evaluationService.generateDepartmentalWorklist(
                    schemeId,
                    districtId,
                    minScore,
                    limit
            );
            return ResponseEntity.ok(new CandidateListResponse(candidates));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(CandidateListResponse.error(e.getMessage()));
        }
    }

    /**
     * Trigger batch evaluation
     * POST /eligibility/candidate-list/batch
     */
    @PostMapping("/batch")
    public ResponseEntity<BatchEvaluationResponse> triggerBatchEvaluation(
            @RequestBody(required = false) BatchEvaluationRequest request
    ) {
        try {
            BatchEvaluationResponse response = evaluationService.evaluateBatch(
                    request != null ? request.getSchemeIds() : null,
                    request != null ? request.getDistrictIds() : null,
                    request != null ? request.getMaxFamilies() : null
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(BatchEvaluationResponse.error(e.getMessage()));
        }
    }

    /**
     * Get batch evaluation status
     * GET /eligibility/candidate-list/batch/{batch_id}
     */
    @GetMapping("/batch/{batch_id}")
    public ResponseEntity<BatchStatusResponse> getBatchStatus(
            @PathVariable("batch_id") String batchId
    ) {
        try {
            BatchStatusResponse response = evaluationService.getBatchStatus(batchId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(BatchStatusResponse.error(e.getMessage()));
        }
    }
}

