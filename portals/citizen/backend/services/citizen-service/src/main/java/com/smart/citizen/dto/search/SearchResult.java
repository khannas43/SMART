package com.smart.citizen.dto.search;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SearchResult {
    private List<SchemeSearchResult> schemes;
    private List<ApplicationSearchResult> applications;
    private List<DocumentSearchResult> documents;
    private Long totalResults;
}

