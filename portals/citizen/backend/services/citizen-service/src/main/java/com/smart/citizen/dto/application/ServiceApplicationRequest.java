package com.smart.citizen.dto.application;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@Data
public class ServiceApplicationRequest {
    private UUID schemeId;

    @NotBlank(message = "Service type is required")
    @Size(max = 100, message = "Service type must not exceed 100 characters")
    private String serviceType;

    @Size(max = 100, message = "Application type must not exceed 100 characters")
    private String applicationType;

    private String subject;

    @Size(max = 5000, message = "Description must not exceed 5000 characters")
    private String description;

    private String priority;
    private LocalDate expectedCompletionDate;
    private Map<String, Object> applicationData;
}

