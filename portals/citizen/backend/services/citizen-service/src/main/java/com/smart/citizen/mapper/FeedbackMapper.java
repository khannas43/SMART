package com.smart.citizen.mapper;

import com.smart.citizen.dto.feedback.FeedbackRequest;
import com.smart.citizen.dto.feedback.FeedbackResponse;
import com.smart.citizen.entity.Feedback;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface FeedbackMapper {
    
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "citizen", ignore = true)
    @Mapping(target = "application", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "resolution", ignore = true)
    @Mapping(target = "resolvedAt", ignore = true)
    @Mapping(target = "resolvedBy", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    Feedback toEntity(FeedbackRequest request);
    
    @Mapping(source = "citizen.id", target = "citizenId")
    @Mapping(source = "application.id", target = "applicationId")
    FeedbackResponse toResponse(Feedback feedback);
}

