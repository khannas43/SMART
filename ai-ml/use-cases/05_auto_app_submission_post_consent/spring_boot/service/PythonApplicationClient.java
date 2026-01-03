package com.smart.platform.aiml.application.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python Application services
 * Executes Python scripts or calls REST API
 * Use Case ID: AI-PLATFORM-05
 */
@Component
public class PythonApplicationClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.application.api.url:http://localhost:8005}")
    private String pythonApiUrl;

    @Value("${python.application.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Process consent event and create/submit application
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> processConsentEvent(
            String familyId,
            String schemeCode,
            Integer consentId) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("scheme_code", schemeCode);
        if (consentId != null) params.put("consent_id", consentId);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("process_consent_event", params);
        } else {
            return callPythonScript("process_consent_event", params);
        }
    }

    /**
     * Get application draft for citizen review
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getApplicationDraft(String familyId, String schemeCode) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("scheme_code", schemeCode);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_application_draft", params);
        } else {
            return callPythonScript("get_application_draft", params);
        }
    }

    /**
     * Confirm and submit reviewed application
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> confirmApplication(Integer applicationId, String schemeCode) {
        Map<String, Object> params = new HashMap<>();
        params.put("application_id", applicationId);
        params.put("scheme_code", schemeCode);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("confirm_application", params);
        } else {
            return callPythonScript("confirm_application", params);
        }
    }

    /**
     * Retry failed submission
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> retrySubmission(Integer applicationId) {
        Map<String, Object> params = new HashMap<>();
        params.put("application_id", applicationId);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("retry_submission", params);
        } else {
            return callPythonScript("retry_submission", params);
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
                    "ai-ml", "use-cases", "05_auto_app_submission_post_consent").toString();
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
                throw new RuntimeException("Python script failed: " + errorOutput.toString());
            }

            String jsonOutput = output.toString();
            if (jsonOutput.isEmpty()) {
                return new HashMap<>();
            }

            return objectMapper.readValue(jsonOutput, Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python script: " + e.getMessage(), e);
        }
    }

    /**
     * Call Python API (REST endpoint)
     */
    private Map<String, Object> callPythonApi(String method, Map<String, Object> params) {
        try {
            // TODO: Implement REST API call when Python API server is available
            // For now, fall back to script mode
            return callPythonScript(method, params);
        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python API: " + e.getMessage(), e);
        }
    }

    /**
     * Create Python script to call method
     */
    private String createPythonCallScript(String method, Map<String, Object> params) {
        StringBuilder script = new StringBuilder();
        script.append("import sys\n");
        script.append("import os\n");
        script.append("import json\n");
        script.append("from pathlib import Path\n");
        script.append("sys.path.append(str(Path(__file__).parent))\n");
        script.append("sys.path.append(str(Path(__file__).parent.parent.parent / 'shared' / 'utils'))\n");
        script.append("\n");
        script.append("from src.application_service import ApplicationService\n");
        script.append("from src.submission_handler import SubmissionHandler\n");
        script.append("\n");
        script.append("params = ").append(convertToPythonDict(params)).append("\n");
        script.append("method = '").append(method).append("'\n");
        script.append("\n");
        script.append("try:\n");
        script.append("    result = None\n");
        script.append("    service = ApplicationService()\n");
        script.append("    \n");
        script.append("    if method == 'process_consent_event':\n");
        script.append("        result = service.process_consent_event(\n");
        script.append("            family_id=params['family_id'],\n");
        script.append("            scheme_code=params['scheme_code'],\n");
        script.append("            consent_id=params.get('consent_id')\n");
        script.append("        )\n");
        script.append("    \n");
        script.append("    elif method == 'get_application_draft':\n");
        script.append("        result = service.get_application_draft(\n");
        script.append("            family_id=params['family_id'],\n");
        script.append("            scheme_code=params['scheme_code']\n");
        script.append("        )\n");
        script.append("    \n");
        script.append("    elif method == 'confirm_application':\n");
        script.append("        result = service.confirm_application(\n");
        script.append("            application_id=params['application_id'],\n");
        script.append("            scheme_code=params['scheme_code']\n");
        script.append("        )\n");
        script.append("    \n");
        script.append("    elif method == 'retry_submission':\n");
        script.append("        handler = SubmissionHandler()\n");
        script.append("        # Get application details first\n");
        script.append("        query = 'SELECT scheme_code, submission_mode FROM application.applications WHERE application_id = %s'\n");
        script.append("        cursor = handler.db.connection.cursor()\n");
        script.append("        cursor.execute(query, [params['application_id']])\n");
        script.append("        row = cursor.fetchone()\n");
        script.append("        cursor.close()\n");
        script.append("        if row:\n");
        script.append("            scheme_code, submission_mode = row\n");
        script.append("            result = handler.handle_submission(\n");
        script.append("                application_id=params['application_id'],\n");
        script.append("                scheme_code=scheme_code,\n");
        script.append("                submission_mode=submission_mode\n");
        script.append("            )\n");
        script.append("        else:\n");
        script.append("            result = {'success': False, 'error': 'Application not found'}\n");
        script.append("    \n");
        script.append("    service.disconnect()\n");
        script.append("    print(json.dumps(result))\n");
        script.append("    \n");
        script.append("except Exception as e:\n");
        script.append("    print(json.dumps({'success': False, 'error': str(e)}))\n");
        script.append("    sys.exit(1)\n");
        
        return script.toString();
    }

    /**
     * Convert Java Map to Python dict string
     */
    private String convertToPythonDict(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) sb.append(", ");
            first = false;
            sb.append("'").append(entry.getKey()).append("': ");
            Object value = entry.getValue();
            if (value == null) {
                sb.append("None");
            } else if (value instanceof String) {
                sb.append("'").append(escapePythonString(value.toString())).append("'");
            } else if (value instanceof List) {
                sb.append(convertToPythonList((List<?>) value));
            } else if (value instanceof Map) {
                sb.append(convertToPythonDict((Map<String, Object>) value));
            } else {
                sb.append(value.toString());
            }
        }
        sb.append("}");
        return sb.toString();
    }

    private String convertToPythonList(List<?> list) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        boolean first = true;
        for (Object item : list) {
            if (!first) sb.append(", ");
            first = false;
            if (item instanceof String) {
                sb.append("'").append(escapePythonString(item.toString())).append("'");
            } else if (item instanceof Map) {
                sb.append(convertToPythonDict((Map<String, Object>) item));
            } else {
                sb.append(item.toString());
            }
        }
        sb.append("]");
        return sb.toString();
    }

    private String escapePythonString(String str) {
        return str.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n");
    }
}

