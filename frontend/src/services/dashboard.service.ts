import { apiClient } from '../lib/api-client';

export interface DashboardStats {
  total_firs: number;
  active_cases: number;
  high_risk_offender_count: number;
  active_alert_count: number;
  computed_at: string;
}

export interface DistrictCrimeData {
  district_id: number;
  district_name: string;
  total_firs: number;
  active_cases: number;
  high_risk_count: number;
  dominant_crime_type: string;
  lat: number;
  lng: number;
}

export interface AlertItem {
  alert_id: number;
  title: string;
  level: 'CRITICAL' | 'WARNING';
  details: string;
  district_name: string;
  crime_type: string;
  spike_ratio: number;
  created_at: string;
  time_ago: string;
}

export interface TrendData {
  crime_category: string;
  weekly_counts: number[];
  bar_heights: number[];
  change_pct: number;
  trend: 'up' | 'down' | 'flat';
  total_current: number;
  total_prior: number;
}

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get('/api/dashboard/stats');
    return res.data;
  },

  getDistrictCrimes: async (timeframe: '24h' | '7d' | '30d'): Promise<DistrictCrimeData[]> => {
    const res = await apiClient.get('/api/dashboard/district-crimes', {
      params: { timeframe },
    });
    return res.data;
  },

  getAlerts: async (limit = 10): Promise<AlertItem[]> => {
    const res = await apiClient.get('/api/dashboard/alerts', {
      params: { limit },
    });
    return res.data;
  },

  getTrends: async (): Promise<TrendData[]> => {
    const res = await apiClient.get('/api/dashboard/trends');
    return res.data;
  },
};
