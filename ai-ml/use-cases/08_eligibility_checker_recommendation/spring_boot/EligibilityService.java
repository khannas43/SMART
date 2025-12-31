package com.smart.platform.eligibility.service;

import com.smart.platform.eligibility.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;

/**
 * Service layer for Eligibility Checker & Recommendations
 * Use Case ID: AI-PLATFORM-08
 */
@Service
public class EligibilityService {

    @Autowired
    private PythonEligibilityClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Check eligibility and get recommendations
     */
    public EligibilityCheckResponse checkEligibility(
            String familyId,
            String beneficiaryId,
            Map<String, Object> questionnaireResponses,
            String sessionId,
            List<String> schemeCodes,
            String checkType,
            String checkMode,
            String language) {
        
        EligibilityCheckResponse response = new EligibilityCheckResponse();
        
        try {
            Map<String, Object> result = pythonClient.checkAndRecommend(
                    familyId, beneficiaryId, questionnaireResponses, sessionId,
                    schemeCodes, checkType, checkMode, language);

            response.setSuccess(true);
            
            Object checkId = result.get("check_id");
            if (checkId != null) {
                response.setCheckId(checkId instanceof Number ? 
                    ((Number) checkId).intValue() : Integer.parseInt(checkId.toString()));
            }
            
            response.setSessionId((String) result.get("session_id"));
            response.setUserType((String) result.get("user_type"));
            
            Object isApprox = result.get("is_approximate");
            if (isApprox != null) {
                response.setIsApproximate(Boolean.parseBoolean(isApprox.toString()));
            }
            
            Object totalSchemes = result.get("total_schemes_checked");
            if (totalSchemes != null) {
                response.setTotalSchemesChecked(totalSchemes instanceof Number ? 
                    ((Number) totalSchemes).intValue() : Integer.parseInt(totalSchemes.toString()));
            }
            
            response.setEligibleCount(getIntValue(result.get("eligible_count")));
            response.setPossibleEligibleCount(getIntValue(result.get("possible_eligible_count")));
            response.setNotEligibleCount(getIntValue(result.get("not_eligible_count")));
            response.setProcessingTimeMs(getIntValue(result.get("processing_time_ms")));
            
            // Convert evaluations
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> topRecs = (List<Map<String, Object>>) result.get("top_recommendations");
            response.setTopRecommendations(convertEvaluations(topRecs));
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> otherSchemes = (List<Map<String, Object>>) result.get("other_schemes");
            response.setOtherSchemes(convertEvaluations(otherSchemes));
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> allEvals = (List<Map<String, Object>>) result.get("all_evaluations");
            response.setAllEvaluations(convertEvaluations(allEvals));
            
            Object recId = result.get("recommendation_id");
            if (recId != null) {
                response.setRecommendationId(recId instanceof Number ? 
                    ((Number) recId).intValue() : Integer.parseInt(recId.toString()));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Eligibility check failed: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get recommendations for logged-in user
     */
    public EligibilityCheckResponse getRecommendations(
            String familyId,
            String beneficiaryId,
            Boolean refresh,
            String language) {
        
        EligibilityCheckResponse response = new EligibilityCheckResponse();
        
        try {
            Map<String, Object> result = pythonClient.getRecommendations(
                    familyId, beneficiaryId, refresh, language);

            response.setSuccess(true);
            
            Object recId = result.get("recommendation_id");
            if (recId != null) {
                response.setRecommendationId(recId instanceof Number ? 
                    ((Number) recId).intValue() : Integer.parseInt(recId.toString()));
            }
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> topRecs = (List<Map<String, Object>>) result.get("top_recommendations");
            response.setTopRecommendations(convertEvaluations(topRecs));
            
            response.setFamilyId(familyId);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get recommendations: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get questionnaire template
     */
    public QuestionnaireResponse getQuestionnaire(String templateName) {
        QuestionnaireResponse response = new QuestionnaireResponse();
        
        try {
            Map<String, Object> result = pythonClient.getQuestionnaire(templateName);
            
            response.setSuccess(true);
            response.setTemplateName((String) result.get("template_name"));
            response.setTemplateVersion((String) result.get("template_version"));
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> questions = (List<Map<String, Object>>) result.get("questions");
            if (questions != null) {
                List<QuestionnaireResponse.Question> questionList = new ArrayList<>();
                for (Map<String, Object> q : questions) {
                    QuestionnaireResponse.Question question = new QuestionnaireResponse.Question();
                    question.setId((String) q.get("id"));
                    question.setQuestion((String) q.get("question"));
                    question.setType((String) q.get("type"));
                    Object required = q.get("required");
                    question.setRequired(required != null && Boolean.parseBoolean(required.toString()));
                    
                    @SuppressWarnings("unchecked")
                    List<String> options = (List<String>) q.get("options");
                    question.setOptions(options);
                    
                    questionList.add(question);
                }
                response.setQuestions(questionList);
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get questionnaire: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get eligibility for specific scheme
     */
    public EligibilityCheckResponse getSchemeEligibility(
            String schemeCode,
            String familyId,
            String sessionId,
            String questionnaire,
            String language) {
        
        // Parse questionnaire if provided
        Map<String, Object> questionnaireResponses = null;
        if (questionnaire != null && !questionnaire.isEmpty()) {
            try {
                questionnaireResponses = objectMapper.readValue(questionnaire, 
                    new TypeReference<Map<String, Object>>() {});
            } catch (Exception e) {
                // Ignore parsing errors
            }
        }
        
        List<String> schemeCodes = Collections.singletonList(schemeCode);
        
        return checkEligibility(
            familyId, null, questionnaireResponses, sessionId,
            schemeCodes, "SCHEME_SPECIFIC", "WEB", language
        );
    }

    /**
     * Get check history
     */
    public List<EligibilityCheckResponse> getCheckHistory(
            String familyId,
            String sessionId,
            Integer limit) {
        
        List<EligibilityCheckResponse> history = new ArrayList<>();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT check_id, session_id, user_type, check_type, " +
                "total_schemes_checked, eligible_count, possible_eligible_count, " +
                "not_eligible_count, check_timestamp " +
                "FROM eligibility_checker.eligibility_checks " +
                "WHERE 1=1 "
            );
            
            List<Object> params = new ArrayList<>();
            
            if (familyId != null && !familyId.isEmpty()) {
                query.append("AND family_id = ?::uuid ");
                params.add(familyId);
            }
            
            if (sessionId != null && !sessionId.isEmpty()) {
                query.append("AND session_id = ? ");
                params.add(sessionId);
            }
            
            query.append("ORDER BY check_timestamp DESC LIMIT ?");
            params.add(limit);
            
            List<Map<String, Object>> checks = jdbcTemplate.query(
                query.toString(),
                new RowMapper<Map<String, Object>>() {
                    @Override
                    public Map<String, Object> mapRow(ResultSet rs, int rowNum) throws SQLException {
                        Map<String, Object> check = new HashMap<>();
                        check.put("check_id", rs.getInt("check_id"));
                        check.put("session_id", rs.getString("session_id"));
                        check.put("user_type", rs.getString("user_type"));
                        check.put("check_type", rs.getString("check_type"));
                        check.put("total_schemes_checked", rs.getInt("total_schemes_checked"));
                        check.put("eligible_count", rs.getInt("eligible_count"));
                        check.put("possible_eligible_count", rs.getInt("possible_eligible_count"));
                        check.put("not_eligible_count", rs.getInt("not_eligible_count"));
                        if (rs.getTimestamp("check_timestamp") != null) {
                            check.put("check_timestamp", 
                                rs.getTimestamp("check_timestamp").toInstant().toString());
                        }
                        return check;
                    }
                },
                params.toArray()
            );
            
            for (Map<String, Object> check : checks) {
                EligibilityCheckResponse response = new EligibilityCheckResponse();
                response.setSuccess(true);
                response.setCheckId(((Number) check.get("check_id")).intValue());
                response.setSessionId((String) check.get("session_id"));
                response.setUserType((String) check.get("user_type"));
                response.setTotalSchemesChecked(((Number) check.get("total_schemes_checked")).intValue());
                response.setEligibleCount(((Number) check.get("eligible_count")).intValue());
                response.setPossibleEligibleCount(((Number) check.get("possible_eligible_count")).intValue());
                response.setNotEligibleCount(((Number) check.get("not_eligible_count")).intValue());
                history.add(response);
            }
            
        } catch (Exception e) {
            // Return empty list on error
        }
        
        return history;
    }

    /**
     * Convert Python evaluation results to DTOs
     */
    private List<EligibilityCheckResponse.SchemeEvaluationResult> convertEvaluations(
            List<Map<String, Object>> evaluations) {
        
        if (evaluations == null) {
            return new ArrayList<>();
        }
        
        List<EligibilityCheckResponse.SchemeEvaluationResult> results = new ArrayList<>();
        
        for (Map<String, Object> eval : evaluations) {
            EligibilityCheckResponse.SchemeEvaluationResult result = 
                new EligibilityCheckResponse.SchemeEvaluationResult();
            
            result.setSchemeCode((String) eval.get("scheme_code"));
            result.setSchemeName((String) eval.get("scheme_name"));
            result.setEligibilityStatus((String) eval.get("eligibility_status"));
            
            Object score = eval.get("eligibility_score");
            if (score != null) {
                result.setEligibilityScore(score instanceof Number ? 
                    ((Number) score).doubleValue() : Double.parseDouble(score.toString()));
            }
            
            result.setConfidenceLevel((String) eval.get("confidence_level"));
            
            Object rank = eval.get("recommendation_rank");
            if (rank != null) {
                result.setRecommendationRank(rank instanceof Number ? 
                    ((Number) rank).intValue() : Integer.parseInt(rank.toString()));
            }
            
            Object priorityScore = eval.get("priority_score");
            if (priorityScore != null) {
                result.setPriorityScore(priorityScore instanceof Number ? 
                    ((Number) priorityScore).doubleValue() : Double.parseDouble(priorityScore.toString()));
            }
            
            Object impactScore = eval.get("impact_score");
            if (impactScore != null) {
                result.setImpactScore(impactScore instanceof Number ? 
                    ((Number) impactScore).doubleValue() : Double.parseDouble(impactScore.toString()));
            }
            
            result.setExplanationText((String) eval.get("explanation_text"));
            
            @SuppressWarnings("unchecked")
            List<String> nextSteps = (List<String>) eval.get("next_steps");
            result.setNextSteps(nextSteps);
            
            @SuppressWarnings("unchecked")
            List<String> metRules = (List<String>) eval.get("met_rules");
            result.setMetRules(metRules);
            
            @SuppressWarnings("unchecked")
            List<String> failedRules = (List<String>) eval.get("failed_rules");
            result.setFailedRules(failedRules);
            
            results.add(result);
        }
        
        return results;
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
}

