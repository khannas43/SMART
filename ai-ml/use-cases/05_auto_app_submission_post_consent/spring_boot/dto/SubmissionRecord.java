package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

/**
 * Submission record
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class SubmissionRecord {
    private Integer submission_id;
    private String connector_type; // REST, SOAP, API_SETU
    private String response_status;
    private String department_application_number;
    private String error_message;
    private LocalDateTime submitted_at;
    private LocalDateTime responded_at;
    private Integer attempt_number;
}

