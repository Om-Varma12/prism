/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { apiClient } from '../lib/api-client';
import { ChatQueryResponse, ConversationItem } from '../types';

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
   * Get conversation history
   */
  getHistory: async (): Promise<ConversationItem[]> => {
    const response = await apiClient.get<{ conversations: ConversationItem[] }>('/api/chat/history');
    return response.data.conversations;
  },

  /**
   * Create a new conversation session
   */
  newConversation: async (): Promise<{ session_id: string }> => {
    const response = await apiClient.post<{ session_id: string }>('/api/chat/new', {});
    return response.data;
  },
};
