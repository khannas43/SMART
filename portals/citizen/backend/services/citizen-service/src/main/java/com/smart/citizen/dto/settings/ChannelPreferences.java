package com.smart.citizen.dto.settings;

import lombok.Data;

@Data
public class ChannelPreferences {
    private Boolean email = true;
    private Boolean sms = false;
    private Boolean push = true;
    private Boolean inApp = true;
}

