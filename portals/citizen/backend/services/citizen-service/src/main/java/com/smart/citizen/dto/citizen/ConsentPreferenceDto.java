package com.smart.citizen.dto.citizen;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for consent preferences
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConsentPreferenceDto {
    private String field;
    private String fieldLabel;
    private Boolean enabled;
    private String source;
}

