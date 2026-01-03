package com.smart.citizen.service.impl;

import com.smart.citizen.dto.chat.ChatConversationRequest;
import com.smart.citizen.dto.chat.ChatConversationResponse;
import com.smart.citizen.dto.chat.ChatMessageRequest;
import com.smart.citizen.dto.chat.ChatMessageResponse;
import com.smart.citizen.entity.ChatConversation;
import com.smart.citizen.entity.ChatMessage;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.repository.ChatConversationRepository;
import com.smart.citizen.repository.ChatMessageRepository;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class ChatServiceImpl implements ChatService {

    private final ChatConversationRepository conversationRepository;
    private final ChatMessageRepository messageRepository;
    private final CitizenRepository citizenRepository;
    private final SimpMessagingTemplate messagingTemplate;

    @Override
    public ChatConversationResponse createConversation(UUID citizenId, ChatConversationRequest request) {
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        ChatConversation conversation = new ChatConversation();
        conversation.setCitizen(citizen);
        conversation.setSubject(request.getSubject());
        conversation.setPriority(ChatConversation.Priority.valueOf(
                request.getPriority() != null ? request.getPriority().toUpperCase() : "MEDIUM"));
        conversation.setCategory(request.getCategory());
        conversation.setStatus(ChatConversation.ConversationStatus.OPEN);
        conversation.setLastMessageAt(LocalDateTime.now());

        ChatConversation savedConversation = conversationRepository.save(conversation);

        // Create initial message
        ChatMessage initialMessage = new ChatMessage();
        initialMessage.setConversation(savedConversation);
        initialMessage.setSenderId(citizenId);
        initialMessage.setSenderType(ChatMessage.SenderType.CITIZEN);
        initialMessage.setMessage(request.getMessage());
        initialMessage.setIsRead(false);
        messageRepository.save(initialMessage);

        return toConversationResponse(savedConversation);
    }

    @Override
    @Transactional(readOnly = true)
    public ChatConversationResponse getConversationById(UUID conversationId) {
        ChatConversation conversation = conversationRepository.findById(conversationId)
                .orElseThrow(() -> new ResourceNotFoundException("ChatConversation", "id", conversationId));
        return toConversationResponse(conversation);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ChatConversationResponse> getConversationsByCitizenId(UUID citizenId, Pageable pageable) {
        return conversationRepository.findByCitizenIdOrderByLastMessageAtDesc(citizenId, pageable)
                .map(this::toConversationResponse);
    }

    @Override
    public ChatMessageResponse sendMessage(UUID conversationId, UUID senderId, ChatMessageRequest request) {
        ChatConversation conversation = conversationRepository.findById(conversationId)
                .orElseThrow(() -> new ResourceNotFoundException("ChatConversation", "id", conversationId));

        ChatMessage message = new ChatMessage();
        message.setConversation(conversation);
        message.setSenderId(senderId);
        message.setSenderType(ChatMessage.SenderType.CITIZEN);
        message.setMessage(request.getMessage());
        message.setIsRead(false);

        ChatMessage savedMessage = messageRepository.save(message);

        // Update conversation last message time
        conversation.setLastMessageAt(LocalDateTime.now());
        conversationRepository.save(conversation);

        // Send via WebSocket
        ChatMessageResponse messageResponse = toMessageResponse(savedMessage);
        messagingTemplate.convertAndSend(
                "/queue/citizen/" + conversation.getCitizen().getId() + "/chat/" + conversationId,
                messageResponse);

        return messageResponse;
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ChatMessageResponse> getMessagesByConversationId(UUID conversationId, Pageable pageable) {
        return messageRepository.findByConversationIdOrderByCreatedAtAsc(conversationId, pageable)
                .map(this::toMessageResponse);
    }

    @Override
    public void markMessagesAsRead(UUID conversationId, List<UUID> messageIds) {
        List<ChatMessage> messages = messageRepository.findAllById(messageIds);
        LocalDateTime now = LocalDateTime.now();
        messages.forEach(message -> {
            if (message.getConversation().getId().equals(conversationId)) {
                message.setIsRead(true);
                message.setReadAt(now);
            }
        });
        messageRepository.saveAll(messages);
    }

    @Override
    public ChatConversationResponse updateConversationStatus(UUID conversationId, String status) {
        ChatConversation conversation = conversationRepository.findById(conversationId)
                .orElseThrow(() -> new ResourceNotFoundException("ChatConversation", "id", conversationId));
        conversation.setStatus(ChatConversation.ConversationStatus.valueOf(status.toUpperCase()));
        ChatConversation updated = conversationRepository.save(conversation);
        return toConversationResponse(updated);
    }

    @Override
    @Transactional(readOnly = true)
    public Long getUnreadCountByCitizenId(UUID citizenId) {
        return messageRepository.countUnreadMessagesByCitizenId(citizenId);
    }

    private ChatConversationResponse toConversationResponse(ChatConversation conversation) {
        // Get last message - get the most recent one
        Pageable pageable = PageRequest.of(0, 1, Sort.by("createdAt").descending());
        Page<ChatMessage> messagesPage = messageRepository.findByConversationIdOrderByCreatedAtDesc(conversation.getId(), pageable);
        ChatMessageResponse lastMessage = messagesPage.isEmpty() ? null : 
                toMessageResponse(messagesPage.getContent().get(0));

        // Get unread count
        Long unreadCount = messageRepository.countUnreadMessagesByConversationId(conversation.getId());

        return ChatConversationResponse.builder()
                .id(conversation.getId())
                .citizenId(conversation.getCitizen().getId())
                .agentId(conversation.getAgentId())
                .subject(conversation.getSubject())
                .status(conversation.getStatus().name())
                .priority(conversation.getPriority().name())
                .category(conversation.getCategory())
                .lastMessage(lastMessage)
                .unreadCount(unreadCount)
                .createdAt(conversation.getCreatedAt())
                .updatedAt(conversation.getUpdatedAt())
                .lastMessageAt(conversation.getLastMessageAt())
                .build();
    }

    private ChatMessageResponse toMessageResponse(ChatMessage message) {
        return ChatMessageResponse.builder()
                .id(message.getId())
                .conversationId(message.getConversation().getId())
                .senderId(message.getSenderId())
                .senderType(message.getSenderType().name())
                .message(message.getMessage())
                .read(message.getIsRead())
                .readAt(message.getReadAt())
                .timestamp(message.getCreatedAt())
                .createdAt(message.getCreatedAt())
                .updatedAt(message.getUpdatedAt())
                .build();
    }
}

