import apiClient from './api';
import { ApiResponse, PagedResponse, Scheme } from '@/types/api';

export const schemeService = {
  /**
   * Get all schemes (paginated)
   */
  getSchemes: async (
    page: number = 0,
    size: number = 10,
    status?: string,
    category?: string
  ): Promise<PagedResponse<Scheme>> => {
    const params: Record<string, any> = { page, size };
    if (status) params.status = status;
    if (category) params.category = category;

    const response = await apiClient.get<ApiResponse<PagedResponse<Scheme>>>('/schemes', {
      params,
    });
    return response.data.data!;
  },

  /**
   * Get scheme by ID
   */
  getSchemeById: async (id: string): Promise<Scheme> => {
    const response = await apiClient.get<ApiResponse<Scheme>>(`/schemes/${id}`);
    return response.data.data!;
  },

  /**
   * Get scheme by code
   */
  getSchemeByCode: async (code: string): Promise<Scheme> => {
    const response = await apiClient.get<ApiResponse<Scheme>>(`/schemes/code/${code}`);
    return response.data.data!;
  },
};

