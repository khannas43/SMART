package com.smart.citizen.dto.application;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApplicationStatusHistoryResponse {
    private UUID id;
    private UUID applicationId;
    private String fromStatus;
    private String toStatus;
    private String stage;
    private String comments;
    private UUID changedBy;
    private String changedByType;
    private LocalDateTime changedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

