/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatService } from '../services/chat.service';
import { ChatQueryResponse, ConversationItem, SessionMessagesResponse } from '../types';

// Query keys for react-query cache
export const chatQueryKeys = {
  all: ['chat'] as const,
  history: () => [...chatQueryKeys.all, 'history'] as const,
  sessionMessages: (sessionId: string) => [...chatQueryKeys.all, 'session', sessionId] as const,
};

/**
 * Hook to fetch chat history (list of conversations)
 */
export const useChatHistory = () => {
  return useQuery({
    queryKey: chatQueryKeys.history(),
    queryFn: () => chatService.getHistory(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to fetch messages for a specific session
 */
export const useSessionMessages = (sessionId: string) => {
  return useQuery({
    queryKey: chatQueryKeys.sessionMessages(sessionId),
    queryFn: () => chatService.getSessionMessages(sessionId),
    enabled: !!sessionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to create a new conversation session
 */
export const useNewConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => chatService.newConversation(),
    onSuccess: () => {
      // Invalidate history query to refresh the list
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.history() });
    },
  });
};

/**
 * Hook to send a chat query
 */
export const useSendQuery = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ query, sessionId }: { query: string; sessionId: string }) =>
      chatService.sendQuery(query, sessionId),
    onSuccess: (_, { sessionId }) => {
      // Invalidate session messages query
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.sessionMessages(sessionId) });
      // Invalidate history query to refresh the list
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.history() });
    },
  });
};
