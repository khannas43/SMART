package com.smart.platform.aiml.eligibility.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.smart.platform.aiml.eligibility.service.RuleManagementService;
import com.smart.platform.aiml.eligibility.dto.*;

import java.util.List;
import java.util.UUID;

/**
 * REST Controller for Rule Management (Admin Interface)
 * Allows users to add/edit/delete eligibility rules via frontend
 * Use Case: AI-PLATFORM-03
 */
@RestController
@RequestMapping("/api/v1/admin/rules")
@CrossOrigin(origins = "*")
public class RuleManagementController {

    @Autowired
    private RuleManagementService ruleManagementService;

    /**
     * List all schemes
     * GET /api/v1/admin/rules/schemes
     */
    @GetMapping("/schemes")
    public ResponseEntity<List<SchemeDto>> listSchemes() {
        try {
            List<SchemeDto> schemes = ruleManagementService.getAllSchemes();
            return ResponseEntity.ok(schemes);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Get all rules for a scheme
     * GET /api/v1/admin/rules/scheme/{scheme_id}
     */
    @GetMapping("/scheme/{scheme_id}")
    public ResponseEntity<SchemeRulesResponse> getSchemeRules(
            @PathVariable("scheme_id") String schemeId,
            @RequestParam(value = "include_inactive", defaultValue = "false") boolean includeInactive
    ) {
        try {
            SchemeRulesResponse response = ruleManagementService.getSchemeRules(schemeId, includeInactive);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(SchemeRulesResponse.error(e.getMessage()));
        }
    }

    /**
     * Get specific rule
     * GET /api/v1/admin/rules/{rule_id}
     */
    @GetMapping("/{rule_id}")
    public ResponseEntity<RuleDto> getRule(@PathVariable("rule_id") Integer ruleId) {
        try {
            RuleDto rule = ruleManagementService.getRule(ruleId);
            return ResponseEntity.ok(rule);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Create new rule
     * POST /api/v1/admin/rules
     */
    @PostMapping
    public ResponseEntity<RuleDto> createRule(@RequestBody CreateRuleRequest request) {
        try {
            RuleDto rule = ruleManagementService.createRule(request);
            return ResponseEntity.ok(rule);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Update existing rule
     * PUT /api/v1/admin/rules/{rule_id}
     */
    @PutMapping("/{rule_id}")
    public ResponseEntity<RuleDto> updateRule(
            @PathVariable("rule_id") Integer ruleId,
            @RequestBody UpdateRuleRequest request
    ) {
        try {
            RuleDto rule = ruleManagementService.updateRule(ruleId, request);
            return ResponseEntity.ok(rule);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Delete rule
     * DELETE /api/v1/admin/rules/{rule_id}
     */
    @DeleteMapping("/{rule_id}")
    public ResponseEntity<Void> deleteRule(@PathVariable("rule_id") Integer ruleId) {
        try {
            ruleManagementService.deleteRule(ruleId);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Clone rule
     * POST /api/v1/admin/rules/{rule_id}/clone
     */
    @PostMapping("/{rule_id}/clone")
    public ResponseEntity<RuleDto> cloneRule(@PathVariable("rule_id") Integer ruleId) {
        try {
            RuleDto clonedRule = ruleManagementService.cloneRule(ruleId);
            return ResponseEntity.ok(clonedRule);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Get rule version history
     * GET /api/v1/admin/rules/{rule_id}/versions
     */
    @GetMapping("/{rule_id}/versions")
    public ResponseEntity<List<RuleVersionDto>> getRuleVersions(@PathVariable("rule_id") Integer ruleId) {
        try {
            List<RuleVersionDto> versions = ruleManagementService.getRuleVersions(ruleId);
            return ResponseEntity.ok(versions);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Rollback rule to previous version
     * POST /api/v1/admin/rules/{rule_id}/rollback
     */
    @PostMapping("/{rule_id}/rollback")
    public ResponseEntity<RuleDto> rollbackRule(
            @PathVariable("rule_id") Integer ruleId,
            @RequestBody RollbackRequest request
    ) {
        try {
            RuleDto rule = ruleManagementService.rollbackRule(ruleId, request.getVersionId());
            return ResponseEntity.ok(rule);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Test rule expression
     * POST /api/v1/admin/rules/test
     */
    @PostMapping("/test")
    public ResponseEntity<RuleTestResponse> testRule(@RequestBody RuleTestRequest request) {
        try {
            RuleTestResponse response = ruleManagementService.testRule(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(RuleTestResponse.error(e.getMessage()));
        }
    }

    /**
     * Validate rule syntax
     * POST /api/v1/admin/rules/validate
     */
    @PostMapping("/validate")
    public ResponseEntity<RuleValidationResponse> validateRule(@RequestBody RuleDto rule) {
        try {
            RuleValidationResponse response = ruleManagementService.validateRule(rule);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(RuleValidationResponse.error(e.getMessage()));
        }
    }

    /**
     * Create rule set snapshot
     * POST /api/v1/admin/rules/scheme/{scheme_id}/snapshot
     */
    @PostMapping("/scheme/{scheme_id}/snapshot")
    public ResponseEntity<RuleSetSnapshotDto> createRuleSetSnapshot(
            @PathVariable("scheme_id") String schemeId,
            @RequestBody CreateSnapshotRequest request
    ) {
        try {
            RuleSetSnapshotDto snapshot = ruleManagementService.createRuleSetSnapshot(
                    schemeId, request.getSnapshotVersion(), request.getSnapshotName(),
                    request.getDescription(), request.getCreatedBy()
            );
            return ResponseEntity.ok(snapshot);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Get rule set snapshots for a scheme
     * GET /api/v1/admin/rules/scheme/{scheme_id}/snapshots
     */
    @GetMapping("/scheme/{scheme_id}/snapshots")
    public ResponseEntity<List<RuleSetSnapshotDto>> getRuleSetSnapshots(
            @PathVariable("scheme_id") String schemeId
    ) {
        try {
            List<RuleSetSnapshotDto> snapshots = ruleManagementService.getRuleSetSnapshots(schemeId);
            return ResponseEntity.ok(snapshots);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Compare evaluations across rule versions
     * GET /api/v1/admin/rules/comparison
     */
    @GetMapping("/comparison")
    public ResponseEntity<EvaluationComparisonResponse> compareRuleVersions(
            @RequestParam("scheme_id") String schemeId,
            @RequestParam("rule_set_version_old") String versionOld,
            @RequestParam("rule_set_version_new") String versionNew,
            @RequestParam(value = "family_id", required = false) UUID familyId
    ) {
        try {
            EvaluationComparisonResponse response = ruleManagementService.compareRuleVersions(
                    schemeId, versionOld, versionNew, familyId
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
}

