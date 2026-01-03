package com.smart.citizen.controller;

import com.smart.citizen.dto.chat.ChatMessageRequest;
import com.smart.citizen.dto.chat.ChatMessageResponse;
import com.smart.citizen.service.ChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;

import java.util.Map;
import java.util.UUID;

@Controller
@RequiredArgsConstructor
@Slf4j
public class ChatWebSocketController {

    private final ChatService chatService;
    private final SimpMessagingTemplate messagingTemplate;

    @MessageMapping("/chat/{conversationId}/send")
    public void sendMessage(@Payload Map<String, Object> payload, @org.springframework.messaging.handler.annotation.DestinationVariable UUID conversationId) {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                log.warn("Unauthenticated WebSocket message attempt");
                return;
            }

            UUID senderId = UUID.fromString(authentication.getName());
            String message = (String) payload.get("message");

            ChatMessageRequest request = new ChatMessageRequest();
            request.setMessage(message);

            ChatMessageResponse response = chatService.sendMessage(conversationId, senderId, request);

            // The service already sends the message via WebSocket, but we can also send confirmation
            log.info("Message sent via WebSocket for conversation: {}", conversationId);
        } catch (Exception e) {
            log.error("Error handling WebSocket message", e);
        }
    }
}

