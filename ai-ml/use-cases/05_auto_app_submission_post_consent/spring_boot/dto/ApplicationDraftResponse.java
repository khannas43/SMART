package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.Map;

/**
 * Response containing application draft for review
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ApplicationDraftResponse {
    private Boolean success;
    private Integer application_id;
    private String scheme_code;
    private Map<String, Object> form_data; // Pre-filled form fields
    private Map<String, Object> field_sources; // Source tracking for each field
    private String[] editable_fields; // Fields citizen can edit
    private String[] read_only_fields; // Fields that are read-only
    private String error; // If success = false
}

