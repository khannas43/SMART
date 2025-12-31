package com.smart.platform.nudging.service;

import com.smart.platform.nudging.dto.NudgeRequest;
import com.smart.platform.nudging.dto.NudgeResponse;
import com.smart.platform.nudging.dto.NudgeHistoryItem;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * Service layer for nudge management
 */
@Service
public class NudgeService {

    @Autowired
    private PythonNudgeClient pythonNudgeClient;

    public NudgeResponse scheduleNudge(NudgeRequest request) {
        Map<String, Object> pythonResult = pythonNudgeClient.scheduleNudge(
            request.getActionType(),
            request.getFamilyId(),
            request.getUrgency(),
            request.getExpiryDate(),
            request.getActionContext(),
            request.getScheduledBy()
        );
        return mapPythonResultToNudgeResponse(pythonResult);
    }

    public List<NudgeHistoryItem> getNudgeHistory(String familyId, Integer limit) {
        List<Map<String, Object>> pythonResults = pythonNudgeClient.getNudgeHistory(familyId, limit);
        return pythonResults.stream()
            .map(this::mapPythonResultToHistoryItem)
            .toList();
    }

    public NudgeResponse recordFeedback(String nudgeId, String eventType, Map<String, Object> metadata) {
        Map<String, Object> pythonResult = pythonNudgeClient.recordFeedback(nudgeId, eventType, metadata);
        return mapPythonResultToNudgeResponse(pythonResult);
    }

    @SuppressWarnings("unchecked")
    private NudgeResponse mapPythonResultToNudgeResponse(Map<String, Object> pythonResult) {
        NudgeResponse response = new NudgeResponse();
        response.setSuccess((Boolean) pythonResult.getOrDefault("success", false));
        response.setNudgeId((String) pythonResult.get("nudge_id"));
        response.setFamilyId((String) pythonResult.get("family_id"));
        response.setActionType((String) pythonResult.get("action_type"));
        response.setUrgency((String) pythonResult.get("urgency"));
        response.setScheduledChannel((String) pythonResult.get("scheduled_channel"));
        
        // Parse scheduled_time if present
        Object scheduledTimeObj = pythonResult.get("scheduled_time");
        if (scheduledTimeObj != null) {
            // Handle ISO format datetime string
            String scheduledTimeStr = scheduledTimeObj.toString();
            try {
                response.setScheduledTime(java.time.LocalDateTime.parse(scheduledTimeStr.replace("Z", "")));
            } catch (Exception e) {
                // Fallback: try other formats
            }
        }
        
        response.setTimeWindow((String) pythonResult.get("time_window"));
        response.setTemplateId((String) pythonResult.get("template_id"));
        response.setPersonalizedContent((String) pythonResult.get("personalized_content"));
        
        // Handle numeric values
        Object channelConf = pythonResult.get("channel_confidence");
        if (channelConf instanceof Number) {
            response.setChannelConfidence(((Number) channelConf).doubleValue());
        }
        
        Object timeConf = pythonResult.get("time_confidence");
        if (timeConf instanceof Number) {
            response.setTimeConfidence(((Number) timeConf).doubleValue());
        }
        
        response.setContentStrategy((String) pythonResult.get("content_strategy"));
        response.setFatigueStatus((Map<String, Object>) pythonResult.get("fatigue_status"));
        response.setReason((String) pythonResult.get("reason"));
        response.setError((String) pythonResult.get("error"));
        
        return response;
    }

    @SuppressWarnings("unchecked")
    private NudgeHistoryItem mapPythonResultToHistoryItem(Map<String, Object> pythonResult) {
        NudgeHistoryItem item = new NudgeHistoryItem();
        item.setNudgeId((String) pythonResult.get("nudge_id"));
        item.setActionType((String) pythonResult.get("action_type"));
        item.setUrgency((String) pythonResult.get("urgency"));
        item.setChannel((String) pythonResult.get("channel"));
        
        // Parse datetime fields
        parseDateTime(pythonResult.get("scheduled_time"), item::setScheduledTime);
        parseDateTime(pythonResult.get("sent_at"), item::setSentAt);
        parseDateTime(pythonResult.get("delivered_at"), item::setDeliveredAt);
        parseDateTime(pythonResult.get("opened_at"), item::setOpenedAt);
        parseDateTime(pythonResult.get("clicked_at"), item::setClickedAt);
        parseDateTime(pythonResult.get("responded_at"), item::setRespondedAt);
        parseDateTime(pythonResult.get("completed_at"), item::setCompletedAt);
        
        item.setStatus((String) pythonResult.get("status"));
        item.setDeliveryStatus((String) pythonResult.get("delivery_status"));
        item.setPersonalizedContent((String) pythonResult.get("personalized_content"));
        item.setTemplateName((String) pythonResult.get("template_name"));
        item.setTone((String) pythonResult.get("tone"));
        
        return item;
    }

    private void parseDateTime(Object value, java.util.function.Consumer<java.time.LocalDateTime> setter) {
        if (value != null) {
            try {
                String str = value.toString().replace("Z", "");
                setter.accept(java.time.LocalDateTime.parse(str));
            } catch (Exception e) {
                // Ignore parsing errors
            }
        }
    }
}

