package com.smart.citizen.dto.search;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApplicationSearchResult {
    private UUID id;
    private String applicationNumber;
    private String serviceType;
    private String subject;
    private String description;
    private String status;
    private String schemeName;
}

