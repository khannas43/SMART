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
public class SchemeSearchResult {
    private UUID id;
    private String code;
    private String name;
    private String description;
    private String category;
    private String department;
    private String status;
}

