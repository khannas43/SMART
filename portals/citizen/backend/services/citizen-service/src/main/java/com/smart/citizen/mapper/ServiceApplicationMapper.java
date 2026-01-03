package com.smart.citizen.mapper;

import com.smart.citizen.dto.application.ServiceApplicationRequest;
import com.smart.citizen.dto.application.ServiceApplicationResponse;
import com.smart.citizen.entity.ServiceApplication;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

import java.util.UUID;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ServiceApplicationMapper {
    
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "applicationNumber", ignore = true)
    @Mapping(target = "citizen", ignore = true)
    @Mapping(target = "scheme", ignore = true)
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "submissionDate", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    ServiceApplication toEntity(ServiceApplicationRequest request);
    
    @Mapping(target = "citizenId", source = ".", qualifiedByName = "getCitizenId")
    @Mapping(target = "citizenName", source = ".", qualifiedByName = "getCitizenName")
    @Mapping(target = "schemeId", source = ".", qualifiedByName = "getSchemeId")
    @Mapping(target = "schemeName", source = ".", qualifiedByName = "getSchemeName")
    @Mapping(target = "schemeCode", source = ".", qualifiedByName = "getSchemeCode")
    @Mapping(source = "status", target = "status", qualifiedByName = "statusToString")
    @Mapping(source = "priority", target = "priority", qualifiedByName = "priorityToString")
    ServiceApplicationResponse toResponse(ServiceApplication application);
    
    @org.mapstruct.Named("getCitizenId")
    default UUID getCitizenId(ServiceApplication application) {
        return application.getCitizen() != null ? application.getCitizen().getId() : null;
    }
    
    @org.mapstruct.Named("getCitizenName")
    default String getCitizenName(ServiceApplication application) {
        return application.getCitizen() != null ? application.getCitizen().getFullName() : null;
    }
    
    @org.mapstruct.Named("getSchemeId")
    default UUID getSchemeId(ServiceApplication application) {
        return application.getScheme() != null ? application.getScheme().getId() : null;
    }
    
    @org.mapstruct.Named("getSchemeName")
    default String getSchemeName(ServiceApplication application) {
        return application.getScheme() != null ? application.getScheme().getName() : null;
    }
    
    @org.mapstruct.Named("getSchemeCode")
    default String getSchemeCode(ServiceApplication application) {
        return application.getScheme() != null ? application.getScheme().getCode() : null;
    }
    
    @org.mapstruct.Named("statusToString")
    default String statusToString(ServiceApplication.ApplicationStatus status) {
        return status != null ? status.name() : null;
    }
    
    @org.mapstruct.Named("priorityToString")
    default String priorityToString(ServiceApplication.Priority priority) {
        return priority != null ? priority.name() : null;
    }
}

