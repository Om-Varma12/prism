/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export enum Screen {
  LOGIN = 'LOGIN',
  CHAT = 'CHAT',
  NETWORK = 'NETWORK',
  DASHBOARD = 'DASHBOARD',
  ANALYTICS = 'ANALYTICS'
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  tableData?: {
    firNo: string;
    crimeType: string;
    district: string;
    status: 'ACTIVE' | 'INVESTIGATION' | 'CLOSED';
  }[];
  sqlQuery?: string;
  scannedRecords?: number;
}

export interface Alert {
  id: string;
  title: string;
  level: 'CRITICAL' | 'ELEVATED' | 'INFO';
  details: string;
  time: string;
  source: string;
}

export interface Connection {
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
  connections: Connection[];
  recentCrime: string;
  status: 'HIGH-RISK' | 'MONITORED' | 'ACTIVE';
  bio?: string;
}

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
