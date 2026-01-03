package com.smart.citizen.dto.settings;

import lombok.Data;

@Data
public class QuietHoursRequest {
    private Boolean enabled = false;
    private String startTime; // Format: "HH:mm"
    private String endTime; // Format: "HH:mm"
}

