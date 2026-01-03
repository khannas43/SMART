package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.chat.ChatConversationRequest;
import com.smart.citizen.dto.chat.ChatConversationResponse;
import com.smart.citizen.dto.chat.ChatMessageRequest;
import com.smart.citizen.dto.chat.ChatMessageResponse;
import com.smart.citizen.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor
@Tag(name = "Chat", description = "API endpoints for chat support conversations and messages")
public class ChatController {

    private final ChatService chatService;

    @Operation(summary = "Create new conversation", description = "Create a new chat conversation with an initial message")
    @PostMapping("/conversations/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<ChatConversationResponse>> createConversation(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody ChatConversationRequest request) {
        ChatConversationResponse response = chatService.createConversation(citizenId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Conversation created successfully", response));
    }

    @Operation(summary = "Get conversation by ID", description = "Retrieve conversation details by unique identifier")
    @GetMapping("/conversations/{conversationId}")
    public ResponseEntity<ApiResponse<ChatConversationResponse>> getConversation(
            @Parameter(description = "Conversation unique identifier") @PathVariable UUID conversationId) {
        ChatConversationResponse response = chatService.getConversationById(conversationId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get conversations by citizen", description = "Retrieve all conversations for a citizen with pagination")
    @GetMapping("/conversations/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PagedResponse<ChatConversationResponse>>> getConversations(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "lastMessageAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<ChatConversationResponse> conversationsPage = chatService.getConversationsByCitizenId(citizenId, pageable);
        
        PagedResponse<ChatConversationResponse> pagedResponse = PagedResponse.<ChatConversationResponse>builder()
                .content(conversationsPage.getContent())
                .page(conversationsPage.getNumber())
                .size(conversationsPage.getSize())
                .totalElements(conversationsPage.getTotalElements())
                .totalPages(conversationsPage.getTotalPages())
                .first(conversationsPage.isFirst())
                .last(conversationsPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Send message", description = "Send a message in a conversation")
    @PostMapping("/conversations/{conversationId}/messages")
    public ResponseEntity<ApiResponse<ChatMessageResponse>> sendMessage(
            @Parameter(description = "Conversation unique identifier") @PathVariable UUID conversationId,
            @Valid @RequestBody ChatMessageRequest request) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        UUID senderId = UUID.fromString(authentication.getName()); // Assuming username is citizen ID
        
        ChatMessageResponse response = chatService.sendMessage(conversationId, senderId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Message sent successfully", response));
    }

    @Operation(summary = "Get messages", description = "Retrieve messages for a conversation with pagination")
    @GetMapping("/conversations/{conversationId}/messages")
    public ResponseEntity<ApiResponse<PagedResponse<ChatMessageResponse>>> getMessages(
            @Parameter(description = "Conversation unique identifier") @PathVariable UUID conversationId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").ascending());
        Page<ChatMessageResponse> messagesPage = chatService.getMessagesByConversationId(conversationId, pageable);
        
        PagedResponse<ChatMessageResponse> pagedResponse = PagedResponse.<ChatMessageResponse>builder()
                .content(messagesPage.getContent())
                .page(messagesPage.getNumber())
                .size(messagesPage.getSize())
                .totalElements(messagesPage.getTotalElements())
                .totalPages(messagesPage.getTotalPages())
                .first(messagesPage.isFirst())
                .last(messagesPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Mark messages as read", description = "Mark one or more messages as read")
    @PatchMapping("/conversations/{conversationId}/messages/read")
    public ResponseEntity<ApiResponse<String>> markAsRead(
            @Parameter(description = "Conversation unique identifier") @PathVariable UUID conversationId,
            @RequestBody List<UUID> messageIds) {
        chatService.markMessagesAsRead(conversationId, messageIds);
        return ResponseEntity.ok(ApiResponse.success("Messages marked as read"));
    }

    @Operation(summary = "Update conversation status", description = "Update conversation status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)")
    @PatchMapping("/conversations/{conversationId}/status")
    public ResponseEntity<ApiResponse<ChatConversationResponse>> updateStatus(
            @Parameter(description = "Conversation unique identifier") @PathVariable UUID conversationId,
            @RequestParam String status) {
        ChatConversationResponse response = chatService.updateConversationStatus(conversationId, status);
        return ResponseEntity.ok(ApiResponse.success("Conversation status updated", response));
    }

    @Operation(summary = "Get unread count", description = "Get total unread message count for a citizen")
    @GetMapping("/conversations/citizens/{citizenId}/unread/count")
    public ResponseEntity<ApiResponse<Long>> getUnreadCount(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        Long count = chatService.getUnreadCountByCitizenId(citizenId);
        return ResponseEntity.ok(ApiResponse.success(count));
    }
}

