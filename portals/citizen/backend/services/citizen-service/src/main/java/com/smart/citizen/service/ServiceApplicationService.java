package com.smart.citizen.service;

import com.smart.citizen.dto.application.ApplicationStatusHistoryResponse;
import com.smart.citizen.dto.application.ApplicationStatusUpdateRequest;
import com.smart.citizen.dto.application.ServiceApplicationRequest;
import com.smart.citizen.dto.application.ServiceApplicationResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface ServiceApplicationService {
    ServiceApplicationResponse createApplication(UUID citizenId, ServiceApplicationRequest request);
    ServiceApplicationResponse getApplicationById(UUID id);
    ServiceApplicationResponse getApplicationByNumber(String applicationNumber);
    Page<ServiceApplicationResponse> getApplicationsByCitizenId(UUID citizenId, Pageable pageable);
    List<ServiceApplicationResponse> getApplicationsByCitizenIdAndStatus(UUID citizenId, String status);
    Page<ServiceApplicationResponse> getApplicationsByStatus(String status, Pageable pageable);
    ServiceApplicationResponse updateApplicationStatus(UUID id, ApplicationStatusUpdateRequest request);
    ServiceApplicationResponse updateApplication(UUID id, ServiceApplicationRequest request);
    void deleteApplication(UUID id);
    List<ApplicationStatusHistoryResponse> getApplicationStatusHistory(UUID applicationId);
}

