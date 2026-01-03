package com.smart.platform.aiml.intimation.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.*;
import java.nio.file.Paths;
import java.util.*;

/**
 * Client to communicate with Python Intimation services
 * Executes Python scripts or calls REST API
 * Use Case ID: AI-PLATFORM-04
 */
@Component
public class PythonIntimationClient {

    @Value("${python.venv.path:/mnt/c/Projects/SMART/ai-ml/.venv}")
    private String pythonVenvPath;

    @Value("${python.intimation.api.url:http://localhost:8004}")
    private String pythonApiUrl;

    @Value("${python.intimation.mode:script}") // script or api
    private String executionMode;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Call Python IntimationService to run intake process
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> runIntakeProcess(String schemeCode) {
        Map<String, Object> params = new HashMap<>();
        if (schemeCode != null) {
            params.put("scheme_code", schemeCode);
        }
        
        if ("api".equals(executionMode)) {
            return callPythonApi("run_intake_process", params);
        } else {
            return callPythonScript("run_intake_process", params);
        }
    }

    /**
     * Call Python IntimationService to schedule intimation
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> scheduleIntimation(
            String schemeCode,
            List<String> familyIds,
            String priority,
            Map<String, Object> eligibilityMeta) {
        
        Map<String, Object> params = new HashMap<>();
        if (schemeCode != null) params.put("scheme_code", schemeCode);
        if (familyIds != null) params.put("family_ids", familyIds);
        if (priority != null) params.put("priority", priority);
        if (eligibilityMeta != null) params.put("eligibility_meta", eligibilityMeta);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("schedule_intimation", params);
        } else {
            return callPythonScript("schedule_intimation", params);
        }
    }

    /**
     * Call Python ConsentManager to create consent
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> createConsent(
            String familyId,
            String schemeCode,
            Boolean consentValue,
            String consentMethod,
            String channel,
            String sessionId,
            String deviceId,
            String ipAddress) {
        
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        params.put("scheme_code", schemeCode);
        params.put("consent_value", consentValue);
        params.put("consent_method", consentMethod);
        params.put("channel", channel);
        if (sessionId != null) params.put("session_id", sessionId);
        if (deviceId != null) params.put("device_id", deviceId);
        if (ipAddress != null) params.put("ip_address", ipAddress);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("create_consent", params);
        } else {
            return callPythonScript("create_consent", params);
        }
    }

    /**
     * Call Python ConsentManager to get consent status
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getConsentStatus(String familyId, String schemeCode) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        if (schemeCode != null) params.put("scheme_code", schemeCode);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_consent_status", params);
        } else {
            return callPythonScript("get_consent_status", params);
        }
    }

    /**
     * Call Python ConsentManager to verify OTP
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> verifyOtp(Integer consentId, String otp) {
        Map<String, Object> params = new HashMap<>();
        params.put("consent_id", consentId);
        params.put("otp", otp);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("verify_otp", params);
        } else {
            return callPythonScript("verify_otp", params);
        }
    }

    /**
     * Call Python ConsentManager to revoke consent
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> revokeConsent(Integer consentId, String revocationReason) {
        Map<String, Object> params = new HashMap<>();
        params.put("consent_id", consentId);
        if (revocationReason != null) params.put("revocation_reason", revocationReason);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("revoke_consent", params);
        } else {
            return callPythonScript("revoke_consent", params);
        }
    }

    /**
     * Call Python ConsentManager to get consent history
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getConsentHistory(String familyId, String schemeCode) {
        Map<String, Object> params = new HashMap<>();
        params.put("family_id", familyId);
        if (schemeCode != null) params.put("scheme_code", schemeCode);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_consent_history", params);
        } else {
            return callPythonScript("get_consent_history", params);
        }
    }

    /**
     * Call Python CampaignManager to create campaign
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> createCampaign(
            String campaignName,
            String schemeCode,
            String campaignType,
            Double eligibilityScoreThreshold,
            List<String> targetDistricts,
            String scheduledAt) {
        
        Map<String, Object> params = new HashMap<>();
        params.put("campaign_name", campaignName);
        params.put("scheme_code", schemeCode);
        params.put("campaign_type", campaignType);
        if (eligibilityScoreThreshold != null) params.put("eligibility_score_threshold", eligibilityScoreThreshold);
        if (targetDistricts != null) params.put("target_districts", targetDistricts);
        if (scheduledAt != null) params.put("scheduled_at", scheduledAt);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("create_campaign", params);
        } else {
            return callPythonScript("create_campaign", params);
        }
    }

    /**
     * Call Python CampaignManager to get campaign
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getCampaign(Integer campaignId) {
        Map<String, Object> params = new HashMap<>();
        params.put("campaign_id", campaignId);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_campaign", params);
        } else {
            return callPythonScript("get_campaign", params);
        }
    }

    /**
     * Call Python CampaignManager to get campaign metrics
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getCampaignMetrics(Integer campaignId) {
        Map<String, Object> params = new HashMap<>();
        params.put("campaign_id", campaignId);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("get_campaign_metrics", params);
        } else {
            return callPythonScript("get_campaign_metrics", params);
        }
    }

    /**
     * Call Python CampaignManager to list campaigns
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> listCampaigns(String schemeCode, String status) {
        Map<String, Object> params = new HashMap<>();
        if (schemeCode != null) params.put("scheme_code", schemeCode);
        if (status != null) params.put("status", status);
        
        if ("api".equals(executionMode)) {
            return callPythonApi("list_campaigns", params);
        } else {
            return callPythonScript("list_campaigns", params);
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
                    "ai-ml", "use-cases", "04_intimation_smart_consent_triggering").toString();
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
                throw new RuntimeException("Python script failed: " + errorOutput.toString());
            }

            // Parse JSON output
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
        script.append("from src.intimation_service import IntimationService\n");
        script.append("from src.consent_manager import ConsentManager\n");
        script.append("from src.campaign_manager import CampaignManager\n");
        script.append("\n");
        script.append("params = ").append(convertToPythonDict(params)).append("\n");
        script.append("method = '").append(method).append("'\n");
        script.append("\n");
        script.append("try:\n");
        script.append("    result = None\n");
        script.append("    \n");
        script.append("    if method == 'run_intake_process':\n");
        script.append("        service = IntimationService()\n");
        script.append("        campaigns = service.run_intake_process(params.get('scheme_code'))\n");
        script.append("        result = {'campaigns': [{'campaign_id': c.campaign_id, 'campaign_name': c.campaign_name, 'scheme_code': c.scheme_code} for c in campaigns]}\n");
        script.append("    \n");
        script.append("    elif method == 'schedule_intimation':\n");
        script.append("        service = IntimationService()\n");
        script.append("        campaigns = service.run_intake_process(params.get('scheme_code'))\n");
        script.append("        result = {'campaigns': [{'campaign_id': c.campaign_id, 'campaign_name': c.campaign_name} for c in campaigns]}\n");
        script.append("    \n");
        script.append("    elif method == 'create_consent':\n");
        script.append("        manager = ConsentManager()\n");
        script.append("        consent = manager.create_consent(\n");
        script.append("            family_id=params['family_id'],\n");
        script.append("            scheme_code=params['scheme_code'],\n");
        script.append("            consent_value=params['consent_value'],\n");
        script.append("            consent_method=params['consent_method'],\n");
        script.append("            channel=params['channel'],\n");
        script.append("            session_id=params.get('session_id'),\n");
        script.append("            device_id=params.get('device_id'),\n");
        script.append("            ip_address=params.get('ip_address')\n");
        script.append("        )\n");
        script.append("        result = consent\n");
        script.append("    \n");
        script.append("    elif method == 'get_consent_status':\n");
        script.append("        manager = ConsentManager()\n");
        script.append("        consent = manager.get_consent_status(\n");
        script.append("            params['family_id'],\n");
        script.append("            params.get('scheme_code')\n");
        script.append("        )\n");
        script.append("        result = consent if consent else {}\n");
        script.append("    \n");
        script.append("    elif method == 'verify_otp':\n");
        script.append("        manager = ConsentManager()\n");
        script.append("        verified = manager.verify_otp(params['consent_id'], params['otp'])\n");
        script.append("        consent = manager.get_consent(params['consent_id'])\n");
        script.append("        result = {'verified': verified, 'consent': consent}\n");
        script.append("    \n");
        script.append("    elif method == 'revoke_consent':\n");
        script.append("        manager = ConsentManager()\n");
        script.append("        consent = manager.revoke_consent(\n");
        script.append("            params['consent_id'],\n");
        script.append("            params.get('revocation_reason')\n");
        script.append("        )\n");
        script.append("        result = consent\n");
        script.append("    \n");
        script.append("    elif method == 'get_consent_history':\n");
        script.append("        manager = ConsentManager()\n");
        script.append("        history = manager.get_consent_history(\n");
        script.append("            params['family_id'],\n");
        script.append("            params.get('scheme_code')\n");
        script.append("        )\n");
        script.append("        result = {'history': history}\n");
        script.append("    \n");
        script.append("    elif method == 'create_campaign':\n");
        script.append("        manager = CampaignManager()\n");
        script.append("        campaign = manager.create_campaign(\n");
        script.append("            campaign_name=params['campaign_name'],\n");
        script.append("            scheme_code=params['scheme_code'],\n");
        script.append("            campaign_type=params['campaign_type'],\n");
        script.append("            eligibility_score_threshold=params.get('eligibility_score_threshold', 0.5),\n");
        script.append("            target_districts=params.get('target_districts'),\n");
        script.append("            scheduled_at=params.get('scheduled_at')\n");
        script.append("        )\n");
        script.append("        result = {'campaign_id': campaign.campaign_id, 'campaign_name': campaign.campaign_name, 'scheme_code': campaign.scheme_code, 'status': campaign.status}\n");
        script.append("    \n");
        script.append("    elif method == 'get_campaign':\n");
        script.append("        manager = CampaignManager()\n");
        script.append("        campaign = manager.get_campaign(params['campaign_id'])\n");
        script.append("        result = {'campaign_id': campaign.campaign_id, 'campaign_name': campaign.campaign_name, 'scheme_code': campaign.scheme_code, 'status': campaign.status, 'total_candidates': campaign.total_candidates}\n");
        script.append("    \n");
        script.append("    elif method == 'get_campaign_metrics':\n");
        script.append("        manager = CampaignManager()\n");
        script.append("        metrics = manager.get_campaign_metrics(params['campaign_id'])\n");
        script.append("        result = metrics\n");
        script.append("    \n");
        script.append("    elif method == 'list_campaigns':\n");
        script.append("        manager = CampaignManager()\n");
        script.append("        campaigns = manager.list_campaigns(\n");
        script.append("            scheme_code=params.get('scheme_code'),\n");
        script.append("            status=params.get('status')\n");
        script.append("        )\n");
        script.append("        result = {'campaigns': [{'campaign_id': c.campaign_id, 'campaign_name': c.campaign_name, 'scheme_code': c.scheme_code, 'status': c.status} for c in campaigns]}\n");
        script.append("    \n");
        script.append("    print(json.dumps(result))\n");
        script.append("    \n");
        script.append("except Exception as e:\n");
        script.append("    print(json.dumps({'error': str(e)}))\n");
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

