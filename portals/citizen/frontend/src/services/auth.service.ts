import apiClient from './api';
import { ApiResponse, TestTokenResponse } from '@/types/api';

export const authService = {
  /**
   * Generate a test JWT token for testing purposes
   * @param username - Username for the token (default: "test-user")
   */
  getTestToken: async (username: string = 'test-user'): Promise<TestTokenResponse> => {
    const response = await apiClient.post<ApiResponse<TestTokenResponse>>(
      '/auth/test-token',
      null,
      {
        params: { username },
      }
    );
    return response.data.data!;
  },

  /**
   * Verify OTP for Jan Aadhaar login
   * @param janAadhaarId - 12-digit Jan Aadhaar ID
   * @param otp - 6-digit OTP (for testing, use: 123456)
   */
  verifyOTP: async (janAadhaarId: string, otp: string): Promise<TestTokenResponse> => {
    const response = await apiClient.post<ApiResponse<TestTokenResponse>>(
      '/auth/verify-otp',
      null,
      {
        params: { 
          janAadhaarId,
          otp,
        },
      }
    );
    return response.data.data!;
  },
};

