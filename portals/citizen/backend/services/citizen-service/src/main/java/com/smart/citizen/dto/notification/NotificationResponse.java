package com.smart.citizen.dto.notification;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationResponse {
    private UUID id;
    private UUID citizenId;
    private UUID applicationId;
    private String type;
    private String channel;
    private String subject;
    private String message;
    private String status;
    private Boolean isRead;
    private LocalDateTime sentAt;
    private LocalDateTime deliveredAt;
    private LocalDateTime readAt;
    private Map<String, Object> metadata;
    private LocalDateTime createdAt;
}

