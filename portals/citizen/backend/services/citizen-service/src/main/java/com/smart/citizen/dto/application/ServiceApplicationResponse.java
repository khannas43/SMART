package com.smart.citizen.dto.application;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ServiceApplicationResponse {
    private UUID id;
    private String applicationNumber;
    private UUID citizenId;
    private String citizenName;
    private UUID schemeId;
    private String schemeName;
    private String schemeCode;
    private String serviceType;
    private String applicationType;
    private String subject;
    private String description;
    private String priority;
    private String status;
    private String currentStage;
    private LocalDateTime submissionDate;
    private String assignedToDept;
    private UUID assignedToOfficer;
    private LocalDate expectedCompletionDate;
    private LocalDateTime actualCompletionDate;
    private Map<String, Object> applicationData;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

