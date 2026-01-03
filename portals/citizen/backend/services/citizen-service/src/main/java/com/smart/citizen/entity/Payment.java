package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "payments", indexes = {
    @Index(name = "idx_payments_citizen", columnList = "citizen_id"),
    @Index(name = "idx_payments_application", columnList = "application_id"),
    @Index(name = "idx_payments_transaction_id", columnList = "transaction_id"),
    @Index(name = "idx_payments_status", columnList = "payment_status"),
    @Index(name = "idx_payments_date", columnList = "payment_date")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Payment extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, foreignKey = @ForeignKey(name = "fk_payment_citizen"))
    private Citizen citizen;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "application_id", foreignKey = @ForeignKey(name = "fk_payment_application"))
    private ServiceApplication application;

    @Column(name = "transaction_id", unique = true, nullable = false, length = 100)
    private String transactionId;

    @Column(name = "payment_method", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private PaymentMethod paymentMethod;

    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(name = "currency", length = 3)
    private String currency = "INR";

    @Column(name = "status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private PaymentStatus status;

    @Column(name = "payment_gateway", length = 50)
    private String paymentGateway;

    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.JSON)
    @Column(name = "gateway_response", columnDefinition = "jsonb")
    private java.util.Map<String, Object> gatewayResponse;

    @Column(name = "initiated_at")
    private LocalDateTime initiatedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column(name = "gateway_transaction_id", length = 100)
    private String gatewayTransactionId;


    public enum PaymentMethod {
        ONLINE, UPI, NET_BANKING, DEBIT_CARD, CREDIT_CARD, WALLET, CASH
    }

    public enum PaymentStatus {
        PENDING, PROCESSING, SUCCESS, FAILED, REFUNDED
    }
}

