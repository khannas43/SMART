package com.smart.citizen.service;

import com.smart.citizen.dto.search.SearchResult;

import java.util.UUID;

public interface SearchService {
    SearchResult searchAll(String query, UUID citizenId);
    SearchResult searchSchemes(String query);
    SearchResult searchApplications(String query, UUID citizenId);
    SearchResult searchDocuments(String query, UUID citizenId);
}

