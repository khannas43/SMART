package com.smart.citizen.dto.payment;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentResponse {
    private UUID id;
    private UUID citizenId;
    private UUID applicationId;
    private String transactionId;
    private String paymentMethod;
    private BigDecimal amount;
    private String currency;
    private String status;
    private String paymentGateway;
    private Map<String, Object> gatewayResponse;
    private String gatewayTransactionId;
    private LocalDateTime initiatedAt;
    private LocalDateTime completedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

