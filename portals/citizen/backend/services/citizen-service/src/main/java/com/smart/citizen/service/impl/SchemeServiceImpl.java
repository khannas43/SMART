package com.smart.citizen.service.impl;

import com.smart.citizen.dto.scheme.SchemeRequest;
import com.smart.citizen.dto.scheme.SchemeResponse;
import com.smart.citizen.entity.Scheme;
import com.smart.citizen.exception.BadRequestException;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.SchemeMapper;
import com.smart.citizen.repository.SchemeRepository;
import com.smart.citizen.service.SchemeService;
import com.smart.citizen.service.TransliterationService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class SchemeServiceImpl implements SchemeService {

    private final SchemeRepository schemeRepository;
    private final SchemeMapper schemeMapper;
    private final TransliterationService transliterationService;

    @Override
    public SchemeResponse createScheme(SchemeRequest request) {
        // Check if scheme code already exists
        if (schemeRepository.existsByCode(request.getCode())) {
            throw new BadRequestException("Scheme code already exists: " + request.getCode());
        }

        Scheme scheme = schemeMapper.toEntity(request);
        if (scheme.getStatus() == null) {
            scheme.setStatus(Scheme.SchemeStatus.ACTIVE);
        }
        
        // Auto-transliterate name and description to Hindi
        if (scheme.getName() != null && !scheme.getName().trim().isEmpty()) {
            String hindiName = transliterationService.transliterateToHindi(scheme.getName());
            scheme.setNameHindi(hindiName);
        }
        if (scheme.getDescription() != null && !scheme.getDescription().trim().isEmpty()) {
            String hindiDescription = transliterationService.transliterateToHindi(scheme.getDescription());
            scheme.setDescriptionHindi(hindiDescription);
        }
        
        Scheme savedScheme = schemeRepository.save(scheme);
        return schemeMapper.toResponse(savedScheme);
    }

    @Override
    @Transactional(readOnly = true)
    public SchemeResponse getSchemeById(UUID id) {
        Scheme scheme = schemeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Scheme", "id", id));
        return schemeMapper.toResponse(scheme);
    }

    @Override
    @Transactional(readOnly = true)
    public SchemeResponse getSchemeByCode(String code) {
        Scheme scheme = schemeRepository.findByCode(code)
                .orElseThrow(() -> new ResourceNotFoundException("Scheme", "code", code));
        return schemeMapper.toResponse(scheme);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<SchemeResponse> getAllSchemes(Pageable pageable) {
        return schemeRepository.findAll(pageable)
                .map(schemeMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public List<SchemeResponse> getActiveSchemes() {
        return schemeRepository.findAllActiveSchemes().stream()
                .map(schemeMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<SchemeResponse> getSchemesByCategory(String category) {
        return schemeRepository.findByCategory(category).stream()
                .map(schemeMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<SchemeResponse> getSchemesByDepartment(String department) {
        return schemeRepository.findByDepartment(department).stream()
                .map(schemeMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public SchemeResponse updateScheme(UUID id, SchemeRequest request) {
        Scheme scheme = schemeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Scheme", "id", id));
        
        // Check if code is being changed and if new code already exists
        if (!scheme.getCode().equals(request.getCode()) && schemeRepository.existsByCode(request.getCode())) {
            throw new BadRequestException("Scheme code already exists: " + request.getCode());
        }
        
        schemeMapper.updateEntityFromRequest(request, scheme);
        
        // Auto-transliterate name and description to Hindi if updated or if missing
        if (scheme.getName() != null && !scheme.getName().trim().isEmpty()) {
            // Update Hindi name if name was changed, or populate if missing
            if (request.getName() != null || scheme.getNameHindi() == null || scheme.getNameHindi().trim().isEmpty()) {
                String hindiName = transliterationService.transliterateToHindi(scheme.getName());
                scheme.setNameHindi(hindiName);
            }
        }
        if (scheme.getDescription() != null && !scheme.getDescription().trim().isEmpty()) {
            // Update Hindi description if description was changed, or populate if missing
            if (request.getDescription() != null || scheme.getDescriptionHindi() == null || scheme.getDescriptionHindi().trim().isEmpty()) {
                String hindiDescription = transliterationService.transliterateToHindi(scheme.getDescription());
                scheme.setDescriptionHindi(hindiDescription);
            }
        }
        
        Scheme updatedScheme = schemeRepository.save(scheme);
        return schemeMapper.toResponse(updatedScheme);
    }

    @Override
    public void deleteScheme(UUID id) {
        Scheme scheme = schemeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Scheme", "id", id));
        schemeRepository.delete(scheme);
    }

    @Override
    @Transactional
    public int populateHindiNamesForExistingSchemes() {
        // Find schemes that need Hindi names:
        // 1. Schemes without Hindi names (null or empty)
        // 2. Schemes with Hindi names that contain English letters (incomplete transliteration)
        List<Scheme> schemesNeedingHindi = schemeRepository.findAll().stream()
                .filter(scheme -> {
                    if (scheme.getName() == null || scheme.getName().trim().isEmpty()) {
                        return false;
                    }
                    // Check if Hindi name is missing or contains English letters
                    if (scheme.getNameHindi() == null || scheme.getNameHindi().trim().isEmpty()) {
                        return true;
                    }
                    // Check if Hindi name contains English letters (A-Z, a-z) - indicates incomplete transliteration
                    return scheme.getNameHindi().matches(".*[A-Za-z].*");
                })
                .collect(Collectors.toList());
        
        if (schemesNeedingHindi.isEmpty()) {
            return 0;
        }
        
        int updated = 0;
        for (Scheme scheme : schemesNeedingHindi) {
            try {
                String hindiName = transliterationService.transliterateToHindi(scheme.getName());
                scheme.setNameHindi(hindiName);
                
                if (scheme.getDescription() != null && !scheme.getDescription().trim().isEmpty()) {
                    // Also update description if it's missing or contains English letters
                    if (scheme.getDescriptionHindi() == null || scheme.getDescriptionHindi().trim().isEmpty() ||
                        scheme.getDescriptionHindi().matches(".*[A-Za-z].*")) {
                        String hindiDescription = transliterationService.transliterateToHindi(scheme.getDescription());
                        scheme.setDescriptionHindi(hindiDescription);
                    }
                }
                
                schemeRepository.save(scheme);
                updated++;
            } catch (Exception e) {
                // Log but continue with other schemes
                System.err.println("Failed to transliterate scheme " + scheme.getCode() + ": " + e.getMessage());
            }
        }
        
        return updated;
    }
}

