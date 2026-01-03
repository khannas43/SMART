import apiClient from './api';
import { ApiResponse, PagedResponse, Notification } from '@/types/api';

export const notificationService = {
  /**
   * Get all notifications for a citizen (paginated)
   */
  getNotificationsByCitizen: async (
    citizenId: string,
    page: number = 0,
    size: number = 10
  ): Promise<PagedResponse<Notification>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<Notification>>>(
      `/notifications/citizens/${citizenId}`,
      { params: { page, size } }
    );
    return response.data.data!;
  },

  /**
   * Get unread notifications for a citizen
   */
  getUnreadNotifications: async (citizenId: string): Promise<Notification[]> => {
    const response = await apiClient.get<ApiResponse<Notification[]>>(
      `/notifications/citizens/${citizenId}/unread`
    );
    return response.data.data || [];
  },

  /**
   * Get notification by ID
   */
  getNotificationById: async (id: string): Promise<Notification> => {
    const response = await apiClient.get<ApiResponse<Notification>>(`/notifications/${id}`);
    return response.data.data!;
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (id: string): Promise<void> => {
    await apiClient.patch(`/notifications/${id}/read`);
  },

  /**
   * Mark all notifications as read for a citizen
   */
  markAllAsRead: async (citizenId: string): Promise<void> => {
    await apiClient.patch(`/notifications/citizens/${citizenId}/read-all`);
  },

  /**
   * Get unread count for a citizen
   */
  getUnreadCount: async (citizenId: string): Promise<number> => {
    const response = await apiClient.get<ApiResponse<number>>(
      `/notifications/citizens/${citizenId}/unread/count`
    );
    return response.data.data || 0;
  },
};

