package com.smart.citizen.repository;

import com.smart.citizen.entity.ApplicationStatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ApplicationStatusHistoryRepository extends JpaRepository<ApplicationStatusHistory, UUID> {

    List<ApplicationStatusHistory> findByApplicationId(UUID applicationId);

    @Query("SELECT h FROM ApplicationStatusHistory h WHERE h.application.id = :applicationId ORDER BY h.changedAt DESC")
    List<ApplicationStatusHistory> findByApplicationIdOrderByChangedAtDesc(@Param("applicationId") UUID applicationId);

    @Query("SELECT h FROM ApplicationStatusHistory h WHERE h.application.id = :applicationId AND h.toStatus = :status")
    List<ApplicationStatusHistory> findByApplicationIdAndToStatus(@Param("applicationId") UUID applicationId,
                                                                  @Param("status") String status);

    @Query("SELECT h FROM ApplicationStatusHistory h WHERE h.changedBy = :changedBy ORDER BY h.changedAt DESC")
    List<ApplicationStatusHistory> findByChangedBy(@Param("changedBy") UUID changedBy);

    @Query("SELECT h FROM ApplicationStatusHistory h WHERE h.changedByType = :changedByType ORDER BY h.changedAt DESC")
    List<ApplicationStatusHistory> findByChangedByType(@Param("changedByType") String changedByType);

    @Query("SELECT h FROM ApplicationStatusHistory h WHERE h.application.id = :applicationId AND h.fromStatus = :fromStatus AND h.toStatus = :toStatus")
    List<ApplicationStatusHistory> findByApplicationIdAndStatusTransition(@Param("applicationId") UUID applicationId,
                                                                          @Param("fromStatus") String fromStatus,
                                                                          @Param("toStatus") String toStatus);
}

