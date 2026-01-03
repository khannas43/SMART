package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "feedback", indexes = {
    @Index(name = "idx_feedback_citizen", columnList = "citizen_id"),
    @Index(name = "idx_feedback_type", columnList = "feedback_type"),
    @Index(name = "idx_feedback_status", columnList = "status"),
    @Index(name = "idx_feedback_created", columnList = "created_at")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Feedback extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, foreignKey = @ForeignKey(name = "fk_feedback_citizen"))
    private Citizen citizen;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "application_id", foreignKey = @ForeignKey(name = "fk_feedback_application"))
    private ServiceApplication application;

    @Column(name = "type", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private FeedbackType type;

    @Column(name = "subject", length = 255)
    private String subject;

    @Column(name = "message", nullable = false, columnDefinition = "TEXT")
    private String message;

    @Column(name = "rating")
    private Integer rating; // 1-5 scale

    @Column(name = "category", length = 100)
    private String category;

    @Column(name = "status", length = 50)
    @Enumerated(EnumType.STRING)
    private FeedbackStatus status = FeedbackStatus.OPEN;

    @Column(name = "resolution", columnDefinition = "TEXT")
    private String resolution;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "resolved_by")
    private UUID resolvedBy;

    public enum FeedbackType {
        FEEDBACK, COMPLAINT, SUGGESTION, RATING
    }

    public enum FeedbackStatus {
        OPEN, IN_PROGRESS, RESOLVED, CLOSED
    }
}

