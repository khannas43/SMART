package com.smart.citizen.service;

import com.smart.citizen.dto.settings.NotificationPreferencesRequest;
import com.smart.citizen.dto.settings.OptOutRequest;
import com.smart.citizen.dto.settings.SettingsResponse;

import java.util.UUID;

public interface SettingsService {
    SettingsResponse getSettingsByCitizenId(UUID citizenId);
    SettingsResponse updateNotificationPreferences(UUID citizenId, NotificationPreferencesRequest request);
    SettingsResponse updateOptOutSchemes(UUID citizenId, OptOutRequest request);
    SettingsResponse updateLanguagePreference(UUID citizenId, String language);
    SettingsResponse updateThemePreference(UUID citizenId, String theme);
    SettingsResponse updateTwoFactorEnabled(UUID citizenId, Boolean enabled);
}

