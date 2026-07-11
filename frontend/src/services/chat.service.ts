/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { apiClient } from '../lib/api-client';
import { ChatQueryResponse, ConversationItem, SessionMessagesResponse } from '../types';

export const chatService = {
  /**
   * Send a chat query to the backend
   */
  sendQuery: async (query: string, sessionId: string): Promise<ChatQueryResponse> => {
    const response = await apiClient.post<ChatQueryResponse>('/api/chat/query', {
      query,
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Get conversation history (list of sessions)
   */
  getHistory: async (): Promise<ConversationItem[]> => {
    const response = await apiClient.get<{ conversations: ConversationItem[] }>('/api/chat/history');
    return response.data.conversations;
  },

  /**
   * Get all messages for a specific session
   */
  getSessionMessages: async (sessionId: string): Promise<SessionMessagesResponse> => {
    const response = await apiClient.get<SessionMessagesResponse>(
      `/api/chat/messages?session_id=${encodeURIComponent(sessionId)}`
    );
    return response.data;
  },

  /**
   * Create a new conversation session
   */
  newConversation: async (): Promise<{ session_id: string }> => {
    const response = await apiClient.post<{ session_id: string }>('/api/chat/new', {});
    return response.data;
  },
};
