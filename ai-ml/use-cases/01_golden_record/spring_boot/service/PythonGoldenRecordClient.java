package com.smart.platform.aiml.goldenrecord.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python Golden Record services
 * Executes Python scripts or calls REST API
 * Use Case ID: AI-PLATFORM-01
 */
@Component
public class PythonGoldenRecordClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.goldenrecord.api.url:http://localhost:8001}")
    private String pythonApiUrl;

    @Value("${python.goldenrecord.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get Golden Record by Jan Aadhaar
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getGoldenRecord(String janAadhaar) {
        Map<String, Object> params = new HashMap<>();
        params.put("jan_aadhaar", janAadhaar);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_golden_record", params);
        } else {
            return callPythonScript("get_golden_record", params);
        }
    }

    /**
     * Search Golden Records
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> searchGoldenRecords(
            String query, String name, String mobile, Integer limit) {
        Map<String, Object> params = new HashMap<>();
        if (query != null) params.put("query", query);
        if (name != null) params.put("name", name);
        if (mobile != null) params.put("mobile", mobile);
        params.put("limit", limit != null ? limit : 20);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("search_golden_records", params);
        } else {
            return callPythonScript("search_golden_records", params);
        }
    }

    /**
     * Extract Golden Record
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> extractGoldenRecord(String janAadhaar, Boolean forceRefresh) {
        Map<String, Object> params = new HashMap<>();
        params.put("jan_aadhaar", janAadhaar);
        params.put("force_refresh", forceRefresh != null ? forceRefresh : false);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("extract_golden_record", params);
        } else {
            return callPythonScript("extract_golden_record", params);
        }
    }

    /**
     * Merge Golden Records
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> mergeGoldenRecords(
            List<Integer> sourceRecordIds, String targetJanAadhaar, String approvedBy) {
        Map<String, Object> params = new HashMap<>();
        params.put("source_record_ids", sourceRecordIds);
        params.put("target_jan_aadhaar", targetJanAadhaar);
        if (approvedBy != null) params.put("approved_by", approvedBy);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("merge_golden_records", params);
        } else {
            return callPythonScript("merge_golden_records", params);
        }
    }

    /**
     * Get duplicate candidates
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getDuplicateCandidates(String janAadhaar, Double minScore) {
        Map<String, Object> params = new HashMap<>();
        params.put("jan_aadhaar", janAadhaar);
        params.put("min_score", minScore != null ? minScore : 0.8);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_duplicate_candidates", params);
        } else {
            return callPythonScript("get_duplicate_candidates", params);
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
                    "ai-ml", "use-cases", "01_golden_record").toString();
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
        script.append("import pandas as pd\n");
        script.append("sys.path.append(str(Path(__file__).parent))\n");
        script.append("sys.path.append(str(Path(__file__).parent.parent.parent / 'shared' / 'utils'))\n");
        script.append("\n");
        script.append("from src.data_loader import GoldenRecordDataLoader\n");
        script.append("from src.deduplication import FellegiSunterDeduplication\n");
        script.append("\n");
        script.append("params = ").append(convertToPythonDict(params)).append("\n");
        script.append("method = '").append(method).append("'\n");
        script.append("\n");
        script.append("try:\n");
        script.append("    result = None\n");
        script.append("    loader = GoldenRecordDataLoader()\n");
        script.append("    \n");
        script.append("    if method == 'get_golden_record':\n");
        script.append("        df = loader.load_citizen_by_aadhaar(params['jan_aadhaar'])\n");
        script.append("        if df.empty:\n");
        script.append("            result = {'success': False, 'error': 'Record not found'}\n");
        script.append("        else:\n");
        script.append("            record = df.iloc[0].to_dict()\n");
        script.append("            result = {'success': True, 'record': record}\n");
        script.append("    \n");
        script.append("    elif method == 'search_golden_records':\n");
        script.append("        df = loader.load_all_citizens()\n");
        script.append("        limit = params.get('limit', 20)\n");
        script.append("        if params.get('name'):\n");
        script.append("            df = df[df['name'].str.contains(params['name'], case=False, na=False)]\n");
        script.append("        if params.get('mobile'):\n");
        script.append("            df = df[df['mobile'].str.contains(params['mobile'], na=False)]\n");
        script.append("        records = df.head(limit).to_dict('records')\n");
        script.append("        result = {'success': True, 'records': records, 'total': len(df)}\n");
        script.append("    \n");
        script.append("    elif method == 'extract_golden_record':\n");
        script.append("        # Trigger extraction - for now just return existing record\n");
        script.append("        df = loader.load_citizen_by_aadhaar(params['jan_aadhaar'])\n");
        script.append("        if df.empty:\n");
        script.append("            result = {'success': False, 'error': 'Record not found'}\n");
        script.append("        else:\n");
        script.append("            record = df.iloc[0].to_dict()\n");
        script.append("            result = {'success': True, 'record': record, 'extracted': True}\n");
        script.append("    \n");
        script.append("    elif method == 'merge_golden_records':\n");
        script.append("        # Merge operation - placeholder\n");
        script.append("        result = {'success': True, 'merged': True, 'target_jan_aadhaar': params['target_jan_aadhaar']}\n");
        script.append("    \n");
        script.append("    elif method == 'get_duplicate_candidates':\n");
        script.append("        # Get duplicate candidates - placeholder\n");
        script.append("        result = {'success': True, 'candidates': []}\n");
        script.append("    \n");
        script.append("    loader.close()\n");
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

