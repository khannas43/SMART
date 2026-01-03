package com.smart.citizen.service.impl;

import com.smart.citizen.dto.search.ApplicationSearchResult;
import com.smart.citizen.dto.search.DocumentSearchResult;
import com.smart.citizen.dto.search.SchemeSearchResult;
import com.smart.citizen.dto.search.SearchResult;
import com.smart.citizen.entity.Document;
import com.smart.citizen.entity.Scheme;
import com.smart.citizen.entity.ServiceApplication;
import com.smart.citizen.repository.DocumentRepository;
import com.smart.citizen.repository.SchemeRepository;
import com.smart.citizen.repository.ServiceApplicationRepository;
import com.smart.citizen.service.SearchService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class SearchServiceImpl implements SearchService {

    private final SchemeRepository schemeRepository;
    private final ServiceApplicationRepository applicationRepository;
    private final DocumentRepository documentRepository;

    @Override
    @Transactional(readOnly = true)
    public SearchResult searchAll(String query, UUID citizenId) {
        if (query == null || query.trim().isEmpty()) {
            return SearchResult.builder()
                    .schemes(List.of())
                    .applications(List.of())
                    .documents(List.of())
                    .totalResults(0L)
                    .build();
        }

        String searchQuery = query.trim();

        // Search schemes (public, no citizen filter needed)
        List<Scheme> schemes = schemeRepository.searchActiveSchemes(searchQuery);
        List<SchemeSearchResult> schemeResults = schemes.stream()
                .map(this::mapToSchemeResult)
                .collect(Collectors.toList());

        // Search applications (citizen-specific)
        List<ServiceApplication> applications = citizenId != null
                ? applicationRepository.searchByCitizenId(citizenId, searchQuery)
                : List.of();
        List<ApplicationSearchResult> applicationResults = applications.stream()
                .map(this::mapToApplicationResult)
                .collect(Collectors.toList());

        // Search documents (citizen-specific)
        List<Document> documents = citizenId != null
                ? documentRepository.searchByCitizenId(citizenId, searchQuery)
                : List.of();
        List<DocumentSearchResult> documentResults = documents.stream()
                .map(this::mapToDocumentResult)
                .collect(Collectors.toList());

        long totalResults = schemeResults.size() + applicationResults.size() + documentResults.size();

        return SearchResult.builder()
                .schemes(schemeResults)
                .applications(applicationResults)
                .documents(documentResults)
                .totalResults(totalResults)
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public SearchResult searchSchemes(String query) {
        if (query == null || query.trim().isEmpty()) {
            return SearchResult.builder()
                    .schemes(List.of())
                    .applications(List.of())
                    .documents(List.of())
                    .totalResults(0L)
                    .build();
        }

        List<Scheme> schemes = schemeRepository.searchActiveSchemes(query.trim());
        List<SchemeSearchResult> schemeResults = schemes.stream()
                .map(this::mapToSchemeResult)
                .collect(Collectors.toList());

        return SearchResult.builder()
                .schemes(schemeResults)
                .applications(List.of())
                .documents(List.of())
                .totalResults((long) schemeResults.size())
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public SearchResult searchApplications(String query, UUID citizenId) {
        if (query == null || query.trim().isEmpty() || citizenId == null) {
            return SearchResult.builder()
                    .schemes(List.of())
                    .applications(List.of())
                    .documents(List.of())
                    .totalResults(0L)
                    .build();
        }

        List<ServiceApplication> applications = applicationRepository.searchByCitizenId(citizenId, query.trim());
        List<ApplicationSearchResult> applicationResults = applications.stream()
                .map(this::mapToApplicationResult)
                .collect(Collectors.toList());

        return SearchResult.builder()
                .schemes(List.of())
                .applications(applicationResults)
                .documents(List.of())
                .totalResults((long) applicationResults.size())
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public SearchResult searchDocuments(String query, UUID citizenId) {
        if (query == null || query.trim().isEmpty() || citizenId == null) {
            return SearchResult.builder()
                    .schemes(List.of())
                    .applications(List.of())
                    .documents(List.of())
                    .totalResults(0L)
                    .build();
        }

        List<Document> documents = documentRepository.searchByCitizenId(citizenId, query.trim());
        List<DocumentSearchResult> documentResults = documents.stream()
                .map(this::mapToDocumentResult)
                .collect(Collectors.toList());

        return SearchResult.builder()
                .schemes(List.of())
                .applications(List.of())
                .documents(documentResults)
                .totalResults((long) documentResults.size())
                .build();
    }

    private SchemeSearchResult mapToSchemeResult(Scheme scheme) {
        return SchemeSearchResult.builder()
                .id(scheme.getId())
                .code(scheme.getCode())
                .name(scheme.getName())
                .description(scheme.getDescription())
                .category(scheme.getCategory())
                .department(scheme.getDepartment())
                .status(scheme.getStatus() != null ? scheme.getStatus().name() : null)
                .build();
    }

    private ApplicationSearchResult mapToApplicationResult(ServiceApplication application) {
        return ApplicationSearchResult.builder()
                .id(application.getId())
                .applicationNumber(application.getApplicationNumber())
                .serviceType(application.getServiceType())
                .subject(application.getSubject())
                .description(application.getDescription())
                .status(application.getStatus() != null ? application.getStatus().name() : null)
                .schemeName(application.getScheme() != null ? application.getScheme().getName() : null)
                .build();
    }

    private DocumentSearchResult mapToDocumentResult(Document document) {
        return DocumentSearchResult.builder()
                .id(document.getId())
                .fileName(document.getDocumentName())
                .documentType(document.getDocumentType())
                .verificationStatus(document.getVerificationStatus() != null ? document.getVerificationStatus().name() : null)
                .applicationNumber(document.getApplication() != null ? document.getApplication().getApplicationNumber() : null)
                .build();
    }
}

