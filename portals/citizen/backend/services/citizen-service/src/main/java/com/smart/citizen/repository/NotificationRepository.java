package com.smart.citizen.repository;

import com.smart.citizen.entity.Notification;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Repository
public interface NotificationRepository extends JpaRepository<Notification, UUID> {

    List<Notification> findByCitizenId(UUID citizenId);

    Page<Notification> findByCitizenId(UUID citizenId, Pageable pageable);

    List<Notification> findByCitizenIdAndStatus(UUID citizenId, String status);

    @Query("SELECT n FROM Notification n WHERE n.citizen.id = :citizenId AND n.isRead = false ORDER BY n.createdAt DESC")
    List<Notification> findUnreadByCitizenId(@Param("citizenId") UUID citizenId);

    @Query("SELECT n FROM Notification n WHERE n.citizen.id = :citizenId ORDER BY n.createdAt DESC")
    List<Notification> findByCitizenIdOrderByCreatedAtDesc(@Param("citizenId") UUID citizenId);

    @Query("SELECT COUNT(n) FROM Notification n WHERE n.citizen.id = :citizenId AND n.isRead = false")
    Long countUnreadByCitizenId(@Param("citizenId") UUID citizenId);

    @Query("SELECT n FROM Notification n WHERE n.application.id = :applicationId ORDER BY n.createdAt DESC")
    List<Notification> findByApplicationId(@Param("applicationId") UUID applicationId);

    @Query("SELECT n FROM Notification n WHERE n.type = :type AND n.citizen.id = :citizenId")
    List<Notification> findByTypeAndCitizenId(@Param("type") String type, @Param("citizenId") UUID citizenId);

    @Modifying
    @Query("UPDATE Notification n SET n.isRead = true, n.readAt = :readAt WHERE n.id = :id")
    void markAsRead(@Param("id") UUID id, @Param("readAt") LocalDateTime readAt);

    @Modifying
    @Query("UPDATE Notification n SET n.isRead = true, n.readAt = :readAt WHERE n.citizen.id = :citizenId AND n.isRead = false")
    void markAllAsReadByCitizenId(@Param("citizenId") UUID citizenId, @Param("readAt") LocalDateTime readAt);

    @Query("SELECT n FROM Notification n WHERE n.createdAt >= :startDate AND n.createdAt <= :endDate")
    List<Notification> findByCreatedAtBetween(@Param("startDate") LocalDateTime startDate,
                                              @Param("endDate") LocalDateTime endDate);
}

