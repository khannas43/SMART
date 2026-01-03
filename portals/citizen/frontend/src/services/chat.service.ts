import apiClient from './api';
import { ApiResponse, PagedResponse } from '@/types/api';

export interface ChatMessage {
  id: string;
  conversationId: string;
  senderId: string;
  senderType: 'CITIZEN' | 'AGENT' | 'SYSTEM';
  message: string;
  timestamp: string;
  read: boolean;
  attachments?: ChatAttachment[];
}

export interface ChatAttachment {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  fileUrl: string;
}

export interface ChatConversation {
  id: string;
  citizenId: string;
  agentId?: string;
  subject?: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  createdAt: string;
  updatedAt: string;
  lastMessage?: ChatMessage;
  unreadCount: number;
}

export interface SendMessageRequest {
  message: string;
  conversationId?: string;
  subject?: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  attachments?: File[];
}

export interface CreateConversationRequest {
  subject: string;
  message: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  category?: string;
}

export const chatService = {
  /**
   * Get all conversations for a citizen (paginated)
   */
  getConversations: async (
    citizenId: string,
    page: number = 0,
    size: number = 20
  ): Promise<PagedResponse<ChatConversation>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<ChatConversation>>>(
      `/chat/conversations/citizens/${citizenId}`,
      { params: { page, size } }
    );
    return response.data.data!;
  },

  /**
   * Get conversation by ID
   */
  getConversation: async (conversationId: string): Promise<ChatConversation> => {
    const response = await apiClient.get<ApiResponse<ChatConversation>>(
      `/chat/conversations/${conversationId}`
    );
    return response.data.data!;
  },

  /**
   * Create a new conversation
   */
  createConversation: async (
    citizenId: string,
    data: CreateConversationRequest
  ): Promise<ChatConversation> => {
    const response = await apiClient.post<ApiResponse<ChatConversation>>(
      `/chat/conversations/citizens/${citizenId}`,
      data
    );
    return response.data.data!;
  },

  /**
   * Get messages for a conversation (paginated)
   */
  getMessages: async (
    conversationId: string,
    page: number = 0,
    size: number = 50
  ): Promise<PagedResponse<ChatMessage>> => {
    const response = await apiClient.get<ApiResponse<PagedResponse<ChatMessage>>>(
      `/chat/conversations/${conversationId}/messages`,
      { params: { page, size } }
    );
    return response.data.data!;
  },

  /**
   * Send a message
   */
  sendMessage: async (
    conversationId: string,
    data: { message: string; attachments?: File[] }
  ): Promise<ChatMessage> => {
    const formData = new FormData();
    formData.append('message', data.message);
    
    if (data.attachments && data.attachments.length > 0) {
      data.attachments.forEach((file) => {
        formData.append('attachments', file);
      });
    }

    const response = await apiClient.post<ApiResponse<ChatMessage>>(
      `/chat/conversations/${conversationId}/messages`,
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
   * Mark messages as read
   */
  markAsRead: async (conversationId: string, messageIds: string[]): Promise<void> => {
    await apiClient.patch(
      `/chat/conversations/${conversationId}/messages/read`,
      { messageIds }
    );
  },

  /**
   * Update conversation status
   */
  updateConversationStatus: async (
    conversationId: string,
    status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED'
  ): Promise<ChatConversation> => {
    const response = await apiClient.patch<ApiResponse<ChatConversation>>(
      `/chat/conversations/${conversationId}/status`,
      { status }
    );
    return response.data.data!;
  },

  /**
   * Get unread conversation count
   */
  getUnreadCount: async (citizenId: string): Promise<number> => {
    const response = await apiClient.get<ApiResponse<number>>(
      `/chat/conversations/citizens/${citizenId}/unread/count`
    );
    return response.data.data!;
  },
};

