package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Request to start application creation from consent event
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class StartApplicationRequest {
    private String family_id;
    private String scheme_code;
    private Integer consent_id; // Optional: specific consent record ID
}

