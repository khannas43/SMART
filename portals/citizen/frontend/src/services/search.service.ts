import apiClient from './api';
import { ApiResponse } from '@/types/api';

export interface SchemeSearchResult {
  id: string;
  code: string;
  name: string;
  description?: string;
  category?: string;
  department?: string;
  status?: string;
}

export interface ApplicationSearchResult {
  id: string;
  applicationNumber: string;
  serviceType: string;
  subject?: string;
  description?: string;
  status?: string;
  schemeName?: string;
}

export interface DocumentSearchResult {
  id: string;
  fileName: string;
  documentType: string;
  verificationStatus?: string;
  applicationNumber?: string;
}

export interface SearchResult {
  schemes: SchemeSearchResult[];
  applications: ApplicationSearchResult[];
  documents: DocumentSearchResult[];
  totalResults: number;
}

export const searchService = {
  /**
   * Global search across all entities
   */
  searchAll: async (query: string, citizenId?: string): Promise<SearchResult> => {
    const params: any = { q: query };
    if (citizenId) {
      params.citizenId = citizenId;
    }
    const response = await apiClient.get<ApiResponse<SearchResult>>('/search', { params });
    return response.data.data!;
  },

  /**
   * Search only schemes
   */
  searchSchemes: async (query: string): Promise<SearchResult> => {
    const response = await apiClient.get<ApiResponse<SearchResult>>('/search/schemes', {
      params: { q: query },
    });
    return response.data.data!;
  },

  /**
   * Search only applications
   */
  searchApplications: async (query: string, citizenId: string): Promise<SearchResult> => {
    const response = await apiClient.get<ApiResponse<SearchResult>>('/search/applications', {
      params: { q: query, citizenId },
    });
    return response.data.data!;
  },

  /**
   * Search only documents
   */
  searchDocuments: async (query: string, citizenId: string): Promise<SearchResult> => {
    const response = await apiClient.get<ApiResponse<SearchResult>>('/search/documents', {
      params: { q: query, citizenId },
    });
    return response.data.data!;
  },
};

