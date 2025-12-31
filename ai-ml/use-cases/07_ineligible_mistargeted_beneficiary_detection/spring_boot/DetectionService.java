package com.smart.platform.detection.service;

import com.smart.platform.detection.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;

/**
 * Service layer for Beneficiary Detection
 * Use Case ID: AI-PLATFORM-07
 * 
 * Integrates with Python DetectionOrchestrator service via PythonDetectionClient
 */
@Service
public class DetectionService {

    @Autowired
    private PythonDetectionClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Start a detection run
     */
    public DetectionRunResponse startDetectionRun(
            String runType,
            List<String> schemeCodes,
            List<String> beneficiaryIds,
            String startedBy) {
        
        DetectionRunResponse response = new DetectionRunResponse();
        
        try {
            // Call Python DetectionOrchestrator
            Map<String, Object> result = pythonClient.runDetection(
                    runType, schemeCodes, beneficiaryIds, startedBy != null ? startedBy : "system");

            // Convert to DetectionRunResponse
            response.setSuccess(true);
            Object runId = result.get("run_id");
            if (runId != null) {
                response.setRunId(runId instanceof Number ? 
                    ((Number) runId).intValue() : Integer.parseInt(runId.toString()));
            }
            response.setRunType((String) result.get("run_type"));
            response.setRunStatus((String) result.get("status"));
            
            Object totalProcessed = result.get("total_processed");
            if (totalProcessed != null) {
                response.setTotalBeneficiariesScanned(totalProcessed instanceof Number ? 
                    ((Number) totalProcessed).intValue() : Integer.parseInt(totalProcessed.toString()));
            }
            
            Object casesFlagged = result.get("cases_flagged");
            if (casesFlagged != null) {
                response.setTotalCasesFlagged(casesFlagged instanceof Number ? 
                    ((Number) casesFlagged).intValue() : Integer.parseInt(casesFlagged.toString()));
            }
            
            @SuppressWarnings("unchecked")
            List<Integer> flaggedIds = (List<Integer>) result.get("flagged_case_ids");
            response.setFlaggedCaseIds(flaggedIds);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Detection run failed: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get detection run details
     */
    public DetectionRunResponse getDetectionRun(Integer runId) {
        DetectionRunResponse response = new DetectionRunResponse();
        
        try {
            Map<String, Object> run = jdbcTemplate.queryForMap(
                "SELECT run_id, run_type, run_status, total_beneficiaries_scanned, " +
                "total_cases_flagged, cases_by_classification, started_by, completed_at " +
                "FROM detection.detection_runs " +
                "WHERE run_id = ?",
                runId
            );
            
            response.setSuccess(true);
            response.setRunId(((Number) run.get("run_id")).intValue());
            response.setRunType((String) run.get("run_type"));
            response.setRunStatus((String) run.get("run_status"));
            
            Object totalScanned = run.get("total_beneficiaries_scanned");
            if (totalScanned != null) {
                response.setTotalBeneficiariesScanned(((Number) totalScanned).intValue());
            }
            
            Object totalFlagged = run.get("total_cases_flagged");
            if (totalFlagged != null) {
                response.setTotalCasesFlagged(((Number) totalFlagged).intValue());
            }
            
            // Parse cases_by_classification JSON
            String casesJson = (String) run.get("cases_by_classification");
            if (casesJson != null) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Integer> casesByType = objectMapper.readValue(casesJson, Map.class);
                    response.setCasesByClassification(casesByType);
                } catch (Exception e) {
                    // Ignore parsing errors
                }
            }
            
            response.setStartedBy((String) run.get("started_by"));
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get detection run: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * List detection runs
     */
    public List<DetectionRunResponse> listDetectionRuns(String status, Integer limit) {
        List<DetectionRunResponse> runs = new ArrayList<>();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT run_id, run_type, run_status, total_beneficiaries_scanned, " +
                "total_cases_flagged, started_by, run_date " +
                "FROM detection.detection_runs " +
                "WHERE 1=1 "
            );
            
            List<Object> params = new ArrayList<>();
            
            if (status != null && !status.isEmpty()) {
                query.append("AND run_status = ? ");
                params.add(status);
            }
            
            query.append("ORDER BY run_date DESC LIMIT ?");
            params.add(limit);
            
            runs = jdbcTemplate.query(
                query.toString(),
                new RowMapper<DetectionRunResponse>() {
                    @Override
                    public DetectionRunResponse mapRow(ResultSet rs, int rowNum) throws SQLException {
                        DetectionRunResponse run = new DetectionRunResponse();
                        run.setSuccess(true);
                        run.setRunId(rs.getInt("run_id"));
                        run.setRunType(rs.getString("run_type"));
                        run.setRunStatus(rs.getString("run_status"));
                        run.setTotalBeneficiariesScanned(rs.getInt("total_beneficiaries_scanned"));
                        run.setTotalCasesFlagged(rs.getInt("total_cases_flagged"));
                        run.setStartedBy(rs.getString("started_by"));
                        return run;
                    }
                },
                params.toArray()
            );
            
        } catch (Exception e) {
            // Return empty list on error
        }
        
        return runs;
    }

    /**
     * Get detected case details
     */
    public DetectedCaseResponse getCase(Integer caseId) {
        DetectedCaseResponse response = new DetectedCaseResponse();
        
        try {
            Map<String, Object> caseData = jdbcTemplate.queryForMap(
                "SELECT case_id, beneficiary_id, family_id, scheme_code, case_type, " +
                "confidence_level, case_status, risk_score, financial_exposure, " +
                "vulnerability_score, priority, detection_rationale, recommended_action, " +
                "action_urgency, rule_evaluations, ml_explanations, assigned_to, " +
                "detection_timestamp " +
                "FROM detection.detected_cases " +
                "WHERE case_id = ?",
                caseId
            );
            
            response.setSuccess(true);
            response.setCaseId(((Number) caseData.get("case_id")).intValue());
            response.setBeneficiaryId((String) caseData.get("beneficiary_id"));
            response.setFamilyId((String) caseData.get("family_id"));
            response.setSchemeCode((String) caseData.get("scheme_code"));
            response.setCaseType((String) caseData.get("case_type"));
            response.setConfidenceLevel((String) caseData.get("confidence_level"));
            response.setCaseStatus((String) caseData.get("case_status"));
            
            if (caseData.get("risk_score") != null) {
                response.setRiskScore(((Number) caseData.get("risk_score")).doubleValue());
            }
            if (caseData.get("financial_exposure") != null) {
                response.setFinancialExposure(((Number) caseData.get("financial_exposure")).doubleValue());
            }
            if (caseData.get("vulnerability_score") != null) {
                response.setVulnerabilityScore(((Number) caseData.get("vulnerability_score")).doubleValue());
            }
            if (caseData.get("priority") != null) {
                response.setPriority(((Number) caseData.get("priority")).intValue());
            }
            
            response.setDetectionRationale((String) caseData.get("detection_rationale"));
            response.setRecommendedAction((String) caseData.get("recommended_action"));
            response.setActionUrgency((String) caseData.get("action_urgency"));
            response.setAssignedTo((String) caseData.get("assigned_to"));
            
            // Parse JSON fields
            String ruleEvalsJson = (String) caseData.get("rule_evaluations");
            if (ruleEvalsJson != null) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> ruleEvals = objectMapper.readValue(ruleEvalsJson, Map.class);
                    response.setRuleEvaluations(ruleEvals);
                } catch (Exception e) {
                    // Ignore
                }
            }
            
            String mlExplJson = (String) caseData.get("ml_explanations");
            if (mlExplJson != null) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> mlExpl = objectMapper.readValue(mlExplJson, Map.class);
                    response.setMlExplanations(mlExpl);
                } catch (Exception e) {
                    // Ignore
                }
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get case: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * List detected cases
     */
    public CaseListResponse listCases(
            String schemeCode,
            String caseType,
            String status,
            Integer priority,
            Integer limit) {
        
        CaseListResponse response = new CaseListResponse();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT case_id, beneficiary_id, scheme_code, case_type, confidence_level, " +
                "case_status, priority, financial_exposure, detection_timestamp " +
                "FROM detection.detected_cases " +
                "WHERE 1=1 "
            );
            
            List<Object> params = new ArrayList<>();
            
            if (schemeCode != null && !schemeCode.isEmpty()) {
                query.append("AND scheme_code = ? ");
                params.add(schemeCode);
            }
            
            if (caseType != null && !caseType.isEmpty()) {
                query.append("AND case_type = ? ");
                params.add(caseType);
            }
            
            if (status != null && !status.isEmpty()) {
                query.append("AND case_status = ? ");
                params.add(status);
            }
            
            if (priority != null) {
                query.append("AND priority = ? ");
                params.add(priority);
            }
            
            query.append("ORDER BY priority ASC, detection_timestamp DESC LIMIT ?");
            params.add(limit);
            
            List<CaseListResponse.DetectedCaseSummary> cases = jdbcTemplate.query(
                query.toString(),
                new RowMapper<CaseListResponse.DetectedCaseSummary>() {
                    @Override
                    public CaseListResponse.DetectedCaseSummary mapRow(ResultSet rs, int rowNum) throws SQLException {
                        CaseListResponse.DetectedCaseSummary summary = 
                            new CaseListResponse.DetectedCaseSummary();
                        summary.setCaseId(rs.getInt("case_id"));
                        summary.setBeneficiaryId(rs.getString("beneficiary_id"));
                        summary.setSchemeCode(rs.getString("scheme_code"));
                        summary.setCaseType(rs.getString("case_type"));
                        summary.setConfidenceLevel(rs.getString("confidence_level"));
                        summary.setCaseStatus(rs.getString("case_status"));
                        summary.setPriority(rs.getInt("priority"));
                        if (rs.getObject("financial_exposure") != null) {
                            summary.setFinancialExposure(rs.getDouble("financial_exposure"));
                        }
                        if (rs.getTimestamp("detection_timestamp") != null) {
                            summary.setDetectionTimestamp(
                                rs.getTimestamp("detection_timestamp").toInstant().toString());
                        }
                        return summary;
                    }
                },
                params.toArray()
            );
            
            response.setSuccess(true);
            response.setCases(cases);
            response.setTotalCount(cases.size());
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to list cases: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Verify a detected case
     */
    public DetectedCaseResponse verifyCase(
            Integer caseId,
            String verificationMethod,
            String verificationResult,
            String decisionType,
            String decisionRationale,
            String verifiedBy,
            String verifiedByName) {
        
        DetectedCaseResponse response = new DetectedCaseResponse();
        
        try {
            // Create verification history record
            jdbcTemplate.update(
                "INSERT INTO detection.case_verification_history (" +
                "case_id, event_type, event_description, verification_method, " +
                "verification_result, decision_type, decision_rationale, event_by" +
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                caseId,
                "VERIFICATION_COMPLETED",
                "Case verified: " + (verificationResult != null ? verificationResult : ""),
                verificationMethod,
                verificationResult,
                decisionType,
                decisionRationale,
                verifiedBy
            );
            
            // Update case status
            String newStatus = "VERIFIED_INELIGIBLE";
            if ("FALSE_POSITIVE".equals(decisionType)) {
                newStatus = "VERIFIED_ELIGIBLE";
            } else if ("REQUIRES_RECALCULATION".equals(decisionType)) {
                newStatus = "UNDER_RECALCULATION";
            } else if ("APPEAL_GRANTED".equals(decisionType)) {
                newStatus = "APPEAL_GRANTED";
            }
            
            jdbcTemplate.update(
                "UPDATE detection.detected_cases " +
                "SET case_status = ?, final_decision = ?, verified_by = ?, " +
                "verified_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP " +
                "WHERE case_id = ?",
                newStatus,
                decisionType,
                verifiedBy,
                caseId
            );
            
            // Return updated case
            return getCase(caseId);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to verify case: " + e.getMessage());
            return response;
        }
    }

    /**
     * Get worklist for officer
     */
    public WorklistResponse getWorklist(String officerId, String queue, String status) {
        WorklistResponse response = new WorklistResponse();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT wa.assignment_id, wa.case_id, wa.worklist_queue, " +
                "dc.beneficiary_id, dc.scheme_code, dc.case_type, dc.case_status, " +
                "dc.priority, dc.financial_exposure, dc.detection_rationale, " +
                "wa.assigned_at " +
                "FROM detection.worklist_assignments wa " +
                "JOIN detection.detected_cases dc ON wa.case_id = dc.case_id " +
                "WHERE 1=1 "
            );
            
            List<Object> params = new ArrayList<>();
            
            if (officerId != null && !officerId.isEmpty()) {
                query.append("AND wa.assigned_to = ? ");
                params.add(officerId);
            }
            
            if (queue != null && !queue.isEmpty()) {
                query.append("AND wa.worklist_queue = ? ");
                params.add(queue);
            }
            
            if (status != null && !status.isEmpty()) {
                query.append("AND wa.status = ? ");
                params.add(status);
            } else {
                query.append("AND wa.status IN ('ASSIGNED', 'IN_PROGRESS') ");
            }
            
            query.append("ORDER BY dc.priority ASC, wa.assigned_at ASC");
            
            List<WorklistResponse.WorklistCase> cases = jdbcTemplate.query(
                query.toString(),
                new RowMapper<WorklistResponse.WorklistCase>() {
                    @Override
                    public WorklistResponse.WorklistCase mapRow(ResultSet rs, int rowNum) throws SQLException {
                        WorklistResponse.WorklistCase worklistCase = 
                            new WorklistResponse.WorklistCase();
                        worklistCase.setAssignmentId(rs.getInt("assignment_id"));
                        worklistCase.setCaseId(rs.getInt("case_id"));
                        worklistCase.setBeneficiaryId(rs.getString("beneficiary_id"));
                        worklistCase.setSchemeCode(rs.getString("scheme_code"));
                        worklistCase.setCaseType(rs.getString("case_type"));
                        worklistCase.setCaseStatus(rs.getString("case_status"));
                        worklistCase.setPriority(rs.getInt("priority"));
                        if (rs.getObject("financial_exposure") != null) {
                            worklistCase.setFinancialExposure(rs.getDouble("financial_exposure"));
                        }
                        worklistCase.setDetectionRationale(rs.getString("detection_rationale"));
                        if (rs.getTimestamp("assigned_at") != null) {
                            worklistCase.setAssignedAt(
                                rs.getTimestamp("assigned_at").toInstant().toString());
                        }
                        return worklistCase;
                    }
                },
                params.toArray()
            );
            
            response.setSuccess(true);
            response.setOfficerId(officerId);
            response.setWorklistQueue(queue);
            response.setCases(cases);
            response.setTotalCount(cases.size());
            response.setActiveCount((int) cases.stream().filter(
                c -> "IN_PROGRESS".equals(c.getCaseStatus())).count());
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get worklist: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Assign case to officer
     */
    public WorklistResponse assignCase(
            Integer caseId,
            String officerId,
            String queue,
            String assignedBy) {
        
        WorklistResponse response = new WorklistResponse();
        
        try {
            // Create worklist assignment
            Integer assignmentId = jdbcTemplate.queryForObject(
                "INSERT INTO detection.worklist_assignments (" +
                "case_id, assigned_to, assigned_by, worklist_queue, assignment_priority, status" +
                ") VALUES (?, ?, ?, ?, " +
                "(SELECT priority FROM detection.detected_cases WHERE case_id = ?), 'ASSIGNED') " +
                "RETURNING assignment_id",
                Integer.class,
                caseId, officerId, assignedBy != null ? assignedBy : "system", 
                queue != null ? queue : "SCHEME_SPECIFIC", caseId
            );
            
            // Update case assignment
            jdbcTemplate.update(
                "UPDATE detection.detected_cases " +
                "SET assigned_to = ?, assigned_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP " +
                "WHERE case_id = ?",
                officerId, caseId
            );
            
            // Return worklist
            return getWorklist(officerId, queue, null);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to assign case: " + e.getMessage());
            return response;
        }
    }

    /**
     * Get leakage analytics
     */
    public LeakageAnalyticsResponse getLeakageAnalytics(
            String schemeCode,
            String startDate,
            String endDate) {
        
        LeakageAnalyticsResponse response = new LeakageAnalyticsResponse();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT SUM(total_beneficiaries_scanned) as total_scanned, " +
                "SUM(total_cases_flagged) as total_flagged, " +
                "SUM(total_financial_exposure) as total_exposure, " +
                "SUM(estimated_savings) as total_savings, " +
                "SUM(confirmed_ineligible_count) as confirmed, " +
                "SUM(false_positive_count) as false_positives " +
                "FROM detection.leakage_analytics " +
                "WHERE 1=1 "
            );
            
            List<Object> params = new ArrayList<>();
            
            if (schemeCode != null && !schemeCode.isEmpty()) {
                query.append("AND scheme_code = ? ");
                params.add(schemeCode);
            }
            
            if (startDate != null && !startDate.isEmpty()) {
                query.append("AND analytics_date >= ?::date ");
                params.add(startDate);
            }
            
            if (endDate != null && !endDate.isEmpty()) {
                query.append("AND analytics_date <= ?::date ");
                params.add(endDate);
            }
            
            Map<String, Object> analytics = jdbcTemplate.queryForMap(
                query.toString(),
                params.toArray()
            );
            
            response.setSuccess(true);
            response.setSchemeCode(schemeCode);
            response.setPeriodStart(startDate);
            response.setPeriodEnd(endDate);
            
            Object totalScanned = analytics.get("total_scanned");
            if (totalScanned != null) {
                response.setTotalBeneficiariesScanned(((Number) totalScanned).intValue());
            }
            
            Object totalFlagged = analytics.get("total_flagged");
            if (totalFlagged != null) {
                response.setTotalCasesFlagged(((Number) totalFlagged).intValue());
            }
            
            if (analytics.get("total_exposure") != null) {
                response.setTotalFinancialExposure(((Number) analytics.get("total_exposure")).doubleValue());
            }
            
            if (analytics.get("total_savings") != null) {
                response.setEstimatedSavings(((Number) analytics.get("total_savings")).doubleValue());
            }
            
            Object confirmed = analytics.get("confirmed");
            if (confirmed != null) {
                response.setConfirmedIneligibleCount(((Number) confirmed).intValue());
            }
            
            Object falsePos = analytics.get("false_positives");
            if (falsePos != null) {
                response.setFalsePositiveCount(((Number) falsePos).intValue());
            }
            
            // Calculate rates
            int totalFlaggedInt = response.getTotalCasesFlagged() != null ? response.getTotalCasesFlagged() : 0;
            int confirmedInt = response.getConfirmedIneligibleCount() != null ? response.getConfirmedIneligibleCount() : 0;
            int falsePosInt = response.getFalsePositiveCount() != null ? response.getFalsePositiveCount() : 0;
            
            if (totalFlaggedInt > 0) {
                response.setConfirmationRate((double) confirmedInt / totalFlaggedInt);
                response.setFalsePositiveRate((double) falsePosInt / totalFlaggedInt);
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get analytics: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Detect single beneficiary (on-demand)
     */
    public DetectedCaseResponse detectBeneficiary(
            String beneficiaryId,
            String familyId,
            String schemeCode) {
        
        DetectedCaseResponse response = new DetectedCaseResponse();
        
        try {
            // Call Python DetectionOrchestrator
            Map<String, Object> result = pythonClient.detectBeneficiary(
                    beneficiaryId, familyId, schemeCode);

            if (result.get("success") != null && !(Boolean) result.get("success")) {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
                return response;
            }

            // If case was created, get it from database
            Object caseId = result.get("case_id");
            if (caseId != null) {
                return getCase(((Number) caseId).intValue());
            } else {
                // No case created (beneficiary passed all checks)
                response.setSuccess(true);
                response.setCaseId(null);
                return response;
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Detection failed: " + e.getMessage());
            return response;
        }
    }
}

