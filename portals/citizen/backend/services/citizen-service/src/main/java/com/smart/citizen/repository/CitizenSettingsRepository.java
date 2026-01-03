package com.smart.citizen.repository;

import com.smart.citizen.entity.CitizenSettings;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface CitizenSettingsRepository extends JpaRepository<CitizenSettings, UUID> {
    Optional<CitizenSettings> findByCitizenId(UUID citizenId);
}

