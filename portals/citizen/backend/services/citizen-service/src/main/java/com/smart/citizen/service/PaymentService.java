package com.smart.citizen.service;

import com.smart.citizen.dto.payment.PaymentRequest;
import com.smart.citizen.dto.payment.PaymentResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface PaymentService {
    PaymentResponse initiatePayment(UUID citizenId, PaymentRequest request);
    PaymentResponse getPaymentById(UUID id);
    PaymentResponse getPaymentByTransactionId(String transactionId);
    Page<PaymentResponse> getPaymentsByCitizenId(UUID citizenId, Pageable pageable);
    List<PaymentResponse> getPaymentsByApplicationId(UUID applicationId);
    PaymentResponse updatePaymentStatus(String transactionId, String status, String gatewayTransactionId, Object gatewayResponse);
}

