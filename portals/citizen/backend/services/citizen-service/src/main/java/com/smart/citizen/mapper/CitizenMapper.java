package com.smart.citizen.mapper;

import com.smart.citizen.dto.citizen.CitizenRequest;
import com.smart.citizen.dto.citizen.CitizenResponse;
import com.smart.citizen.dto.citizen.CitizenUpdateRequest;
import com.smart.citizen.entity.Citizen;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface CitizenMapper {
    
    Citizen toEntity(CitizenRequest request);
    
    CitizenResponse toResponse(Citizen citizen);
    
    void updateEntityFromRequest(CitizenUpdateRequest request, @MappingTarget Citizen citizen);
}

