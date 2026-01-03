package com.smart.citizen.service;

import com.smart.citizen.dto.document.DocumentResponse;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.util.List;
import java.util.UUID;

public interface DocumentService {
    DocumentResponse uploadDocument(UUID citizenId, MultipartFile file, String documentType, UUID applicationId);
    DocumentResponse getDocumentById(UUID id);
    List<DocumentResponse> getDocumentsByCitizenId(UUID citizenId);
    List<DocumentResponse> getDocumentsByApplicationId(UUID applicationId);
    List<DocumentResponse> getDocumentsByCitizenIdAndType(UUID citizenId, String documentType);
    DocumentResponse updateDocumentVerificationStatus(UUID id, String status, String notes);
    void deleteDocument(UUID id);
    Path getDocumentFilePath(UUID documentId);
}

