package com.smart.platform.aiml.eligibility.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python evaluation service
 * Executes Python scripts or calls REST API
 */
@Component
public class PythonEvaluationClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.evaluation.script:src/evaluator_service.py}")
    private String evaluationScriptPath;

    @Value("${python.evaluation.api.url:http://localhost:8000}")
    private String pythonApiUrl;

    @Value("${python.evaluation.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Call Python evaluation service
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callEvaluationService(String method, Map<String, Object> params) {
        if ("api".equals(executionMode)) {
            return callPythonApi(method, params);
        } else {
            return callPythonScript(method, params);
        }
    }

    /**
     * Call Python script directly
     */
    private Map<String, Object> callPythonScript(String method, Map<String, Object> params) {
        try {
            // Create Python script to call method
            String script = createPythonCallScript(method, params);

            // Execute Python
            ProcessBuilder pb = new ProcessBuilder(
                    Paths.get(pythonVenvPath, "bin", "python").toString(),
                    "-c", script
            );

            pb.directory(Paths.get(System.getProperty("user.dir")).toFile());
            Process process = pb.start();

            // Read output
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("Python script execution failed with code: " + exitCode);
            }

            // Parse JSON output
            return objectMapper.readValue(output.toString(), Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python service: " + e.getMessage(), e);
        }
    }

    /**
     * Call Python REST API
     */
    private Map<String, Object> callPythonApi(String method, Map<String, Object> params) {
        // TODO: Implement HTTP client to call Python API
        // For now, fall back to script execution
        return callPythonScript(method, params);
    }

    /**
     * Create Python script to call method
     */
    private String createPythonCallScript(String method, Map<String, Object> params) {
        StringBuilder script = new StringBuilder();
        script.append("import sys\n");
        script.append("import json\n");
        script.append("from pathlib import Path\n");
        script.append("sys.path.append(str(Path.cwd() / 'use-cases' / '03_identification_beneficiary' / 'src'))\n");
        script.append("from evaluator_service import EligibilityEvaluationService\n");
        script.append("\n");
        script.append("service = EligibilityEvaluationService()\n");
        script.append("params = ").append(paramsToPythonDict(params)).append("\n");
        script.append("result = service.").append(method).append("(**params)\n");
        script.append("print(json.dumps(result, default=str))\n");
        script.append("service.close()\n");

        return script.toString();
    }

    /**
     * Convert Java Map to Python dict string
     */
    private String paramsToPythonDict(Map<String, Object> params) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            sb.append("'").append(entry.getKey()).append("': ");
            
            Object value = entry.getValue();
            if (value instanceof String) {
                sb.append("'").append(value).append("'");
            } else if (value instanceof List) {
                sb.append("[");
                List<?> list = (List<?>) value;
                for (int i = 0; i < list.size(); i++) {
                    if (i > 0) sb.append(", ");
                    sb.append("'").append(list.get(i)).append("'");
                }
                sb.append("]");
            } else {
                sb.append(value);
            }
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }
}

