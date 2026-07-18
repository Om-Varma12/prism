/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { networkService } from '../services/network.service';
import { NetworkGraphFilters } from '../types/network';

/**
 * Hook for fetching the network graph with filters
 */
export function useNetworkGraph(filters: NetworkGraphFilters) {
  return useQuery({
    queryKey: ['network-graph', filters],
    queryFn: () => networkService.getGraph(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook for fetching a single accused profile
 */
export function useAccusedProfile(accusedId: number | null, rowId?: number | null) {
  return useQuery({
    queryKey: ['accused-profile', accusedId, rowId],
    queryFn: () => networkService.getProfile(accusedId ?? null, rowId ?? undefined),
    enabled: accusedId !== null || (rowId !== null && rowId !== undefined),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Hook for searching accused persons with optional filters
 */
export function useSearchAccused(query: string, filters?: NetworkGraphFilters) {
  return useQuery({
    queryKey: ['accused-search', query, filters],
    queryFn: () => networkService.search(query, 10, filters),
    enabled: query.length >= 2,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook for invalidating network graph cache (useful after mutations)
 */
export function useInvalidateNetworkGraph() {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries({ queryKey: ['network-graph'] });
  };
}
