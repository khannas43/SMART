package com.smart.citizen.service;

import com.smart.citizen.dto.notification.NotificationResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface NotificationService {
    NotificationResponse getNotificationById(UUID id);
    Page<NotificationResponse> getNotificationsByCitizenId(UUID citizenId, Pageable pageable);
    List<NotificationResponse> getUnreadNotificationsByCitizenId(UUID citizenId);
    Long getUnreadNotificationCount(UUID citizenId);
    void markNotificationAsRead(UUID id);
    void markAllNotificationsAsRead(UUID citizenId);
}

