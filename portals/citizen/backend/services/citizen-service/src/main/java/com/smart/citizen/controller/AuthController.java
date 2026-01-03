package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.security.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/auth")
@Tag(name = "Authentication", description = "Authentication endpoints for testing and token management")
@RequiredArgsConstructor
public class AuthController {

    private final JwtTokenProvider jwtTokenProvider;

    // Hardcoded OTP for testing - accepts 123456 for any Aadhaar number
    private static final String TEST_OTP = "123456";

    @PostMapping("/test-token")
    @Operation(
            summary = "Generate test JWT token",
            description = "Generates a JWT token for testing purposes. This endpoint should be removed or secured in production."
    )
    public ResponseEntity<ApiResponse<Map<String, String>>> generateTestToken(
            @Parameter(description = "Username or identifier for the token", required = true)
            @RequestParam(defaultValue = "test-user") String username
    ) {
        String token = jwtTokenProvider.generateToken(username);
        
        Map<String, String> responseData = new HashMap<>();
        responseData.put("token", token);
        responseData.put("tokenType", "Bearer");
        responseData.put("username", username);
        responseData.put("expiresIn", "24 hours");
        
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder()
                .success(true)
                .data(responseData)
                .message("Test token generated successfully. Use this token in the 'Authorize' button in Swagger UI.")
                .build());
    }

    @PostMapping("/verify-otp")
    @Operation(
            summary = "Verify OTP for Jan Aadhaar login",
            description = "Verifies OTP for Jan Aadhaar ID. For testing, OTP '123456' is accepted for any Aadhaar number."
    )
    public ResponseEntity<ApiResponse<Map<String, String>>> verifyOTP(
            @Parameter(description = "Jan Aadhaar ID (12 digits)", required = true)
            @RequestParam String janAadhaarId,
            @Parameter(description = "OTP code (6 digits)", required = true)
            @RequestParam String otp
    ) {
        // Validate Jan Aadhaar ID format (12 digits)
        if (janAadhaarId == null || !janAadhaarId.matches("^\\d{12}$")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error("Invalid Jan Aadhaar ID. Must be 12 digits."));
        }

        // Validate OTP format (6 digits)
        if (otp == null || !otp.matches("^\\d{6}$")) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error("Invalid OTP format. Must be 6 digits."));
        }

        // Hardcoded OTP validation for testing - accept 123456 for any Aadhaar
        if (!TEST_OTP.equals(otp)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid OTP. For testing, use OTP: 123456"));
        }

        // Generate JWT token with Jan Aadhaar ID as username
        String token = jwtTokenProvider.generateToken(janAadhaarId);
        
        Map<String, String> responseData = new HashMap<>();
        responseData.put("token", token);
        responseData.put("tokenType", "Bearer");
        responseData.put("username", janAadhaarId);
        responseData.put("expiresIn", "24 hours");
        
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder()
                .success(true)
                .data(responseData)
                .message("OTP verified successfully. Token generated.")
                .build());
    }
}

