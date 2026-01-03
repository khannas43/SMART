package com.smart.citizen.dto.settings;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class OptOutRequest {
    private List<UUID> schemeIds;
}

