package com.smart.platform.inclusion.service;

import com.smart.platform.inclusion.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Service layer for Proactive Inclusion & Exception Handling
 * Use Case ID: AI-PLATFORM-09
 */
@Service
public class InclusionService {

    @Autowired
    private PythonInclusionClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get priority status and nudges
     */
    public PriorityStatusResponse getPriorityStatus(String familyId, Boolean includeNudges) {
        PriorityStatusResponse response = new PriorityStatusResponse();
        
        try {
            Map<String, Object> result = pythonClient.getPriorityStatus(
                    familyId, includeNudges != null ? includeNudges : true);

            response.setSuccess(true);
            response.setFamilyId(familyId);
            
            Object isPriority = result.get("is_priority");
            response.setIsPriority(isPriority != null && Boolean.parseBoolean(isPriority.toString()));
            
            // Convert priority household
            @SuppressWarnings("unchecked")
            Map<String, Object> priorityHousehold = (Map<String, Object>) result.get("priority_household");
            if (priorityHousehold != null) {
                PriorityStatusResponse.PriorityHousehold ph = new PriorityStatusResponse.PriorityHousehold();
                ph.setPriorityId(getIntValue(priorityHousehold.get("priority_id")));
                ph.setFamilyId((String) priorityHousehold.get("family_id"));
                ph.setInclusionGapScore(getDoubleValue(priorityHousehold.get("inclusion_gap_score")));
                ph.setVulnerabilityScore(getDoubleValue(priorityHousehold.get("vulnerability_score")));
                ph.setCoverageGapScore(getDoubleValue(priorityHousehold.get("coverage_gap_score")));
                ph.setPriorityLevel((String) priorityHousehold.get("priority_level"));
                
                @SuppressWarnings("unchecked")
                List<String> segments = (List<String>) priorityHousehold.get("priority_segments");
                ph.setPrioritySegments(segments);
                
                ph.setPredictedEligibleCount(getIntValue(priorityHousehold.get("predicted_eligible_count")));
                ph.setActualEnrolledCount(getIntValue(priorityHousehold.get("actual_enrolled_count")));
                ph.setEligibilityGapCount(getIntValue(priorityHousehold.get("eligibility_gap_count")));
                
                response.setPriorityHousehold(ph);
            }
            
            // Convert exception flags
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> exceptions = (List<Map<String, Object>>) result.get("exception_flags");
            if (exceptions != null) {
                List<PriorityStatusResponse.ExceptionFlag> exceptionFlags = new ArrayList<>();
                for (Map<String, Object> exc : exceptions) {
                    PriorityStatusResponse.ExceptionFlag flag = new PriorityStatusResponse.ExceptionFlag();
                    flag.setFamilyId((String) exc.get("family_id"));
                    flag.setBeneficiaryId((String) exc.get("beneficiary_id"));
                    flag.setExceptionCategory((String) exc.get("exception_category"));
                    flag.setExceptionDescription((String) exc.get("exception_description"));
                    flag.setAnomalyScore(getDoubleValue(exc.get("anomaly_score")));
                    flag.setReviewStatus("PENDING_REVIEW"); // Default
                    exceptionFlags.add(flag);
                }
                response.setExceptionFlags(exceptionFlags);
            }
            
            // Convert nudges
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> nudges = (List<Map<String, Object>>) result.get("nudges");
            if (nudges != null) {
                List<PriorityStatusResponse.Nudge> nudgeList = new ArrayList<>();
                for (Map<String, Object> nudge : nudges) {
                    PriorityStatusResponse.Nudge n = new PriorityStatusResponse.Nudge();
                    n.setNudgeType((String) nudge.get("nudge_type"));
                    n.setNudgeMessage((String) nudge.get("nudge_message"));
                    
                    @SuppressWarnings("unchecked")
                    List<String> actions = (List<String>) nudge.get("recommended_actions");
                    n.setRecommendedActions(actions);
                    
                    @SuppressWarnings("unchecked")
                    List<String> schemes = (List<String>) nudge.get("scheme_codes");
                    n.setSchemeCodes(schemes);
                    
                    n.setChannel((String) nudge.get("channel"));
                    n.setPriorityLevel((String) nudge.get("priority_level"));
                    n.setDeliveryStatus("SCHEDULED");
                    nudgeList.add(n);
                }
                response.setNudges(nudgeList);
            }
            
            response.setTimestamp((String) result.get("timestamp"));
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get priority status: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get priority list
     */
    public PriorityListResponse getPriorityList(
            String blockId, String district, List<String> segments,
            String priorityLevel, Integer limit) {
        
        PriorityListResponse response = new PriorityListResponse();
        
        try {
            Map<String, Object> result = pythonClient.getPriorityList(
                    blockId, district, segments, priorityLevel, limit);

            response.setSuccess(true);
            response.setTotalCount(getIntValue(result.get("total_count")));
            
            // Convert households
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> households = (List<Map<String, Object>>) result.get("households");
            if (households != null) {
                List<PriorityListResponse.PriorityHouseholdItem> householdList = new ArrayList<>();
                for (Map<String, Object> hh : households) {
                    PriorityListResponse.PriorityHouseholdItem item = 
                        new PriorityListResponse.PriorityHouseholdItem();
                    
                    item.setPriorityId(getIntValue(hh.get("priority_id")));
                    item.setFamilyId((String) hh.get("family_id"));
                    item.setHouseholdHeadId((String) hh.get("household_head_id"));
                    item.setBlockId((String) hh.get("block_id"));
                    item.setDistrict((String) hh.get("district"));
                    item.setGramPanchayat((String) hh.get("gram_panchayat"));
                    item.setInclusionGapScore(getDoubleValue(hh.get("inclusion_gap_score")));
                    item.setVulnerabilityScore(getDoubleValue(hh.get("vulnerability_score")));
                    item.setPriorityLevel((String) hh.get("priority_level"));
                    
                    @SuppressWarnings("unchecked")
                    List<String> segmentsList = (List<String>) hh.get("priority_segments");
                    item.setPrioritySegments(segmentsList);
                    
                    item.setPredictedEligibleCount(getIntValue(hh.get("predicted_eligible_count")));
                    item.setActualEnrolledCount(getIntValue(hh.get("actual_enrolled_count")));
                    item.setEligibilityGapCount(getIntValue(hh.get("eligibility_gap_count")));
                    item.setDetectedAt((String) hh.get("detected_at"));
                    
                    householdList.add(item);
                }
                response.setHouseholds(householdList);
            }
            
            @SuppressWarnings("unchecked")
            Map<String, Object> filters = (Map<String, Object>) result.get("filters");
            response.setFilters(filters);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get priority list: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Schedule nudge delivery
     */
    public NudgeDeliveryResponse scheduleNudgeDelivery(
            String familyId, String nudgeType, String nudgeMessage,
            List<String> recommendedActions, List<String> schemeCodes,
            String channel, String priorityLevel, String scheduledAt) {
        
        NudgeDeliveryResponse response = new NudgeDeliveryResponse();
        
        try {
            Map<String, Object> result = pythonClient.scheduleNudgeDelivery(
                    familyId, nudgeType, nudgeMessage, recommendedActions,
                    schemeCodes, channel, priorityLevel, scheduledAt);

            response.setSuccess(true);
            response.setNudgeId(getIntValue(result.get("nudge_id")));
            response.setDeliveryStatus((String) result.get("delivery_status"));
            response.setScheduledAt((String) result.get("scheduled_at"));
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to schedule nudge: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get exception flags
     */
    public List<PriorityStatusResponse.ExceptionFlag> getExceptionFlags(String familyId) {
        try {
            PriorityStatusResponse status = getPriorityStatus(familyId, false);
            return status.getExceptionFlags() != null ? status.getExceptionFlags() : new ArrayList<>();
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    /**
     * Review exception
     */
    public PriorityStatusResponse.ExceptionFlag reviewException(
            Integer exceptionId, String reviewStatus, String reviewNotes, String reviewedBy) {
        
        PriorityStatusResponse.ExceptionFlag flag = new PriorityStatusResponse.ExceptionFlag();
        
        try {
            String sql = """
                UPDATE inclusion.exception_flags
                SET review_status = ?,
                    reviewed_by = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_notes = ?
                WHERE exception_id = ?
                RETURNING exception_id, family_id, beneficiary_id, exception_category,
                          exception_description, anomaly_score, review_status
            """;
            
            PriorityStatusResponse.ExceptionFlag result = jdbcTemplate.queryForObject(
                sql,
                new RowMapper<PriorityStatusResponse.ExceptionFlag>() {
                    @Override
                    public PriorityStatusResponse.ExceptionFlag mapRow(ResultSet rs, int rowNum) throws SQLException {
                        PriorityStatusResponse.ExceptionFlag f = new PriorityStatusResponse.ExceptionFlag();
                        f.setExceptionId(rs.getInt("exception_id"));
                        f.setFamilyId(rs.getString("family_id"));
                        f.setBeneficiaryId(rs.getString("beneficiary_id"));
                        f.setExceptionCategory(rs.getString("exception_category"));
                        f.setExceptionDescription(rs.getString("exception_description"));
                        f.setAnomalyScore(rs.getDouble("anomaly_score"));
                        f.setReviewStatus(rs.getString("review_status"));
                        return f;
                    }
                },
                reviewStatus, reviewedBy, reviewNotes, exceptionId
            );
            
            return result;
            
        } catch (Exception e) {
            flag.setExceptionId(exceptionId);
            flag.setReviewStatus("ERROR");
            return flag;
        }
    }

    private Integer getIntValue(Object value) {
        if (value == null) return 0;
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (Exception e) {
            return 0;
        }
    }

    private Double getDoubleValue(Object value) {
        if (value == null) return 0.0;
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(value.toString());
        } catch (Exception e) {
            return 0.0;
        }
    }
}

