package com.smart.citizen.service.impl;

import com.smart.citizen.dto.document.DocumentResponse;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.Document;
import com.smart.citizen.entity.ServiceApplication;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.DocumentMapper;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.DocumentRepository;
import com.smart.citizen.repository.ServiceApplicationRepository;
import com.smart.citizen.service.DocumentService;
import com.smart.citizen.service.FileStorageService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
@Slf4j
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final CitizenRepository citizenRepository;
    private final ServiceApplicationRepository applicationRepository;
    private final DocumentMapper documentMapper;
    private final FileStorageService fileStorageService;

    @Override
    public DocumentResponse uploadDocument(UUID citizenId, MultipartFile file, String documentType, UUID applicationId) {
        // Validate citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        // Validate file
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("File is required");
        }

        try {
            // Store file
            String subDirectory = "citizen_" + citizenId.toString();
            String filePath = fileStorageService.storeFile(file, subDirectory);

            // Calculate file hash
            byte[] fileContent = file.getBytes();
            String fileHash = fileStorageService.calculateFileHash(fileContent);

            // Create document entity
            Document document = new Document();
            document.setCitizen(citizen);
            document.setDocumentType(documentType);
            document.setDocumentName(file.getOriginalFilename());
            document.setFilePath(filePath);
            document.setFileSize(file.getSize());
            document.setMimeType(file.getContentType());
            document.setFileHash(fileHash);
            document.setVerificationStatus(Document.VerificationStatus.PENDING);
            document.setUploadedAt(LocalDateTime.now());

            // Get current user ID if available
            try {
                Authentication auth = SecurityContextHolder.getContext().getAuthentication();
                if (auth != null && auth.getPrincipal() instanceof org.springframework.security.core.userdetails.UserDetails) {
                    // Extract user ID from authentication if available
                    // For now, we'll use citizen ID as uploadedBy
                    document.setUploadedBy(citizenId);
                }
            } catch (Exception e) {
                log.warn("Could not extract user from security context", e);
                document.setUploadedBy(citizenId);
            }

            // Set application if provided
            if (applicationId != null) {
                ServiceApplication application = applicationRepository.findById(applicationId)
                        .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", applicationId));
                document.setApplication(application);
            }

            Document savedDocument = documentRepository.save(document);
            log.info("Document uploaded successfully: {} for citizen: {}", savedDocument.getId(), citizenId);
            return documentMapper.toResponse(savedDocument);
        } catch (IOException e) {
            log.error("Error storing file", e);
            throw new RuntimeException("Failed to store file", e);
        }
    }

    @Override
    public Path getDocumentFilePath(UUID documentId) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new ResourceNotFoundException("Document", "id", documentId));
        return fileStorageService.loadFileAsPath(document.getFilePath());
    }

    @Override
    @Transactional(readOnly = true)
    public DocumentResponse getDocumentById(UUID id) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Document", "id", id));
        return documentMapper.toResponse(document);
    }

    @Override
    @Transactional(readOnly = true)
    public List<DocumentResponse> getDocumentsByCitizenId(UUID citizenId) {
        return documentRepository.findByCitizenId(citizenId).stream()
                .map(documentMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DocumentResponse> getDocumentsByApplicationId(UUID applicationId) {
        return documentRepository.findByApplicationId(applicationId).stream()
                .map(documentMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DocumentResponse> getDocumentsByCitizenIdAndType(UUID citizenId, String documentType) {
        return documentRepository.findByCitizenIdAndDocumentType(citizenId, documentType).stream()
                .map(documentMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public DocumentResponse updateDocumentVerificationStatus(UUID id, String status, String notes) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Document", "id", id));
        
        document.setVerificationStatus(Document.VerificationStatus.valueOf(status.toUpperCase()));
        document.setVerificationNotes(notes);
        document.setVerifiedAt(LocalDateTime.now());
        
        Document updatedDocument = documentRepository.save(document);
        return documentMapper.toResponse(updatedDocument);
    }

    @Override
    public void deleteDocument(UUID id) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Document", "id", id));
        
        // Delete physical file
        try {
            fileStorageService.deleteFile(document.getFilePath());
        } catch (IOException e) {
            log.warn("Failed to delete physical file: {}", document.getFilePath(), e);
        }
        
        // Delete database record
        documentRepository.delete(document);
        log.info("Document deleted: {}", id);
    }
}

