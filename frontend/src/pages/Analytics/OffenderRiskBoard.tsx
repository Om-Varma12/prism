/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';
import { OffenderRiskResponse, OffenderRiskFilters, OffenderRisk } from '../../types/analytics';

export default function OffenderRiskBoard() {
  // Offender filters
  const [filters, setFilters] = useState<OffenderRiskFilters>({
    district: undefined,
    min_risk_score: undefined,
    is_absconding: undefined,
  });

  // Search query
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Sort field
  const [sortBy, setSortBy] = useState<'risk_score' | 'fir_count'>('risk_score');

  // Fetch offender risk data
  const { data: offenderData, isLoading } = useQuery({
    queryKey: ['offender-risk', filters, page, pageSize],
    queryFn: () => analyticsService.getOffenderRisk(filters, page, pageSize),
  });

  // Handle search change
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Handle district filter change
  const handleDistrictChange = useCallback((district: string) => {
    setFilters(prev => ({
      ...prev,
      district: district || undefined,
    }));
    setPage(1); // Reset to first page on filter change
  }, []);

  // Handle min risk score change
  const handleMinRiskScoreChange = useCallback((score: string) => {
    const numScore = score ? parseFloat(score) : undefined;
    setFilters(prev => ({
      ...prev,
      min_risk_score: numScore,
    }));
    setPage(1);
  }, []);

  // Handle absconding filter change
  const handleAbscondingChange = useCallback((value: string) => {
    const boolValue = value === 'true' ? true : value === 'false' ? false : undefined;
    setFilters(prev => ({
      ...prev,
      is_absconding: boolValue,
    }));
    setPage(1);
  }, []);

  // Handle page change
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  // Handle page size change
  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1);
  }, []);

  // Handle sort change
  const handleSortChange = useCallback((field: 'risk_score' | 'fir_count') => {
    setSortBy(field);
  }, []);

  // Filter offenders by search query (client-side filtering)
  const filteredOffenders = offenderData?.offenders.filter((offender: OffenderRisk) =>
    offender.accused_name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  // Sort offenders
  const sortedOffenders = [...filteredOffenders].sort((a, b) => {
    if (sortBy === 'risk_score') return b.risk_score - a.risk_score;
    return b.fir_count - a.fir_count;
  });

  // Get risk score color
  const getRiskScoreColor = (score: number) => {
    if (score >= 70) return 'text-error';
    if (score >= 40) return 'text-[#ff9f0a]';
    return 'text-primary';
  };

  // Get risk badge color
  const getRiskBadgeColor = (score: number) => {
    if (score >= 70) return 'border-[#ff4d4d] text-[#ff4d4d]';
    if (score >= 40) return 'border-[#ff9f0a] text-[#ff9f0a]';
    return 'border-primary text-primary';
  };

  // Get risk label
  const getRiskLabel = (score: number) => {
    if (score >= 70) return 'HIGH-RISK';
    if (score >= 40) return 'MEDIUM-RISK';
    return 'LOW-RISK';
  };

  return (
    <div className="space-y-4">
      {/* Filters Row */}
      <div className="flex flex-wrap gap-4 items-center bg-surface border border-outline-variant p-4">
        <div className="flex items-center gap-2">
          <label className="font-label-mono text-label-mono text-on-surface-variant">District:</label>
          <input
            type="text"
            placeholder="All districts"
            value={filters.district || ''}
            onChange={(e) => handleDistrictChange(e.target.value)}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary w-40"
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Min Risk Score:</label>
          <input
            type="number"
            placeholder="0"
            min="0"
            max="100"
            value={filters.min_risk_score || ''}
            onChange={(e) => handleMinRiskScoreChange(e.target.value)}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary w-24"
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Absconding:</label>
          <select
            value={filters.is_absconding === undefined ? '' : filters.is_absconding.toString()}
            onChange={(e) => handleAbscondingChange(e.target.value)}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary"
          >
            <option value="">All</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => handleSortChange(e.target.value as 'risk_score' | 'fir_count')}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary"
          >
            <option value="risk_score">Risk Score</option>
            <option value="fir_count">FIR Count</option>
          </select>
        </div>
      </div>

      {/* Search Bar */}
      <div className="max-w-md relative border border-outline-variant bg-[#0A0C10] flex items-center px-3 py-2 rounded-none">
        <span className="material-symbols-outlined text-outline text-[18px] mr-2">filter_alt</span>
        <input
          type="text"
          placeholder="FILTER REPEAT OFFENDERS..."
          value={searchQuery}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="bg-transparent border-none p-0 text-xs text-white placeholder-white/20 w-full outline-none focus:ring-0 font-mono font-bold"
        />
      </div>

      {/* Offender Cards Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <span className="text-primary font-body-sm text-body-sm">Loading offenders...</span>
        </div>
      ) : sortedOffenders.length === 0 ? (
        <div className="text-on-surface-variant font-body-sm text-body-sm text-center py-8">
          No offenders found matching the current filters
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedOffenders.map((offender) => (
            <div
              key={offender.accused_id}
              className="bg-[#111318] border border-outline-variant p-4 rounded-none flex flex-col justify-between group hover:border-[#00F0FF]/50 transition-all"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-black text-white uppercase tracking-tight text-sm">{offender.accused_name}</h4>
                    <span className="text-[9px] font-mono text-white/40 font-black tracking-wider uppercase">
                      ID: {offender.accused_id} // FIRs: {offender.fir_count}
                    </span>
                  </div>
                  <span
                    className={`text-[8px] font-mono font-black border px-1.5 py-0.5 rounded-none uppercase tracking-wider ${getRiskBadgeColor(offender.risk_score)}`}
                  >
                    {getRiskLabel(offender.risk_score)}
                  </span>
                </div>

                {offender.mo_tag && (
                  <p className="text-xs text-white/70 leading-relaxed font-sans mb-4 pt-1.5 border-t border-outline-variant">
                    {offender.mo_tag}
                  </p>
                )}

                <div className="flex items-center gap-2 mb-2">
                  {offender.is_absconding && (
                    <span className="text-[8px] font-mono font-black border border-error text-error px-1.5 py-0.5 rounded-none uppercase tracking-wider">
                      ABSCONDING
                    </span>
                  )}
                  {offender.district_ids.length > 0 && (
                    <span className="text-[8px] font-mono text-white/40 uppercase tracking-wider">
                      {offender.district_ids.length} DISTRICTS
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-outline-variant font-mono text-[9px] font-black uppercase tracking-wider">
                <span className="text-white/40">
                  Risk Score: <strong className={getRiskScoreColor(offender.risk_score)}>{offender.risk_score.toFixed(0)}%</strong>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {offenderData && offenderData.total_count > 0 && (
        <div className="flex items-center justify-between bg-surface border border-outline-variant p-4">
          <div className="font-label-mono text-label-mono text-on-surface-variant">
            Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, offenderData.total_count)} of {offenderData.total_count} offenders
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="px-3 py-1.5 bg-surface-variant border border-outline-variant text-on-surface font-body-sm text-body-sm rounded-none hover:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="font-label-mono text-label-mono text-on-surface px-2">
              Page {page}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page * pageSize >= offenderData.total_count}
              className="px-3 py-1.5 bg-surface-variant border border-outline-variant text-on-surface font-body-sm text-body-sm rounded-none hover:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="ml-4 bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary"
            >
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
              <option value="100">100 per page</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
}

