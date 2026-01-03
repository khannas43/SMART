package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.document.DocumentResponse;
import com.smart.citizen.service.DocumentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.util.UUID;

@RestController
@RequestMapping("/documents")
@RequiredArgsConstructor
@Tag(name = "Documents", description = "API endpoints for document upload, retrieval, and verification management")
public class DocumentController {

    private final DocumentService documentService;

    @Operation(summary = "Upload document", description = "Upload a new document for a citizen. Can be associated with an application or standalone.")
    @PostMapping(value = "/citizens/{citizenId}", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<DocumentResponse>> uploadDocument(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Parameter(description = "File to upload") @RequestParam("file") MultipartFile file,
            @Parameter(description = "Document type (e.g., AADHAAR, PAN, INCOME_CERTIFICATE)") @RequestParam("documentType") String documentType,
            @Parameter(description = "Optional application ID to associate document with") @RequestParam(value = "applicationId", required = false) UUID applicationId) {
        DocumentResponse response = documentService.uploadDocument(citizenId, file, documentType, applicationId);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Document uploaded successfully", response));
    }

    @Operation(summary = "Get document by ID", description = "Retrieve document details by unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<DocumentResponse>> getDocumentById(
            @Parameter(description = "Document unique identifier") @PathVariable UUID id) {
        DocumentResponse response = documentService.getDocumentById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get documents by citizen", description = "Retrieve all documents uploaded by a specific citizen")
    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<java.util.List<DocumentResponse>>> getDocumentsByCitizenId(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        java.util.List<DocumentResponse> response = documentService.getDocumentsByCitizenId(citizenId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get documents by application", description = "Retrieve all documents associated with a specific application")
    @GetMapping("/applications/{applicationId}")
    public ResponseEntity<ApiResponse<java.util.List<DocumentResponse>>> getDocumentsByApplicationId(
            @Parameter(description = "Application unique identifier") @PathVariable UUID applicationId) {
        java.util.List<DocumentResponse> response = documentService.getDocumentsByApplicationId(applicationId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get documents by citizen and type", description = "Retrieve documents of a specific type for a citizen (e.g., Aadhaar, PAN, Income Certificate)")
    @GetMapping("/citizens/{citizenId}/type/{documentType}")
    public ResponseEntity<ApiResponse<java.util.List<DocumentResponse>>> getDocumentsByCitizenIdAndType(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Parameter(description = "Document type (e.g., AADHAAR, PAN, INCOME_CERTIFICATE)") @PathVariable String documentType) {
        java.util.List<DocumentResponse> response = documentService.getDocumentsByCitizenIdAndType(citizenId, documentType);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update document verification status", description = "Update the verification status of a document (PENDING, VERIFIED, REJECTED)")
    @PatchMapping("/{id}/verification")
    public ResponseEntity<ApiResponse<DocumentResponse>> updateDocumentVerificationStatus(
            @Parameter(description = "Document unique identifier") @PathVariable UUID id,
            @Parameter(description = "Verification status (PENDING, VERIFIED, REJECTED)") @RequestParam String status,
            @Parameter(description = "Optional verification notes") @RequestParam(required = false) String notes) {
        DocumentResponse response = documentService.updateDocumentVerificationStatus(id, status, notes);
        return ResponseEntity.ok(ApiResponse.success("Document verification status updated successfully", response));
    }

    @Operation(summary = "Delete document", description = "Delete a document by its unique identifier")
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteDocument(
            @Parameter(description = "Document unique identifier") @PathVariable UUID id) {
        documentService.deleteDocument(id);
        return ResponseEntity.ok(ApiResponse.success("Document deleted successfully", null));
    }

    @Operation(summary = "Download document", description = "Download a document file by its unique identifier")
    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> downloadDocument(
            @Parameter(description = "Document unique identifier") @PathVariable UUID id) {
        try {
            DocumentResponse document = documentService.getDocumentById(id);
            Path filePath = documentService.getDocumentFilePath(id);
            Resource resource = new UrlResource(filePath.toUri());

            if (!resource.exists() || !resource.isReadable()) {
                return ResponseEntity.notFound().build();
            }

            String contentType = document.getMimeType() != null 
                    ? document.getMimeType() 
                    : "application/octet-stream";

            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.CONTENT_DISPOSITION, 
                            "attachment; filename=\"" + (document.getDocumentName() != null 
                                    ? document.getDocumentName() 
                                    : "document") + "\"")
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
}

