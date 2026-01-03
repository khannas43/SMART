import apiClient from './api';
import { ApiResponse, Document } from '@/types/api';

export const documentService = {
  /**
   * Get all documents for a citizen
   */
  getDocumentsByCitizen: async (citizenId: string): Promise<Document[]> => {
    const response = await apiClient.get<ApiResponse<Document[]>>(
      `/documents/citizens/${citizenId}`
    );
    return response.data.data || [];
  },

  /**
   * Get documents for an application
   */
  getDocumentsByApplication: async (applicationId: string): Promise<Document[]> => {
    const response = await apiClient.get<ApiResponse<Document[]>>(
      `/documents/applications/${applicationId}`
    );
    return response.data.data || [];
  },

  /**
   * Get document by ID
   */
  getDocumentById: async (id: string): Promise<Document> => {
    const response = await apiClient.get<ApiResponse<Document>>(`/documents/${id}`);
    return response.data.data!;
  },

  /**
   * Upload a document
   */
  uploadDocument: async (
    citizenId: string,
    file: File,
    documentType: string,
    applicationId?: string
  ): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('documentType', documentType);
    if (applicationId) {
      formData.append('applicationId', applicationId);
    }

    const response = await apiClient.post<ApiResponse<Document>>(
      `/documents/citizens/${citizenId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data!;
  },

  /**
   * Download a document
   */
  downloadDocument: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Delete a document
   */
  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },

  /**
   * Update document verification status
   */
  updateVerificationStatus: async (
    id: string,
    status: string,
    notes?: string
  ): Promise<Document> => {
    const response = await apiClient.patch<ApiResponse<Document>>(
      `/documents/${id}/verification`,
      null,
      {
        params: {
          status,
          ...(notes && { notes }),
        },
      }
    );
    return response.data.data!;
  },
};

