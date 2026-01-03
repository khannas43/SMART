package com.smart.citizen.mapper;

import com.smart.citizen.dto.notification.NotificationResponse;
import com.smart.citizen.entity.Notification;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface NotificationMapper {
    
    @Mapping(source = "citizen.id", target = "citizenId")
    @Mapping(source = "application.id", target = "applicationId")
    NotificationResponse toResponse(Notification notification);
}

