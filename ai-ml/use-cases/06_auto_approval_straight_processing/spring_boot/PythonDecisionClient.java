package com.smart.platform.decision.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python DecisionEngine service
 * Executes Python scripts or calls REST API
 * Use Case ID: AI-PLATFORM-06
 */
@Component
public class PythonDecisionClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.decision.script:src/decision_engine.py}")
    private String decisionScriptPath;

    @Value("${python.decision.api.url:http://localhost:8001}")
    private String pythonApiUrl;

    @Value("${python.decision.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Call Python DecisionEngine to evaluate an application
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> evaluateApplication(
            Integer applicationId,
            String familyId,
            String schemeCode) {
        
        Map<String, Object> params = new HashMap<>();
        params.put("application_id", applicationId);
        if (familyId != null) {
            params.put("family_id", familyId);
        }
        if (schemeCode != null) {
            params.put("scheme_code", schemeCode);
        }
        
        if ("api".equals(executionMode)) {
            return callPythonApi("evaluate_application", params);
        } else {
            return callPythonScript("evaluate_application", params);
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
            String pythonExecutable = Paths.get(pythonVenvPath, "bin", "python").toString();
            ProcessBuilder pb = new ProcessBuilder(
                    pythonExecutable,
                    "-c", script
            );

            // Set working directory to use case directory
            String useCaseDir = Paths.get(System.getProperty("user.dir"), 
                    "ai-ml", "use-cases", "06_auto_approval_straight_processing").toString();
            pb.directory(new File(useCaseDir));
            
            // Set environment
            Map<String, String> env = pb.environment();
            env.put("PYTHONPATH", useCaseDir + ":" + Paths.get(useCaseDir, "..", "..", "..", "shared", "utils").toString());

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

            // Read error output
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

            // Parse JSON output
            String outputStr = output.toString().trim();
            if (outputStr.isEmpty()) {
                throw new RuntimeException("Python script returned empty output");
            }

            return objectMapper.readValue(outputStr, Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python DecisionEngine: " + e.getMessage(), e);
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
     * Create Python script to call DecisionEngine method
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
        script.append("use_case_dir = base_dir / 'ai-ml' / 'use-cases' / '06_auto_approval_straight_processing'\n");
        script.append("if not use_case_dir.exists():\n");
        script.append("    use_case_dir = Path.cwd()\n");
        script.append("sys.path.insert(0, str(use_case_dir / 'src'))\n");
        script.append("sys.path.insert(0, str(use_case_dir / '..' / '..' / '..' / 'shared' / 'utils'))\n");
        script.append("\n");
        script.append("from decision_engine import DecisionEngine\n");
        script.append("\n");
        script.append("try:\n");
        script.append("    engine = DecisionEngine()\n");
        script.append("    engine.connect()\n");
        script.append("    \n");
        
        if ("evaluate_application".equals(method)) {
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = engine.evaluate_application(\n");
            script.append("        application_id=params.get('application_id'),\n");
            script.append("        family_id=params.get('family_id'),\n");
            script.append("        scheme_code=params.get('scheme_code')\n");
            script.append("    )\n");
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
        script.append("    engine.disconnect()\n");
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
            } else {
                sb.append("'").append(value.toString().replace("'", "\\'")).append("'");
            }
        }
        sb.append("}");
        return sb.toString();
    }
}

