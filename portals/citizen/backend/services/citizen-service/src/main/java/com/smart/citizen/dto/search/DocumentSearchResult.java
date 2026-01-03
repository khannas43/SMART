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
public class DocumentSearchResult {
    private UUID id;
    private String fileName;
    private String documentType;
    private String verificationStatus;
    private String applicationNumber;
}

