package com.smart.platform.aiml.intimation.service;

import com.smart.platform.aiml.intimation.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

/**
 * Service layer for Campaign Management
 * Use Case ID: AI-PLATFORM-04
 */
@Service
public class CampaignService {

    @Autowired
    private PythonIntimationClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Create new campaign
     */
    public CreateCampaignResponse createCampaign(
            String campaignName,
            String schemeCode,
            String campaignType,
            Double eligibilityScoreThreshold,
            List<String> targetDistricts,
            String scheduledAt) {
        
        CreateCampaignResponse response = new CreateCampaignResponse();
        
        try {
            Map<String, Object> result = pythonClient.createCampaign(
                    campaignName, schemeCode, campaignType, eligibilityScoreThreshold,
                    targetDistricts, scheduledAt);
            
            response.setSuccess(true);
            
            Object campaignId = result.get("campaign_id");
            if (campaignId != null) {
                response.setCampaignId(campaignId instanceof Number ? 
                    ((Number) campaignId).intValue() : Integer.parseInt(campaignId.toString()));
            }
            
            response.setCampaignName((String) result.get("campaign_name"));
            response.setSchemeCode((String) result.get("scheme_code"));
            response.setStatus((String) result.get("status"));
            response.setMessage("Campaign created successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to create campaign: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get campaign details
     */
    public CampaignDetails getCampaign(Integer campaignId) {
        CampaignDetails campaign = new CampaignDetails();
        
        try {
            Map<String, Object> result = pythonClient.getCampaign(campaignId);
            
            campaign.setCampaignId(campaignId);
            campaign.setCampaignName((String) result.get("campaign_name"));
            campaign.setSchemeCode((String) result.get("scheme_code"));
            campaign.setStatus((String) result.get("status"));
            
            Object totalCandidates = result.get("total_candidates");
            if (totalCandidates != null) {
                campaign.setTotalCandidates(totalCandidates instanceof Number ? 
                    ((Number) totalCandidates).intValue() : Integer.parseInt(totalCandidates.toString()));
            }
            
            // Query additional details from database
            String query = "SELECT campaign_type, eligibility_score_threshold, " +
                "priority_threshold, scheduled_at, created_at " +
                "FROM intimation.campaigns WHERE campaign_id = ?";
            
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(query, campaignId);
            if (!rows.isEmpty()) {
                Map<String, Object> row = rows.get(0);
                campaign.setCampaignType((String) row.get("campaign_type"));
                
                Object threshold = row.get("eligibility_score_threshold");
                if (threshold != null) {
                    campaign.setEligibilityScoreThreshold(threshold instanceof Number ? 
                        ((Number) threshold).doubleValue() : Double.parseDouble(threshold.toString()));
                }
                
                if (row.get("scheduled_at") != null) {
                    campaign.setScheduledAt(row.get("scheduled_at").toString());
                }
                
                if (row.get("created_at") != null) {
                    campaign.setCreatedAt(row.get("created_at").toString());
                }
            }
            
        } catch (Exception e) {
            campaign.setError("Failed to get campaign: " + e.getMessage());
        }
        
        return campaign;
    }

    /**
     * Get campaign metrics
     */
    public CampaignMetrics getCampaignMetrics(Integer campaignId) {
        CampaignMetrics metrics = new CampaignMetrics();
        
        try {
            Map<String, Object> result = pythonClient.getCampaignMetrics(campaignId);
            
            metrics.setCampaignId(campaignId);
            
            Object totalCandidates = result.get("total_candidates");
            if (totalCandidates != null) {
                metrics.setTotalCandidates(totalCandidates instanceof Number ? 
                    ((Number) totalCandidates).intValue() : Integer.parseInt(totalCandidates.toString()));
            }
            
            Object messagesSent = result.get("messages_sent");
            if (messagesSent != null) {
                metrics.setMessagesSent(messagesSent instanceof Number ? 
                    ((Number) messagesSent).intValue() : Integer.parseInt(messagesSent.toString()));
            }
            
            Object messagesDelivered = result.get("messages_delivered");
            if (messagesDelivered != null) {
                metrics.setMessagesDelivered(messagesDelivered instanceof Number ? 
                    ((Number) messagesDelivered).intValue() : Integer.parseInt(messagesDelivered.toString()));
            }
            
            Object messagesFailed = result.get("messages_failed");
            if (messagesFailed != null) {
                metrics.setMessagesFailed(messagesFailed instanceof Number ? 
                    ((Number) messagesFailed).intValue() : Integer.parseInt(messagesFailed.toString()));
            }
            
            Object consentsGiven = result.get("consents_given");
            if (consentsGiven != null) {
                metrics.setConsentsGiven(consentsGiven instanceof Number ? 
                    ((Number) consentsGiven).intValue() : Integer.parseInt(consentsGiven.toString()));
            }
            
            Object consentsRejected = result.get("consents_rejected");
            if (consentsRejected != null) {
                metrics.setConsentsRejected(consentsRejected instanceof Number ? 
                    ((Number) consentsRejected).intValue() : Integer.parseInt(consentsRejected.toString()));
            }
            
            Object responseRate = result.get("response_rate");
            if (responseRate != null) {
                metrics.setResponseRate(responseRate instanceof Number ? 
                    ((Number) responseRate).doubleValue() : Double.parseDouble(responseRate.toString()));
            }
            
            Object deliveryRate = result.get("delivery_rate");
            if (deliveryRate != null) {
                metrics.setDeliveryRate(deliveryRate instanceof Number ? 
                    ((Number) deliveryRate).doubleValue() : Double.parseDouble(deliveryRate.toString()));
            }
            
        } catch (Exception e) {
            metrics.setError("Failed to get campaign metrics: " + e.getMessage());
        }
        
        return metrics;
    }

    /**
     * Pause campaign
     */
    public CampaignStatusResponse pauseCampaign(Integer campaignId) {
        CampaignStatusResponse response = new CampaignStatusResponse();
        
        try {
            String query = "UPDATE intimation.campaigns SET status = 'PAUSED', updated_at = CURRENT_TIMESTAMP " +
                "WHERE campaign_id = ? RETURNING status";
            
            String status = jdbcTemplate.queryForObject(query, String.class, campaignId);
            
            response.setSuccess(true);
            response.setCampaignId(campaignId);
            response.setStatus(status);
            response.setMessage("Campaign paused successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to pause campaign: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Resume campaign
     */
    public CampaignStatusResponse resumeCampaign(Integer campaignId) {
        CampaignStatusResponse response = new CampaignStatusResponse();
        
        try {
            String query = "UPDATE intimation.campaigns SET status = 'ACTIVE', updated_at = CURRENT_TIMESTAMP " +
                "WHERE campaign_id = ? AND status = 'PAUSED' RETURNING status";
            
            String status = jdbcTemplate.queryForObject(query, String.class, campaignId);
            
            response.setSuccess(true);
            response.setCampaignId(campaignId);
            response.setStatus(status);
            response.setMessage("Campaign resumed successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to resume campaign: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Cancel campaign
     */
    public CampaignStatusResponse cancelCampaign(Integer campaignId) {
        CampaignStatusResponse response = new CampaignStatusResponse();
        
        try {
            String query = "UPDATE intimation.campaigns SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP " +
                "WHERE campaign_id = ? RETURNING status";
            
            String status = jdbcTemplate.queryForObject(query, String.class, campaignId);
            
            response.setSuccess(true);
            response.setCampaignId(campaignId);
            response.setStatus(status);
            response.setMessage("Campaign cancelled successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to cancel campaign: " + e.getMessage());
        }
        
        return response;
    }
}

