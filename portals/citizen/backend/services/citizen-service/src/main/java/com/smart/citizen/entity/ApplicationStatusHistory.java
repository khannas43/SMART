package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "application_status_history", indexes = {
    @Index(name = "idx_status_history_application", columnList = "application_id"),
    @Index(name = "idx_status_history_changed_at", columnList = "changed_at")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ApplicationStatusHistory extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "application_id", nullable = false, foreignKey = @ForeignKey(name = "fk_status_history_application"))
    private ServiceApplication application;

    @Column(name = "to_status", nullable = false, length = 50)
    private String toStatus;

    @Column(name = "from_status", length = 50)
    private String fromStatus;

    @Column(name = "stage", length = 100)
    private String stage;

    @Column(name = "changed_at", nullable = false)
    private LocalDateTime changedAt;

    @Column(name = "changed_by")
    private UUID changedBy;

    @Column(name = "changed_by_type", length = 50)
    private String changedByType; // citizen, officer, system

    @Column(name = "comments", columnDefinition = "TEXT")
    private String comments;
}

