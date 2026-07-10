/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { ChatMessage, ChatQueryResponse, ConversationItem } from '../types';
import { chatService } from '../services/chat.service';

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [history, setHistory] = useState<ConversationItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [latestResponse, setLatestResponse] = useState<ChatQueryResponse | null>(null);

  // Generate session ID on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const { session_id } = await chatService.newConversation();
        setActiveSessionId(session_id);
      } catch (error) {
        console.error('Failed to create new session:', error);
        // Fallback to a random UUID
        setActiveSessionId(crypto.randomUUID());
      }
    };
    initSession();
  }, []);

  /**
   * Send a message to the chat API
   */
  const sendMessage = async (text: string) => {
    if (!text.trim() || !activeSessionId) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Call API
      const response = await chatService.sendQuery(text, activeSessionId);

      // Convert ChatQueryResponse to ChatMessage
      const aiMessage: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: response.response_text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tableData: response.table_data,
        sqlQuery: response.sql_query,
        scannedRecords: response.scanned_records,
      };

      setMessages((prev) => [...prev, aiMessage]);
      setLatestResponse(response);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
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
   * Load conversation history
   */
  const loadHistory = async () => {
    try {
      const conversations = await chatService.getHistory();
      setHistory(conversations);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  /**
   * Start a new conversation
   */
  const startNewConversation = async () => {
    try {
      const { session_id } = await chatService.newConversation();
      setActiveSessionId(session_id);
      setMessages([]);
      setLatestResponse(null);
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  };

  /**
   * Select a specific conversation (placeholder)
   */
  const selectConversation = async (sessionId: string) => {
    // TODO: Implement loading specific conversation messages
    setActiveSessionId(sessionId);
    console.log('Selected conversation:', sessionId);
  };

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
