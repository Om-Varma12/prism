import { useState, useEffect } from 'react';
import {
  dashboardService,
  DashboardStats,
  DistrictCrimeData,
  AlertItem,
  TrendData,
} from '../services/dashboard.service';

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      dashboardService.getStats()
        .then(setStats)
        .catch(() => setError('Failed to load stats'))
        .finally(() => setLoading(false));
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return { stats, loading, error };
}

export function useDistrictCrimes(timeframe: '24h' | '7d' | '30d') {
  const [data, setData] = useState<DistrictCrimeData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      dashboardService.getDistrictCrimes(timeframe)
        .then(setData)
        .finally(() => setLoading(false));
    }, 3000);

    return () => clearTimeout(timer);
  }, [timeframe]);

  return { data, loading };
}

export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      dashboardService.getAlerts().then(setAlerts).finally(() => setLoading(false));

      const interval = setInterval(() => {
        dashboardService.getAlerts().then(setAlerts);
      }, 60_000);

      return () => clearInterval(interval);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return { alerts, loading };
}

export function useTrends() {
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      dashboardService.getTrends()
        .then(setTrends)
        .finally(() => setLoading(false));
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return { trends, loading };
}
