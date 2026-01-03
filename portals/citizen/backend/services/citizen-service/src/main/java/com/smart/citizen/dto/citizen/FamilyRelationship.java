package com.smart.citizen.dto.citizen;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FamilyRelationship {
    private UUID from;
    private UUID to;
    private String relationship;
    private Integer confidence;
}

