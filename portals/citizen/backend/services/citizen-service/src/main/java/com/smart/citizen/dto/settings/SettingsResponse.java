package com.smart.citizen.dto.settings;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalTime;
import java.util.List;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SettingsResponse {
    private UUID id;
    private UUID citizenId;
    private JsonNode notificationPreferences;
    private Boolean quietHoursEnabled;
    private LocalTime quietHoursStart;
    private LocalTime quietHoursEnd;
    private List<UUID> optedOutSchemes;
    private String languagePreference;
    private String themePreference;
    private Boolean twoFactorEnabled;
    private Integer sessionTimeoutMinutes;
}

