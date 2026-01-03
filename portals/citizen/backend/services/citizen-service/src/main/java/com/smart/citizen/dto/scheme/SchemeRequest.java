package com.smart.citizen.dto.scheme;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDate;
import java.util.Map;

@Data
public class SchemeRequest {
    @NotBlank(message = "Scheme code is required")
    @Size(max = 50, message = "Scheme code must not exceed 50 characters")
    private String code;

    @NotBlank(message = "Scheme name is required")
    @Size(max = 255, message = "Scheme name must not exceed 255 characters")
    private String name;

    private String description;
    private String category;
    private String department;
    private Map<String, Object> eligibilityCriteria;
    private LocalDate startDate;
    private LocalDate endDate;
    private String status;
}

