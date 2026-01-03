package com.smart.citizen.service.impl;

import com.smart.citizen.dto.payment.PaymentRequest;
import com.smart.citizen.dto.payment.PaymentResponse;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.Payment;
import com.smart.citizen.entity.ServiceApplication;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.PaymentMapper;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.PaymentRepository;
import com.smart.citizen.repository.ServiceApplicationRepository;
import com.smart.citizen.service.PaymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class PaymentServiceImpl implements PaymentService {

    private final PaymentRepository paymentRepository;
    private final CitizenRepository citizenRepository;
    private final ServiceApplicationRepository applicationRepository;
    private final PaymentMapper paymentMapper;

    @Override
    public PaymentResponse initiatePayment(UUID citizenId, PaymentRequest request) {
        // Validate citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        Payment payment = paymentMapper.toEntity(request);
        payment.setCitizen(citizen);
        payment.setStatus(Payment.PaymentStatus.PENDING);
        payment.setCurrency(request.getCurrency() != null ? request.getCurrency() : "INR");
        payment.setInitiatedAt(LocalDateTime.now());

        // Set application if provided
        if (request.getApplicationId() != null) {
            ServiceApplication application = applicationRepository.findById(request.getApplicationId())
                    .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", request.getApplicationId()));
            payment.setApplication(application);
        }

        // Generate transaction ID (in real implementation, use UUID or payment gateway)
        payment.setTransactionId("TXN-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());

        Payment savedPayment = paymentRepository.save(payment);
        return paymentMapper.toResponse(savedPayment);
    }

    @Override
    @Transactional(readOnly = true)
    public PaymentResponse getPaymentById(UUID id) {
        Payment payment = paymentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Payment", "id", id));
        return paymentMapper.toResponse(payment);
    }

    @Override
    @Transactional(readOnly = true)
    public PaymentResponse getPaymentByTransactionId(String transactionId) {
        Payment payment = paymentRepository.findByTransactionId(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException("Payment", "transactionId", transactionId));
        return paymentMapper.toResponse(payment);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<PaymentResponse> getPaymentsByCitizenId(UUID citizenId, Pageable pageable) {
        return paymentRepository.findByCitizenId(citizenId, pageable)
                .map(paymentMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public List<PaymentResponse> getPaymentsByApplicationId(UUID applicationId) {
        return paymentRepository.findByApplicationId(applicationId).stream()
                .map(paymentMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public PaymentResponse updatePaymentStatus(String transactionId, String status, String gatewayTransactionId, Object gatewayResponse) {
        Payment payment = paymentRepository.findByTransactionId(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException("Payment", "transactionId", transactionId));
        
        payment.setStatus(Payment.PaymentStatus.valueOf(status.toUpperCase()));
        if (gatewayTransactionId != null) {
            payment.setGatewayTransactionId(gatewayTransactionId);
        }
        if (gatewayResponse != null) {
            // Convert gatewayResponse to Map if needed
            if (gatewayResponse instanceof Map) {
                payment.setGatewayResponse((Map<String, Object>) gatewayResponse);
            }
        }
        payment.setCompletedAt(LocalDateTime.now());
        
        Payment updatedPayment = paymentRepository.save(payment);
        return paymentMapper.toResponse(updatedPayment);
    }
}

