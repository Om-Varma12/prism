/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';
import { TrendDataResponse, TrendFilters, TrendGranularity, FestivalCalendarResponse, TrendPoint, SeasonalComparison } from '../../types/analytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

  // Combine historical and forecast data points with the same date
  const chartData = React.useMemo(() => {
    if (!trendsData?.data) return [];
    
    const merged: Record<string, {
      date: string;
      historical: number | null;
      forecast: number | null;
      lower_bound: number | null;
      upper_bound: number | null;
    }> = {};

    trendsData.data.forEach((point: TrendPoint) => {
      const key = point.date;
      if (!merged[key]) {
        merged[key] = {
          date: key,
          historical: null,
          forecast: null,
          lower_bound: null,
          upper_bound: null,
        };
      }
      
      if (point.is_forecast) {
        merged[key].forecast = (merged[key].forecast ?? 0) + point.count;
        if (point.lower_bound !== null && point.lower_bound !== undefined) {
          merged[key].lower_bound = (merged[key].lower_bound ?? 0) + point.lower_bound;
        }
        if (point.upper_bound !== null && point.upper_bound !== undefined) {
          merged[key].upper_bound = (merged[key].upper_bound ?? 0) + point.upper_bound;
        }
      } else {
        merged[key].historical = (merged[key].historical ?? 0) + point.count;
      }
    });

    const result = Object.values(merged).sort((a, b) => a.date.localeCompare(b.date));

    // Connect the historical line and forecast line smoothly at the transition point
    const lastHistoricalIdx = result.map(d => d.historical !== null).lastIndexOf(true);
    const firstForecastIdx = result.findIndex(d => d.forecast !== null);
    
    if (lastHistoricalIdx !== -1 && firstForecastIdx !== -1 && firstForecastIdx >= lastHistoricalIdx) {
      const transitionPoint = result[lastHistoricalIdx];
      transitionPoint.forecast = transitionPoint.historical;
    }

    return result;
  }, [trendsData]);

  // Fetch festival calendar with filters
  const { data: festivalData } = useQuery({
    queryKey: ['festival-calendar', filters],
    queryFn: () => analyticsService.getFestivalCalendar(filters),
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
          <div className="flex items-center justify-center h-80">
            <span className="text-primary font-body-sm text-body-sm">Loading trends...</span>
          </div>
        ) : (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#252830" vertical={false} />
                <XAxis 
                  dataKey="date" 
                  stroke="#8b92a5"
                  tick={{ fill: '#8b92a5', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#252830' }}
                />
                <YAxis 
                  stroke="#8b92a5"
                  tick={{ fill: '#8b92a5', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#252830' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#111318', 
                    border: '1px solid #252830',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                  itemStyle={{ color: '#fff', fontSize: '12px' }}
                  labelStyle={{ color: '#8b92a5', fontSize: '11px', fontFamily: 'monospace' }}
                  formatter={(value: any, name: any) => {
                    if (name === 'Historical Crimes') {
                      return [value, 'Historical'];
                    }
                    if (name === 'Forecasted Crimes') {
                      return [value, 'Predicted (Prophet)'];
                    }
                    return [value, name];
                  }}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: '10px' }}
                  iconType="line"
                />
                <Line 
                  type="monotone" 
                  dataKey="historical" 
                  stroke="#00F0FF" 
                  strokeWidth={3}
                  dot={false}
                  name="Historical Crimes"
                  activeDot={{ r: 5, stroke: '#00F0FF', strokeWidth: 2, fill: '#111318' }}
                  connectNulls={true}
                />
                {showForecast && (
                  <Line 
                    type="monotone" 
                    dataKey="forecast" 
                    stroke="#ff4d4d" 
                    strokeWidth={2}
                    strokeDasharray="6 4"
                    dot={false}
                    name="Forecasted Crimes"
                    activeDot={{ r: 5, stroke: '#ff4d4d', strokeWidth: 2, fill: '#111318' }}
                    connectNulls={true}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
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
            No seasonal data available. Try adjusting filters or date range.
          </div>
        ) : (
          <div className="space-y-4">
            {festivalData?.comparisons.map((comparison: SeasonalComparison) => (
              <div
                key={comparison.event_name}
                className="border border-outline-variant bg-surface-variant p-4"
              >
                {/* Festival Header */}
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-body-sm text-body-sm font-semibold text-on-surface text-lg">
                      {comparison.event_name}
                    </div>
                    <div className="font-label-mono text-label-mono text-on-surface-variant text-xs">
                      {comparison.event_date} • Window: {comparison.window_start} to {comparison.window_end}
                    </div>
                  </div>
                  <div
                    className={`px-3 py-1 rounded-none font-label-mono text-label-mono text-sm ${
                      comparison.percentage_change > 20 ? 'bg-error/20 text-error' :
                      comparison.percentage_change < -20 ? 'bg-primary/20 text-primary' :
                      'bg-outline-variant/20 text-on-surface-variant'
                    }`}
                  >
                    {comparison.percentage_change > 0 ? '+' : ''}{comparison.percentage_change.toFixed(1)}%
                  </div>
                </div>
                
                {/* Comparison Bar Chart */}
                <div className="space-y-2">
                  <div className="flex items-center gap-4">
                    <div className="w-32 font-label-mono text-label-mono text-on-surface-variant text-xs">
                      Festival Window
                    </div>
                    <div className="flex-1 bg-surface h-6 rounded-none overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{
                          width: `${Math.min((comparison.event_window_count / Math.max(comparison.baseline_window_count, 1)) * 100, 100)}%`
                        }}
                      />
                    </div>
                    <div className="w-16 text-right font-data-mono-bold text-data-mono-bold text-on-surface text-sm">
                      {comparison.event_window_count}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="w-32 font-label-mono text-label-mono text-on-surface-variant text-xs">
                      Baseline
                    </div>
                    <div className="flex-1 bg-surface h-6 rounded-none overflow-hidden">
                      <div
                        className="h-full bg-outline-variant transition-all duration-300"
                        style={{
                          width: `${Math.min((comparison.baseline_window_count / Math.max(comparison.event_window_count, 1)) * 100, 100)}%`
                        }}
                      />
                    </div>
                    <div className="w-16 text-right font-data-mono-bold text-data-mono-bold text-on-surface-variant text-sm">
                      {comparison.baseline_window_count}
                    </div>
                  </div>
                </div>
                
                {/* Insight Text */}
                <div className="mt-3 font-body-sm text-body-sm text-on-surface-variant text-xs">
                  {comparison.percentage_change > 20 
                    ? `⚠️ High crime spike detected during ${comparison.event_name}`
                    : comparison.percentage_change < -20
                    ? `✓ Lower crime rate during ${comparison.event_name}`
                    : `Normal crime pattern around ${comparison.event_name}`
                  }
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

