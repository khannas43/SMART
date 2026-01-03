import apiClient from './api';
import {
  ApiResponse,
  PagedResponse,
  ServiceApplication,
  ServiceApplicationRequest,
  ApplicationStatusHistory,
} from '@/types/api';

export const applicationService = {
  /**
   * Get all applications for a citizen (paginated)
   */
  getApplicationsByCitizen: async (
    citizenId: string,
    page: number = 0,
    size: number = 10,
    status?: string
  ): Promise<PagedResponse<ServiceApplication>> => {
    const params: Record<string, any> = { page, size };
    if (status) params.status = status;

    const response = await apiClient.get<ApiResponse<PagedResponse<ServiceApplication>>>(
      `/applications/citizens/${citizenId}`,
      { params }
    );
    return response.data.data!;
  },

  /**
   * Get application by ID
   */
  getApplicationById: async (id: string): Promise<ServiceApplication> => {
    const response = await apiClient.get<ApiResponse<ServiceApplication>>(`/applications/${id}`);
    return response.data.data!;
  },

  /**
   * Get application by application number
   */
  getApplicationByNumber: async (applicationNumber: string): Promise<ServiceApplication> => {
    const response = await apiClient.get<ApiResponse<ServiceApplication>>(
      `/applications/number/${applicationNumber}`
    );
    return response.data.data!;
  },

  /**
   * Create a new application
   */
  createApplication: async (citizenId: string, data: ServiceApplicationRequest): Promise<ServiceApplication> => {
    const response = await apiClient.post<ApiResponse<ServiceApplication>>(
      `/applications/citizens/${citizenId}`,
      data
    );
    return response.data.data!;
  },

  /**
   * Update application status
   */
  updateApplicationStatus: async (
    id: string,
    status: string,
    remarks?: string
  ): Promise<ServiceApplication> => {
    const response = await apiClient.put<ApiResponse<ServiceApplication>>(
      `/applications/${id}/status`,
      { status, remarks }
    );
    return response.data.data!;
  },

  /**
   * Get application status history/timeline
   */
  getApplicationStatusHistory: async (applicationId: string): Promise<ApplicationStatusHistory[]> => {
    try {
      const response = await apiClient.get<ApiResponse<ApplicationStatusHistory[]>>(
        `/applications/${applicationId}/history`
      );
      return response.data.data || [];
    } catch (err: any) {
      // If endpoint doesn't exist (404) or server error (500), return empty array
      // This allows the page to load even if history endpoint is not available
      if (err.response?.status === 404 || err.response?.status === 500) {
        console.warn('History endpoint not available, returning empty array');
        return [];
      }
      // For other errors, still return empty array to prevent page from breaking
      console.warn('Error fetching application history:', err);
      return [];
    }
  },
};

