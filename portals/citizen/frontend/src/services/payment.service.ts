import apiClient from './api';
import { ApiResponse, PagedResponse, Payment, PaymentRequest } from '@/types/api';

export const paymentService = {
  /**
   * Get all payments for a citizen (paginated)
   */
  getPaymentsByCitizen: async (
    citizenId: string,
    page: number = 0,
    size: number = 10
  ): Promise<PagedResponse<Payment>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<Payment>>>(
      `/payments/citizens/${citizenId}`,
      { params: { page, size } }
    );
    return response.data.data!;
  },

  /**
   * Get payments for an application
   */
  getPaymentsByApplication: async (applicationId: string): Promise<Payment[]> => {
    const response = await apiClient.get<ApiResponse<Payment[]>>(
      `/payments/applications/${applicationId}`
    );
    return response.data.data || [];
  },

  /**
   * Get payment by ID
   */
  getPaymentById: async (id: string): Promise<Payment> => {
    const response = await apiClient.get<ApiResponse<Payment>>(`/payments/${id}`);
    return response.data.data!;
  },

  /**
   * Get payment by transaction ID
   */
  getPaymentByTransactionId: async (transactionId: string): Promise<Payment> => {
    const response = await apiClient.get<ApiResponse<Payment>>(
      `/payments/transaction/${transactionId}`
    );
    return response.data.data!;
  },

  /**
   * Initiate a payment
   */
  initiatePayment: async (citizenId: string, data: PaymentRequest): Promise<Payment> => {
    const response = await apiClient.post<ApiResponse<Payment>>(
      `/payments/citizens/${citizenId}`,
      data
    );
    return response.data.data!;
  },
};

