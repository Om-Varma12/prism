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
}
