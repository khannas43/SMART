package com.smart.platform.aiml.goldenrecord.controller;

import com.smart.platform.aiml.goldenrecord.dto.*;
import com.smart.platform.aiml.goldenrecord.service.GoldenRecordService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Golden Record Management
 * Use Case: AI-PLATFORM-01 - Golden Records
 */
@RestController
@RequestMapping("/api/v1/golden-record")
@CrossOrigin(origins = "*")
public class GoldenRecordController {

    @Autowired
    private GoldenRecordService goldenRecordService;

    /**
     * Get Golden Record by Jan Aadhaar
     * GET /api/v1/golden-record/{jan_aadhaar}
     */
    @GetMapping("/{jan_aadhaar}")
    public ResponseEntity<GoldenRecordResponse> getGoldenRecord(
            @PathVariable("jan_aadhaar") String janAadhaar) {
        try {
            GoldenRecordResponse response = goldenRecordService.getGoldenRecord(janAadhaar);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            GoldenRecordResponse errorResponse = new GoldenRecordResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError("Failed to get golden record: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Search Golden Records
     * GET /api/v1/golden-record/search?query={query}&limit={limit}
     */
    @GetMapping("/search")
    public ResponseEntity<GoldenRecordSearchResponse> searchGoldenRecords(
            @RequestParam(value = "query", required = false) String query,
            @RequestParam(value = "name", required = false) String name,
            @RequestParam(value = "mobile", required = false) String mobile,
            @RequestParam(value = "limit", defaultValue = "20") Integer limit) {
        try {
            GoldenRecordSearchResponse response = goldenRecordService.searchGoldenRecords(
                    query, name, mobile, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            GoldenRecordSearchResponse errorResponse = new GoldenRecordSearchResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError("Failed to search golden records: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Trigger Golden Record extraction
     * POST /api/v1/golden-record/extract
     */
    @PostMapping("/extract")
    public ResponseEntity<ExtractGoldenRecordResponse> extractGoldenRecord(
            @RequestBody ExtractGoldenRecordRequest request) {
        try {
            ExtractGoldenRecordResponse response = goldenRecordService.extractGoldenRecord(
                    request.getJanAadhaar(),
                    request.getForceRefresh());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ExtractGoldenRecordResponse errorResponse = new ExtractGoldenRecordResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError("Failed to extract golden record: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Manual merge approval
     * POST /api/v1/golden-record/merge
     */
    @PostMapping("/merge")
    public ResponseEntity<MergeGoldenRecordResponse> mergeGoldenRecords(
            @RequestBody MergeGoldenRecordRequest request) {
        try {
            MergeGoldenRecordResponse response = goldenRecordService.mergeGoldenRecords(
                    request.getSourceRecordIds(),
                    request.getTargetJanAadhaar(),
                    request.getApprovedBy());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            MergeGoldenRecordResponse errorResponse = new MergeGoldenRecordResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError("Failed to merge golden records: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Get duplicate candidates for a record
     * GET /api/v1/golden-record/{jan_aadhaar}/duplicates
     */
    @GetMapping("/{jan_aadhaar}/duplicates")
    public ResponseEntity<DuplicateCandidatesResponse> getDuplicateCandidates(
            @PathVariable("jan_aadhaar") String janAadhaar,
            @RequestParam(value = "min_score", defaultValue = "0.8") Double minScore) {
        try {
            DuplicateCandidatesResponse response = goldenRecordService.getDuplicateCandidates(
                    janAadhaar, minScore);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            DuplicateCandidatesResponse errorResponse = new DuplicateCandidatesResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError("Failed to get duplicate candidates: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
}

