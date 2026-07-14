/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// Hotspot Map Types
export interface HotspotCluster {
  cluster_id: number;
  centroid_lat: number;
  centroid_lng: number;
  point_count: number;
  radius_km: number;
  dominant_crime_type: string | null;
  district: string | null;
}

export interface HotspotFilters {
  date_from?: string;
  date_to?: string;
  district?: string;
}

export interface HotspotClusterResponse {
  clusters: HotspotCluster[];
  total_incidents: number;
  filters: HotspotFilters;
  generated_at: string;
}

// Emerging Clusters Types
export interface CrimeAlert {
  alert_id: number;
  crime_type: string;
  district: string;
  spike_ratio: number;
  baseline_count: number;
  current_count: number;
  detected_at: string;
  acknowledged: boolean;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface CrimeAlertResponse {
  alerts: CrimeAlert[];
  total_alerts: number;
  generated_at: string;
}

// Trend Analysis Types
export type TrendGranularity = 'month' | 'week';

export interface TrendPoint {
  date: string;
  count: number;
  is_forecast: boolean;
  lower_bound?: number;
  upper_bound?: number;
}

export interface TrendFilters {
  granularity: TrendGranularity;
  crime_type?: string;
  district?: string;
}

export interface TrendDataResponse {
  data: TrendPoint[];
  filters: TrendFilters;
  total_count: number;
  generated_at: string;
}

export interface SeasonalComparison {
  event_name: string;
  event_date: string;
  window_start: string;
  window_end: string;
  event_window_count: number;
  baseline_window_count: number;
  percentage_change: number;
}

export interface FestivalCalendarResponse {
  comparisons: SeasonalComparison[];
  generated_at: string;
}

// Offender Risk Board Types
export interface OffenderRisk {
  accused_id: number;
  accused_name: string;
  risk_score: number;
  mo_tag: string | null;
  district_ids: string[];
  is_absconding: boolean;
  fir_count: number;
}

export interface OffenderRiskFilters {
  district?: string;
  min_risk_score?: number;
  is_absconding?: boolean;
}

export interface OffenderRiskResponse {
  offenders: OffenderRisk[];
  total_count: number;
  page: number;
  page_size: number;
  filters: OffenderRiskFilters;
  generated_at: string;
}

// Sociological Data Types
export interface DistrictSocioeconomic {
  district: string;
  literacy_rate: number;
  urbanization_percentage: number;
  population: number;
}

export interface SocioeconomicResponse {
  districts: DistrictSocioeconomic[];
  generated_at: string;
}
