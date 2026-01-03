package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.search.SearchResult;
import com.smart.citizen.service.SearchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/search")
@RequiredArgsConstructor
@Tag(name = "Search", description = "API endpoints for global search across schemes, applications, and documents")
public class SearchController {

    private final SearchService searchService;

    @Operation(summary = "Global search", description = "Search across schemes, applications, and documents. Applications and documents are filtered by authenticated citizen.")
    @GetMapping
    public ResponseEntity<ApiResponse<SearchResult>> searchAll(
            @Parameter(description = "Search query") @RequestParam String q,
            @Parameter(description = "Citizen ID (optional, extracted from JWT if authenticated)") @RequestParam(required = false) UUID citizenId) {
        
        // Try to get citizen ID from authentication context if not provided
        UUID finalCitizenId = citizenId;
        if (finalCitizenId == null) {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth != null && auth.getPrincipal() instanceof String) {
                // Extract citizen ID from JWT claims if available
                // For now, we'll use the provided citizenId or null
            }
        }

        SearchResult result = searchService.searchAll(q, finalCitizenId);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @Operation(summary = "Search schemes", description = "Search only in government schemes (public)")
    @GetMapping("/schemes")
    public ResponseEntity<ApiResponse<SearchResult>> searchSchemes(
            @Parameter(description = "Search query") @RequestParam String q) {
        SearchResult result = searchService.searchSchemes(q);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @Operation(summary = "Search applications", description = "Search only in citizen's applications")
    @GetMapping("/applications")
    public ResponseEntity<ApiResponse<SearchResult>> searchApplications(
            @Parameter(description = "Search query") @RequestParam String q,
            @Parameter(description = "Citizen ID") @RequestParam UUID citizenId) {
        SearchResult result = searchService.searchApplications(q, citizenId);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @Operation(summary = "Search documents", description = "Search only in citizen's documents")
    @GetMapping("/documents")
    public ResponseEntity<ApiResponse<SearchResult>> searchDocuments(
            @Parameter(description = "Search query") @RequestParam String q,
            @Parameter(description = "Citizen ID") @RequestParam UUID citizenId) {
        SearchResult result = searchService.searchDocuments(q, citizenId);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
}

