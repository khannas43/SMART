package com.smart.platform.inclusion.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python InclusionOrchestrator service
 * Use Case ID: AI-PLATFORM-09
 */
@Component
public class PythonInclusionClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.inclusion.api.url:http://localhost:8004}")
    private String pythonApiUrl;

    @Value("${python.inclusion.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get priority status
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getPriorityStatus(String familyId, Boolean includeNudges) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("include_nudges", includeNudges != null ? includeNudges : true);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_priority_status", params);
        } else {
            return callPythonScript("get_priority_status", params);
        }
    }

    /**
     * Get priority list
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getPriorityList(
            String blockId, String district, List<String> segments,
            String priorityLevel, Integer limit) {
        Map<String, Object> params = new HashMap<>();
        if (blockId != null) params.put("block_id", blockId);
        if (district != null) params.put("district", district);
        if (segments != null) params.put("segment_filters", segments);
        if (priorityLevel != null) params.put("priority_level_filter", priorityLevel);
        params.put("limit", limit != null ? limit : 50);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_priority_list", params);
        } else {
            return callPythonScript("get_priority_list", params);
        }
    }

    /**
     * Schedule nudge delivery
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> scheduleNudgeDelivery(
            String familyId, String nudgeType, String nudgeMessage,
            List<String> recommendedActions, List<String> schemeCodes,
            String channel, String priorityLevel, String scheduledAt) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("nudge_type", nudgeType);
        params.put("nudge_message", nudgeMessage);
        if (recommendedActions != null) params.put("recommended_actions", recommendedActions);
        if (schemeCodes != null) params.put("scheme_codes", schemeCodes);
        params.put("channel", channel);
        params.put("priority_level", priorityLevel);
        if (scheduledAt != null) params.put("scheduled_at", scheduledAt);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("schedule_nudge_delivery", params);
        } else {
            return callPythonScript("schedule_nudge_delivery", params);
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
                    "ai-ml", "use-cases", "09_proactive_inclusion_exception_handling").toString();
            pb.directory(new File(useCaseDir));
            
            Map<String, String> env = pb.environment();
            env.put("PYTHONPATH", useCaseDir + ":" + 
                    Paths.get(useCaseDir, "..", "..", "..", "shared", "utils").toString());

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
            throw new RuntimeException("Failed to call Python InclusionOrchestrator: " + e.getMessage(), e);
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
     * Create Python script to call InclusionOrchestrator method
     */
    private String createPythonCallScript(String method, Map<String, Object> params) {
        StringBuilder script = new StringBuilder();
        script.append("import sys\n");
        script.append("import json\n");
        script.append("from pathlib import Path\n");
        script.append("import os\n");
        script.append("from datetime import datetime\n");
        script.append("\n");
        script.append("# Add paths\n");
        script.append("base_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()\n");
        script.append("use_case_dir = base_dir / 'ai-ml' / 'use-cases' / '09_proactive_inclusion_exception_handling'\n");
        script.append("if not use_case_dir.exists():\n");
        script.append("    use_case_dir = Path.cwd()\n");
        script.append("sys.path.insert(0, str(use_case_dir / 'src'))\n");
        script.append("sys.path.insert(0, str(use_case_dir / '..' / '..' / '..' / 'shared' / 'utils'))\n");
        script.append("\n");
        script.append("from services.inclusion_orchestrator import InclusionOrchestrator\n");
        script.append("\n");
        script.append("try:\n");
        
        if ("get_priority_status".equals(method)) {
            script.append("    orchestrator = InclusionOrchestrator()\n");
            script.append("    orchestrator.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = orchestrator.get_priority_status(\n");
            script.append("        family_id=params.get('family_id'),\n");
            script.append("        include_nudges=params.get('include_nudges', True)\n");
            script.append("    )\n");
            script.append("    orchestrator.disconnect()\n");
        } else if ("get_priority_list".equals(method)) {
            script.append("    orchestrator = InclusionOrchestrator()\n");
            script.append("    orchestrator.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    result = orchestrator.get_priority_list(\n");
            script.append("        block_id=params.get('block_id'),\n");
            script.append("        district=params.get('district'),\n");
            script.append("        segment_filters=params.get('segment_filters'),\n");
            script.append("        priority_level_filter=params.get('priority_level_filter'),\n");
            script.append("        limit=params.get('limit', 50)\n");
            script.append("    )\n");
            script.append("    orchestrator.disconnect()\n");
        } else if ("schedule_nudge_delivery".equals(method)) {
            script.append("    orchestrator = InclusionOrchestrator()\n");
            script.append("    orchestrator.connect()\n");
            script.append("    params = ").append(paramsToPythonDict(params)).append("\n");
            script.append("    from datetime import datetime\n");
            script.append("    scheduled_at = None\n");
            script.append("    if params.get('scheduled_at'):\n");
            script.append("        scheduled_at = datetime.fromisoformat(params.get('scheduled_at').replace('Z', '+00:00'))\n");
            script.append("    result = orchestrator.schedule_nudge_delivery(\n");
            script.append("        family_id=params.get('family_id'),\n");
            script.append("        nudge_type=params.get('nudge_type'),\n");
            script.append("        nudge_message=params.get('nudge_message'),\n");
            script.append("        recommended_actions=params.get('recommended_actions', []),\n");
            script.append("        scheme_codes=params.get('scheme_codes', []),\n");
            script.append("        channel=params.get('channel'),\n");
            script.append("        priority_level=params.get('priority_level'),\n");
            script.append("        scheduled_at=scheduled_at\n");
            script.append("    )\n");
            script.append("    orchestrator.disconnect()\n");
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
            } else {
                sb.append("'").append(value.toString().replace("'", "\\'")).append("'");
            }
        }
        sb.append("}");
        return sb.toString();
    }
}

