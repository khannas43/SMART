package com.smart.platform.nudging.controller;

import com.smart.platform.nudging.dto.NudgeRequest;
import com.smart.platform.nudging.dto.NudgeResponse;
import com.smart.platform.nudging.dto.NudgeHistoryItem;
import com.smart.platform.nudging.service.NudgeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller for AI-PLATFORM-11: Personalized Communication & Nudging
 */
@RestController
@RequestMapping("/nudges")
@CrossOrigin(origins = "*")
public class NudgeController {

    @Autowired
    private NudgeService nudgeService;

    /**
     * Schedule a new nudge
     * POST /nudges/schedule
     */
    @PostMapping("/schedule")
    public ResponseEntity<NudgeResponse> scheduleNudge(@RequestBody NudgeRequest request) {
        try {
            NudgeResponse response = nudgeService.scheduleNudge(request);
            if (response.isSuccess()) {
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
            }
        } catch (Exception e) {
            NudgeResponse errorResponse = new NudgeResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get nudge history for a family
     * GET /nudges/history?familyId={familyId}&limit={limit}
     */
    @GetMapping("/history")
    public ResponseEntity<List<NudgeHistoryItem>> getNudgeHistory(
            @RequestParam String familyId,
            @RequestParam(defaultValue = "50") Integer limit) {
        try {
            List<NudgeHistoryItem> history = nudgeService.getNudgeHistory(familyId, limit);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Record feedback for a nudge (delivered, opened, clicked, responded, completed, etc.)
     * POST /nudges/{nudgeId}/feedback
     */
    @PostMapping("/{nudgeId}/feedback")
    public ResponseEntity<NudgeResponse> recordFeedback(
            @PathVariable String nudgeId,
            @RequestParam String eventType,
            @RequestBody(required = false) Map<String, Object> metadata) {
        try {
            NudgeResponse response = nudgeService.recordFeedback(nudgeId, eventType, metadata);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            NudgeResponse errorResponse = new NudgeResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}

