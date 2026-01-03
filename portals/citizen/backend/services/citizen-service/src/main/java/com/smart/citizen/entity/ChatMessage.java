package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "chat_messages", indexes = {
    @Index(name = "idx_chat_message_conversation", columnList = "conversation_id"),
    @Index(name = "idx_chat_message_sender", columnList = "sender_id"),
    @Index(name = "idx_chat_message_created", columnList = "created_at"),
    @Index(name = "idx_chat_message_read", columnList = "is_read")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessage extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "conversation_id", nullable = false, foreignKey = @ForeignKey(name = "fk_chat_message_conversation"))
    private ChatConversation conversation;

    @Column(name = "sender_id", nullable = false)
    private UUID senderId;

    @Column(name = "sender_type", length = 50, nullable = false)
    @Enumerated(EnumType.STRING)
    private SenderType senderType;

    @Column(name = "message", nullable = false, columnDefinition = "TEXT")
    private String message;

    @Column(name = "is_read", nullable = false)
    private Boolean isRead = false;

    @Column(name = "read_at")
    private LocalDateTime readAt;

    public enum SenderType {
        CITIZEN, AGENT, SYSTEM
    }
}

