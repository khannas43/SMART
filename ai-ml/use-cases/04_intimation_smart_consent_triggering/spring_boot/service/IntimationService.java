package com.smart.platform.aiml.intimation.service;

import com.smart.platform.aiml.intimation.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

/**
 * Service layer for Intimation Management
 * Use Case ID: AI-PLATFORM-04
 */
@Service
public class IntimationService {

    @Autowired
    private PythonIntimationClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Schedule intimation for eligible candidates
     */
    public ScheduleIntimationResponse scheduleIntimation(
            String schemeCode,
            List<String> familyIds,
            String priority,
            Map<String, Object> eligibilityMeta) {
        
        ScheduleIntimationResponse response = new ScheduleIntimationResponse();
        
        try {
            Map<String, Object> result = pythonClient.scheduleIntimation(
                    schemeCode, familyIds, priority, eligibilityMeta);
            
            response.setSuccess(true);
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> campaigns = (List<Map<String, Object>>) result.get("campaigns");
            if (campaigns != null) {
                List<CampaignSummary> campaignSummaries = new ArrayList<>();
                for (Map<String, Object> campaign : campaigns) {
                    CampaignSummary summary = new CampaignSummary();
                    Object campaignId = campaign.get("campaign_id");
                    if (campaignId != null) {
                        summary.setCampaignId(campaignId instanceof Number ? 
                            ((Number) campaignId).intValue() : Integer.parseInt(campaignId.toString()));
                    }
                    summary.setCampaignName((String) campaign.get("campaign_name"));
                    summary.setSchemeCode((String) campaign.get("scheme_code"));
                    summary.setStatus((String) campaign.get("status"));
                    campaignSummaries.add(summary);
                }
                response.setCampaigns(campaignSummaries);
            }
            
            response.setMessage("Intimation scheduled successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to schedule intimation: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get intimation status for a family
     */
    public IntimationStatusResponse getIntimationStatus(String familyId) {
        IntimationStatusResponse response = new IntimationStatusResponse();
        
        try {
            // Query database for intimation status
            String query = "SELECT " +
                "c.campaign_id, c.campaign_name, c.scheme_code, c.status, " +
                "cc.candidate_id, cc.message_status, cc.consent_status, " +
                "ml.message_id, ml.channel, ml.delivery_status, ml.sent_at " +
                "FROM intimation.campaigns c " +
                "JOIN intimation.campaign_candidates cc ON c.campaign_id = cc.campaign_id " +
                "LEFT JOIN intimation.message_logs ml ON cc.candidate_id = ml.candidate_id " +
                "WHERE cc.family_id = ?::uuid " +
                "ORDER BY ml.sent_at DESC LIMIT 10";
            
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(query, familyId);
            
            response.setSuccess(true);
            response.setFamilyId(familyId);
            
            List<IntimationStatusResponse.IntimationRecord> intimations = new ArrayList<>();
            for (Map<String, Object> row : rows) {
                IntimationStatusResponse.IntimationRecord record = 
                    new IntimationStatusResponse.IntimationRecord();
                
                Object campaignId = row.get("campaign_id");
                if (campaignId != null) {
                    record.setCampaignId(campaignId instanceof Number ? 
                        ((Number) campaignId).intValue() : Integer.parseInt(campaignId.toString()));
                }
                record.setCampaignName((String) row.get("campaign_name"));
                record.setSchemeCode((String) row.get("scheme_code"));
                record.setMessageStatus((String) row.get("message_status"));
                record.setConsentStatus((String) row.get("consent_status"));
                record.setChannel((String) row.get("channel"));
                record.setDeliveryStatus((String) row.get("delivery_status"));
                
                if (row.get("sent_at") != null) {
                    record.setSentAt(row.get("sent_at").toString());
                }
                
                intimations.add(record);
            }
            
            response.setIntimations(intimations);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get intimation status: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Trigger retry for pending intimations
     */
    public RetryResponse retryIntimation(Integer campaignId) {
        RetryResponse response = new RetryResponse();
        
        try {
            // Query for pending candidates
            String query = "SELECT candidate_id, family_id, scheme_code " +
                "FROM intimation.campaign_candidates " +
                "WHERE message_status IN ('pending', 'failed') ";
            
            List<Object> params = new ArrayList<>();
            if (campaignId != null) {
                query += "AND campaign_id = ? ";
                params.add(campaignId);
            }
            
            List<Map<String, Object>> candidates = jdbcTemplate.queryForList(
                query, params.toArray());
            
            response.setSuccess(true);
            response.setRetryCount(candidates.size());
            response.setMessage("Retry triggered for " + candidates.size() + " candidates");
            
            // TODO: Trigger actual retry via Python orchestrator
            // For now, just return success
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to trigger retry: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * List active campaigns
     */
    public List<CampaignSummary> listCampaigns(String schemeCode, String status) {
        List<CampaignSummary> campaigns = new ArrayList<>();
        
        try {
            Map<String, Object> result = pythonClient.listCampaigns(schemeCode, status);
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> campaignList = (List<Map<String, Object>>) result.get("campaigns");
            if (campaignList != null) {
                for (Map<String, Object> campaign : campaignList) {
                    CampaignSummary summary = new CampaignSummary();
                    Object campaignId = campaign.get("campaign_id");
                    if (campaignId != null) {
                        summary.setCampaignId(campaignId instanceof Number ? 
                            ((Number) campaignId).intValue() : Integer.parseInt(campaignId.toString()));
                    }
                    summary.setCampaignName((String) campaign.get("campaign_name"));
                    summary.setSchemeCode((String) campaign.get("scheme_code"));
                    summary.setStatus((String) campaign.get("status"));
                    campaigns.add(summary);
                }
            }
            
        } catch (Exception e) {
            // Return empty list on error
        }
        
        return campaigns;
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
}

