package com.smart.citizen.controller;

import com.smart.citizen.dto.ApiResponse;
import com.smart.citizen.dto.PagedResponse;
import com.smart.citizen.dto.notification.NotificationResponse;
import com.smart.citizen.service.NotificationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
@Tag(name = "Notifications", description = "API endpoints for managing notifications and alerts for citizens")
public class NotificationController {

    private final NotificationService notificationService;

    @Operation(summary = "Get notification by ID", description = "Retrieve a specific notification by its unique identifier")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<NotificationResponse>> getNotificationById(
            @Parameter(description = "Notification unique identifier") @PathVariable UUID id) {
        NotificationResponse response = notificationService.getNotificationById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get notifications by citizen", description = "Retrieve all notifications for a citizen with pagination support")
    @GetMapping("/citizens/{citizenId}")
    public ResponseEntity<ApiResponse<PagedResponse<NotificationResponse>>> getNotificationsByCitizenId(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("ASC") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<NotificationResponse> notificationPage = notificationService.getNotificationsByCitizenId(citizenId, pageable);
        
        PagedResponse<NotificationResponse> pagedResponse = PagedResponse.<NotificationResponse>builder()
                .content(notificationPage.getContent())
                .page(notificationPage.getNumber())
                .size(notificationPage.getSize())
                .totalElements(notificationPage.getTotalElements())
                .totalPages(notificationPage.getTotalPages())
                .first(notificationPage.isFirst())
                .last(notificationPage.isLast())
                .build();
        
        return ResponseEntity.ok(ApiResponse.success(pagedResponse));
    }

    @Operation(summary = "Get unread notifications", description = "Retrieve all unread notifications for a citizen")
    @GetMapping("/citizens/{citizenId}/unread")
    public ResponseEntity<ApiResponse<java.util.List<NotificationResponse>>> getUnreadNotifications(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        java.util.List<NotificationResponse> response = notificationService.getUnreadNotificationsByCitizenId(citizenId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "Get unread notification count", description = "Get the count of unread notifications for a citizen")
    @GetMapping("/citizens/{citizenId}/unread/count")
    public ResponseEntity<ApiResponse<Long>> getUnreadNotificationCount(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        Long count = notificationService.getUnreadNotificationCount(citizenId);
        return ResponseEntity.ok(ApiResponse.success(count));
    }

    @Operation(summary = "Mark notification as read", description = "Mark a specific notification as read")
    @PatchMapping("/{id}/read")
    public ResponseEntity<ApiResponse<Void>> markNotificationAsRead(
            @Parameter(description = "Notification unique identifier") @PathVariable UUID id) {
        notificationService.markNotificationAsRead(id);
        return ResponseEntity.ok(ApiResponse.success("Notification marked as read", null));
    }

    @Operation(summary = "Mark all notifications as read", description = "Mark all notifications for a citizen as read")
    @PatchMapping("/citizens/{citizenId}/read-all")
    public ResponseEntity<ApiResponse<Void>> markAllNotificationsAsRead(
            @Parameter(description = "Citizen unique identifier") @PathVariable UUID citizenId) {
        notificationService.markAllNotificationsAsRead(citizenId);
        return ResponseEntity.ok(ApiResponse.success("All notifications marked as read", null));
    }
}

