/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { apiClient } from '../lib/api-client';
import {
  HotspotClusterResponse,
  HotspotFilters,
  CrimeAlertResponse,
  TrendDataResponse,
  TrendFilters,
  FestivalCalendarResponse,
  OffenderRiskResponse,
  OffenderRiskFilters,
  SocioeconomicResponse,
} from '../types/analytics';

export const analyticsService = {
  /**
   * Get spatial crime hotspots using DBSCAN clustering
   */
  getHotspots: async (filters: HotspotFilters): Promise<HotspotClusterResponse> => {
    const params = new URLSearchParams();
    
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);
    if (filters.district) params.append('district', filters.district);
    
    const response = await apiClient.get<HotspotClusterResponse>(
      `/api/analytics/hotspots?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get emerging crime clusters from crime_alerts table
   */
  getEmergingClusters: async (): Promise<CrimeAlertResponse> => {
    const response = await apiClient.get<CrimeAlertResponse>(
      '/api/analytics/emerging-clusters'
    );
    return response.data;
  },

  /**
   * Get crime trend analysis with time-series aggregation
   */
  getTrends: async (filters: TrendFilters): Promise<TrendDataResponse> => {
    const params = new URLSearchParams();
    
    params.append('granularity', filters.granularity);
    if (filters.crime_type) params.append('crime_type', filters.crime_type);
    if (filters.district) params.append('district', filters.district);
    
    const response = await apiClient.get<TrendDataResponse>(
      `/api/analytics/trends?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get seasonal event comparisons for Karnataka festivals
   */
  getFestivalCalendar: async (): Promise<FestivalCalendarResponse> => {
    const response = await apiClient.get<FestivalCalendarResponse>(
      '/api/analytics/festival-calendar'
    );
    return response.data;
  },

  /**
   * Get offender risk scores from risk_scores table
   */
  getOffenderRisk: async (
    filters: OffenderRiskFilters,
    page: number = 1,
    page_size: number = 20
  ): Promise<OffenderRiskResponse> => {
    const params = new URLSearchParams();
    
    if (filters.district) params.append('district', filters.district);
    if (filters.min_risk_score !== undefined) params.append('min_risk_score', filters.min_risk_score.toString());
    if (filters.is_absconding !== undefined) params.append('is_absconding', filters.is_absconding.toString());
    params.append('page', page.toString());
    params.append('page_size', page_size.toString());
    
    const response = await apiClient.get<OffenderRiskResponse>(
      `/api/analytics/offender-risk?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get district-level socioeconomic indicators
   */
  getSocioeconomic: async (): Promise<SocioeconomicResponse> => {
    const response = await apiClient.get<SocioeconomicResponse>(
      '/api/analytics/socioeconomic'
    );
    return response.data;
  },
};
