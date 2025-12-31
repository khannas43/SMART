package com.smart.platform.aiml.eligibility.service;

import com.smart.platform.aiml.eligibility.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service layer for Eligibility Evaluation
 * Integrates with Python evaluation service via process execution or REST API
 * Use Case: AI-PLATFORM-03
 */
@Service
public class EligibilityEvaluationService {

    @Autowired
    private PythonEvaluationClient pythonClient;

    @Value("${eligibility.evaluation.enabled:true}")
    private boolean evaluationEnabled;

    @Value("${eligibility.evaluation.use_ml:true}")
    private boolean useMl;

    /**
     * Evaluate eligibility for a family
     */
    public EvaluationResponse evaluateFamily(
            UUID familyId,
            List<String> schemeIds,
            boolean useMlOverride
    ) {
        if (!evaluationEnabled) {
            return EvaluationResponse.error("Evaluation service is disabled");
        }

        try {
            // Call Python evaluation service
            Map<String, Object> result = pythonClient.callEvaluationService(
                    "evaluate_family",
                    Map.of(
                            "family_id", familyId.toString(),
                            "scheme_ids", schemeIds != null ? schemeIds : Collections.emptyList(),
                            "use_ml", useMlOverride || useMl
                    )
            );

            // Convert to response DTO
            return EvaluationResponse.fromMap(result);

        } catch (Exception e) {
            return EvaluationResponse.error("Evaluation failed: " + e.getMessage());
        }
    }

    /**
     * Get precomputed eligibility results
     */
    public PrecomputedResultsResponse getPrecomputedResults(
            UUID familyId,
            List<String> schemeIds
    ) {
        try {
            Map<String, Object> result = pythonClient.callEvaluationService(
                    "get_precomputed_results",
                    Map.of(
                            "family_id", familyId.toString(),
                            "scheme_ids", schemeIds != null ? schemeIds : Collections.emptyList()
                    )
            );

            return PrecomputedResultsResponse.fromMap(result);

        } catch (Exception e) {
            return PrecomputedResultsResponse.error("Failed to retrieve results: " + e.getMessage());
        }
    }

    /**
     * Generate citizen-facing eligibility hints
     */
    public List<SchemeHint> generateCitizenHints(UUID familyId) {
        try {
            Map<String, Object> result = pythonClient.callEvaluationService(
                    "generate_citizen_hints",
                    Map.of("family_id", familyId.toString())
            );

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> hintsData = (List<Map<String, Object>>) result.get("hints");

            return hintsData.stream()
                    .map(SchemeHint::fromMap)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    /**
     * Generate departmental worklist
     */
    public List<Candidate> generateDepartmentalWorklist(
            String schemeId,
            Integer districtId,
            double minScore,
            int limit
    ) {
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("scheme_id", schemeId);
            params.put("min_score", minScore);
            params.put("limit", limit);
            if (districtId != null) {
                params.put("district_id", districtId);
            }

            Map<String, Object> result = pythonClient.callEvaluationService(
                    "generate_departmental_worklist",
                    params
            );

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> candidatesData = (List<Map<String, Object>>) result.get("worklist");

            return candidatesData.stream()
                    .map(Candidate::fromMap)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    /**
     * Trigger batch evaluation
     */
    public BatchEvaluationResponse evaluateBatch(
            List<String> schemeIds,
            List<Integer> districtIds,
            Integer maxFamilies
    ) {
        try {
            Map<String, Object> params = new HashMap<>();
            if (schemeIds != null) {
                params.put("scheme_ids", schemeIds);
            }
            if (districtIds != null) {
                params.put("district_ids", districtIds);
            }
            if (maxFamilies != null) {
                params.put("max_families", maxFamilies);
            }

            Map<String, Object> result = pythonClient.callEvaluationService(
                    "evaluate_batch",
                    params
            );

            return BatchEvaluationResponse.fromMap(result);

        } catch (Exception e) {
            return BatchEvaluationResponse.error("Batch evaluation failed: " + e.getMessage());
        }
    }

    /**
     * Get batch evaluation status
     */
    public BatchStatusResponse getBatchStatus(String batchId) {
        try {
            Map<String, Object> result = pythonClient.callEvaluationService(
                    "get_batch_status",
                    Map.of("batch_id", batchId)
            );

            return BatchStatusResponse.fromMap(result);

        } catch (Exception e) {
            return BatchStatusResponse.error("Failed to get batch status: " + e.getMessage());
        }
    }

    /**
     * Get scheme configuration
     */
    public SchemeConfigResponse getSchemeConfig(String schemeId) {
        try {
            // Query database for scheme configuration
            // This would typically use a repository
            return SchemeConfigResponse.builder()
                    .schemeId(schemeId)
                    .schemeName("Scheme Name") // TODO: Load from database
                    .rules(Collections.emptyList())
                    .mlModelAvailable(false)
                    .build();

        } catch (Exception e) {
            return SchemeConfigResponse.error("Failed to get scheme config: " + e.getMessage());
        }
    }
}

