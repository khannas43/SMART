package com.smart.citizen.dto.document;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.UUID;

@Data
public class DocumentRequest {
    private UUID applicationId;

    @NotBlank(message = "Document type is required")
    @Size(max = 100, message = "Document type must not exceed 100 characters")
    private String documentType;

    @NotBlank(message = "File path is required")
    private String filePath;

    private String documentName;
    private Long fileSize;
    private String mimeType;
}

