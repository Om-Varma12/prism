/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// ─── Navigation ───────────────────────────────────────────────────────────────

export enum Screen {
  LOGIN = 'LOGIN',
  DASHBOARD = 'DASHBOARD',
  CHAT = 'CHAT',
  NETWORK = 'NETWORK',
  ANALYTICS = 'ANALYTICS',
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface Alert {
  id: string;
  title: string;
  level: 'CRITICAL' | 'ELEVATED' | 'INFO';
  details: string;
  time: string;
  source: string;
}

// ─── Network Explorer ─────────────────────────────────────────────────────────

export interface SuspectConnection {
  name: string;
  type: 'ASSOC' | 'KIN';
  status: string;
}

export interface SuspectProfile {
  id: string;
  name: string;
  age: number;
  gender: string;
  riskScore: number;
  firsCount: number;
  districtsCount: number;
  connections: SuspectConnection[];
  recentCrime: string;
  status: string;
  bio?: string;
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export interface ClusterItem {
  id: string;
  name: string;
  change: string;
  location: string;
  incidents: number;
  rangeDays: number;
  primaryType: string;
  hourlyDistribution: number[];
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface ChatTableRow {
  firNo: string;
  crimeType: string;
  district: string;
  status: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  tableData?: ChatTableRow[];
  sqlQuery?: string;
  scannedRecords?: number;
  status?: string;
  sources?: string[];
}

export interface ChatEntity {
  name: string;
  type: string;
  detail: string;
}

export interface ChatQueryResponse {
  message_id: string;
  response_text: string;
  table_data: ChatTableRow[];
  sql_query: string;
  scanned_records: number;
  sources: string[];
  entities: ChatEntity[];
  follow_ups: string[];
  timestamp: string;
}

export interface ConversationItem {
  session_id: string;
  title: string;
  created_at: string;
  category: string;
}

export interface SessionMessage {
  role: 'user' | 'assistant';
  content: string;
  sql_generated?: string | null;
  created_at: string;
  table_data_json?: string | null;
  entities_json?: string | null;
  follow_ups_json?: string | null;
  sources_json?: string | null;
  scanned_records?: number | null;
}

export interface SessionMessagesResponse {
  session_id: string;
  messages: SessionMessage[];
}
