package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

/**
 * Summary of an application
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ApplicationSummary {
    private Integer application_id;
    private String scheme_code;
    private String scheme_name;
    private String status;
    private String department_application_number;
    private LocalDateTime created_at;
    private LocalDateTime submitted_at;
}

