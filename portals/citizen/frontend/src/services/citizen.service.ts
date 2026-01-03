import apiClient from './api';
import { ApiResponse, PagedResponse, User, CitizenRequest, CitizenUpdateRequest } from '@/types/api';

export const citizenService = {
  /**
   * Get current authenticated user profile
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>('/citizens/me');
    return response.data.data!;
  },

  /**
   * Get citizen by ID
   */
  getCitizenById: async (id: string): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>(`/citizens/${id}`);
    return response.data.data!;
  },

  /**
   * Get citizen by mobile number
   */
  getCitizenByMobile: async (mobile: string): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>(`/citizens/mobile/${mobile}`);
    return response.data.data!;
  },

  /**
   * Get all citizens (paginated)
   */
  getCitizens: async (page: number = 0, size: number = 10): Promise<PagedResponse<User>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<User>>>('/citizens', {
      params: { page, size },
    });
    return response.data.data!;
  },

  /**
   * Create a new citizen
   */
  createCitizen: async (data: CitizenRequest): Promise<User> => {
    const response = await apiClient.post<ApiResponse<User>>('/citizens', data);
    return response.data.data!;
  },

  /**
   * Update citizen profile
   */
  updateCitizen: async (id: string, data: CitizenUpdateRequest): Promise<User> => {
    const response = await apiClient.put<ApiResponse<User>>(`/citizens/${id}`, data);
    return response.data.data!;
  },

  /**
   * Delete citizen (soft delete - sets status to INACTIVE)
   */
  deleteCitizen: async (id: string): Promise<void> => {
    await apiClient.delete(`/citizens/${id}`);
  },

  /**
   * Get family relationships graph (AI-PLATFORM-02)
   */
  getFamilyRelationships: async (citizenId: string, depth: number = 3): Promise<import('@/types/api').FamilyGraphResponse> => {
    // TODO: Replace with actual API endpoint when AI-PLATFORM-02 is integrated
    // For now, return mock data
    const response = await apiClient.get<import('@/types/api').ApiResponse<import('@/types/api').FamilyGraphResponse>>(
      `/citizens/${citizenId}/family/relationships`,
      { params: { depth } }
    ).catch(() => {
      // Mock data if API doesn't exist yet
      return {
        data: {
          success: true,
          data: {
            members: [],
            relationships: [],
          },
        },
      };
    });
    return response.data.data || { members: [], relationships: [] };
  },

  /**
   * Get family benefit allocations (for Sankey diagram)
   */
  getFamilyBenefits: async (citizenId: string): Promise<import('@/types/api').BenefitAllocation[]> => {
    // TODO: Replace with actual API endpoint
    const response = await apiClient.get<import('@/types/api').ApiResponse<import('@/types/api').BenefitAllocation[]>>(
      `/citizens/${citizenId}/family/benefits`
    ).catch(() => {
      return { data: { success: true, data: [] } };
    });
    return response.data.data || [];
  },

  /**
   * Get consent preferences
   */
  getConsentPreferences: async (citizenId: string): Promise<import('@/types/api').ConsentPreference[]> => {
    const response = await apiClient.get<import('@/types/api').ApiResponse<import('@/types/api').ConsentPreference[]>>(
      `/citizens/${citizenId}/consent/preferences`
    ).catch(() => {
      return { data: { success: true, data: [] } };
    });
    return response.data.data || [];
  },

  /**
   * Update consent preferences
   */
  updateConsentPreferences: async (citizenId: string, preferences: import('@/types/api').ConsentPreference[]): Promise<void> => {
    await apiClient.put(`/citizens/${citizenId}/consent/preferences`, preferences);
  },

  /**
   * Get audit timeline (GR change history)
   */
  getAuditTimeline: async (citizenId: string): Promise<import('@/types/api').AuditEntry[]> => {
    const response = await apiClient.get<import('@/types/api').ApiResponse<import('@/types/api').AuditEntry[]>>(
      `/citizens/${citizenId}/audit/timeline`
    ).catch(() => {
      return { data: { success: true, data: [] } };
    });
    return response.data.data || [];
  },

  /**
   * Get ML-suggested relations
   */
  getMLSuggestedRelations: async (citizenId: string): Promise<import('@/types/api').MLSuggestedRelation[]> => {
    const response = await apiClient.get<import('@/types/api').ApiResponse<import('@/types/api').MLSuggestedRelation[]>>(
      `/citizens/${citizenId}/ml/suggested-relations`
    ).catch(() => {
      return { data: { success: true, data: [] } };
    });
    return response.data.data || [];
  },

  /**
   * Accept ML-suggested relation
   */
  acceptSuggestedRelation: async (citizenId: string, suggestionId: string): Promise<void> => {
    await apiClient.post(`/citizens/${citizenId}/ml/suggested-relations/${suggestionId}/accept`);
  },

  /**
   * Reject ML-suggested relation
   */
  rejectSuggestedRelation: async (citizenId: string, suggestionId: string): Promise<void> => {
    await apiClient.post(`/citizens/${citizenId}/ml/suggested-relations/${suggestionId}/reject`);
  },
};

