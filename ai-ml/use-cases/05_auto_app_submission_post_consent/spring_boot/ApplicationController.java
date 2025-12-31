package com.smart.platform.aiml.application.controller;

import com.smart.platform.aiml.application.dto.*;
import com.smart.platform.aiml.application.service.ApplicationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller for Application Management
 * Handles application creation, submission, and status queries
 */
@RestController
@RequestMapping("/api/v1/application")
@CrossOrigin(origins = "*")
public class ApplicationController {

    @Autowired
    private ApplicationService applicationService;

    /**
     * Start application creation from consent event
     * POST /api/v1/application/start
     */
    @PostMapping("/start")
    public ResponseEntity<StartApplicationResponse> startApplication(
            @RequestBody StartApplicationRequest request) {
        try {
            StartApplicationResponse response = applicationService.startApplication(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(StartApplicationResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Get application draft for review
     * GET /api/v1/application/draft?family_id={uuid}&scheme_code={code}
     */
    @GetMapping("/draft")
    public ResponseEntity<ApplicationDraftResponse> getApplicationDraft(
            @RequestParam String family_id,
            @RequestParam String scheme_code) {
        try {
            ApplicationDraftResponse response = applicationService.getApplicationDraft(
                    family_id, scheme_code);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(ApplicationDraftResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Confirm and submit reviewed application
     * POST /api/v1/application/confirm
     */
    @PostMapping("/confirm")
    public ResponseEntity<ConfirmApplicationResponse> confirmApplication(
            @RequestBody ConfirmApplicationRequest request) {
        try {
            ConfirmApplicationResponse response = applicationService.confirmApplication(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(ConfirmApplicationResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Get application status
     * GET /api/v1/application/status?family_id={uuid}
     */
    @GetMapping("/status")
    public ResponseEntity<ApplicationStatusResponse> getApplicationStatus(
            @RequestParam String family_id,
            @RequestParam(required = false) String scheme_code) {
        try {
            ApplicationStatusResponse response = applicationService.getApplicationStatus(
                    family_id, scheme_code);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(ApplicationStatusResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Get application details
     * GET /api/v1/application/{application_id}
     */
    @GetMapping("/{application_id}")
    public ResponseEntity<ApplicationDetailResponse> getApplicationDetails(
            @PathVariable Integer application_id) {
        try {
            ApplicationDetailResponse response = applicationService.getApplicationDetails(
                    application_id);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(ApplicationDetailResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Update application field (for citizen review edits)
     * PUT /api/v1/application/{application_id}/field
     */
    @PutMapping("/{application_id}/field")
    public ResponseEntity<UpdateFieldResponse> updateApplicationField(
            @PathVariable Integer application_id,
            @RequestBody UpdateFieldRequest request) {
        try {
            UpdateFieldResponse response = applicationService.updateApplicationField(
                    application_id, request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(UpdateFieldResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }

    /**
     * Retry failed submission
     * POST /api/v1/application/{application_id}/retry
     */
    @PostMapping("/{application_id}/retry")
    public ResponseEntity<RetrySubmissionResponse> retrySubmission(
            @PathVariable Integer application_id) {
        try {
            RetrySubmissionResponse response = applicationService.retrySubmission(
                    application_id);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(RetrySubmissionResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .build());
        }
    }
}

