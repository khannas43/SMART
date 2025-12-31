package com.smart.platform.aiml.intimation.controller;

import com.smart.platform.aiml.intimation.dto.*;
import com.smart.platform.aiml.intimation.service.IntimationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller for Intimation Management
 * Handles intimation scheduling, status queries, and campaign management
 */
@RestController
@RequestMapping("/api/v1/intimation")
@CrossOrigin(origins = "*")
public class IntimationController {

    @Autowired
    private IntimationService intimationService;

    /**
     * Schedule intimation for eligible candidates
     * POST /api/v1/intimation/schedule
     */
    @PostMapping("/scheme")
    public ResponseEntity<ScheduleIntimationResponse> scheduleIntimation(
            @RequestBody ScheduleIntimationRequest request) {
        
        ScheduleIntimationResponse response = intimationService.scheduleIntimation(
            request.getSchemeCode(),
            request.getFamilyIds(),
            request.getPriority(),
            request.getEligibilityMeta()
        );
        
        return ResponseEntity.ok(response);
    }

    /**
     * Get intimation status for a family
     * GET /api/v1/intimation/status?family_id={uuid}
     */
    @GetMapping("/status")
    public ResponseEntity<IntimationStatusResponse> getIntimationStatus(
            @RequestParam("family_id") String familyId) {
        
        IntimationStatusResponse response = intimationService.getIntimationStatus(familyId);
        return ResponseEntity.ok(response);
    }

    /**
     * Trigger retry for pending intimations
     * POST /api/v1/intimation/retry?campaign_id={id}
     */
    @PostMapping("/retry")
    public ResponseEntity<RetryResponse> retryIntimation(
            @RequestParam(value = "campaign_id", required = false) Integer campaignId) {
        
        RetryResponse response = intimationService.retryIntimation(campaignId);
        return ResponseEntity.ok(response);
    }

    /**
     * List active campaigns
     * GET /api/v1/intimation/campaigns
     */
    @GetMapping("/campaigns")
    public ResponseEntity<List<CampaignSummary>> listCampaigns(
            @RequestParam(value = "scheme_code", required = false) String schemeCode,
            @RequestParam(value = "status", required = false) String status) {
        
        List<CampaignSummary> campaigns = intimationService.listCampaigns(schemeCode, status);
        return ResponseEntity.ok(campaigns);
    }

    /**
     * Get campaign metrics
     * GET /api/v1/intimation/campaigns/{campaign_id}/metrics
     */
    @GetMapping("/campaigns/{campaign_id}/metrics")
    public ResponseEntity<CampaignMetrics> getCampaignMetrics(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignMetrics metrics = intimationService.getCampaignMetrics(campaignId);
        return ResponseEntity.ok(metrics);
    }
}

