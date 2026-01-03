package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.scheme.SchemeRequest;
import com.smart.citizen.dto.scheme.SchemeResponse;
import com.smart.citizen.service.SchemeService;
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
@RequestMapping("/schemes")
@RequiredArgsConstructor
@Tag(name = "Schemes", description = "API endpoints for managing government schemes")
public class SchemeController {

    private final SchemeService schemeService;

    @Operation(summary = "Create new scheme", description = "Create a new government scheme with eligibility criteria")
    @PostMapping
    public ResponseEntity<ApiResponse<SchemeResponse>> createScheme(@Valid @RequestBody SchemeRequest request) {
        SchemeResponse response = schemeService.createScheme(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Scheme created successfully", response));
    }

    @Operation(summary = "Get scheme by ID", description = "Retrieve scheme details by unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<SchemeResponse>> getSchemeById(
            @Parameter(description = "Scheme unique identifier") @PathVariable UUID id) {
        SchemeResponse response = schemeService.getSchemeById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get scheme by code", description = "Retrieve scheme details by scheme code")
    @GetMapping("/code/{code}")
    public ResponseEntity<ApiResponse<SchemeResponse>> getSchemeByCode(
            @Parameter(description = "Scheme code") @PathVariable String code) {
        SchemeResponse response = schemeService.getSchemeByCode(code);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get all schemes", description = "Retrieve a paginated list of all schemes")
    @GetMapping
    public ResponseEntity<ApiResponse<PagedResponse<SchemeResponse>>> getAllSchemes(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "ASC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<SchemeResponse> schemePage = schemeService.getAllSchemes(pageable);
        
        PagedResponse<SchemeResponse> pagedResponse = PagedResponse.<SchemeResponse>builder()
                .content(schemePage.getContent())
                .page(schemePage.getNumber())
                .size(schemePage.getSize())
                .totalElements(schemePage.getTotalElements())
                .totalPages(schemePage.getTotalPages())
                .first(schemePage.isFirst())
                .last(schemePage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Get active schemes", description = "Retrieve all currently active schemes")
    @GetMapping("/active")
    public ResponseEntity<ApiResponse<java.util.List<SchemeResponse>>> getActiveSchemes() {
        java.util.List<SchemeResponse> response = schemeService.getActiveSchemes();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get schemes by category", description = "Retrieve schemes filtered by category")
    @GetMapping("/category/{category}")
    public ResponseEntity<ApiResponse<java.util.List<SchemeResponse>>> getSchemesByCategory(
            @Parameter(description = "Scheme category") @PathVariable String category) {
        java.util.List<SchemeResponse> response = schemeService.getSchemesByCategory(category);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get schemes by department", description = "Retrieve schemes filtered by department")
    @GetMapping("/department/{department}")
    public ResponseEntity<ApiResponse<java.util.List<SchemeResponse>>> getSchemesByDepartment(
            @Parameter(description = "Department name") @PathVariable String department) {
        java.util.List<SchemeResponse> response = schemeService.getSchemesByDepartment(department);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update scheme", description = "Update scheme details")
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<SchemeResponse>> updateScheme(
            @Parameter(description = "Scheme unique identifier") @PathVariable UUID id,
            @Valid @RequestBody SchemeRequest request) {
        SchemeResponse response = schemeService.updateScheme(id, request);
        return ResponseEntity.ok(ApiResponse.success("Scheme updated successfully", response));
    }

    @Operation(summary = "Delete scheme", description = "Delete a scheme by ID")
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteScheme(
            @Parameter(description = "Scheme unique identifier") @PathVariable UUID id) {
        schemeService.deleteScheme(id);
        return ResponseEntity.ok(ApiResponse.success("Scheme deleted successfully", null));
    }

    @Operation(summary = "Populate Hindi names for existing schemes", description = "Transliterate and populate Hindi names for all schemes that don't have them")
    @PostMapping("/populate-hindi-names")
    public ResponseEntity<ApiResponse<Integer>> populateHindiNames() {
        int updatedCount = schemeService.populateHindiNamesForExistingSchemes();
        return ResponseEntity.ok(ApiResponse.success(
            "Hindi names populated for " + updatedCount + " schemes", 
            updatedCount
        ));
    }
}
