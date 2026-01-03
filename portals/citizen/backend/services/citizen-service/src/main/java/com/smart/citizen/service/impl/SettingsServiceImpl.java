package com.smart.citizen.service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smart.citizen.dto.settings.NotificationPreferencesRequest;
import com.smart.citizen.dto.settings.OptOutRequest;
import com.smart.citizen.dto.settings.SettingsResponse;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.CitizenSettings;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.CitizenSettingsRepository;
import com.smart.citizen.service.SettingsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SettingsServiceImpl implements SettingsService {

    private final CitizenSettingsRepository settingsRepository;
    private final CitizenRepository citizenRepository;
    private final ObjectMapper objectMapper;

    @Override
    @Transactional(readOnly = true)
    public SettingsResponse getSettingsByCitizenId(UUID citizenId) {
        CitizenSettings settings = settingsRepository.findByCitizenId(citizenId)
                .orElseGet(() -> createDefaultSettings(citizenId));
        return mapToResponse(settings);
    }

    @Override
    @Transactional
    public SettingsResponse updateNotificationPreferences(UUID citizenId, NotificationPreferencesRequest request) {
        CitizenSettings settings = getOrCreateSettings(citizenId);

        try {
            // Convert preferences to JSON
            Map<String, Object> prefsMap = new HashMap<>();
            if (request.getPreferences() != null) {
                prefsMap.putAll(request.getPreferences());
            }
            JsonNode prefsJson = objectMapper.valueToTree(prefsMap);
            settings.setNotificationPreferences(prefsJson);

            // Update quiet hours
            if (request.getQuietHours() != null) {
                settings.setQuietHoursEnabled(request.getQuietHours().getEnabled());
                if (request.getQuietHours().getStartTime() != null) {
                    settings.setQuietHoursStart(LocalTime.parse(request.getQuietHours().getStartTime(), DateTimeFormatter.ofPattern("HH:mm")));
                }
                if (request.getQuietHours().getEndTime() != null) {
                    settings.setQuietHoursEnd(LocalTime.parse(request.getQuietHours().getEndTime(), DateTimeFormatter.ofPattern("HH:mm")));
                }
            }

            settings = settingsRepository.save(settings);
            return mapToResponse(settings);
        } catch (Exception e) {
            log.error("Error updating notification preferences for citizen {}", citizenId, e);
            throw new RuntimeException("Failed to update notification preferences", e);
        }
    }

    @Override
    @Transactional
    public SettingsResponse updateOptOutSchemes(UUID citizenId, OptOutRequest request) {
        CitizenSettings settings = getOrCreateSettings(citizenId);
        settings.setOptedOutSchemes(request.getSchemeIds() != null ? request.getSchemeIds() : new ArrayList<>());
        settings = settingsRepository.save(settings);
        return mapToResponse(settings);
    }

    @Override
    @Transactional
    public SettingsResponse updateLanguagePreference(UUID citizenId, String language) {
        CitizenSettings settings = getOrCreateSettings(citizenId);
        settings.setLanguagePreference(language);
        settings = settingsRepository.save(settings);
        return mapToResponse(settings);
    }

    @Override
    @Transactional
    public SettingsResponse updateThemePreference(UUID citizenId, String theme) {
        CitizenSettings settings = getOrCreateSettings(citizenId);
        settings.setThemePreference(theme);
        settings = settingsRepository.save(settings);
        return mapToResponse(settings);
    }

    @Override
    @Transactional
    public SettingsResponse updateTwoFactorEnabled(UUID citizenId, Boolean enabled) {
        CitizenSettings settings = getOrCreateSettings(citizenId);
        settings.setTwoFactorEnabled(enabled);
        settings = settingsRepository.save(settings);
        return mapToResponse(settings);
    }

    private CitizenSettings getOrCreateSettings(UUID citizenId) {
        return settingsRepository.findByCitizenId(citizenId)
                .orElseGet(() -> createDefaultSettings(citizenId));
    }

    private CitizenSettings createDefaultSettings(UUID citizenId) {
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen not found with id: " + citizenId));

        CitizenSettings settings = new CitizenSettings();
        settings.setCitizen(citizen);
        settings.setQuietHoursEnabled(false);
        settings.setQuietHoursStart(LocalTime.of(22, 0));
        settings.setQuietHoursEnd(LocalTime.of(8, 0));
        settings.setOptedOutSchemes(new ArrayList<>());
        settings.setLanguagePreference("en");
        settings.setThemePreference("light");
        settings.setTwoFactorEnabled(false);
        settings.setSessionTimeoutMinutes(30);

        // Default notification preferences
        try {
            Map<String, Map<String, Boolean>> defaultPrefs = new HashMap<>();
            defaultPrefs.put("applicationStatusUpdates", Map.of("email", true, "sms", true, "push", true, "inApp", true));
            defaultPrefs.put("paymentNotifications", Map.of("email", true, "sms", false, "push", true, "inApp", true));
            defaultPrefs.put("documentVerification", Map.of("email", true, "sms", true, "push", false, "inApp", true));
            defaultPrefs.put("schemeAnnouncements", Map.of("email", false, "sms", false, "push", true, "inApp", true));
            defaultPrefs.put("systemUpdates", Map.of("email", false, "sms", false, "push", false, "inApp", true));
            settings.setNotificationPreferences(objectMapper.valueToTree(defaultPrefs));
        } catch (Exception e) {
            log.error("Error creating default notification preferences", e);
        }

        return settingsRepository.save(settings);
    }

    private SettingsResponse mapToResponse(CitizenSettings settings) {
        return SettingsResponse.builder()
                .id(settings.getId())
                .citizenId(settings.getCitizen().getId())
                .notificationPreferences(settings.getNotificationPreferences())
                .quietHoursEnabled(settings.getQuietHoursEnabled())
                .quietHoursStart(settings.getQuietHoursStart())
                .quietHoursEnd(settings.getQuietHoursEnd())
                .optedOutSchemes(settings.getOptedOutSchemes())
                .languagePreference(settings.getLanguagePreference())
                .themePreference(settings.getThemePreference())
                .twoFactorEnabled(settings.getTwoFactorEnabled())
                .sessionTimeoutMinutes(settings.getSessionTimeoutMinutes())
                .build();
    }
}

