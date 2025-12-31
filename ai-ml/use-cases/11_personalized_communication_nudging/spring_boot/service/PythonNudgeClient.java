package com.smart.platform.nudging.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.io.*;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;

@Component
public class PythonNudgeClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.nudge.orchestrator.script:src/services/nudge_orchestrator.py}")
    private String nudgeOrchestratorScriptPath;

    @Value("${python.nudge.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public PythonNudgeClient() {
        objectMapper.registerModule(new JavaTimeModule());
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> scheduleNudge(
            String actionType,
            String familyId,
            String urgency,
            LocalDateTime expiryDate,
            Map<String, Object> actionContext,
            String scheduledBy) {
        
        Map<String, Object> params = new HashMap<>();
        params.put("action_type", actionType);
        params.put("family_id", familyId);
        params.put("urgency", urgency);
        if (expiryDate != null) {
            params.put("expiry_date", expiryDate.toString());
        }
        if (actionContext != null) {
            params.put("action_context", actionContext);
        }
        if (scheduledBy != null) {
            params.put("scheduled_by", scheduledBy);
        }

        return callPythonScript("schedule_nudge", params);
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getNudgeHistory(String familyId, Integer limit) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        if (limit != null) {
            params.put("limit", limit);
        }

        Map<String, Object> result = callPythonScript("get_nudge_history", params);
        Object history = result.get("history");
        
        if (history instanceof List) {
            return (List<Map<String, Object>>) history;
        }
        return Collections.emptyList();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> recordFeedback(String nudgeId, String eventType, Map<String, Object> metadata) {
        Map<String, Object> params = new HashMap<>();
        params.put("nudge_id", nudgeId);
        params.put("event_type", eventType);
        if (metadata != null) {
            params.put("metadata", metadata);
        }

        return callPythonScript("record_feedback", params);
    }

    private Map<String, Object> callPythonScript(String method, Map<String, Object> params) {
        try {
            String script = createPythonCallScript(method, params);

            ProcessBuilder pb = new ProcessBuilder(
                    Paths.get(pythonVenvPath, "bin", "python").toString(),
                    "-c", script
            );

            pb.directory(Paths.get(System.getProperty("user.dir")).toFile());
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                StringBuilder errorOutput = new StringBuilder();
                while ((line = errorReader.readLine()) != null) {
                    errorOutput.append(line).append("\n");
                }
                throw new RuntimeException("Python script execution failed: " + errorOutput.toString());
            }

            return objectMapper.readValue(output.toString(), Map.class);

        } catch (Exception e) {
            throw new RuntimeException("Failed to call Python service: " + e.getMessage(), e);
        }
    }

    private String createPythonCallScript(String method, Map<String, Object> params) {
        StringBuilder sb = new StringBuilder();
        sb.append("import sys\n");
        sb.append("import json\n");
        sb.append("from pathlib import Path\n");
        sb.append("from datetime import datetime\n");
        sb.append("sys.path.append(str(Path.cwd() / 'ai-ml' / 'use-cases' / '11_personalized_communication_nudging' / 'src' / 'services'))\n");
        sb.append("from nudge_orchestrator import NudgeOrchestrator\n");
        sb.append("\n");
        sb.append("orchestrator = NudgeOrchestrator()\n");
        sb.append("try:\n");
        sb.append("    orchestrator.connect()\n");
        sb.append("    params = ").append(paramsToPythonDict(params)).append("\n");
        
        if ("schedule_nudge".equals(method)) {
            sb.append("    from datetime import datetime as dt\n");
            sb.append("    if 'expiry_date' in params and params['expiry_date']:\n");
            sb.append("        params['expiry_date'] = dt.fromisoformat(params['expiry_date'])\n");
            sb.append("    result = orchestrator.schedule_nudge(**params)\n");
        } else if ("get_nudge_history".equals(method)) {
            sb.append("    history = orchestrator.get_nudge_history(params['family_id'], params.get('limit', 50))\n");
            sb.append("    result = {'history': history}\n");
        } else if ("record_feedback".equals(method)) {
            sb.append("    result = orchestrator.record_feedback(**params)\n");
        }
        
        sb.append("    print(json.dumps(result, default=str))\n");
        sb.append("finally:\n");
        sb.append("    orchestrator.disconnect()\n");
        return sb.toString();
    }

    private String paramsToPythonDict(Map<String, Object> params) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            sb.append("'").append(entry.getKey()).append("': ");

            Object value = entry.getValue();
            if (value == null) {
                sb.append("None");
            } else if (value instanceof String) {
                sb.append("'").append(value).append("'");
            } else if (value instanceof Number || value instanceof Boolean) {
                sb.append(value);
            } else if (value instanceof List) {
                sb.append("[");
                List<?> list = (List<?>) value;
                for (int i = 0; i < list.size(); i++) {
                    if (i > 0) sb.append(", ");
                    Object item = list.get(i);
                    if (item instanceof String) {
                        sb.append("'").append(item).append("'");
                    } else {
                        sb.append(item);
                    }
                }
                sb.append("]");
            } else if (value instanceof Map) {
                sb.append(paramsToPythonDict((Map<String, Object>) value));
            } else {
                sb.append("'").append(value.toString()).append("'");
            }
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }
}

