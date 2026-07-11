/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef } from 'react';
import { ChatMessage, ChatQueryResponse, ConversationItem } from '../types';
import { chatService } from '../services/chat.service';

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [history, setHistory] = useState<ConversationItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [latestResponse, setLatestResponse] = useState<ChatQueryResponse | null>(null);

  // Track whether this session has been added to history yet
  const isNewSession = useRef(true);

  // Generate session ID on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const { session_id } = await chatService.newConversation();
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
    if (!text.trim() || !activeSessionId) return;

    // Add user message optimistically
    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await chatService.sendQuery(text, activeSessionId);

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
        setTimeout(() => loadHistory(), 800); // small delay for DB write to commit
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
    try {
      const conversations = await chatService.getHistory();
      setHistory(conversations);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  /**
   * Start a brand-new conversation
   */
  const startNewConversation = async () => {
    try {
      const { session_id } = await chatService.newConversation();
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

    try {
      const { messages: rows } = await chatService.getSessionMessages(sessionId);

      const restored: ChatMessage[] = rows.map((row, idx) => ({
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
      }));

      setMessages(restored);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
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
