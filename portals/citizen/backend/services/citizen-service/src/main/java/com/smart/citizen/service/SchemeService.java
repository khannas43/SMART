package com.smart.citizen.service;

import com.smart.citizen.dto.scheme.SchemeRequest;
import com.smart.citizen.dto.scheme.SchemeResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface SchemeService {
    SchemeResponse createScheme(SchemeRequest request);
    SchemeResponse getSchemeById(UUID id);
    SchemeResponse getSchemeByCode(String code);
    Page<SchemeResponse> getAllSchemes(Pageable pageable);
    List<SchemeResponse> getActiveSchemes();
    List<SchemeResponse> getSchemesByCategory(String category);
    List<SchemeResponse> getSchemesByDepartment(String department);
    SchemeResponse updateScheme(UUID id, SchemeRequest request);
    void deleteScheme(UUID id);
    int populateHindiNamesForExistingSchemes();
}

