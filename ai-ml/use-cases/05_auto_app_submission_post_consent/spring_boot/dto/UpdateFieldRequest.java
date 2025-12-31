package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Request to update an application field
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class UpdateFieldRequest {
    private String field_name;
    private Object field_value;
    private String updated_by; // Citizen ID or session ID
}

