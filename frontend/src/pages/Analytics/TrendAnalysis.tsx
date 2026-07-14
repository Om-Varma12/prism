/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';
import { TrendDataResponse, TrendFilters, TrendGranularity, FestivalCalendarResponse, TrendPoint, SeasonalComparison } from '../../types/analytics';

export default function TrendAnalysis() {
  // Trend filters
  const [filters, setFilters] = useState<TrendFilters>({
    granularity: 'month',
    crime_type: undefined,
    district: undefined,
  });

  // Show forecast toggle
  const [showForecast, setShowForecast] = useState(true);

  // Fetch trends data
  const { data: trendsData, isLoading: trendsLoading } = useQuery({
    queryKey: ['trends', filters],
    queryFn: () => analyticsService.getTrends(filters),
  });

  // Fetch festival calendar
  const { data: festivalData } = useQuery({
    queryKey: ['festival-calendar'],
    queryFn: () => analyticsService.getFestivalCalendar(),
  });

  // Handle granularity change
  const handleGranularityChange = useCallback((granularity: TrendGranularity) => {
    setFilters(prev => ({
      ...prev,
      granularity,
    }));
  }, []);

  // Handle crime type filter change
  const handleCrimeTypeChange = useCallback((crimeType: string) => {
    setFilters(prev => ({
      ...prev,
      crime_type: crimeType || undefined,
    }));
  }, []);

  // Handle district filter change
  const handleDistrictChange = useCallback((district: string) => {
    setFilters(prev => ({
      ...prev,
      district: district || undefined,
    }));
  }, []);

  return (
    <div className="space-y-6">
      {/* Filters Row */}
      <div className="flex flex-wrap gap-4 items-center bg-surface border border-outline-variant p-4">
        <div className="flex items-center gap-2">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Granularity:</label>
          <select
            value={filters.granularity}
            onChange={(e) => handleGranularityChange(e.target.value as TrendGranularity)}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary"
          >
            <option value="month">Monthly</option>
            <option value="week">Weekly</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Crime Type:</label>
          <input
            type="text"
            placeholder="All types"
            value={filters.crime_type || ''}
            onChange={(e) => handleCrimeTypeChange(e.target.value)}
            className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary w-40"
          />
        </div>

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

        <div className="flex items-center gap-2 ml-auto">
          <label className="font-label-mono text-label-mono text-on-surface-variant">Show Forecast:</label>
          <button
            onClick={() => setShowForecast(!showForecast)}
            className={`w-12 h-6 rounded-none transition-colors ${
              showForecast ? 'bg-primary' : 'bg-outline-variant'
            }`}
          >
            <div
              className={`w-5 h-5 bg-white rounded-none transition-transform ${
                showForecast ? 'translate-x-6' : 'translate-x-0.5'
              }`}
            ></div>
          </button>
        </div>
      </div>

      {/* Main Chart Area */}
      <div className="bg-surface border border-outline-variant p-5 rounded-none">
        <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
          CRIME TREND ANALYSIS {showForecast ? '(WITH FORECAST)' : '(HISTORICAL)'}
        </h3>
        
        {trendsLoading ? (
          <div className="flex items-center justify-center h-64">
            <span className="text-primary font-body-sm text-body-sm">Loading trends...</span>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-on-surface-variant">
            <div className="text-center">
              <p className="font-label-mono text-label-mono mb-2">CHART VISUALIZATION</p>
              <p className="font-body-sm text-body-sm">Install Recharts: npm install recharts</p>
              {trendsData && (
                <p className="mt-2 text-on-surface">
                  {trendsData.data.length} data points ({filters.granularity} granularity)
                </p>
              )}
              {trendsData && showForecast && (
                <p className="mt-1 text-primary">
                  {trendsData.data.filter((d: TrendPoint) => d.is_forecast).length} forecast points
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Seasonal Comparison Panel */}
      <div className="bg-surface border border-outline-variant p-5 rounded-none">
        <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
          SEASONAL FESTIVAL COMPARISON
        </h3>
        
        {festivalData?.comparisons.length === 0 ? (
          <div className="text-on-surface-variant font-body-sm text-body-sm">
            No seasonal data available
          </div>
        ) : (
          <div className="space-y-3">
            {festivalData?.comparisons.map((comparison: SeasonalComparison) => (
              <div
                key={comparison.event_name}
                className="flex items-center justify-between p-3 border border-outline-variant bg-surface-variant"
              >
                <div>
                  <div className="font-body-sm text-body-sm font-semibold text-on-surface">
                    {comparison.event_name}
                  </div>
                  <div className="font-label-mono text-label-mono text-on-surface-variant text-[10px]">
                    {comparison.event_date}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-data-mono-bold text-data-mono-bold text-on-surface">
                    {comparison.event_window_count} vs {comparison.baseline_window_count}
                  </div>
                  <div
                    className={`font-label-mono text-label-mono text-[10px] ${
                      comparison.percentage_change > 0 ? 'text-error' : 'text-primary'
                    }`}
                  >
                    {comparison.percentage_change > 0 ? '+' : ''}{comparison.percentage_change.toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

