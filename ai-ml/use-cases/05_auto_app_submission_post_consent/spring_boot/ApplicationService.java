package com.smart.platform.aiml.application.service;

import com.smart.platform.aiml.application.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.*;

/**
 * Application Service
 * Orchestrates application creation, mapping, validation, and submission
 * Use Case ID: AI-PLATFORM-05
 */
@Service
public class ApplicationService {

    @Autowired
    private PythonApplicationClient pythonClient;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * Start application creation from consent event
     */
    public StartApplicationResponse startApplication(StartApplicationRequest request) {
        StartApplicationResponse response = new StartApplicationResponse();
        
        try {
            Map<String, Object> result = pythonClient.processConsentEvent(
                    request.getFamily_id(),
                    request.getScheme_code(),
                    request.getConsent_id());
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                
                Object applicationId = result.get("application_id");
                if (applicationId != null) {
                    response.setApplication_id(applicationId instanceof Number ? 
                        ((Number) applicationId).intValue() : Integer.parseInt(applicationId.toString()));
                }
                
                // Get application status from database
                if (response.getApplication_id() != null) {
                    String statusQuery = "SELECT status FROM application.applications WHERE application_id = ?";
                    String status = jdbcTemplate.queryForObject(statusQuery, String.class, response.getApplication_id());
                    response.setStatus(status);
                } else {
                    response.setStatus("creating");
                }
                
                response.setMessage("Application creation initiated successfully");
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to start application: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get application draft for citizen review
     */
    public ApplicationDraftResponse getApplicationDraft(String family_id, String scheme_code) {
        ApplicationDraftResponse response = new ApplicationDraftResponse();
        
        try {
            Map<String, Object> result = pythonClient.getApplicationDraft(family_id, scheme_code);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                
                Object applicationId = result.get("application_id");
                if (applicationId != null) {
                    response.setApplication_id(applicationId instanceof Number ? 
                        ((Number) applicationId).intValue() : Integer.parseInt(applicationId.toString()));
                }
                
                response.setScheme_code((String) result.get("scheme_code"));
                
                @SuppressWarnings("unchecked")
                Map<String, Object> formData = (Map<String, Object>) result.get("form_data");
                response.setForm_data(formData != null ? formData : new HashMap<>());
                
                @SuppressWarnings("unchecked")
                Map<String, Object> fieldSources = (Map<String, Object>) result.get("field_sources");
                response.setField_sources(fieldSources != null ? fieldSources : new HashMap<>());
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get application draft: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Confirm and submit reviewed application
     */
    public ConfirmApplicationResponse confirmApplication(ConfirmApplicationRequest request) {
        ConfirmApplicationResponse response = new ConfirmApplicationResponse();
        
        try {
            // First verify application is in pending_review status
            String statusQuery = "SELECT status, scheme_code FROM application.applications WHERE application_id = ?";
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(statusQuery, request.getApplication_id());
            
            if (rows.isEmpty()) {
                response.setSuccess(false);
                response.setError("Application not found");
                return response;
            }
            
            Map<String, Object> appRow = rows.get(0);
            String status = (String) appRow.get("status");
            String schemeCode = (String) appRow.get("scheme_code");
            
            if (!"pending_review".equals(status)) {
                response.setSuccess(false);
                response.setError("Application is not in pending_review status. Current status: " + status);
                return response;
            }
            
            // Call Python service to confirm and submit
            Map<String, Object> result = pythonClient.confirmApplication(
                    request.getApplication_id(), schemeCode);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                response.setApplication_id(request.getApplication_id());
                
                Object submissionId = result.get("submission_id");
                if (submissionId != null) {
                    response.setSubmission_id(submissionId instanceof Number ? 
                        ((Number) submissionId).intValue() : Integer.parseInt(submissionId.toString()));
                }
                
                response.setDepartment_application_number((String) result.get("department_application_number"));
                response.setMessage((String) result.get("message"));
                if (response.getMessage() == null) {
                    response.setMessage("Application submitted successfully");
                }
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to confirm application: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get application status
     */
    public ApplicationStatusResponse getApplicationStatus(String family_id, String scheme_code) {
        ApplicationStatusResponse response = new ApplicationStatusResponse();
        
        try {
            StringBuilder query = new StringBuilder(
                "SELECT application_id, scheme_code, status, submission_mode, " +
                "created_at, updated_at " +
                "FROM application.applications " +
                "WHERE family_id::text = ? "
            );
            
            List<Object> params = new ArrayList<>();
            params.add(family_id);
            
            if (scheme_code != null && !scheme_code.isEmpty()) {
                query.append("AND scheme_code = ? ");
                params.add(scheme_code);
            }
            
            query.append("ORDER BY created_at DESC");
            
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(
                query.toString(), params.toArray());
            
            response.setSuccess(true);
            response.setFamily_id(family_id);
            
            List<ApplicationSummary> applications = new ArrayList<>();
            for (Map<String, Object> row : rows) {
                ApplicationSummary summary = new ApplicationSummary();
                
                Object applicationId = row.get("application_id");
                if (applicationId != null) {
                    summary.setApplication_id(applicationId instanceof Number ? 
                        ((Number) applicationId).intValue() : Integer.parseInt(applicationId.toString()));
                }
                
                summary.setScheme_code((String) row.get("scheme_code"));
                summary.setStatus((String) row.get("status"));
                summary.setSubmission_mode((String) row.get("submission_mode"));
                
                if (row.get("created_at") != null) {
                    summary.setCreated_at(row.get("created_at").toString());
                }
                
                if (row.get("updated_at") != null) {
                    summary.setUpdated_at(row.get("updated_at").toString());
                }
                
                applications.add(summary);
            }
            
            response.setApplications(applications);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get application status: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Get application details
     */
    public ApplicationDetailResponse getApplicationDetails(Integer application_id) {
        ApplicationDetailResponse response = new ApplicationDetailResponse();
        
        try {
            // Load application record
            String appQuery = "SELECT application_id, family_id, scheme_code, status, " +
                "submission_mode, created_at, updated_at " +
                "FROM application.applications WHERE application_id = ?";
            
            List<Map<String, Object>> appRows = jdbcTemplate.queryForList(appQuery, application_id);
            
            if (appRows.isEmpty()) {
                response.setSuccess(false);
                response.setError("Application not found");
                return response;
            }
            
            Map<String, Object> appRow = appRows.get(0);
            response.setSuccess(true);
            response.setApplication_id(application_id);
            response.setScheme_code((String) appRow.get("scheme_code"));
            response.setStatus((String) appRow.get("status"));
            response.setSubmission_mode((String) appRow.get("submission_mode"));
            
            if (appRow.get("created_at") != null) {
                response.setCreated_at(appRow.get("created_at").toString());
            }
            
            // Load application fields
            String fieldsQuery = "SELECT field_name, field_value, source_type, mapping_type " +
                "FROM application.application_fields WHERE application_id = ?";
            
            List<Map<String, Object>> fieldRows = jdbcTemplate.queryForList(fieldsQuery, application_id);
            
            Map<String, Object> formData = new HashMap<>();
            Map<String, Object> fieldSources = new HashMap<>();
            
            for (Map<String, Object> fieldRow : fieldRows) {
                String fieldName = (String) fieldRow.get("field_name");
                Object fieldValue = fieldRow.get("field_value");
                String sourceType = (String) fieldRow.get("source_type");
                String mappingType = (String) fieldRow.get("mapping_type");
                
                formData.put(fieldName, fieldValue);
                
                Map<String, Object> sourceInfo = new HashMap<>();
                sourceInfo.put("source_type", sourceType);
                sourceInfo.put("mapping_type", mappingType);
                fieldSources.put(fieldName, sourceInfo);
            }
            
            response.setForm_data(formData);
            response.setField_sources(fieldSources);
            
            // Load validation results
            String validationQuery = "SELECT validation_rule, passed, error_message " +
                "FROM application.application_validation_results WHERE application_id = ?";
            
            List<Map<String, Object>> validationRows = jdbcTemplate.queryForList(validationQuery, application_id);
            List<ValidationResult> validationResults = new ArrayList<>();
            
            for (Map<String, Object> valRow : validationRows) {
                ValidationResult vr = new ValidationResult();
                vr.setValidation_rule((String) valRow.get("validation_rule"));
                
                Object passed = valRow.get("passed");
                if (passed != null) {
                    vr.setPassed(Boolean.parseBoolean(passed.toString()));
                }
                
                vr.setError_message((String) valRow.get("error_message"));
                validationResults.add(vr);
            }
            
            response.setValidation_results(validationResults);
            
            // Load submission records
            String submissionQuery = "SELECT submission_id, submission_status, " +
                "department_application_number, submitted_at, error_message " +
                "FROM application.application_submissions WHERE application_id = ? " +
                "ORDER BY submitted_at DESC";
            
            List<Map<String, Object>> submissionRows = jdbcTemplate.queryForList(submissionQuery, application_id);
            List<SubmissionRecord> submissions = new ArrayList<>();
            
            for (Map<String, Object> subRow : submissionRows) {
                SubmissionRecord sr = new SubmissionRecord();
                
                Object submissionId = subRow.get("submission_id");
                if (submissionId != null) {
                    sr.setSubmission_id(submissionId instanceof Number ? 
                        ((Number) submissionId).intValue() : Integer.parseInt(submissionId.toString()));
                }
                
                sr.setSubmission_status((String) subRow.get("submission_status"));
                sr.setDepartment_application_number((String) subRow.get("department_application_number"));
                
                if (subRow.get("submitted_at") != null) {
                    sr.setSubmitted_at(subRow.get("submitted_at").toString());
                }
                
                sr.setError_message((String) subRow.get("error_message"));
                submissions.add(sr);
            }
            
            response.setSubmission_history(submissions);
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to get application details: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Update application field (for citizen review)
     */
    public UpdateFieldResponse updateApplicationField(
            Integer application_id, UpdateFieldRequest request) {
        UpdateFieldResponse response = new UpdateFieldResponse();
        
        try {
            // Verify application is in editable status
            String statusQuery = "SELECT status FROM application.applications WHERE application_id = ?";
            String status = jdbcTemplate.queryForObject(statusQuery, String.class, application_id);
            
            if (!"pending_review".equals(status)) {
                response.setSuccess(false);
                response.setError("Application is not in pending_review status. Cannot update fields.");
                return response;
            }
            
            // Update field value
            String updateQuery = "UPDATE application.application_fields " +
                "SET field_value = ?, source_type = 'CITIZEN', updated_at = CURRENT_TIMESTAMP " +
                "WHERE application_id = ? AND field_name = ?";
            
            int updated = jdbcTemplate.update(updateQuery, 
                request.getField_value(), application_id, request.getField_name());
            
            if (updated == 0) {
                // Field doesn't exist, insert it
                String insertQuery = "INSERT INTO application.application_fields " +
                    "(application_id, field_name, field_value, source_type, mapping_type, created_at, updated_at) " +
                    "VALUES (?, ?, ?, 'CITIZEN', 'direct', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)";
                
                jdbcTemplate.update(insertQuery, application_id, request.getField_name(), request.getField_value());
            }
            
            // Log audit event
            String auditQuery = "INSERT INTO application.application_audit_logs " +
                "(application_id, action_type, action_details, performed_by, performed_at) " +
                "VALUES (?, 'FIELD_UPDATED', ?, 'citizen', CURRENT_TIMESTAMP)";
            
            String details = String.format("Field '%s' updated to '%s'", 
                request.getField_name(), request.getField_value());
            jdbcTemplate.update(auditQuery, application_id, details);
            
            response.setSuccess(true);
            response.setApplication_id(application_id);
            response.setField_name(request.getField_name());
            response.setMessage("Field updated successfully");
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to update field: " + e.getMessage());
        }
        
        return response;
    }

    /**
     * Retry failed submission
     */
    public RetrySubmissionResponse retrySubmission(Integer application_id) {
        RetrySubmissionResponse response = new RetrySubmissionResponse();
        
        try {
            // Verify application exists and is in failed status
            String statusQuery = "SELECT status, scheme_code FROM application.applications WHERE application_id = ?";
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(statusQuery, application_id);
            
            if (rows.isEmpty()) {
                response.setSuccess(false);
                response.setError("Application not found");
                return response;
            }
            
            Map<String, Object> appRow = rows.get(0);
            String status = (String) appRow.get("status");
            
            if (!"submission_failed".equals(status) && !"draft".equals(status)) {
                response.setSuccess(false);
                response.setError("Application is not in a retryable status. Current status: " + status);
                return response;
            }
            
            // Call Python service to retry submission
            Map<String, Object> result = pythonClient.retrySubmission(application_id);
            
            Object success = result.get("success");
            if (success != null && Boolean.parseBoolean(success.toString())) {
                response.setSuccess(true);
                response.setApplication_id(application_id);
                
                Object submissionId = result.get("submission_id");
                if (submissionId != null) {
                    response.setSubmission_id(submissionId instanceof Number ? 
                        ((Number) submissionId).intValue() : Integer.parseInt(submissionId.toString()));
                }
                
                response.setMessage((String) result.get("message"));
                if (response.getMessage() == null) {
                    response.setMessage("Submission retry initiated");
                }
            } else {
                response.setSuccess(false);
                response.setError((String) result.get("error"));
            }
            
        } catch (Exception e) {
            response.setSuccess(false);
            response.setError("Failed to retry submission: " + e.getMessage());
        }
        
        return response;
    }
}

