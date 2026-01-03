import apiClient from './api';
import { ApiResponse, PagedResponse, Feedback, FeedbackRequest } from '@/types/api';

export const feedbackService = {
  /**
   * Get all feedback for a citizen (paginated)
   */
  getFeedbackByCitizen: async (
    citizenId: string,
    page: number = 0,
    size: number = 10
  ): Promise<PagedResponse<Feedback>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<Feedback>>>(
      `/feedback/citizens/${citizenId}`,
      { params: { page, size } }
    );
    return response.data.data!;
  },

  /**
   * Get feedback by ID
   */
  getFeedbackById: async (id: string): Promise<Feedback> => {
    const response = await apiClient.get<ApiResponse<Feedback>>(`/feedback/${id}`);
    return response.data.data!;
  },

  /**
   * Submit feedback
   */
  submitFeedback: async (citizenId: string, data: FeedbackRequest): Promise<Feedback> => {
    const response = await apiClient.post<ApiResponse<Feedback>>(
      `/feedback/citizens/${citizenId}`,
      data
    );
    return response.data.data!;
  },
};

