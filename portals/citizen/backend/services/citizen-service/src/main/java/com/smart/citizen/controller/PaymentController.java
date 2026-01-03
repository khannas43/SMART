package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.payment.PaymentRequest;
import com.smart.citizen.dto.payment.PaymentResponse;
import com.smart.citizen.service.PaymentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/payments")
@RequiredArgsConstructor
@Tag(name = "Payments", description = "API endpoints for payment processing and transaction management")
public class PaymentController {

    private final PaymentService paymentService;

    @Operation(summary = "Initiate payment", description = "Initiate a new payment transaction for a citizen. Can be associated with an application or standalone.")
    @PostMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PaymentResponse>> initiatePayment(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @Valid @RequestBody PaymentRequest request) {
        PaymentResponse response = paymentService.initiatePayment(citizenId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Payment initiated successfully", response));
    }

    @Operation(summary = "Get payment by ID", description = "Retrieve payment details by unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<PaymentResponse>> getPaymentById(
            @Parameter(description = "Payment unique identifier") @PathVariable UUID id) {
        PaymentResponse response = paymentService.getPaymentById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get payment by transaction ID", description = "Retrieve payment details by transaction ID (useful for payment gateway callbacks)")
    @GetMapping("/transaction/{transactionId}")
    public ResponseEntity<ApiResponse<PaymentResponse>> getPaymentByTransactionId(
            @Parameter(description = "Payment transaction ID") @PathVariable String transactionId) {
        PaymentResponse response = paymentService.getPaymentByTransactionId(transactionId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get payments by citizen", description = "Retrieve all payment transactions for a citizen with pagination support")
    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PagedResponse<PaymentResponse>>> getPaymentsByCitizenId(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "initiatedAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<PaymentResponse> paymentPage = paymentService.getPaymentsByCitizenId(citizenId, pageable);
        
        PagedResponse<PaymentResponse> pagedResponse = PagedResponse.<PaymentResponse>builder()
                .content(paymentPage.getContent())
                .page(paymentPage.getNumber())
                .size(paymentPage.getSize())
                .totalElements(paymentPage.getTotalElements())
                .totalPages(paymentPage.getTotalPages())
                .first(paymentPage.isFirst())
                .last(paymentPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Get payments by application", description = "Retrieve all payment transactions associated with a specific application")
    @GetMapping("/applications/{applicationId}")
    public ResponseEntity<ApiResponse<java.util.List<PaymentResponse>>> getPaymentsByApplicationId(
            @Parameter(description = "Application unique identifier") @PathVariable UUID applicationId) {
        java.util.List<PaymentResponse> response = paymentService.getPaymentsByApplicationId(applicationId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Update payment status", description = "Update payment status from payment gateway callback (typically called by payment gateway webhook)")
    @PatchMapping("/transaction/{transactionId}/status")
    public ResponseEntity<ApiResponse<PaymentResponse>> updatePaymentStatus(
            @Parameter(description = "Payment transaction ID") @PathVariable String transactionId,
            @Parameter(description = "Payment status (PENDING, PROCESSING, SUCCESS, FAILED, REFUNDED)") @RequestParam String status,
            @Parameter(description = "Gateway transaction ID from payment gateway") @RequestParam(required = false) String gatewayTransactionId,
            @Parameter(description = "Gateway response data (JSON)") @RequestBody(required = false) Object gatewayResponse) {
        PaymentResponse response = paymentService.updatePaymentStatus(transactionId, status, gatewayTransactionId, gatewayResponse);
        return ResponseEntity.ok(ApiResponse.success("Payment status updated successfully", response));
    }
}

