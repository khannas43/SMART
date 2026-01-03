package com.smart.citizen.dto.feedback;

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
public class FeedbackResponse {
    private UUID id;
    private UUID citizenId;
    private UUID applicationId;
    private String type;
    private String category;
    private String subject;
    private String message;
    private Integer rating;
    private String status;
    private String resolution;
    private LocalDateTime resolvedAt;
    private UUID resolvedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

