package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Response from starting application creation
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class StartApplicationResponse {
    private Boolean success;
    private Integer application_id;
    private String status; // creating, draft, pending_review, etc.
    private String message;
    private String error; // If success = false
}

