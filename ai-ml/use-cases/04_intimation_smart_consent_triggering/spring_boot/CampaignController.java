package com.smart.platform.aiml.intimation.controller;

import com.smart.platform.aiml.intimation.dto.*;
import com.smart.platform.aiml.intimation.service.CampaignService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Campaign Management
 * Handles campaign creation, management, and monitoring
 */
@RestController
@RequestMapping("/api/v1/campaigns")
@CrossOrigin(origins = "*")
public class CampaignController {

    @Autowired
    private CampaignService campaignService;

    /**
     * Create new campaign
     * POST /api/v1/campaigns/create
     */
    @PostMapping("/create")
    public ResponseEntity<CreateCampaignResponse> createCampaign(
            @RequestBody CreateCampaignRequest request) {
        
        CreateCampaignResponse response = campaignService.createCampaign(
            request.getCampaignName(),
            request.getSchemeCode(),
            request.getCampaignType(),
            request.getEligibilityScoreThreshold(),
            request.getTargetDistricts(),
            request.getScheduledAt()
        );
        
        return ResponseEntity.ok(response);
    }

    /**
     * Get campaign details
     * GET /api/v1/campaigns/{campaign_id}
     */
    @GetMapping("/{campaign_id}")
    public ResponseEntity<CampaignDetails> getCampaign(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignDetails campaign = campaignService.getCampaign(campaignId);
        return ResponseEntity.ok(campaign);
    }

    /**
     * Get campaign metrics
     * GET /api/v1/campaigns/{campaign_id}/metrics
     */
    @GetMapping("/{campaign_id}/metrics")
    public ResponseEntity<CampaignMetrics> getCampaignMetrics(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignMetrics metrics = campaignService.getCampaignMetrics(campaignId);
        return ResponseEntity.ok(metrics);
    }

    /**
     * Pause campaign
     * PUT /api/v1/campaigns/{campaign_id}/pause
     */
    @PutMapping("/{campaign_id}/pause")
    public ResponseEntity<CampaignStatusResponse> pauseCampaign(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignStatusResponse response = campaignService.pauseCampaign(campaignId);
        return ResponseEntity.ok(response);
    }

    /**
     * Resume campaign
     * PUT /api/v1/campaigns/{campaign_id}/resume
     */
    @PutMapping("/{campaign_id}/resume")
    public ResponseEntity<CampaignStatusResponse> resumeCampaign(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignStatusResponse response = campaignService.resumeCampaign(campaignId);
        return ResponseEntity.ok(response);
    }

    /**
     * Cancel campaign
     * DELETE /api/v1/campaigns/{campaign_id}
     */
    @DeleteMapping("/{campaign_id}")
    public ResponseEntity<CampaignStatusResponse> cancelCampaign(
            @PathVariable("campaign_id") Integer campaignId) {
        
        CampaignStatusResponse response = campaignService.cancelCampaign(campaignId);
        return ResponseEntity.ok(response);
    }
}

