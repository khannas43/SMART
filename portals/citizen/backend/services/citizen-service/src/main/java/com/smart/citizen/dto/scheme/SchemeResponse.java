package com.smart.citizen.dto.scheme;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SchemeResponse {
    private UUID id;
    private String code;
    private String name;
    private String nameHindi;
    private String description;
    private String descriptionHindi;
    private String category;
    private String department;
    private Map<String, Object> eligibilityCriteria;
    private LocalDate startDate;
    private LocalDate endDate;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

