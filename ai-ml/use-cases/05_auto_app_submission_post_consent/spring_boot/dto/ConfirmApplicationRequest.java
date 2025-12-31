package com.smart.platform.aiml.application.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Request to confirm and submit reviewed application
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ConfirmApplicationRequest {
    private Integer application_id;
    private String confirmed_by; // Citizen ID or session ID
    private String confirmation_method; // click, tap, otp, e_sign
}

