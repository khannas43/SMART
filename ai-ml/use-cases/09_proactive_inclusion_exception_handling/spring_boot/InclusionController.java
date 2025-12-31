package com.smart.platform.inclusion.controller;

import com.smart.platform.inclusion.dto.*;
import com.smart.platform.inclusion.service.InclusionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for Proactive Inclusion & Exception Handling
 * Use Case ID: AI-PLATFORM-09
 */
@RestController
@RequestMapping("/inclusion")
@CrossOrigin(origins = "*")
public class InclusionController {

    @Autowired
    private InclusionService inclusionService;

    /**
     * Get priority status and nudges for a family
     * GET /inclusion/priority?family_id={id}&include_nudges={bool}
     */
    @GetMapping("/priority")
    public ResponseEntity<PriorityStatusResponse> getPriorityStatus(
            @RequestParam String familyId,
            @RequestParam(required = false, defaultValue = "true") Boolean includeNudges) {
        try {
            PriorityStatusResponse response = inclusionService.getPriorityStatus(familyId, includeNudges);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            PriorityStatusResponse errorResponse = new PriorityStatusResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get priority household list for field workers
     * GET /inclusion/priority-list?block_id={id}&district={name}&segment={seg}&priority_level={level}&limit={limit}
     */
    @GetMapping("/priority-list")
    public ResponseEntity<PriorityListResponse> getPriorityList(
            @RequestParam(required = false) String blockId,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) List<String> segment,
            @RequestParam(required = false) String priorityLevel,
            @RequestParam(required = false, defaultValue = "50") Integer limit) {
        try {
            PriorityListResponse response = inclusionService.getPriorityList(
                    blockId, district, segment, priorityLevel, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            PriorityListResponse errorResponse = new PriorityListResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Schedule and record nudge delivery
     * POST /inclusion/nudge-delivery
     */
    @PostMapping("/nudge-delivery")
    public ResponseEntity<NudgeDeliveryResponse> scheduleNudgeDelivery(
            @RequestBody NudgeDeliveryRequest request) {
        try {
            NudgeDeliveryResponse response = inclusionService.scheduleNudgeDelivery(
                    request.getFamilyId(),
                    request.getNudgeType(),
                    request.getNudgeMessage(),
                    request.getRecommendedActions(),
                    request.getSchemeCodes(),
                    request.getChannel(),
                    request.getPriorityLevel(),
                    request.getScheduledAt()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            NudgeDeliveryResponse errorResponse = new NudgeDeliveryResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get exception flags for a family
     * GET /inclusion/exceptions?family_id={id}
     */
    @GetMapping("/exceptions")
    public ResponseEntity<List<PriorityStatusResponse.ExceptionFlag>> getExceptionFlags(
            @RequestParam String familyId) {
        try {
            List<PriorityStatusResponse.ExceptionFlag> response = inclusionService.getExceptionFlags(familyId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Update exception review status
     * POST /inclusion/exceptions/{exceptionId}/review
     */
    @PostMapping("/exceptions/{exceptionId}/review")
    public ResponseEntity<PriorityStatusResponse.ExceptionFlag> reviewException(
            @PathVariable Integer exceptionId,
            @RequestParam String reviewStatus,
            @RequestParam(required = false) String reviewNotes,
            @RequestParam String reviewedBy) {
        try {
            PriorityStatusResponse.ExceptionFlag response = inclusionService.reviewException(
                    exceptionId, reviewStatus, reviewNotes, reviewedBy);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}

