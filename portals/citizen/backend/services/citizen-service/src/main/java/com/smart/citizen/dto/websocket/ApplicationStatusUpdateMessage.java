package com.smart.citizen.dto.websocket;

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
public class ApplicationStatusUpdateMessage {
    private UUID applicationId;
    private String applicationNumber;
    private String fromStatus;
    private String toStatus;
    private String stage;
    private String comments;
    private LocalDateTime updatedAt;
    private String message;
}

