/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Alert, SuspectProfile, ClusterItem, ChatMessage } from '../types';

export const INITIAL_ALERTS: Alert[] = [
  {
    id: 'AL-001',
    title: 'Robbery spike — Bengaluru North',
    level: 'CRITICAL',
    details: '340% above 90-day average',
    time: '2h ago',
    source: 'Automated Trigger'
  },
  {
    id: 'AL-002',
    title: 'Suspect Vehicle Sighted — Mysuru',
    level: 'ELEVATED',
    details: 'Match: KA-09-XX-9832 (94% conf)',
    time: '4h ago',
    source: 'ANPR Node 42'
  },
  {
    id: 'AL-003',
    title: 'Assault Cluster — Hubballi',
    level: 'ELEVATED',
    details: '6 incidents in 12h radius',
    time: '7h ago',
    source: 'NLP Analysis'
  },
  {
    id: 'AL-004',
    title: 'Intel Report: Illegal Arms Sighting',
    level: 'INFO',
    details: 'Srinivaspur Border Patrol intercept',
    time: '12h ago',
    source: 'Intelligence Feed'
  }
];

export const MOCK_SUSPECTS: SuspectProfile[] = [
  {
    id: 'SP-90210',
    name: 'Suresh Hegde',
    age: 42,
    gender: 'Male',
    riskScore: 78,
    firsCount: 6,
    districtsCount: 2,
    connections: [
      { name: 'K. Manjunath', type: 'ASSOC', status: 'ACTIVE' },
      { name: 'R. Ravi', type: 'ASSOC', status: 'SUSPENDED' },
      { name: 'S. Kumar', type: 'KIN', status: 'MONITORED' }
    ],
    recentCrime: 'Robbery',
    status: 'HIGH-RISK',
    bio: 'Primary suspect in multiple highway heists along the outer ring road. Known associate of Bengaluru North gang clusters.'
  },
  {
    id: 'SP-90211',
    name: 'K. Manjunath',
    age: 38,
    gender: 'Male',
    riskScore: 64,
    firsCount: 4,
    districtsCount: 1,
    connections: [
      { name: 'Suresh Hegde', type: 'ASSOC', status: 'HIGH-RISK' },
      { name: 'D. Gowda', type: 'ASSOC', status: 'ACTIVE' }
    ],
    recentCrime: 'Theft',
    status: 'ACTIVE',
    bio: 'Logistics handler for high-value merchandise robberies. Specializes in fence networks in Yelahanka area.'
  },
  {
    id: 'SP-90212',
    name: 'R. Ravi',
    age: 29,
    gender: 'Male',
    riskScore: 45,
    firsCount: 3,
    districtsCount: 1,
    connections: [
      { name: 'Suresh Hegde', type: 'ASSOC', status: 'HIGH-RISK' }
    ],
    recentCrime: 'Vehicle Theft',
    status: 'MONITORED',
    bio: 'Vehicle procurement and transport runner. Connected to Suresh Hegde for escape route planning.'
  },
  {
    id: 'SP-90213',
    name: 'Ramesh Gowda',
    age: 51,
    gender: 'Male',
    riskScore: 82,
    firsCount: 11,
    districtsCount: 4,
    connections: [
      { name: 'S. Kumar', type: 'ASSOC', status: 'MONITORED' },
      { name: 'A. Shetty', type: 'ASSOC', status: 'ACTIVE' }
    ],
    recentCrime: 'House Break-in',
    status: 'HIGH-RISK',
    bio: 'Veteran criminal lead. Orchestrates highly technical break-ins across Southern districts.'
  },
  {
    id: 'SP-90214',
    name: 'S. Kumar',
    age: 31,
    gender: 'Male',
    riskScore: 50,
    firsCount: 2,
    districtsCount: 1,
    connections: [
      { name: 'Suresh Hegde', type: 'KIN', status: 'HIGH-RISK' },
      { name: 'Ramesh Gowda', type: 'ASSOC', status: 'HIGH-RISK' }
    ],
    recentCrime: 'Burglary',
    status: 'MONITORED',
    bio: 'Cousin of Suresh Hegde. Suspected facilitator of safe houses and fund pooling.'
  }
];

export const EMERGING_CLUSTERS: ClusterItem[] = [
  {
    id: 'CL-001',
    name: 'Vehicle Theft',
    change: '+340%',
    location: 'BENGALURU SOUTH',
    incidents: 42,
    rangeDays: 7,
    primaryType: 'VEHICLE CRIME',
    hourlyDistribution: [5, 3, 2, 1, 2, 8, 12, 18, 22, 25, 30, 42, 38, 30, 20, 15, 10, 8, 12, 15, 20, 25, 30, 15]
  },
  {
    id: 'CL-002',
    name: 'House Break-in',
    change: '+120%',
    location: 'MYSORE WEST',
    incidents: 24,
    rangeDays: 14,
    primaryType: 'ROBBERY',
    hourlyDistribution: [10, 5, 20, 15, 10, 5, 5, 10, 30, 40, 80, 100, 90, 70, 40, 20, 10, 5, 5, 15, 20, 30, 15, 10]
  },
  {
    id: 'CL-003',
    name: 'Chain Snatching',
    change: '+85%',
    location: 'HUBBALLI CENTRAL',
    incidents: 18,
    rangeDays: 30,
    primaryType: 'ASSAULT',
    hourlyDistribution: [2, 1, 1, 0, 1, 5, 8, 12, 25, 35, 40, 55, 60, 50, 45, 35, 25, 15, 10, 8, 12, 18, 14, 8]
  }
];

export const INITIAL_CHAT_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-001',
    sender: 'user',
    text: 'Show me recent robbery FIRs in Bengaluru North with active status.',
    timestamp: '08:41 AM'
  },
  {
    id: 'msg-002',
    sender: 'ai',
    text: 'I have retrieved 4 active robbery cases in the Bengaluru North jurisdiction from the last 14 days. The analysis shows a concentrated pattern around the Yelahanka industrial area.',
    timestamp: '08:41 AM',
    tableData: [
      { firNo: 'FIR-2023-BN-0847', crimeType: 'Robbery', district: 'Bengaluru North', status: 'ACTIVE' },
      { firNo: 'FIR-2023-BN-0912', crimeType: 'Robbery', district: 'Bengaluru North', status: 'INVESTIGATION' },
      { firNo: 'FIR-2023-BN-1004', crimeType: 'Robbery', district: 'Bengaluru North', status: 'ACTIVE' }
    ],
    sqlQuery: 'SELECT * FROM fir_records WHERE crime_type = "Robbery" AND district = "Bengaluru North" AND status = "ACTIVE" AND incident_date >= NOW() - INTERVAL 14 DAY;',
    scannedRecords: 847
  }
];

export const CONVERSATION_HISTORY = [
  { id: 'ch-1', title: 'Robbery cases in Bengaluru North', category: 'Today' },
  { id: 'ch-2', title: 'Analysis of suspect KA-01-XP-42', category: 'Today' },
  { id: 'ch-3', title: 'Pattern detection: Hubballi Cluster', category: 'Today' },
  { id: 'ch-4', title: 'Financial links to Shell Co Alpha', category: 'Previous 7 Days' },
  { id: 'ch-5', title: 'Vehicle tracking 2023-10-24', category: 'Previous 7 Days' }
];

export const CHAT_RESPONSES: Record<string, Omit<ChatMessage, 'id' | 'timestamp'>> = {
  'expand search to surrounding sectors': {
    sender: 'ai',
    text: 'Expanding analysis to adjacent jurisdictions (Bengaluru East and Devanahalli). Retreiving 8 additional records. Heat signature highlights highway toll booths as potential getaway coordination points.',
    tableData: [
      { firNo: 'FIR-2023-BE-1102', crimeType: 'Robbery', district: 'Bengaluru East', status: 'ACTIVE' },
      { firNo: 'FIR-2023-DH-0492', crimeType: 'Highway Robbery', district: 'Devanahalli', status: 'INVESTIGATION' },
      { firNo: 'FIR-2023-BN-1045', crimeType: 'Snatching', district: 'Bengaluru North', status: 'ACTIVE' }
    ],
    sqlQuery: 'SELECT * FROM fir_records WHERE crime_type IN ("Robbery", "Snatching") AND district IN ("Bengaluru North", "Bengaluru East", "Devanahalli") AND status != "CLOSED";',
    scannedRecords: 1420
  },
  'show similar modus operandi in mysore': {
    sender: 'ai',
    text: 'Queried Mysore West database. Found 3 related break-ins matching the identical modus operandi (night entry, utility line tampering, specialized glass-cutter tool). These match historical cases linked to Ramesh Gowda.',
    tableData: [
      { firNo: 'FIR-2023-MW-0419', crimeType: 'House Break-in', district: 'Mysore West', status: 'INVESTIGATION' },
      { firNo: 'FIR-2023-MW-0502', crimeType: 'House Break-in', district: 'Mysore West', status: 'ACTIVE' }
    ],
    sqlQuery: 'SELECT * FROM mysore_firs WHERE entry_method = "utility_tamper" AND status = "ACTIVE";',
    scannedRecords: 512
  },
  'cross-reference with ka-01 vehicle sightings': {
    sender: 'ai',
    text: 'Cross-referenced Automatic Number Plate Recognition (ANPR) logs with vehicles registered under KA-01. Found 1 positive hit of a silver hatchback registered to R. Ravi (known Suresh Hegde associate) crossing Hebbal flyover twice within 45 minutes of the Yelahanka robbery.',
    tableData: [
      { firNo: 'FIR-2023-BN-0847', crimeType: 'ANPR Vehicle Match', district: 'Bengaluru North', status: 'ACTIVE' }
    ],
    sqlQuery: 'SELECT sighting_time, camera_id, confidence FROM anpr_logs WHERE plate_no LIKE "KA-01%" AND sighting_time BETWEEN "2023-10-24 02:00" AND "2023-10-24 04:00";',
    scannedRecords: 32900
  }
};
