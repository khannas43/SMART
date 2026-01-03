package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "service_applications", indexes = {
    @Index(name = "idx_applications_citizen", columnList = "citizen_id"),
    @Index(name = "idx_applications_scheme", columnList = "scheme_id"),
    @Index(name = "idx_applications_status", columnList = "status"),
    @Index(name = "idx_applications_number", columnList = "application_number")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ServiceApplication extends BaseEntity {

    @Column(name = "application_number", unique = true, nullable = false, length = 50)
    private String applicationNumber;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, foreignKey = @ForeignKey(name = "fk_application_citizen"))
    private Citizen citizen;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "scheme_id", foreignKey = @ForeignKey(name = "fk_application_scheme"))
    private Scheme scheme;

    @Column(name = "service_type", nullable = false, length = 100)
    private String serviceType;

    @Column(name = "application_type", length = 100)
    private String applicationType;

    @Column(name = "subject", columnDefinition = "TEXT")
    private String subject;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "priority", length = 20)
    @Enumerated(EnumType.STRING)
    private Priority priority = Priority.NORMAL;

    @Column(name = "status", length = 50)
    @Enumerated(EnumType.STRING)
    private ApplicationStatus status = ApplicationStatus.SUBMITTED;

    @Column(name = "current_stage", length = 100)
    private String currentStage;

    @Column(name = "submission_date")
    private LocalDateTime submissionDate;

    @Column(name = "assigned_to_dept", length = 255)
    private String assignedToDept;

    @Column(name = "assigned_to_officer")
    private UUID assignedToOfficer;

    @Column(name = "expected_completion_date")
    private java.time.LocalDate expectedCompletionDate;

    @Column(name = "actual_completion_date")
    private LocalDateTime actualCompletionDate;

    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.JSON)
    @Column(name = "application_data", columnDefinition = "jsonb")
    private java.util.Map<String, Object> applicationData;

    public enum Priority {
        LOW, NORMAL, HIGH, URGENT
    }

    public enum ApplicationStatus {
        SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, COMPLETED, CANCELLED
    }
}

