package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Response containing application status for a family
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ApplicationStatusResponse {
    private Boolean success;
    private String family_id;
    private List<ApplicationSummary> applications; // List of applications
    private String error; // If success = false
}

