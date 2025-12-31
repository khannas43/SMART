package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Validation result for a field or application
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ValidationResult {
    private String validation_type; // syntactic, semantic, completeness
    private String validation_category;
    private Boolean is_valid;
    private String severity; // error, warning, info
    private String field_name;
    private String error_code;
    private String error_message;
}

