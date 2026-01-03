package com.smart.citizen.scheduler;

import com.smart.citizen.entity.Scheme;
import com.smart.citizen.repository.SchemeRepository;
import com.smart.citizen.service.TransliterationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Scheduled task to populate Hindi names for existing schemes that don't have them
 * Runs daily at 10 AM
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class SchemeTransliterationScheduler {

    private final SchemeRepository schemeRepository;
    private final TransliterationService transliterationService;

    @Scheduled(cron = "0 0 10 * * ?") // Run daily at 10 AM
    @Transactional
    public void populateMissingHindiNames() {
        log.info("Starting scheduled task to populate Hindi names for schemes");
        
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
                .toList();
        
        if (schemesNeedingHindi.isEmpty()) {
            log.info("No schemes found needing Hindi name updates");
            return;
        }
        
        log.info("Found {} schemes needing Hindi name updates, populating...", schemesNeedingHindi.size());
        
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
                log.debug("Updated scheme {} with Hindi name: {}", scheme.getCode(), hindiName);
            } catch (Exception e) {
                log.warn("Failed to transliterate scheme {}: {}", scheme.getCode(), e.getMessage());
            }
        }
        
        log.info("Completed: Updated {} schemes with Hindi names", updated);
    }
}

