package com.smart.citizen.service;

import com.smart.citizen.dto.websocket.ApplicationStatusUpdateMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ApplicationStatusNotificationService {

    private final SimpMessagingTemplate messagingTemplate;

    /**
     * Broadcast application status update to all subscribers
     */
    public void broadcastStatusUpdate(UUID applicationId, String applicationNumber, 
                                     String fromStatus, String toStatus, 
                                     String stage, String comments) {
        ApplicationStatusUpdateMessage message = ApplicationStatusUpdateMessage.builder()
                .applicationId(applicationId)
                .applicationNumber(applicationNumber)
                .fromStatus(fromStatus)
                .toStatus(toStatus)
                .stage(stage)
                .comments(comments)
                .updatedAt(LocalDateTime.now())
                .message(String.format("Application %s status changed from %s to %s", 
                        applicationNumber != null ? applicationNumber : applicationId.toString(),
                        fromStatus != null ? fromStatus : "N/A",
                        toStatus))
                .build();

        // Broadcast to all subscribers of the application-specific topic
        String topic = "/topic/application/" + applicationId;
        messagingTemplate.convertAndSend(topic, message);
        
        log.info("Broadcasted status update for application {} to topic {}", applicationId, topic);
    }

    /**
     * Broadcast status update to a specific citizen's queue
     */
    public void notifyCitizen(UUID citizenId, UUID applicationId, String applicationNumber,
                              String fromStatus, String toStatus, String stage, String comments) {
        ApplicationStatusUpdateMessage message = ApplicationStatusUpdateMessage.builder()
                .applicationId(applicationId)
                .applicationNumber(applicationNumber)
                .fromStatus(fromStatus)
                .toStatus(toStatus)
                .stage(stage)
                .comments(comments)
                .updatedAt(LocalDateTime.now())
                .message(String.format("Your application %s status has been updated to %s", 
                        applicationNumber != null ? applicationNumber : applicationId.toString(),
                        toStatus))
                .build();

        // Send to citizen-specific queue
        String queue = "/queue/citizen/" + citizenId + "/applications";
        messagingTemplate.convertAndSend(queue, message);
        
        log.info("Sent status update notification to citizen {} for application {}", citizenId, applicationId);
    }
}

