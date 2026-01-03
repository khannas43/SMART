package com.smart.citizen.service.impl;

import com.smart.citizen.dto.application.ApplicationStatusHistoryResponse;
import com.smart.citizen.dto.application.ApplicationStatusUpdateRequest;
import com.smart.citizen.dto.application.ServiceApplicationRequest;
import com.smart.citizen.dto.application.ServiceApplicationResponse;
import com.smart.citizen.entity.ApplicationStatusHistory;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.Scheme;
import com.smart.citizen.entity.ServiceApplication;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.ServiceApplicationMapper;
import com.smart.citizen.repository.ApplicationStatusHistoryRepository;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.SchemeRepository;
import com.smart.citizen.repository.ServiceApplicationRepository;
import com.smart.citizen.service.ApplicationStatusNotificationService;
import com.smart.citizen.service.ServiceApplicationService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class ServiceApplicationServiceImpl implements ServiceApplicationService {

    private final ServiceApplicationRepository applicationRepository;
    private final CitizenRepository citizenRepository;
    private final SchemeRepository schemeRepository;
    private final ApplicationStatusHistoryRepository statusHistoryRepository;
    private final ApplicationStatusNotificationService notificationService;
    private final ServiceApplicationMapper applicationMapper;

    @Override
    public ServiceApplicationResponse createApplication(UUID citizenId, ServiceApplicationRequest request) {
        // Validate citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        ServiceApplication application = applicationMapper.toEntity(request);
        application.setCitizen(citizen);
        application.setStatus(ServiceApplication.ApplicationStatus.SUBMITTED);
        application.setSubmissionDate(LocalDateTime.now());

        // Set scheme if provided
        if (request.getSchemeId() != null) {
            Scheme scheme = schemeRepository.findById(request.getSchemeId())
                    .orElseThrow(() -> new ResourceNotFoundException("Scheme", "id", request.getSchemeId()));
            application.setScheme(scheme);
        }

        ServiceApplication savedApplication = applicationRepository.save(application);
        return applicationMapper.toResponse(savedApplication);
    }

    @Override
    @Transactional(readOnly = true)
    public ServiceApplicationResponse getApplicationById(UUID id) {
        ServiceApplication application = applicationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", id));
        return applicationMapper.toResponse(application);
    }

    @Override
    @Transactional(readOnly = true)
    public ServiceApplicationResponse getApplicationByNumber(String applicationNumber) {
        ServiceApplication application = applicationRepository.findByApplicationNumber(applicationNumber)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "applicationNumber", applicationNumber));
        return applicationMapper.toResponse(application);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ServiceApplicationResponse> getApplicationsByCitizenId(UUID citizenId, Pageable pageable) {
        // Fetch application IDs for the current page
        Page<UUID> applicationIdsPage = applicationRepository.findIdsByCitizenId(citizenId, pageable);

        // Fetch the actual applications with their relationships eagerly
        List<ServiceApplication> applicationsWithDetails = applicationRepository.findByIdInWithCitizenAndScheme(applicationIdsPage.getContent());

        // Map to DTOs
        List<ServiceApplicationResponse> content = applicationsWithDetails.stream()
                .map(applicationMapper::toResponse)
                .collect(Collectors.toList());

        // Reconstruct the Page object
        return new PageImpl<>(content, pageable, applicationIdsPage.getTotalElements());
    }

    @Override
    @Transactional(readOnly = true)
    public List<ServiceApplicationResponse> getApplicationsByCitizenIdAndStatus(UUID citizenId, String status) {
        ServiceApplication.ApplicationStatus applicationStatus = ServiceApplication.ApplicationStatus.valueOf(status.toUpperCase());
        return applicationRepository.findByCitizenIdAndStatus(citizenId, applicationStatus).stream()
                .map(applicationMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ServiceApplicationResponse> getApplicationsByStatus(String status, Pageable pageable) {
        ServiceApplication.ApplicationStatus applicationStatus = ServiceApplication.ApplicationStatus.valueOf(status.toUpperCase());
        return applicationRepository.findByStatus(applicationStatus, pageable)
                .map(applicationMapper::toResponse);
    }

    @Override
    public ServiceApplicationResponse updateApplicationStatus(UUID id, ApplicationStatusUpdateRequest request) {
        ServiceApplication application = applicationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", id));
        
        String fromStatus = application.getStatus().name();
        String toStatus = request.getStatus().toUpperCase();
        
        application.setStatus(ServiceApplication.ApplicationStatus.valueOf(toStatus));
        if (request.getCurrentStage() != null) {
            application.setCurrentStage(request.getCurrentStage());
        }
        
        ServiceApplication updatedApplication = applicationRepository.save(application);
        
        // Broadcast status update via WebSocket
        notificationService.broadcastStatusUpdate(
                updatedApplication.getId(),
                updatedApplication.getApplicationNumber(),
                fromStatus,
                toStatus,
                updatedApplication.getCurrentStage(),
                request.getComments()
        );
        
        // Notify the citizen who owns this application
        notificationService.notifyCitizen(
                updatedApplication.getCitizen().getId(),
                updatedApplication.getId(),
                updatedApplication.getApplicationNumber(),
                fromStatus,
                toStatus,
                updatedApplication.getCurrentStage(),
                request.getComments()
        );
        
        return applicationMapper.toResponse(updatedApplication);
    }

    @Override
    public ServiceApplicationResponse updateApplication(UUID id, ServiceApplicationRequest request) {
        ServiceApplication application = applicationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", id));
        
        // Update scheme if provided
        if (request.getSchemeId() != null) {
            Scheme scheme = schemeRepository.findById(request.getSchemeId())
                    .orElseThrow(() -> new ResourceNotFoundException("Scheme", "id", request.getSchemeId()));
            application.setScheme(scheme);
        }
        
        // Update other fields
        if (request.getServiceType() != null) {
            application.setServiceType(request.getServiceType());
        }
        if (request.getDescription() != null) {
            application.setDescription(request.getDescription());
        }
        // Add other field updates as needed
        
        ServiceApplication updatedApplication = applicationRepository.save(application);
        return applicationMapper.toResponse(updatedApplication);
    }

    @Override
    public void deleteApplication(UUID id) {
        ServiceApplication application = applicationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", id));
        applicationRepository.delete(application);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ApplicationStatusHistoryResponse> getApplicationStatusHistory(UUID applicationId) {
        // Verify application exists
        applicationRepository.findById(applicationId)
                .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", applicationId));

        List<ApplicationStatusHistory> history = statusHistoryRepository.findByApplicationIdOrderByChangedAtDesc(applicationId);
        
        return history.stream()
                .map(this::mapToHistoryResponse)
                .collect(Collectors.toList());
    }

    private ApplicationStatusHistoryResponse mapToHistoryResponse(ApplicationStatusHistory history) {
        return ApplicationStatusHistoryResponse.builder()
                .id(history.getId())
                .applicationId(history.getApplication().getId())
                .fromStatus(history.getFromStatus())
                .toStatus(history.getToStatus())
                .stage(history.getStage())
                .comments(history.getComments())
                .changedBy(history.getChangedBy())
                .changedByType(history.getChangedByType())
                .changedAt(history.getChangedAt())
                .createdAt(history.getCreatedAt())
                .updatedAt(history.getUpdatedAt())
                .build();
    }
}

