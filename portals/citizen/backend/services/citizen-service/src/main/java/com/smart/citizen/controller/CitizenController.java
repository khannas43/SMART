package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.citizen.BulkUpdateFamilyRelationshipsRequest;
import com.smart.citizen.dto.citizen.ConsentPreferenceDto;
import com.smart.citizen.dto.citizen.CitizenRequest;
import com.smart.citizen.dto.citizen.CitizenResponse;
import com.smart.citizen.dto.citizen.CitizenUpdateRequest;
import com.smart.citizen.dto.citizen.FamilyGraphResponse;
import com.smart.citizen.service.CitizenService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/citizens")
@RequiredArgsConstructor
@Tag(name = "Citizens", description = "API endpoints for managing citizen accounts and profiles")
public class CitizenController {

    private final CitizenService citizenService;

    @Operation(summary = "Create new citizen", description = "Register a new citizen account with mobile number and basic information")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Citizen created successfully")
    @PostMapping
    public ResponseEntity<ApiResponse<CitizenResponse>> createCitizen(@Valid @RequestBody CitizenRequest request) {
        CitizenResponse response = citizenService.createCitizen(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Citizen created successfully", response));
    }

    @Operation(summary = "Get citizen by ID", description = "Retrieve citizen details by their unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<CitizenResponse>> getCitizenById(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID id) {
        CitizenResponse response = citizenService.getCitizenById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get citizen by mobile number", description = "Retrieve citizen details by mobile number")
    @GetMapping("/mobile/{mobileNumber}")
    public ResponseEntity<ApiResponse<CitizenResponse>> getCitizenByMobileNumber(
            @Parameter(description = "10-digit mobile number") @PathVariable String mobileNumber) {
        CitizenResponse response = citizenService.getCitizenByMobileNumber(mobileNumber);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/aadhaar/{aadhaarNumber}")
    public ResponseEntity<ApiResponse<CitizenResponse>> getCitizenByAadhaarNumber(@PathVariable String aadhaarNumber) {
        CitizenResponse response = citizenService.getCitizenByAadhaarNumber(aadhaarNumber);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get all citizens", description = "Retrieve a paginated list of all citizens with sorting options")
    @GetMapping
    public ResponseEntity<ApiResponse<PagedResponse<CitizenResponse>>> getAllCitizens(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<CitizenResponse> citizenPage = citizenService.getAllCitizens(pageable);
        
        PagedResponse<CitizenResponse> pagedResponse = PagedResponse.<CitizenResponse>builder()
                .content(citizenPage.getContent())
                .page(citizenPage.getNumber())
                .size(citizenPage.getSize())
                .totalElements(citizenPage.getTotalElements())
                .totalPages(citizenPage.getTotalPages())
                .first(citizenPage.isFirst())
                .last(citizenPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<ApiResponse<java.util.List<CitizenResponse>>> getCitizensByStatus(@PathVariable String status) {
        java.util.List<CitizenResponse> response = citizenService.getCitizensByStatus(status);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<CitizenResponse>> updateCitizen(
            @PathVariable UUID id,
            @Valid @RequestBody CitizenUpdateRequest request) {
        CitizenResponse response = citizenService.updateCitizen(id, request);
        return ResponseEntity.ok(ApiResponse.success("Citizen updated successfully", response));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteCitizen(@PathVariable UUID id) {
        citizenService.deleteCitizen(id);
        return ResponseEntity.ok(ApiResponse.success("Citizen deleted successfully", null));
    }

    @GetMapping("/exists/mobile/{mobileNumber}")
    public ResponseEntity<ApiResponse<Boolean>> checkMobileNumberExists(@PathVariable String mobileNumber) {
        boolean exists = citizenService.existsByMobileNumber(mobileNumber);
        return ResponseEntity.ok(ApiResponse.success(exists));
    }

    @GetMapping("/exists/aadhaar/{aadhaarNumber}")
    public ResponseEntity<ApiResponse<Boolean>> checkAadhaarNumberExists(@PathVariable String aadhaarNumber) {
        boolean exists = citizenService.existsByAadhaarNumber(aadhaarNumber);
        return ResponseEntity.ok(ApiResponse.success(exists));
    }

    @Operation(summary = "Get current authenticated user", description = "Retrieve the citizen profile of the currently authenticated user based on JWT token")
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<CitizenResponse>> getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        if (authentication == null || !authentication.isAuthenticated() || authentication.getPrincipal().equals("anonymousUser")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("User is not authenticated"));
        }
        
        String username = authentication.getName(); // This is the username from JWT token (Jan Aadhaar ID in our case)
        
        try {
            // Try to find citizen by Aadhaar number (username in token)
            CitizenResponse response = citizenService.getCitizenByAadhaarNumber(username);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (com.smart.citizen.exception.ResourceNotFoundException e) {
            // Citizen not found - return 404
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.error("Citizen profile not found. Please complete your registration."));
        }
    }

    @Operation(summary = "Get family relationships graph", description = "Retrieve family relationships graph for a citizen (3-level depth) from AI-PLATFORM-02")
    @GetMapping("/{id}/family/relationships")
    public ResponseEntity<ApiResponse<FamilyGraphResponse>> getFamilyRelationships(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID id,
            @Parameter(description = "Depth of relationships to retrieve (default: 3)") 
            @RequestParam(defaultValue = "3") int depth) {
        FamilyGraphResponse response = citizenService.getFamilyRelationships(id, depth);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update family relationships", description = "Bulk update family relationships for a citizen. Replaces existing relationships with the provided ones.")
    @PutMapping("/{id}/family/relationships")
    public ResponseEntity<ApiResponse<Integer>> updateFamilyRelationships(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID id,
            @Valid @RequestBody BulkUpdateFamilyRelationshipsRequest request) {
        int updatedCount = citizenService.updateFamilyRelationships(id, request);
        return ResponseEntity.ok(ApiResponse.success(
            updatedCount + " family relationship(s) updated successfully", 
            updatedCount
        ));
    }

    @Operation(summary = "Get consent preferences", description = "Retrieve data sharing consent preferences for a citizen")
    @GetMapping("/{id}/consent/preferences")
    public ResponseEntity<ApiResponse<java.util.List<ConsentPreferenceDto>>> getConsentPreferences(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID id) {
        java.util.List<ConsentPreferenceDto> preferences = citizenService.getConsentPreferences(id);
        return ResponseEntity.ok(ApiResponse.success(preferences));
    }

    @Operation(summary = "Update consent preferences", description = "Update data sharing consent preferences for a citizen")
    @PutMapping("/{id}/consent/preferences")
    public ResponseEntity<ApiResponse<java.util.List<ConsentPreferenceDto>>> updateConsentPreferences(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID id,
            @Valid @RequestBody java.util.List<ConsentPreferenceDto> preferences) {
        java.util.List<ConsentPreferenceDto> updated = citizenService.updateConsentPreferences(id, preferences);
        return ResponseEntity.ok(ApiResponse.success("Consent preferences updated successfully", updated));
    }
}

