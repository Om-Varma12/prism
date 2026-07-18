/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef } from 'react';
import { ChatMessage, ChatQueryResponse, ConversationItem } from '../types';
import { useChatHistory, useSessionMessages, useNewConversation, useSendQuery } from './useChatQuery';

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [latestResponse, setLatestResponse] = useState<ChatQueryResponse | null>(null);

  // React Query hooks
  const { data: history = [] } = useChatHistory();
  const { data: sessionData } = useSessionMessages(activeSessionId);
  const newConversationMutation = useNewConversation();
  const sendQueryMutation = useSendQuery();

  // Track whether this session has been added to history yet
  const isNewSession = useRef(true);
  const isInitialized = useRef(false);

  // Generate session ID on mount
  useEffect(() => {
    const initSession = async () => {
      if (isInitialized.current) return;
      isInitialized.current = true;

      try {
        const { session_id } = await newConversationMutation.mutateAsync();
        setActiveSessionId(session_id);
        isNewSession.current = true;
      } catch (error) {
        console.error('Failed to create new session:', error);
        setActiveSessionId(crypto.randomUUID());
        isNewSession.current = true;
      }
    };
    initSession();
  }, []);

  /**
   * Send a message to the chat API
   */
  const sendMessage = async (text: string) => {
    const trimmedText = text.trim();
    if (!trimmedText) return;

    let sessionId = activeSessionId;
    if (!sessionId) {
      try {
        const created = await newConversationMutation.mutateAsync();
        sessionId = created.session_id;
        setActiveSessionId(sessionId);
        isNewSession.current = true;
      } catch (error) {
        console.error('Failed to create session before sending message:', error);
        sessionId = crypto.randomUUID();
        setActiveSessionId(sessionId);
        isNewSession.current = true;
      }
    }

    // Add user message optimistically
    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: trimmedText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await sendQueryMutation.mutateAsync({ query: trimmedText, sessionId });

      const aiMessage: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: response.response_text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tableData: response.table_data,
        sqlQuery: response.sql_query,
        scannedRecords: response.scanned_records,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, aiMessage]);
      setLatestResponse(response);

      // After the first message in a new session, refresh the sidebar
      if (isNewSession.current) {
        isNewSession.current = false;
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: `msg-error-${Date.now()}`,
        sender: 'ai',
        text: 'Failed to process your request. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Load conversation history list into the sidebar
   */
  const loadHistory = async () => {
    // History is automatically loaded by react-query hook
    // This function is kept for compatibility but no longer needed
  };

  /**
   * Start a brand-new conversation
   */
  const startNewConversation = async () => {
    try {
      const { session_id } = await newConversationMutation.mutateAsync();
      setActiveSessionId(session_id);
      setMessages([]);
      setLatestResponse(null);
      isNewSession.current = true;
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  };

  /**
   * Restore a previous conversation by loading its messages from the DB
   */
  const selectConversation = async (sessionId: string) => {
    if (sessionId === activeSessionId) return; // already active

    setActiveSessionId(sessionId);
    setMessages([]);
    setLatestResponse(null);
    isNewSession.current = false; // this session already exists in history

    // Messages will be loaded automatically by useSessionMessages hook
    // We need to wait for the data to be available
  };

  // Update messages when sessionData changes (from react-query)
  useEffect(() => {
    if (sessionData && sessionData.session_id === activeSessionId && sessionData.messages && activeSessionId) {
      const rows = sessionData.messages;
      
      const restored: ChatMessage[] = rows.map((row: any, idx: number) => {
        const message: ChatMessage = {
          id: `msg-restored-${idx}-${Date.now()}`,
          sender: row.role === 'user' ? 'user' : 'ai',
          text: row.content,
          timestamp: row.created_at
            ? new Date(row.created_at.replace(' ', 'T')).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })
            : '',
          sqlQuery: row.sql_generated ?? undefined,
        };

        // Restore table data if available
        if (row.table_data_json) {
          try {
            message.tableData = JSON.parse(row.table_data_json);
          } catch (e) {
            console.error('Failed to parse table_data_json:', e);
          }
        }

        // Restore sources if available
        if (row.sources_json) {
          try {
            message.sources = JSON.parse(row.sources_json);
          } catch (e) {
            console.error('Failed to parse sources_json:', e);
          }
        }

        // Restore scanned records if available
        if (row.scanned_records !== null && row.scanned_records !== undefined) {
          message.scannedRecords = row.scanned_records;
        }

        return message;
      });

      setMessages(restored);

      // Restore latestResponse from the last assistant message
      const lastAssistantMessage = rows.filter((r: any) => r.role === 'assistant').pop();
      if (lastAssistantMessage) {
        try {
          const latestResponseData: ChatQueryResponse = {
            message_id: '',
            response_text: lastAssistantMessage.content,
            table_data: lastAssistantMessage.table_data_json ? JSON.parse(lastAssistantMessage.table_data_json) : [],
            sql_query: lastAssistantMessage.sql_generated || '',
            scanned_records: lastAssistantMessage.scanned_records || 0,
            sources: lastAssistantMessage.sources_json ? JSON.parse(lastAssistantMessage.sources_json) : [],
            entities: lastAssistantMessage.entities_json ? JSON.parse(lastAssistantMessage.entities_json) : [],
            follow_ups: lastAssistantMessage.follow_ups_json ? JSON.parse(lastAssistantMessage.follow_ups_json) : [],
            timestamp: lastAssistantMessage.created_at,
          };
          setLatestResponse(latestResponseData);
        } catch (e) {
          console.error('Failed to restore latestResponse:', e);
        }
      }
    }
  }, [sessionData, activeSessionId]);

  return {
    messages,
    isTyping,
    history,
    activeSessionId,
    latestResponse,
    sendMessage,
    loadHistory,
    startNewConversation,
    selectConversation,
  };
};
