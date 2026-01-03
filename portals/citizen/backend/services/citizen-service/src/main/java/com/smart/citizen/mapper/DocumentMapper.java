package com.smart.citizen.mapper;

import com.smart.citizen.dto.document.DocumentRequest;
import com.smart.citizen.dto.document.DocumentResponse;
import com.smart.citizen.entity.Document;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface DocumentMapper {
    
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "citizen", ignore = true)
    @Mapping(target = "application", ignore = true)
    @Mapping(target = "verificationStatus", ignore = true)
    @Mapping(target = "uploadedAt", ignore = true)
    @Mapping(target = "fileHash", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    Document toEntity(DocumentRequest request);
    
    @Mapping(source = "citizen.id", target = "citizenId")
    @Mapping(source = "application.id", target = "applicationId")
    DocumentResponse toResponse(Document document);
}

