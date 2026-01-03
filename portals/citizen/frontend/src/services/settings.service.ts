import apiClient from './api';
import { ApiResponse } from '@/types/api';

export interface SettingsResponse {
  id: string;
  citizenId: string;
  notificationPreferences: Record<string, any>;
  quietHoursEnabled: boolean;
  quietHoursStart?: string;
  quietHoursEnd?: string;
  optedOutSchemes: string[];
  languagePreference: string;
  themePreference: string;
  twoFactorEnabled: boolean;
  sessionTimeoutMinutes: number;
}

export interface NotificationPreferencesRequest {
  preferences?: Record<string, {
    email: boolean;
    sms: boolean;
    push: boolean;
    inApp: boolean;
  }>;
  quietHours?: {
    enabled: boolean;
    startTime: string;
    endTime: string;
  };
}

export interface OptOutRequest {
  schemeIds: string[];
}

export const settingsService = {
  /**
   * Get settings for a citizen
   */
  getSettings: async (citizenId: string): Promise<SettingsResponse> => {
    const response = await apiClient.get<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}`
    );
    return response.data.data!;
  },

  /**
   * Update notification preferences
   */
  updateNotificationPreferences: async (
    citizenId: string,
    data: NotificationPreferencesRequest
  ): Promise<SettingsResponse> => {
    const response = await apiClient.put<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}/notifications`,
      data
    );
    return response.data.data!;
  },

  /**
   * Update opt-out schemes
   */
  updateOptOutSchemes: async (
    citizenId: string,
    data: OptOutRequest
  ): Promise<SettingsResponse> => {
    const response = await apiClient.put<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}/opt-out`,
      data
    );
    return response.data.data!;
  },

  /**
   * Update language preference
   */
  updateLanguagePreference: async (
    citizenId: string,
    language: string
  ): Promise<SettingsResponse> => {
    const response = await apiClient.patch<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}/language?language=${language}`
    );
    return response.data.data!;
  },

  /**
   * Update theme preference
   */
  updateThemePreference: async (
    citizenId: string,
    theme: string
  ): Promise<SettingsResponse> => {
    const response = await apiClient.patch<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}/theme?theme=${theme}`
    );
    return response.data.data!;
  },

  /**
   * Update two-factor authentication
   */
  updateTwoFactorEnabled: async (
    citizenId: string,
    enabled: boolean
  ): Promise<SettingsResponse> => {
    const response = await apiClient.patch<ApiResponse<SettingsResponse>>(
      `/settings/citizens/${citizenId}/two-factor?enabled=${enabled}`
    );
    return response.data.data!;
  },
};

