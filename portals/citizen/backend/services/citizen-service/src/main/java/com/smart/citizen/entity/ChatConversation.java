package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "chat_conversations", indexes = {
    @Index(name = "idx_chat_conversation_citizen", columnList = "citizen_id"),
    @Index(name = "idx_chat_conversation_status", columnList = "status"),
    @Index(name = "idx_chat_conversation_created", columnList = "created_at")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ChatConversation extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, foreignKey = @ForeignKey(name = "fk_chat_conversation_citizen"))
    private Citizen citizen;

    @Column(name = "agent_id")
    private UUID agentId;

    @Column(name = "subject", length = 255)
    private String subject;

    @Column(name = "status", length = 50)
    @Enumerated(EnumType.STRING)
    private ConversationStatus status = ConversationStatus.OPEN;

    @Column(name = "priority", length = 50)
    @Enumerated(EnumType.STRING)
    private Priority priority = Priority.MEDIUM;

    @Column(name = "category", length = 100)
    private String category;

    @Column(name = "last_message_at")
    private LocalDateTime lastMessageAt;

    public enum ConversationStatus {
        OPEN, IN_PROGRESS, RESOLVED, CLOSED
    }

    public enum Priority {
        LOW, MEDIUM, HIGH, URGENT
    }
}

