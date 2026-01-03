package com.smart.citizen.dto.document;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentResponse {
    private UUID id;
    private UUID citizenId;
    private UUID applicationId;
    private String documentType;
    private String documentName;
    private String filePath;
    private Long fileSize;
    private String mimeType;
    private String fileHash;
    private String verificationStatus;
    private LocalDateTime uploadedAt;
    private LocalDateTime verifiedAt;
    private UUID verifiedBy;
    private String verificationNotes;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

