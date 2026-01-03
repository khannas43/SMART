package com.smart.citizen.dto.settings;

import lombok.Data;

import java.util.Map;

@Data
public class NotificationPreferencesRequest {
    private Map<String, ChannelPreferences> preferences;
    private QuietHoursRequest quietHours;
}

