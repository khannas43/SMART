package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.application.ApplicationStatusHistoryResponse;
import com.smart.citizen.dto.application.ApplicationStatusUpdateRequest;
import com.smart.citizen.dto.application.ServiceApplicationRequest;
import com.smart.citizen.dto.application.ServiceApplicationResponse;
import com.smart.citizen.service.ServiceApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/applications")
@RequiredArgsConstructor
@Tag(name = "Applications", description = "API endpoints for managing service applications")
public class ServiceApplicationController {

    private final ServiceApplicationService applicationService;

    @Operation(summary = "Submit new application", description = "Create a new service application for a citizen")
    @PostMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<ServiceApplicationResponse>> createApplication(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody ServiceApplicationRequest request) {
        ServiceApplicationResponse response = applicationService.createApplication(citizenId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Application submitted successfully", response));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<ServiceApplicationResponse>> getApplicationById(@PathVariable UUID id) {
        ServiceApplicationResponse response = applicationService.getApplicationById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/number/{applicationNumber}")
    public ResponseEntity<ApiResponse<ServiceApplicationResponse>> getApplicationByNumber(@PathVariable String applicationNumber) {
        ServiceApplicationResponse response = applicationService.getApplicationByNumber(applicationNumber);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PagedResponse<ServiceApplicationResponse>>> getApplicationsByCitizenId(
            @PathVariable UUID citizenId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        // Validate sortBy field to prevent SQL injection
        String validSortBy = sortBy;
        if (!sortBy.equals("createdAt") && !sortBy.equals("updatedAt") && 
            !sortBy.equals("submissionDate") && !sortBy.equals("status")) {
            validSortBy = "createdAt";
        }
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(validSortBy).ascending() : Sort.by(validSortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<ServiceApplicationResponse> applicationPage = applicationService.getApplicationsByCitizenId(citizenId, pageable);
        
        PagedResponse<ServiceApplicationResponse> pagedResponse = PagedResponse.<ServiceApplicationResponse>builder()
                .content(applicationPage.getContent())
                .page(applicationPage.getNumber())
                .size(applicationPage.getSize())
                .totalElements(applicationPage.getTotalElements())
                .totalPages(applicationPage.getTotalPages())
                .first(applicationPage.isFirst())
                .last(applicationPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @GetMapping("/citizens/{citizenId}/status/{status}")
    public ResponseEntity<ApiResponse<java.util.List<ServiceApplicationResponse>>> getApplicationsByCitizenIdAndStatus(
            @PathVariable UUID citizenId,
            @PathVariable String status) {
        java.util.List<ServiceApplicationResponse> response = applicationService.getApplicationsByCitizenIdAndStatus(citizenId, status);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<ApiResponse<PagedResponse<ServiceApplicationResponse>>> getApplicationsByStatus(
            @PathVariable String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "submissionDate") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<ServiceApplicationResponse> applicationPage = applicationService.getApplicationsByStatus(status, pageable);
        
        PagedResponse<ServiceApplicationResponse> pagedResponse = PagedResponse.<ServiceApplicationResponse>builder()
                .content(applicationPage.getContent())
                .page(applicationPage.getNumber())
                .size(applicationPage.getSize())
                .totalElements(applicationPage.getTotalElements())
                .totalPages(applicationPage.getTotalPages())
                .first(applicationPage.isFirst())
                .last(applicationPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<ApiResponse<ServiceApplicationResponse>> updateApplicationStatus(
            @PathVariable UUID id,
            @Valid @RequestBody ApplicationStatusUpdateRequest request) {
        ServiceApplicationResponse response = applicationService.updateApplicationStatus(id, request);
        return ResponseEntity.ok(ApiResponse.success("Application status updated successfully", response));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<ServiceApplicationResponse>> updateApplication(
            @PathVariable UUID id,
            @Valid @RequestBody ServiceApplicationRequest request) {
        ServiceApplicationResponse response = applicationService.updateApplication(id, request);
        return ResponseEntity.ok(ApiResponse.success("Application updated successfully", response));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteApplication(@PathVariable UUID id) {
        applicationService.deleteApplication(id);
        return ResponseEntity.ok(ApiResponse.success("Application deleted successfully", null));
    }

    @Operation(summary = "Get application status history", description = "Retrieve the complete status change history/timeline for an application")
    @GetMapping("/{id}/history")
    public ResponseEntity<ApiResponse<java.util.List<ApplicationStatusHistoryResponse>>> getApplicationStatusHistory(
            @Parameter(description = "Application unique identifier") @PathVariable UUID id) {
        java.util.List<ApplicationStatusHistoryResponse> history = applicationService.getApplicationStatusHistory(id);
        return ResponseEntity.ok(ApiResponse.success(history));
    }
}

