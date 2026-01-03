package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "documents", indexes = {
    @Index(name = "idx_documents_citizen", columnList = "citizen_id"),
    @Index(name = "idx_documents_application", columnList = "application_id"),
    @Index(name = "idx_documents_type", columnList = "document_type"),
    @Index(name = "idx_documents_status", columnList = "verification_status")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Document extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, foreignKey = @ForeignKey(name = "fk_document_citizen"))
    private Citizen citizen;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "application_id", foreignKey = @ForeignKey(name = "fk_document_application"))
    private ServiceApplication application;

    @Column(name = "document_type", nullable = false, length = 100)
    private String documentType;

    @Column(name = "document_name", length = 255)
    private String documentName;

    @Column(name = "file_path", nullable = false, columnDefinition = "TEXT")
    private String filePath;

    @Column(name = "file_hash", length = 64)
    private String fileHash;

    @Column(name = "file_size")
    private Long fileSize;

    @Column(name = "mime_type", length = 100)
    private String mimeType;

    @Column(name = "uploaded_at")
    private LocalDateTime uploadedAt;

    @Column(name = "verification_status", length = 50)
    @Enumerated(EnumType.STRING)
    private VerificationStatus verificationStatus = VerificationStatus.PENDING;

    @Column(name = "verified_at")
    private LocalDateTime verifiedAt;

    @Column(name = "uploaded_by")
    private UUID uploadedBy;

    @Column(name = "verified_by")
    private UUID verifiedBy;

    @Column(name = "verification_notes", columnDefinition = "TEXT")
    private String verificationNotes;

    public enum VerificationStatus {
        PENDING, VERIFIED, REJECTED, EXPIRED
    }
}

