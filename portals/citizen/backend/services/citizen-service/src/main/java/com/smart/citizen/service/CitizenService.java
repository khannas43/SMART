package com.smart.citizen.service;

import com.smart.citizen.dto.citizen.BulkUpdateFamilyRelationshipsRequest;
import com.smart.citizen.dto.citizen.ConsentPreferenceDto;
import com.smart.citizen.dto.citizen.CitizenRequest;
import com.smart.citizen.dto.citizen.CitizenResponse;
import com.smart.citizen.dto.citizen.CitizenUpdateRequest;
import com.smart.citizen.dto.citizen.FamilyGraphResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface CitizenService {
    CitizenResponse createCitizen(CitizenRequest request);
    CitizenResponse getCitizenById(UUID id);
    CitizenResponse getCitizenByMobileNumber(String mobileNumber);
    CitizenResponse getCitizenByAadhaarNumber(String aadhaarNumber);
    Page<CitizenResponse> getAllCitizens(Pageable pageable);
    List<CitizenResponse> getCitizensByStatus(String status);
    CitizenResponse updateCitizen(UUID id, CitizenUpdateRequest request);
    void deleteCitizen(UUID id);
    boolean existsByMobileNumber(String mobileNumber);
    boolean existsByAadhaarNumber(String aadhaarNumber);
    FamilyGraphResponse getFamilyRelationships(UUID citizenId, int depth);
    int updateFamilyRelationships(UUID citizenId, BulkUpdateFamilyRelationshipsRequest request);
    java.util.List<ConsentPreferenceDto> getConsentPreferences(UUID citizenId);
    java.util.List<ConsentPreferenceDto> updateConsentPreferences(UUID citizenId, java.util.List<ConsentPreferenceDto> preferences);
}

