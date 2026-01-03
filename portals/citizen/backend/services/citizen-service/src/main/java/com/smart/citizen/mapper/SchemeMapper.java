package com.smart.citizen.mapper;

import com.smart.citizen.dto.scheme.SchemeRequest;
import com.smart.citizen.dto.scheme.SchemeResponse;
import com.smart.citizen.entity.Scheme;
import org.mapstruct.Mapper;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface SchemeMapper {
    
    Scheme toEntity(SchemeRequest request);
    
    SchemeResponse toResponse(Scheme scheme);
    
    void updateEntityFromRequest(SchemeRequest request, @MappingTarget Scheme scheme);
}

