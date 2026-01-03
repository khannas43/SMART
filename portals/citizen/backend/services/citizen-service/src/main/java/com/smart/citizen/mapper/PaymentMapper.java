package com.smart.citizen.mapper;

import com.smart.citizen.dto.payment.PaymentRequest;
import com.smart.citizen.dto.payment.PaymentResponse;
import com.smart.citizen.entity.Payment;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface PaymentMapper {
    
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "transactionId", ignore = true)
    @Mapping(target = "citizen", ignore = true)
    @Mapping(target = "application", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "paymentGateway", ignore = true)
    @Mapping(target = "gatewayResponse", ignore = true)
    @Mapping(target = "gatewayTransactionId", ignore = true)
    @Mapping(target = "initiatedAt", ignore = true)
    @Mapping(target = "completedAt", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    Payment toEntity(PaymentRequest request);
    
    @Mapping(source = "citizen.id", target = "citizenId")
    @Mapping(source = "application.id", target = "applicationId")
    @Mapping(source = "status", target = "status")
    PaymentResponse toResponse(Payment payment);
}

