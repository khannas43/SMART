package com.smart.platform.forecast.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python ForecastOrchestrator service
 * Use Case ID: AI-PLATFORM-10
 */
@Component
public class PythonForecastClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.forecast.mode:script}")
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Generate forecast
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> generateForecast(String familyId, Integer horizon, String scenario) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("horizon_months", horizon);
        if (scenario != null) params.put("scenario_name", scenario);
        params.put("save_to_db", true);
        
        return callPythonScript("generate_forecast", params);
    }

    /**
     * Get forecast by ID
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getForecastById(Integer forecastId) {
        Map<String, Object> params = new HashMap<>();
        params.put("forecast_id", forecastId);
        
        return callPythonScript("get_forecast_by_id", params);
    }

    /**
     * Get latest forecast for family
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getLatestForecast(String familyId) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        
        return callPythonScript("get_latest_forecast", params);
    }

    /**
     * Get aggregate forecast
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getAggregateForecast(
            String level, String blockId, String district, String state,
            Integer horizon, String scenario, String modelType, List<String> schemeCodes) {
        Map<String, Object> params = new HashMap<>();
        params.put("aggregation_level", level);
        if (blockId != null) params.put("block_id", blockId);
        if (district != null) params.put("district", district);
        if (state != null) params.put("state", state);
        params.put("horizon_months", horizon);
        if (scenario != null) params.put("scenario_name", scenario);
        params.put("model_type", modelType != null ? modelType : "ARIMA");
        if (schemeCodes != null) params.put("scheme_codes", schemeCodes);
        
        return callPythonScript("get_aggregate_forecast", params);
    }

    /**
     * Estimate recommendation probability
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> estimateProbability(
            String familyId, String schemeCode, String eligibilityStatus, 
            Integer rank, Integer daysSince) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("scheme_code", schemeCode);
        params.put("eligibility_status", eligibilityStatus);
        params.put("recommendation_rank", rank);
        params.put("days_since_recommendation", daysSince != null ? daysSince : 0);
        
        return callPythonScript("estimate_probability", params);
    }

    /**
     * Handle event and refresh forecast
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> handleEvent(String eventType, Map<String, Object> eventData) {
        Map<String, Object> params = new HashMap<>();
        params.put("event_type", eventType);
        params.put("event_data", eventData);
        
        return callPythonScript("handle_event", params);
    }

    /**
     * Refresh stale forecasts
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> refreshStaleForecasts(Integer daysStale, Integer limit) {
        Map<String, Object> params = new HashMap<>();
        params.put("days_stale", daysStale != null ? daysStale : 30);
        params.put("limit", limit != null ? limit : 100);
        
        return callPythonScript("refresh_stale_forecasts", params);
    }

    /**
     * Call Python script directly
     */
    private Map<String, Object> callPythonScript(String method, Map<String, Object> params) {
        try {
            String script = createPythonCallScript(method, params);
            String pythonExecutable = Paths.get(pythonVenvPath, "bin", "python").toString();
            
            ProcessBuilder pb = new ProcessBuilder(pythonExecutable, "-c", script);
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
        sb.append("sys.path.append(str(Path.cwd() / 'ai-ml' / 'use-cases' / '10_entitlement_benefit_forecast' / 'src' / 'services'))\n");
        sb.append("from forecast_orchestrator import ForecastOrchestrator\n");
        sb.append("\n");
        sb.append("orchestrator = ForecastOrchestrator()\n");
        sb.append("try:\n");
        sb.append("    orchestrator.connect()\n");
        sb.append("    params = ").append(paramsToPythonDict(params)).append("\n");
        
        if ("generate_forecast".equals(method)) {
            sb.append("    result = orchestrator.generate_forecast(**params)\n");
        } else if ("get_forecast_by_id".equals(method)) {
            sb.append("    result = orchestrator.get_forecast(None, params.get('forecast_id'))\n");
            sb.append("    result = result if result else {'success': False, 'message': 'Forecast not found'}\n");
        } else if ("get_latest_forecast".equals(method)) {
            sb.append("    result = orchestrator.get_forecast(params['family_id'], None)\n");
            sb.append("    result = result if result else {'success': False, 'message': 'Forecast not found'}\n");
        } else if ("get_aggregate_forecast".equals(method)) {
            sb.append("    result = orchestrator.get_aggregate_forecast(**params)\n");
        } else if ("estimate_probability".equals(method)) {
            sb.append("    result = {'probability': orchestrator.estimate_recommendation_probability(**params)}\n");
        } else if ("handle_event".equals(method)) {
            sb.append("    result = orchestrator.handle_event(params.get('event_type'), params.get('event_data', {}))\n");
        } else if ("refresh_stale_forecasts".equals(method)) {
            sb.append("    result = orchestrator.refresh_stale_forecasts(**params)\n");
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
            if (!first) sb.append(", ");
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

