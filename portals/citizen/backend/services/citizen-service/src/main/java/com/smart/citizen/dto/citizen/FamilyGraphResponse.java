package com.smart.citizen.dto.citizen;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FamilyGraphResponse {
    private List<FamilyMember> members;
    private List<FamilyRelationship> relationships;
}

