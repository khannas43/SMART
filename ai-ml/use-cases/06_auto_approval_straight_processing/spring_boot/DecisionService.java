package com.smart.platform.decision.service;

import com.smart.platform.decision.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;

/**
 * Service layer for Decision Evaluation
 * Use Case ID: AI-PLATFORM-06
 * 
 * Integrates with Python DecisionEngine service via PythonDecisionClient
 */
@Service
public class DecisionService {

    @Autowired
    private PythonDecisionClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Evaluate an application and make a decision
     */
    public DecisionResponse evaluateApplication(
            Integer applicationId,
            String familyId,
            String schemeCode) {
        
        try {
            // Call Python DecisionEngine
            Map<String, Object> result = pythonClient.evaluateApplication(
                    applicationId, familyId, schemeCode);

            // Convert to DecisionResponse
            return mapToDecisionResponse(result);

        } catch (Exception e) {
            DecisionResponse response = new DecisionResponse();
            response.setSuccess(false);
            response.setError("Decision evaluation failed: " + e.getMessage());
            return response;
        }
    }

    /**
     * Map Python result to DecisionResponse DTO
     */
    @SuppressWarnings("unchecked")
    private DecisionResponse mapToDecisionResponse(Map<String, Object> result) {
        DecisionResponse response = new DecisionResponse();
        
        Boolean success = (Boolean) result.get("success");
        response.setSuccess(success != null ? success : false);
        
        if (success != null && success) {
            // Decision ID
            Object decisionId = result.get("decision_id");
            if (decisionId != null) {
                response.setDecisionId(decisionId instanceof Number ? 
                    ((Number) decisionId).intValue() : Integer.parseInt(decisionId.toString()));
            }
            
            // Decision details
            Map<String, Object> decision = (Map<String, Object>) result.get("decision");
            if (decision != null) {
                response.setDecisionType((String) decision.get("decision_type"));
                response.setDecisionStatus((String) decision.get("decision_status"));
                
                Object riskScore = decision.get("risk_score");
                if (riskScore != null) {
                    response.setRiskScore(riskScore instanceof Number ? 
                        ((Number) riskScore).doubleValue() : Double.parseDouble(riskScore.toString()));
                }
                
                response.setRiskBand((String) decision.get("risk_band"));
                response.setReason((String) decision.get("reason"));
            }
            
            // Rule results
            Map<String, Object> ruleResults = (Map<String, Object>) result.get("rule_results");
            if (ruleResults != null) {
                DecisionResponse.RuleEvaluationResult ruleEval = new DecisionResponse.RuleEvaluationResult();
                ruleEval.setAllPassed((Boolean) ruleResults.get("all_passed"));
                
                Object passedCount = ruleResults.get("passed_count");
                if (passedCount != null) {
                    ruleEval.setPassedCount(passedCount instanceof Number ? 
                        ((Number) passedCount).intValue() : Integer.parseInt(passedCount.toString()));
                }
                
                Object failedCount = ruleResults.get("failed_count");
                if (failedCount != null) {
                    ruleEval.setFailedCount(failedCount instanceof Number ? 
                        ((Number) failedCount).intValue() : Integer.parseInt(failedCount.toString()));
                }
                
                List<String> criticalFailures = (List<String>) ruleResults.get("critical_failures");
                ruleEval.setCriticalFailures(criticalFailures != null ? criticalFailures : new ArrayList<>());
                
                response.setRuleResults(ruleEval);
            }
            
            // Risk results
            Map<String, Object> riskResults = (Map<String, Object>) result.get("risk_results");
            if (riskResults != null) {
                DecisionResponse.RiskScoreResult riskScoreResult = new DecisionResponse.RiskScoreResult();
                
                Object riskScore = riskResults.get("risk_score");
                if (riskScore != null) {
                    riskScoreResult.setRiskScore(riskScore instanceof Number ? 
                        ((Number) riskScore).doubleValue() : Double.parseDouble(riskScore.toString()));
                }
                
                riskScoreResult.setRiskBand((String) riskResults.get("risk_band"));
                riskScoreResult.setModelVersion((String) riskResults.get("model_version"));
                riskScoreResult.setModelType((String) riskResults.get("model_type"));
                
                List<String> topFactors = (List<String>) riskResults.get("top_factors");
                riskScoreResult.setTopFactors(topFactors != null ? topFactors : new ArrayList<>());
                
                response.setRiskResults(riskScoreResult);
            }
            
            // Routing
            Map<String, Object> routing = (Map<String, Object>) result.get("routing");
            if (routing != null) {
                DecisionResponse.RoutingResult routingResult = new DecisionResponse.RoutingResult();
                routingResult.setAction((String) routing.get("action"));
                routingResult.setStatus((String) routing.get("status"));
                routingResult.setMessage((String) routing.get("message"));
                routingResult.setQueue((String) routing.get("queue"));
                
                Object triggerId = routing.get("trigger_id");
                if (triggerId != null) {
                    routingResult.setTriggerId(triggerId instanceof Number ? 
                        ((Number) triggerId).intValue() : Integer.parseInt(triggerId.toString()));
                }
                
                response.setRouting(routingResult);
            }
        } else {
            response.setError((String) result.get("error"));
        }
        
        return response;
    }

    /**
     * Get decision history for an application
     */
    public DecisionHistoryResponse getDecisionHistory(Integer applicationId) {
        DecisionHistoryResponse response = new DecisionHistoryResponse();
        
        try {
            // Get decision ID for this application
            Integer decisionId = jdbcTemplate.queryForObject(
                "SELECT decision_id FROM decision.decisions WHERE application_id = ? ORDER BY decision_timestamp DESC LIMIT 1",
                Integer.class,
                applicationId
            );
            
            if (decisionId == null) {
                response.setSuccess(false);
                response.setError("No decision found for application ID: " + applicationId);
                return response;
            }
            
            // Get decision history
            List<DecisionHistoryResponse.DecisionHistoryEntry> history = jdbcTemplate.query(
                "SELECT history_id, from_status, to_status, from_decision_type, to_decision_type, " +
                "change_reason, changed_by, changed_by_type, changed_at " +
                "FROM decision.decision_history " +
                "WHERE decision_id = ? " +
                "ORDER BY changed_at ASC",
                new RowMapper<DecisionHistoryResponse.DecisionHistoryEntry>() {
                    @Override
                    public DecisionHistoryResponse.DecisionHistoryEntry mapRow(ResultSet rs, int rowNum) throws SQLException {
                        DecisionHistoryResponse.DecisionHistoryEntry entry = new DecisionHistoryResponse.DecisionHistoryEntry();
                        entry.setHistoryId(rs.getInt("history_id"));
                        entry.setFromStatus(rs.getString("from_status"));
                        entry.setToStatus(rs.getString("to_status"));
                        entry.setFromDecisionType(rs.getString("from_decision_type"));
                        entry.setToDecisionType(rs.getString("to_decision_type"));
                        entry.setChangeReason(rs.getString("change_reason"));
                        entry.setChangedBy(rs.getString("changed_by"));
                        entry.setChangedByType(rs.getString("changed_by_type"));
                        if (rs.getTimestamp("changed_at") != null) {
                            entry.setChangedAt(rs.getTimestamp("changed_at").toInstant().toString());
                        }
                        return entry;
                    }
                },
                decisionId
            );
            
            response.setSuccess(true);
            response.setApplicationId(applicationId);
            response.setHistory(history);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get decision history: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get decision details by decision ID
     */
    public DecisionDetailResponse getDecision(Integer decisionId) {
        DecisionDetailResponse response = new DecisionDetailResponse();
        
        try {
            // Get decision details
            Map<String, Object> decision = jdbcTemplate.queryForMap(
                "SELECT decision_id, application_id, family_id, scheme_code, decision_type, " +
                "decision_status, risk_score, risk_band, routing_reason, decision_timestamp " +
                "FROM decision.decisions " +
                "WHERE decision_id = ?",
                decisionId
            );
            
            response.setSuccess(true);
            response.setDecisionId(decisionId);
            response.setApplicationId(((Number) decision.get("application_id")).intValue());
            response.setFamilyId((String) decision.get("family_id"));
            response.setSchemeCode((String) decision.get("scheme_code"));
            response.setDecisionType((String) decision.get("decision_type"));
            response.setDecisionStatus((String) decision.get("decision_status"));
            
            if (decision.get("risk_score") != null) {
                response.setRiskScore(((Number) decision.get("risk_score")).doubleValue());
            }
            response.setRiskBand((String) decision.get("risk_band"));
            response.setRoutingReason((String) decision.get("routing_reason"));
            
            if (decision.get("decision_timestamp") != null) {
                response.setDecisionTimestamp(decision.get("decision_timestamp").toString());
            }
            
            // Get rule evaluations
            List<DecisionDetailResponse.RuleEvaluationDetail> ruleEvals = jdbcTemplate.query(
                "SELECT rule_category, rule_name, passed, severity, result_message, result_details " +
                "FROM decision.rule_evaluations " +
                "WHERE decision_id = ? " +
                "ORDER BY rule_category, rule_name",
                new RowMapper<DecisionDetailResponse.RuleEvaluationDetail>() {
                    @Override
                    public DecisionDetailResponse.RuleEvaluationDetail mapRow(ResultSet rs, int rowNum) throws SQLException {
                        DecisionDetailResponse.RuleEvaluationDetail eval = new DecisionDetailResponse.RuleEvaluationDetail();
                        eval.setRuleCategory(rs.getString("rule_category"));
                        eval.setRuleName(rs.getString("rule_name"));
                        eval.setPassed(rs.getBoolean("passed"));
                        eval.setSeverity(rs.getString("severity"));
                        eval.setResultMessage(rs.getString("result_message"));
                        
                        // Parse result_details JSON
                        String resultDetailsJson = rs.getString("result_details");
                        if (resultDetailsJson != null) {
                            try {
                                @SuppressWarnings("unchecked")
                                Map<String, Object> details = objectMapper.readValue(resultDetailsJson, Map.class);
                                eval.setResultDetails(details);
                            } catch (Exception e) {
                                // If parsing fails, set empty map
                                eval.setResultDetails(new HashMap<>());
                            }
                        }
                        return eval;
                    }
                },
                decisionId
            );
            
            response.setRuleEvaluations(ruleEvals);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get decision details: " + e.getMessage());
        }
        
        return response;
    }
    
    private final com.fasterxml.jackson.databind.ObjectMapper objectMapper = new com.fasterxml.jackson.databind.ObjectMapper();

    /**
     * Override a decision (officer override)
     */
    public OverrideResponse overrideDecision(
            Integer decisionId,
            String overrideDecisionType,
            String overrideReason,
            String officerId,
            String officerName) {
        
        OverrideResponse response = new OverrideResponse();
        
        try {
            // Get original decision
            Map<String, Object> originalDecision = jdbcTemplate.queryForMap(
                "SELECT decision_type, risk_score, routing_reason " +
                "FROM decision.decisions " +
                "WHERE decision_id = ?",
                decisionId
            );
            
            String originalDecisionType = (String) originalDecision.get("decision_type");
            
            // Create override record
            Integer overrideId = jdbcTemplate.queryForObject(
                "INSERT INTO decision.decision_overrides " +
                "(decision_id, original_decision_type, original_risk_score, " +
                "override_decision_type, override_reason, officer_id, officer_name, overridden_at) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP) " +
                "RETURNING override_id",
                Integer.class,
                decisionId,
                originalDecisionType,
                originalDecision.get("risk_score"),
                overrideDecisionType,
                overrideReason,
                officerId,
                officerName
            );
            
            // Update decision
            jdbcTemplate.update(
                "UPDATE decision.decisions " +
                "SET decision_type = ?, " +
                "    decision_status = CASE " +
                "        WHEN ? = 'OFFICER_APPROVED' THEN 'approved' " +
                "        WHEN ? = 'OFFICER_REJECTED' THEN 'rejected' " +
                "        ELSE decision_status END, " +
                "    decision_by = ?, " +
                "    updated_at = CURRENT_TIMESTAMP " +
                "WHERE decision_id = ?",
                overrideDecisionType,
                overrideDecisionType,
                overrideDecisionType,
                officerId,
                decisionId
            );
            
            response.setSuccess(true);
            response.setOverrideId(overrideId);
            response.setDecisionId(decisionId);
            response.setOriginalDecisionType(originalDecisionType);
            response.setOverrideDecisionType(overrideDecisionType);
            response.setMessage("Decision overridden successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to override decision: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get decisions by family ID
     */
    public DecisionListResponse getDecisionsByFamily(String familyId) {
        DecisionListResponse response = new DecisionListResponse();
        
        try {
            List<DecisionListResponse.DecisionSummary> decisions = jdbcTemplate.query(
                "SELECT decision_id, application_id, family_id, scheme_code, decision_type, " +
                "decision_status, risk_score, risk_band, decision_timestamp " +
                "FROM decision.decisions " +
                "WHERE family_id = ? " +
                "ORDER BY decision_timestamp DESC",
                new RowMapper<DecisionListResponse.DecisionSummary>() {
                    @Override
                    public DecisionListResponse.DecisionSummary mapRow(ResultSet rs, int rowNum) throws SQLException {
                        DecisionListResponse.DecisionSummary summary = new DecisionListResponse.DecisionSummary();
                        summary.setDecisionId(rs.getInt("decision_id"));
                        summary.setApplicationId(rs.getInt("application_id"));
                        summary.setFamilyId(rs.getString("family_id"));
                        summary.setSchemeCode(rs.getString("scheme_code"));
                        summary.setDecisionType(rs.getString("decision_type"));
                        summary.setDecisionStatus(rs.getString("decision_status"));
                        if (rs.getObject("risk_score") != null) {
                            summary.setRiskScore(rs.getDouble("risk_score"));
                        }
                        summary.setRiskBand(rs.getString("risk_band"));
                        if (rs.getTimestamp("decision_timestamp") != null) {
                            summary.setDecisionTimestamp(rs.getTimestamp("decision_timestamp").toInstant().toString());
                        }
                        return summary;
                    }
                },
                familyId
            );
            
            response.setSuccess(true);
            response.setDecisions(decisions);
            response.setTotalCount(decisions.size());
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get decisions by family: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get decisions by scheme code
     */
    public DecisionListResponse getDecisionsByScheme(String schemeCode) {
        DecisionListResponse response = new DecisionListResponse();
        
        try {
            List<DecisionListResponse.DecisionSummary> decisions = jdbcTemplate.query(
                "SELECT decision_id, application_id, family_id, scheme_code, decision_type, " +
                "decision_status, risk_score, risk_band, decision_timestamp " +
                "FROM decision.decisions " +
                "WHERE scheme_code = ? " +
                "ORDER BY decision_timestamp DESC",
                new RowMapper<DecisionListResponse.DecisionSummary>() {
                    @Override
                    public DecisionListResponse.DecisionSummary mapRow(ResultSet rs, int rowNum) throws SQLException {
                        DecisionListResponse.DecisionSummary summary = new DecisionListResponse.DecisionSummary();
                        summary.setDecisionId(rs.getInt("decision_id"));
                        summary.setApplicationId(rs.getInt("application_id"));
                        summary.setFamilyId(rs.getString("family_id"));
                        summary.setSchemeCode(rs.getString("scheme_code"));
                        summary.setDecisionType(rs.getString("decision_type"));
                        summary.setDecisionStatus(rs.getString("decision_status"));
                        if (rs.getObject("risk_score") != null) {
                            summary.setRiskScore(rs.getDouble("risk_score"));
                        }
                        summary.setRiskBand(rs.getString("risk_band"));
                        if (rs.getTimestamp("decision_timestamp") != null) {
                            summary.setDecisionTimestamp(rs.getTimestamp("decision_timestamp").toInstant().toString());
                        }
                        return summary;
                    }
                },
                schemeCode
            );
            
            response.setSuccess(true);
            response.setDecisions(decisions);
            response.setTotalCount(decisions.size());
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get decisions by scheme: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get STP metrics
     */
    public STPMetricsResponse getSTPMetrics(
            String schemeCode,
            String startDate,
            String endDate) {
        
        STPMetricsResponse response = new STPMetricsResponse();
        
        try {
            StringBuilder query = new StringBuilder();
            query.append("SELECT ");
            query.append("    COUNT(*) as total_decisions, ");
            query.append("    COUNT(*) FILTER (WHERE decision_type = 'AUTO_APPROVE') as auto_approved_count, ");
            query.append("    COUNT(*) FILTER (WHERE decision_type IN ('ROUTE_TO_OFFICER', 'ROUTE_TO_FRAUD')) as officer_reviewed_count, ");
            query.append("    COUNT(*) FILTER (WHERE decision_type = 'AUTO_REJECT') as rejected_count, ");
            query.append("    ROUND(COUNT(*) FILTER (WHERE decision_type = 'AUTO_APPROVE')::numeric / NULLIF(COUNT(*), 0) * 100, 2) as auto_approval_rate ");
            query.append("FROM decision.decisions ");
            query.append("WHERE 1=1 ");
            
            List<Object> params = new ArrayList<>();
            
            if (schemeCode != null && !schemeCode.isEmpty()) {
                query.append("AND scheme_code = ? ");
                params.add(schemeCode);
            }
            
            if (startDate != null && !startDate.isEmpty()) {
                query.append("AND decision_timestamp >= ?::timestamp ");
                params.add(startDate);
            }
            
            if (endDate != null && !endDate.isEmpty()) {
                query.append("AND decision_timestamp <= ?::timestamp ");
                params.add(endDate);
            }
            
            Map<String, Object> metrics = jdbcTemplate.queryForMap(
                query.toString(),
                params.toArray()
            );
            
            response.setSuccess(true);
            response.setSchemeCode(schemeCode);
            response.setPeriodStart(startDate);
            response.setPeriodEnd(endDate);
            response.setTotalDecisions(((Number) metrics.get("total_decisions")).intValue());
            response.setAutoApprovedCount(((Number) metrics.get("auto_approved_count")).intValue());
            response.setOfficerReviewedCount(((Number) metrics.get("officer_reviewed_count")).intValue());
            response.setRejectedCount(((Number) metrics.get("rejected_count")).intValue());
            
            if (metrics.get("auto_approval_rate") != null) {
                response.setAutoApprovalRate(((Number) metrics.get("auto_approval_rate")).doubleValue() / 100.0);
            }
            
            // Decisions by type
            Map<String, Integer> decisionsByType = new HashMap<>();
            List<Map<String, Object>> typeCounts = jdbcTemplate.queryForList(
                "SELECT decision_type, COUNT(*) as count " +
                "FROM decision.decisions " +
                (schemeCode != null ? "WHERE scheme_code = ? " : "") +
                "GROUP BY decision_type",
                schemeCode != null ? new Object[]{schemeCode} : new Object[]{}
            );
            for (Map<String, Object> row : typeCounts) {
                decisionsByType.put((String) row.get("decision_type"), ((Number) row.get("count")).intValue());
            }
            response.setDecisionsByType(decisionsByType);
            
            // Decisions by risk band
            Map<String, Integer> decisionsByRiskBand = new HashMap<>();
            List<Map<String, Object>> riskCounts = jdbcTemplate.queryForList(
                "SELECT risk_band, COUNT(*) as count " +
                "FROM decision.decisions " +
                (schemeCode != null ? "WHERE scheme_code = ? " : "") +
                "GROUP BY risk_band",
                schemeCode != null ? new Object[]{schemeCode} : new Object[]{}
            );
            for (Map<String, Object> row : riskCounts) {
                decisionsByRiskBand.put((String) row.get("risk_band"), ((Number) row.get("count")).intValue());
            }
            response.setDecisionsByRiskBand(decisionsByRiskBand);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get STP metrics: " + e.getMessage());
        }
        
        return response;
    }
}

