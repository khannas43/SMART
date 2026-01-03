package com.smart.citizen.scheduler;

import com.smart.citizen.service.FamilyRelationshipSyncService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class FamilyRelationshipSyncScheduler {
    
    private final FamilyRelationshipSyncService syncService;
    
    @Value("${family-relationships.cache.cleanup-enabled:true}")
    private boolean cleanupEnabled;
    
    /**
     * Clean up expired cache entries daily at 2 AM
     */
    @Scheduled(cron = "0 0 2 * * *")
    public void cleanupExpiredCache() {
        if (!cleanupEnabled) {
            log.debug("Cache cleanup is disabled, skipping scheduled cleanup");
            return;
        }
        
        log.info("Starting scheduled cache cleanup...");
        try {
            int cleaned = syncService.cleanupExpiredCache();
            log.info("Scheduled cache cleanup completed. Removed {} expired entries", cleaned);
        } catch (Exception e) {
            log.error("Error during scheduled cache cleanup", e);
        }
    }
}

