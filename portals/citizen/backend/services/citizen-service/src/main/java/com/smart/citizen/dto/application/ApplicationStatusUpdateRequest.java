package com.smart.citizen.dto.application;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ApplicationStatusUpdateRequest {
    @NotBlank(message = "Status is required")
    private String status;
    private String currentStage;
    private String comments;
}

