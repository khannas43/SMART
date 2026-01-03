package com.smart.citizen.service;

import com.smart.citizen.dto.chat.ChatConversationRequest;
import com.smart.citizen.dto.chat.ChatConversationResponse;
import com.smart.citizen.dto.chat.ChatMessageRequest;
import com.smart.citizen.dto.chat.ChatMessageResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface ChatService {
    ChatConversationResponse createConversation(UUID citizenId, ChatConversationRequest request);
    ChatConversationResponse getConversationById(UUID conversationId);
    Page<ChatConversationResponse> getConversationsByCitizenId(UUID citizenId, Pageable pageable);
    ChatMessageResponse sendMessage(UUID conversationId, UUID senderId, ChatMessageRequest request);
    Page<ChatMessageResponse> getMessagesByConversationId(UUID conversationId, Pageable pageable);
    void markMessagesAsRead(UUID conversationId, List<UUID> messageIds);
    ChatConversationResponse updateConversationStatus(UUID conversationId, String status);
    Long getUnreadCountByCitizenId(UUID citizenId);
}

