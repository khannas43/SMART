package com.smart.citizen.repository;

import com.smart.citizen.entity.AuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, UUID> {

    List<AuditLog> findByEntityTypeAndEntityId(String entityType, UUID entityId);

    Page<AuditLog> findByEntityTypeAndEntityId(String entityType, UUID entityId, Pageable pageable);

    List<AuditLog> findByPerformedBy(UUID performedBy);

    List<AuditLog> findByPerformedByType(String performedByType);

    List<AuditLog> findByAction(String action);

    @Query("SELECT a FROM AuditLog a WHERE a.entityType = :entityType AND a.entityId = :entityId ORDER BY a.performedAt DESC")
    List<AuditLog> findByEntityTypeAndEntityIdOrderByPerformedAtDesc(@Param("entityType") String entityType,
                                                                      @Param("entityId") UUID entityId);

    @Query("SELECT a FROM AuditLog a WHERE a.performedBy = :performedBy ORDER BY a.performedAt DESC")
    List<AuditLog> findByPerformedByOrderByPerformedAtDesc(@Param("performedBy") UUID performedBy);

    @Query("SELECT a FROM AuditLog a WHERE a.performedAt >= :startDate AND a.performedAt <= :endDate")
    List<AuditLog> findByPerformedAtBetween(@Param("startDate") LocalDateTime startDate,
                                            @Param("endDate") LocalDateTime endDate);

    @Query("SELECT a FROM AuditLog a WHERE a.entityType = :entityType AND a.action = :action")
    List<AuditLog> findByEntityTypeAndAction(@Param("entityType") String entityType,
                                             @Param("action") String action);

    @Query("SELECT COUNT(a) FROM AuditLog a WHERE a.entityType = :entityType AND a.entityId = :entityId")
    Long countByEntityTypeAndEntityId(@Param("entityType") String entityType, @Param("entityId") UUID entityId);
}

