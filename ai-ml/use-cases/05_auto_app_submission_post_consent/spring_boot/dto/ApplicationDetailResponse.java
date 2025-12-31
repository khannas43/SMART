package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.Map;
import java.util.List;

/**
 * Detailed application information
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ApplicationDetailResponse {
    private Boolean success;
    private Integer application_id;
    private String scheme_code;
    private String status;
    private String submission_mode;
    private Map<String, Object> form_data;
    private Map<String, Object> field_sources; // Source tracking
    private List<ValidationResult> validation_results;
    private List<SubmissionRecord> submission_history;
    private String error; // If success = false
}

