package com.smart.citizen.dto.citizen;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * DTO for bulk updating multiple family relationships
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BulkUpdateFamilyRelationshipsRequest {
    
    @NotEmpty(message = "At least one relationship is required")
    @Valid
    private List<UpdateFamilyRelationshipRequest> relationships;
}

