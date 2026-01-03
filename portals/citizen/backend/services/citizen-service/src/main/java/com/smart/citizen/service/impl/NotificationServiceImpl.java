package com.smart.citizen.service.impl;

import com.smart.citizen.dto.notification.NotificationResponse;
import com.smart.citizen.entity.Notification;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.NotificationMapper;
import com.smart.citizen.repository.NotificationRepository;
import com.smart.citizen.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class NotificationServiceImpl implements NotificationService {

    private final NotificationRepository notificationRepository;
    private final NotificationMapper notificationMapper;

    @Override
    @Transactional(readOnly = true)
    public NotificationResponse getNotificationById(UUID id) {
        Notification notification = notificationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Notification", "id", id));
        return notificationMapper.toResponse(notification);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<NotificationResponse> getNotificationsByCitizenId(UUID citizenId, Pageable pageable) {
        return notificationRepository.findByCitizenId(citizenId, pageable)
                .map(notificationMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public List<NotificationResponse> getUnreadNotificationsByCitizenId(UUID citizenId) {
        return notificationRepository.findUnreadByCitizenId(citizenId).stream()
                .map(notificationMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public Long getUnreadNotificationCount(UUID citizenId) {
        return notificationRepository.countUnreadByCitizenId(citizenId);
    }

    @Override
    public void markNotificationAsRead(UUID id) {
        Notification notification = notificationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Notification", "id", id));
        notificationRepository.markAsRead(id, LocalDateTime.now());
    }

    @Override
    public void markAllNotificationsAsRead(UUID citizenId) {
        notificationRepository.markAllAsReadByCitizenId(citizenId, LocalDateTime.now());
    }
}

