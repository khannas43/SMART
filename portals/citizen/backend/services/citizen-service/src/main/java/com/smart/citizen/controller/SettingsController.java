package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.settings.NotificationPreferencesRequest;
import com.smart.citizen.dto.settings.OptOutRequest;
import com.smart.citizen.dto.settings.SettingsResponse;
import com.smart.citizen.service.SettingsService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/settings")
@RequiredArgsConstructor
@Tag(name = "Settings", description = "API endpoints for managing citizen settings and preferences")
public class SettingsController {

    private final SettingsService settingsService;

    @Operation(summary = "Get settings", description = "Retrieve all settings for a citizen")
    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<SettingsResponse>> getSettings(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        SettingsResponse response = settingsService.getSettingsByCitizenId(citizenId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update notification preferences", description = "Update notification channel preferences and quiet hours")
    @PutMapping("/citizens/{citizenId}/notifications")
    public ResponseEntity<ApiResponse<SettingsResponse>> updateNotificationPreferences(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody NotificationPreferencesRequest request) {
        SettingsResponse response = settingsService.updateNotificationPreferences(citizenId, request);
        return ResponseEntity.ok(ApiResponse.success("Notification preferences updated successfully", response));
    }

    @Operation(summary = "Update opt-out schemes", description = "Update list of schemes the citizen has opted out of")
    @PutMapping("/citizens/{citizenId}/opt-out")
    public ResponseEntity<ApiResponse<SettingsResponse>> updateOptOutSchemes(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody OptOutRequest request) {
        SettingsResponse response = settingsService.updateOptOutSchemes(citizenId, request);
        return ResponseEntity.ok(ApiResponse.success("Opt-out preferences updated successfully", response));
    }

    @Operation(summary = "Update language preference", description = "Update preferred language")
    @PatchMapping("/citizens/{citizenId}/language")
    public ResponseEntity<ApiResponse<SettingsResponse>> updateLanguagePreference(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Parameter(description = "Language code (en, hi, rj)") @RequestParam String language) {
        SettingsResponse response = settingsService.updateLanguagePreference(citizenId, language);
        return ResponseEntity.ok(ApiResponse.success("Language preference updated successfully", response));
    }

    @Operation(summary = "Update theme preference", description = "Update preferred theme (light/dark)")
    @PatchMapping("/citizens/{citizenId}/theme")
    public ResponseEntity<ApiResponse<SettingsResponse>> updateThemePreference(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Parameter(description = "Theme (light/dark)") @RequestParam String theme) {
        SettingsResponse response = settingsService.updateThemePreference(citizenId, theme);
        return ResponseEntity.ok(ApiResponse.success("Theme preference updated successfully", response));
    }

    @Operation(summary = "Update two-factor authentication", description = "Enable or disable two-factor authentication")
    @PatchMapping("/citizens/{citizenId}/two-factor")
    public ResponseEntity<ApiResponse<SettingsResponse>> updateTwoFactorEnabled(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Parameter(description = "Enable two-factor authentication") @RequestParam Boolean enabled) {
        SettingsResponse response = settingsService.updateTwoFactorEnabled(citizenId, enabled);
        return ResponseEntity.ok(ApiResponse.success("Two-factor authentication updated successfully", response));
    }
}

