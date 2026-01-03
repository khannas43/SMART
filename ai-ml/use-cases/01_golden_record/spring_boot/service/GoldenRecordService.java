package com.smart.platform.aiml.goldenrecord.service;

import com.smart.platform.aiml.goldenrecord.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

/**
 * Service layer for Golden Record Management
 * Use Case ID: AI-PLATFORM-01
 */
@Service
public class GoldenRecordService {

    @Autowired
    private PythonGoldenRecordClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Get Golden Record by Jan Aadhaar
     */
    public GoldenRecordResponse getGoldenRecord(String janAadhaar) {
        GoldenRecordResponse response = new GoldenRecordResponse();
        
        try {
            Map<String, Object> result = pythonClient.getGoldenRecord(janAadhaar);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                
                @SuppressWarnings("unchecked")
                Map<String, Object> record = (Map<String, Object>) result.get("record");
                if (record != null) {
                    response.setJanAadhaar((String) record.get("jan_aadhaar"));
                    response.setName((String) record.get("name"));
                    response.setDateOfBirth((String) record.get("date_of_birth"));
                    response.setGender((String) record.get("gender"));
                    response.setMobile((String) record.get("mobile"));
                    response.setEmail((String) record.get("email"));
                    response.setAddress((String) record.get("address"));
                    response.setDistrict((String) record.get("district"));
                    response.setBlock((String) record.get("block"));
                    response.setVillage((String) record.get("village"));
                    response.setPincode((String) record.get("pincode"));
                    
                    // Convert any additional fields
                    Map<String, Object> additionalFields = new HashMap<>();
                    for (Map.Entry<String, Object> entry : record.entrySet()) {
                        String key = entry.getKey();
                        if (!key.equals("jan_aadhaar") && !key.equals("name") && 
                            !key.equals("date_of_birth") && !key.equals("gender") &&
                            !key.equals("mobile") && !key.equals("email") &&
                            !key.equals("address") && !key.equals("district") &&
                            !key.equals("block") && !key.equals("village") &&
                            !key.equals("pincode")) {
                            additionalFields.put(key, entry.getValue());
                        }
                    }
                    response.setAdditionalFields(additionalFields);
                }
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get golden record: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Search Golden Records
     */
    public GoldenRecordSearchResponse searchGoldenRecords(
            String query, String name, String mobile, Integer limit) {
        GoldenRecordSearchResponse response = new GoldenRecordSearchResponse();
        
        try {
            Map<String, Object> result = pythonClient.searchGoldenRecords(query, name, mobile, limit);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> records = (List<Map<String, Object>>) result.get("records");
                if (records != null) {
                    List<GoldenRecordResponse> goldenRecords = new ArrayList<>();
                    for (Map<String, Object> record : records) {
                        GoldenRecordResponse gr = new GoldenRecordResponse();
                        gr.setJanAadhaar((String) record.get("jan_aadhaar"));
                        gr.setName((String) record.get("name"));
                        gr.setDateOfBirth((String) record.get("date_of_birth"));
                        gr.setGender((String) record.get("gender"));
                        gr.setMobile((String) record.get("mobile"));
                        gr.setEmail((String) record.get("email"));
                        gr.setAddress((String) record.get("address"));
                        gr.setDistrict((String) record.get("district"));
                        gr.setBlock((String) record.get("block"));
                        gr.setVillage((String) record.get("village"));
                        gr.setPincode((String) record.get("pincode"));
                        goldenRecords.add(gr);
                    }
                    response.setRecords(goldenRecords);
                }
                
                Object total = result.get("total");
                if (total != null) {
                    response.setTotal(total instanceof Number ? 
                        ((Number) total).intValue() : Integer.parseInt(total.toString()));
                }
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to search golden records: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Extract Golden Record
     */
    public ExtractGoldenRecordResponse extractGoldenRecord(String janAadhaar, Boolean forceRefresh) {
        ExtractGoldenRecordResponse response = new ExtractGoldenRecordResponse();
        
        try {
            Map<String, Object> result = pythonClient.extractGoldenRecord(janAadhaar, forceRefresh);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                response.setJanAadhaar(janAadhaar);
                
                Object extracted = result.get("extracted");
                if (extracted != null) {
                    response.setExtracted(Boolean.parseBoolean(extracted.toString()));
                }
                
                @SuppressWarnings("unchecked")
                Map<String, Object> record = (Map<String, Object>) result.get("record");
                if (record != null) {
                    response.setRecordExtracted(true);
                }
                
                response.setMessage("Golden record extraction completed");
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to extract golden record: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Merge Golden Records
     */
    public MergeGoldenRecordResponse mergeGoldenRecords(
            List<Integer> sourceRecordIds, String targetJanAadhaar, String approvedBy) {
        MergeGoldenRecordResponse response = new MergeGoldenRecordResponse();
        
        try {
            Map<String, Object> result = pythonClient.mergeGoldenRecords(
                    sourceRecordIds, targetJanAadhaar, approvedBy);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                response.setTargetJanAadhaar(targetJanAadhaar);
                
                Object merged = result.get("merged");
                if (merged != null) {
                    response.setMerged(Boolean.parseBoolean(merged.toString()));
                }
                
                response.setMessage("Golden records merged successfully");
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to merge golden records: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get duplicate candidates
     */
    public DuplicateCandidatesResponse getDuplicateCandidates(String janAadhaar, Double minScore) {
        DuplicateCandidatesResponse response = new DuplicateCandidatesResponse();
        
        try {
            Map<String, Object> result = pythonClient.getDuplicateCandidates(janAadhaar, minScore);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                response.setJanAadhaar(janAadhaar);
                
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> candidates = (List<Map<String, Object>>) result.get("candidates");
                if (candidates != null) {
                    List<DuplicateCandidatesResponse.DuplicateCandidate> candidateList = new ArrayList<>();
                    for (Map<String, Object> candidate : candidates) {
                        DuplicateCandidatesResponse.DuplicateCandidate dc = 
                            new DuplicateCandidatesResponse.DuplicateCandidate();
                        
                        Object recordId = candidate.get("record_id");
                        if (recordId != null) {
                            dc.setRecordId(recordId instanceof Number ? 
                                ((Number) recordId).intValue() : Integer.parseInt(recordId.toString()));
                        }
                        
                        dc.setJanAadhaar((String) candidate.get("jan_aadhaar"));
                        dc.setName((String) candidate.get("name"));
                        dc.setMobile((String) candidate.get("mobile"));
                        
                        Object matchScore = candidate.get("match_score");
                        if (matchScore != null) {
                            dc.setMatchScore(matchScore instanceof Number ? 
                                ((Number) matchScore).doubleValue() : Double.parseDouble(matchScore.toString()));
                        }
                        
                        candidateList.add(dc);
                    }
                    response.setCandidates(candidateList);
                }
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get duplicate candidates: " + e.getMessage());
        }
        
        return response;
    }
}

