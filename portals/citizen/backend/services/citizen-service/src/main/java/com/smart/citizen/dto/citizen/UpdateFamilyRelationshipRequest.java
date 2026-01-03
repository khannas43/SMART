package com.smart.citizen.dto.citizen;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Max;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for updating a single family relationship
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpdateFamilyRelationshipRequest {
    
    @NotBlank(message = "Related citizen Aadhaar number is required")
    private String relatedCitizenAadhaar;
    
    @NotBlank(message = "Relationship type is required")
    private String relationshipType; // SPOUSE, CHILD, PARENT, SIBLING, FAMILY_MEMBER
    
    @NotBlank(message = "Relationship label is required")
    private String relationshipLabel; // Spouse, Child, Parent, etc.
    
    @NotNull(message = "Confidence is required")
    @Min(value = 0, message = "Confidence must be between 0 and 100")
    @Max(value = 100, message = "Confidence must be between 0 and 100")
    private Integer confidence;
}

