package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Response from updating an application field
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class UpdateFieldResponse {
    private Boolean success;
    private Integer application_id;
    private String field_name;
    private String message;
    private String error; // If success = false
}

