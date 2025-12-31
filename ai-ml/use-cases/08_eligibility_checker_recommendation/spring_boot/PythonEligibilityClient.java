package com.smart.platform.eligibility.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python EligibilityOrchestrator service
 * Use Case ID: AI-PLATFORM-08
 */
@Component
public class PythonEligibilityClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.eligibility.api.url:http://localhost:8003}")
    private String pythonApiUrl;

    @Value("${python.eligibility.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Check eligibility and get recommendations
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> checkAndRecommend(
            String familyId,
            String beneficiaryId,
            Map<String, Object> questionnaireResponses,
            String sessionId,
            List<String> schemeCodes,
            String checkType,
            String checkMode,
            String language) {
        
        Map<String, Object> params = new HashMap<>();
        if (familyId != null) params.put("family_id", familyId);
        if (beneficiaryId != null) params.put("beneficiary_id", beneficiaryId);
        if (questionnaireResponses != null) params.put("questionnaire_responses", questionnaireResponses);
        if (sessionId != null) params.put("session_id", sessionId);
        if (schemeCodes != null) params.put("scheme_codes", schemeCodes);
        params.put("check_type", checkType != null ? checkType : "FULL_CHECK");
        params.put("check_mode", checkMode != null ? checkMode : "WEB");
        params.put("language", language != null ? language : "en");
        params.put("generate_recommendations", true);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("check_and_recommend", params);
        } else {
            return callPythonScript("check_and_recommend", params);
        }
    }

    /**
     * Get recommendations
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getRecommendations(
            String familyId,
            String beneficiaryId,
            Boolean refresh,
            String language) {
        
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        if (beneficiaryId != null) params.put("beneficiary_id", beneficiaryId);
        params.put("refresh", refresh != null ? refresh : false);
        params.put("language", language != null ? language : "en");
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_recommendations", params);
        } else {
            return callPythonScript("get_recommendations", params);
        }
    }

    /**
     * Get questionnaire
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getQuestionnaire(String templateName) {
        Map<String, Object> params = new HashMap<>();
        params.put("template_name", templateName != null ? templateName : "default_guest_questionnaire");
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_questionnaire", params);
        } else {
            return callPythonScript("get_questionnaire", params);
        }
    }

    /**
     * Call Python script directly
     */
    private Map<String, Object> callPythonScript(String method, Map<String, Object> params) {
        try {
            String script = createPythonCallScript(method, params);

            String pythonExecutable = Paths.get(pythonVenvPath, "bin", "python").toString();
            ProcessBuilder pb = new ProcessBuilder(
                    pythonExecutable,
                    "-c", script
            );

            String useCaseDir = Paths.get(System.getProperty("user.dir"), 
                    "ai-ml", "use-cases", "08_eligibility_checker_recommendation").toString();
            pb.directory(new File(useCaseDir));
            
            Map<String, String> env = pb.environment();
            env.put("PYTHONPATH", useCaseDir + ":" + Paths.get(useCaseDir, "..", "..", "..", "shared", "utils").toString());

            Process process = pb.start();

            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            BufferedReader errorReader = new BufferedReader(
                    new InputStreamReader(process.getErrorStream())
            );
            StringBuilder errorOutput = new StringBuilder();
            while ((line = errorReader.readLine()) != null) {
                errorOutput.append(line).append("\n");
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("Python script execution failed with code: " + exitCode + 
                        "\nError: " + errorOutput.toString());
            }

            String outputStr = output.toString().trim();
            if (outputStr.isEmpty()) {
                throw new RuntimeException("Python script returned empty output");
            }

            return objectMapper.readValue(outputStr, Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python EligibilityOrchestrator: " + e.getMessage(), e);
        }
    }

    /**
     * Call Python REST API
     */
    private Map<String, Object> callPythonApi(String method, Map<String, Object> params) {
        // TODO: Implement HTTP client to call Python API
        return callPythonScript(method, params);
    }

    /**
     * Create Python script to call EligibilityOrchestrator method
     */
    private String createPythonCallScript(String method, Map<String, Object> params) {
        StringBuilder script = new StringBuilder();
        script.append("import sys\n");
        script.append("import json\n");
        script.append("from pathlib import Path\n");
        script.append("import os\n");
        script.append("\n");
        script.append("# Add paths\n");
        script.append("base_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()\n");
        script.append("use_case_dir = base_dir / 'ai-ml' / 'use-cases' / '08_eligibility_checker_recommendation'\n");
        script.append("if not use_case_dir.exists():\n");
        script.append("    use_case_dir = Path.cwd()\n");
        script.append("sys.path.insert(0, str(use_case_dir / 'src'))\n");
        script.append("sys.path.insert(0, str(use_case_dir / '..' / '..' / '..' / 'shared' / 'utils'))\n");
        script.append("sys.path.insert(0, str(use_case_dir / '..' / '03_identification_beneficiary' / 'src'))\n");
        script.append("\n");
        script.append("from services.eligibility_orchestrator import EligibilityOrchestrator\n");
        script.append("from services.questionnaire_handler import QuestionnaireHandler\n");
        script.append("\n");
        script.append("try:\n");
        
        if ("check_and_recommend".equals(method)) {
            script.append("    orchestrator = EligibilityOrchestrator()\n");
            script.append("    orchestrator.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = orchestrator.check_and_recommend(\n");
            script.append("        family_id=params.get('family_id'),\n");
            script.append("        beneficiary_id=params.get('beneficiary_id'),\n");
            script.append("        questionnaire_responses=params.get('questionnaire_responses'),\n");
            script.append("        session_id=params.get('session_id'),\n");
            script.append("        scheme_codes=params.get('scheme_codes'),\n");
            script.append("        check_type=params.get('check_type', 'FULL_CHECK'),\n");
            script.append("        check_mode=params.get('check_mode', 'WEB'),\n");
            script.append("        generate_recommendations=params.get('generate_recommendations', True),\n");
            script.append("        language=params.get('language', 'en')\n");
            script.append("    )\n");
            script.append("    orchestrator.disconnect()\n");
        } else if ("get_recommendations".equals(method)) {
            script.append("    orchestrator = EligibilityOrchestrator()\n");
            script.append("    orchestrator.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = orchestrator.get_recommendations(\n");
            script.append("        family_id=params.get('family_id'),\n");
            script.append("        beneficiary_id=params.get('beneficiary_id'),\n");
            script.append("        refresh=params.get('refresh', False),\n");
            script.append("        language=params.get('language', 'en')\n");
            script.append("    )\n");
            script.append("    orchestrator.disconnect()\n");
        } else if ("get_questionnaire".equals(method)) {
            script.append("    handler = QuestionnaireHandler()\n");
            script.append("    handler.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = handler.get_questionnaire(\n");
            script.append("        template_name=params.get('template_name', 'default_guest_questionnaire')\n");
            script.append("    )\n");
            script.append("    handler.disconnect()\n");
        }
        
        script.append("    \n");
        script.append("    # Convert to JSON-serializable format\n");
        script.append("    def convert_value(v):\n");
        script.append("        if hasattr(v, 'isoformat'):  # datetime\n");
        script.append("            return v.isoformat()\n");
        script.append("        elif hasattr(v, '__dict__'):  # object\n");
        script.append("            return str(v)\n");
        script.append("        return v\n");
        script.append("    \n");
        script.append("    def convert_dict(d):\n");
        script.append("        if isinstance(d, dict):\n");
        script.append("            return {k: convert_dict(v) for k, v in d.items()}\n");
        script.append("        elif isinstance(d, list):\n");
        script.append("            return [convert_dict(v) for v in d]\n");
        script.append("        else:\n");
        script.append("            return convert_value(d)\n");
        script.append("    \n");
        script.append("    result_serializable = convert_dict(result)\n");
        script.append("    print(json.dumps(result_serializable, default=str))\n");
        script.append("    \n");
        script.append("except Exception as e:\n");
        script.append("    print(json.dumps({'success': False, 'error': str(e)}))\n");
        script.append("    sys.exit(1)\n");

        return script.toString();
    }

    /**
     * Convert Java Map to Python dict string
     */
    private String paramsToPythonDict(Map<String, Object> params) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            first = false;
            sb.append("'").append(entry.getKey()).append("': ");
            Object value = entry.getValue();
            if (value == null) {
                sb.append("None");
            } else if (value instanceof String) {
                sb.append("'").append(value.toString().replace("'", "\\'")).append("'");
            } else if (value instanceof Number || value instanceof Boolean) {
                sb.append(value);
            } else if (value instanceof List) {
                sb.append("[");
                List<?> list = (List<?>) value;
                for (int i = 0; i < list.size(); i++) {
                    if (i > 0) sb.append(", ");
                    Object item = list.get(i);
                    if (item instanceof String) {
                        sb.append("'").append(item.toString().replace("'", "\\'")).append("'");
                    } else {
                        sb.append(item);
                    }
                }
                sb.append("]");
            } else if (value instanceof Map) {
                sb.append("{");
                Map<?, ?> map = (Map<?, ?>) value;
                boolean mapFirst = true;
                for (Map.Entry<?, ?> mapEntry : map.entrySet()) {
                    if (!mapFirst) sb.append(", ");
                    mapFirst = false;
                    if (mapEntry.getKey() instanceof String) {
                        sb.append("'").append(mapEntry.getKey().toString().replace("'", "\\'")).append("': ");
                    } else {
                        sb.append(mapEntry.getKey()).append(": ");
                    }
                    Object mapValue = mapEntry.getValue();
                    if (mapValue instanceof String) {
                        sb.append("'").append(mapValue.toString().replace("'", "\\'")).append("'");
                    } else {
                        sb.append(mapValue);
                    }
                }
                sb.append("}");
            } else {
                sb.append("'").append(value.toString().replace("'", "\\'")).append("'");
            }
        }
        sb.append("}");
        return sb.toString();
    }
}

