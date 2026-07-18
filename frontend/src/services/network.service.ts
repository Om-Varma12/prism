/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { apiClient } from '../lib/api-client';
import {
  NetworkGraphResponse,
  NetworkGraphFilters,
  AccusedProfileResponse,
  NetworkSearchResponse,
} from '../types/network';

export const networkService = {
  /**
   * Get the co-accused network graph with optional filters
   */
  getGraph: async (filters: NetworkGraphFilters): Promise<NetworkGraphResponse> => {
    const params = new URLSearchParams();
    
    if (filters.crime_type) params.append('crime_type', filters.crime_type);
    if (filters.district) params.append('district', filters.district);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);
    if (filters.view) params.append('view', filters.view);
    
    const response = await apiClient.get<NetworkGraphResponse>(
      `/api/network/graph?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get a single accused profile by ID or ROWID.
   * When accusedId is null (node has no AccusedMasterID), pass 0 as the path param
   * and supply row_id as a query param — the backend resolves by ROWID in that case.
   */
  getProfile: async (accusedId: number | null, rowId?: number): Promise<AccusedProfileResponse> => {
    const params = new URLSearchParams();
    if (rowId) params.append('row_id', rowId.toString());
    // Use 0 as sentinel when we only have a row_id; backend handles accused_id=0 gracefully
    const idParam = accusedId ?? 0;
    const queryString = params.toString();
    const url = queryString
      ? `/api/network/profile/${idParam}?${queryString}`
      : `/api/network/profile/${idParam}`;
    const response = await apiClient.get<AccusedProfileResponse>(url);
    return response.data;
  },

  /**
   * Search accused persons by name with optional filters
   */
  search: async (query: string, limit = 10, filters?: NetworkGraphFilters): Promise<NetworkSearchResponse> => {
    const params = new URLSearchParams();
    params.append('q', query);
    params.append('limit', limit.toString());
    
    if (filters?.crime_type) params.append('crime_type', filters.crime_type);
    if (filters?.district) params.append('district', filters.district);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    
    const response = await apiClient.get<NetworkSearchResponse>(
      `/api/network/search?${params.toString()}`
    );
    return response.data;
  },
};
