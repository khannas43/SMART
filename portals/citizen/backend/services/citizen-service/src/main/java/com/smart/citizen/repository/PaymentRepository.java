package com.smart.citizen.repository;

import com.smart.citizen.entity.Payment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, UUID> {

    Optional<Payment> findByTransactionId(String transactionId);

    List<Payment> findByCitizenId(UUID citizenId);

    Page<Payment> findByCitizenId(UUID citizenId, Pageable pageable);

    List<Payment> findByApplicationId(UUID applicationId);

    List<Payment> findByStatus(Payment.PaymentStatus status);

    List<Payment> findByCitizenIdAndStatus(UUID citizenId, Payment.PaymentStatus status);

    @Query("SELECT p FROM Payment p WHERE p.citizen.id = :citizenId ORDER BY p.initiatedAt DESC")
    List<Payment> findByCitizenIdOrderByInitiatedAtDesc(@Param("citizenId") UUID citizenId);

    @Query("SELECT p FROM Payment p WHERE p.paymentMethod = :paymentMethod AND p.status = :status")
    List<Payment> findByPaymentMethodAndStatus(@Param("paymentMethod") Payment.PaymentMethod paymentMethod,
                                               @Param("status") Payment.PaymentStatus status);

    @Query("SELECT p FROM Payment p WHERE p.initiatedAt >= :startDate AND p.initiatedAt <= :endDate")
    List<Payment> findByInitiatedAtBetween(@Param("startDate") LocalDateTime startDate,
                                           @Param("endDate") LocalDateTime endDate);

    @Query("SELECT SUM(p.amount) FROM Payment p WHERE p.citizen.id = :citizenId AND p.status = 'SUCCESS'")
    BigDecimal sumSuccessfulPaymentsByCitizenId(@Param("citizenId") UUID citizenId);

    @Query("SELECT COUNT(p) FROM Payment p WHERE p.citizen.id = :citizenId AND p.status = :status")
    Long countByCitizenIdAndStatus(@Param("citizenId") UUID citizenId, @Param("status") Payment.PaymentStatus status);

    @Query("SELECT p FROM Payment p WHERE p.gatewayTransactionId = :gatewayTransactionId")
    Optional<Payment> findByGatewayTransactionId(@Param("gatewayTransactionId") String gatewayTransactionId);

    boolean existsByTransactionId(String transactionId);
}

