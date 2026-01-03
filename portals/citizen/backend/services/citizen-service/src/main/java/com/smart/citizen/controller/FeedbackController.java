package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.feedback.FeedbackRequest;
import com.smart.citizen.dto.feedback.FeedbackResponse;
import com.smart.citizen.service.FeedbackService;
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
@RequestMapping("/feedback")
@RequiredArgsConstructor
@Tag(name = "Feedback", description = "API endpoints for submitting and managing feedback, complaints, and ratings")
public class FeedbackController {

    private final FeedbackService feedbackService;

    @Operation(summary = "Submit feedback", description = "Submit feedback, complaint, suggestion, or rating. Can be associated with an application or standalone.")
    @PostMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<FeedbackResponse>> submitFeedback(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody FeedbackRequest request) {
        FeedbackResponse response = feedbackService.submitFeedback(citizenId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Feedback submitted successfully", response));
    }

    @Operation(summary = "Get feedback by ID", description = "Retrieve feedback details by unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<FeedbackResponse>> getFeedbackById(
            @Parameter(description = "Feedback unique identifier") @PathVariable UUID id) {
        FeedbackResponse response = feedbackService.getFeedbackById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get feedback by citizen", description = "Retrieve all feedback submitted by a citizen with pagination support")
    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PagedResponse<FeedbackResponse>>> getFeedbackByCitizenId(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<FeedbackResponse> feedbackPage = feedbackService.getFeedbackByCitizenId(citizenId, pageable);
        
        PagedResponse<FeedbackResponse> pagedResponse = PagedResponse.<FeedbackResponse>builder()
                .content(feedbackPage.getContent())
                .page(feedbackPage.getNumber())
                .size(feedbackPage.getSize())
                .totalElements(feedbackPage.getTotalElements())
                .totalPages(feedbackPage.getTotalPages())
                .first(feedbackPage.isFirst())
                .last(feedbackPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Get feedback by application", description = "Retrieve all feedback associated with a specific application")
    @GetMapping("/applications/{applicationId}")
    public ResponseEntity<ApiResponse<java.util.List<FeedbackResponse>>> getFeedbackByApplicationId(
            @Parameter(description = "Application unique identifier") @PathVariable UUID applicationId) {
        java.util.List<FeedbackResponse> response = feedbackService.getFeedbackByApplicationId(applicationId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get feedback by type", description = "Retrieve feedback filtered by type (FEEDBACK, COMPLAINT, SUGGESTION, RATING)")
    @GetMapping("/type/{type}")
    public ResponseEntity<ApiResponse<java.util.List<FeedbackResponse>>> getFeedbackByType(
            @Parameter(description = "Feedback type (FEEDBACK, COMPLAINT, SUGGESTION, RATING)") @PathVariable String type) {
        java.util.List<FeedbackResponse> response = feedbackService.getFeedbackByType(type);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update feedback status", description = "Update feedback status and add resolution (typically done by support/admin team)")
    @PatchMapping("/{id}/status")
    public ResponseEntity<ApiResponse<FeedbackResponse>> updateFeedbackStatus(
            @Parameter(description = "Feedback unique identifier") @PathVariable UUID id,
            @Parameter(description = "Feedback status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)") @RequestParam String status,
            @Parameter(description = "Optional resolution text") @RequestParam(required = false) String resolution) {
        FeedbackResponse response = feedbackService.updateFeedbackStatus(id, status, resolution);
        return ResponseEntity.ok(ApiResponse.success("Feedback status updated successfully", response));
    }
}

