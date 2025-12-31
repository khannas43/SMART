package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Response from confirming application submission
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ConfirmApplicationResponse {
    private Boolean success;
    private Integer application_id;
    private Integer submission_id;
    private String department_application_number;
    private String status; // submitted, submission_failed
    private String message;
    private String error; // If success = false
}

