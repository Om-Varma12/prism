/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AlertItem,
  dashboardService,
  DistrictCrimeData,
  TrendData,
} from '../services/dashboard.service';
import { districtCoordinates } from '../constants/districtCoordinates';
import { Badge } from 'components/ui/badge';
import { Skeleton } from 'components/ui/skeleton';

type Timeframe = '24h' | '7d' | '30d';
type SeverityFilter = 'all' | 'critical' | 'warning';
type SortMode = 'newest' | 'oldest' | 'district';

const SVG_WIDTH = 4.12756;
const SVG_HEIGHT = 6.33471;

const fallbackAlerts: AlertItem[] = [
  {
    alert_id: 1,
    title: 'Robbery spike in Bengaluru North',
    level: 'CRITICAL',
    details: '+150% above 90-day average',
    district_name: 'Bengaluru North',
    crime_type: 'Robbery',
    spike_ratio: 2.5,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    time_ago: '1 hour ago',
  },
  {
    alert_id: 2,
    title: 'Vehicle theft rise in Bengaluru South',
    level: 'CRITICAL',
    details: '+220% above 90-day average',
    district_name: 'Bengaluru South',
    crime_type: 'Vehicle Theft',
    spike_ratio: 3.2,
    created_at: new Date(Date.now() - 7200000).toISOString(),
    time_ago: '2 hours ago',
  },
  {
    alert_id: 3,
    title: 'Theft increase in Mysuru Central',
    level: 'WARNING',
    details: '+80% above 90-day average',
    district_name: 'Mysuru Central',
    crime_type: 'Theft',
    spike_ratio: 1.8,
    created_at: new Date(Date.now() - 10800000).toISOString(),
    time_ago: '3 hours ago',
  },
  {
    alert_id: 4,
    title: 'Narcotics pattern in Belagavi',
    level: 'CRITICAL',
    details: '+110% above 90-day average',
    district_name: 'Belagavi',
    crime_type: 'Drug Trafficking',
    spike_ratio: 2.1,
    created_at: new Date(Date.now() - 14400000).toISOString(),
    time_ago: '4 hours ago',
  },
  {
    alert_id: 5,
    title: 'Chain snatching cluster in Mangalore',
    level: 'WARNING',
    details: '+50% above 90-day average',
    district_name: 'Mangalore',
    crime_type: 'Chain Snatching',
    spike_ratio: 1.5,
    created_at: new Date(Date.now() - 18000000).toISOString(),
    time_ago: '5 hours ago',
  },
  {
    alert_id: 6,
    title: 'Homicide watch in Dharwad',
    level: 'CRITICAL',
    details: '+180% above 90-day average',
    district_name: 'Dharwad',
    crime_type: 'Murder',
    spike_ratio: 2.8,
    created_at: new Date(Date.now() - 21600000).toISOString(),
    time_ago: '6 hours ago',
  },
];

function formatNumber(value: number | undefined) {
  if (value === undefined || Number.isNaN(value)) return '--';
  return value.toLocaleString('en-IN');
}

function getTrendTone(trend: TrendData) {
  if (trend.trend === 'up') {
    return {
      icon: 'trending_up',
      text: 'text-[#ff6b66]',
      stroke: '#ff6b66',
      fill: 'rgba(255, 107, 102, 0.16)',
    };
  }

  if (trend.trend === 'down') {
    return {
      icon: 'trending_down',
      text: 'text-[#78a8ff]',
      stroke: '#78a8ff',
      fill: 'rgba(120, 168, 255, 0.14)',
    };
  }

  return {
    icon: 'trending_flat',
    text: 'text-[#9aa4b8]',
    stroke: '#9aa4b8',
    fill: 'rgba(154, 164, 184, 0.12)',
  };
}

function buildSparkPath(values: number[]) {
  if (values.length === 0) return '';

  return values
    .map((height, index) => {
      const x = values.length === 1 ? 50 : 4 + (index / (values.length - 1)) * 92;
      const y = 38 - (height / 100) * 32;
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(' ');
}

function buildAreaPath(values: number[]) {
  const line = buildSparkPath(values);
  return line ? `${line} L 96 42 L 4 42 Z` : '';
}

function getDistrictTone(ratio: number, isActive: boolean) {
  if (isActive) {
    return {
      dot: '#d8e5ff',
      border: '#78a8ff',
      glow: '0 0 0 7px rgba(120, 168, 255, 0.2), 0 0 30px rgba(120, 168, 255, 0.48)',
      text: '#d8e5ff',
    };
  }

  if (ratio > 0.7) {
    return {
      dot: '#ff6b66',
      border: '#ff9a91',
      glow: '0 0 0 5px rgba(255, 107, 102, 0.15), 0 0 26px rgba(255, 107, 102, 0.35)',
      text: '#ffb0aa',
    };
  }

  if (ratio > 0.4) {
    return {
      dot: '#d9a751',
      border: '#ffd27a',
      glow: '0 0 0 5px rgba(217, 167, 81, 0.14), 0 0 22px rgba(217, 167, 81, 0.24)',
      text: '#ffd27a',
    };
  }

  return {
    dot: '#7ea0d8',
    border: '#a9c3f6',
    glow: '0 0 0 5px rgba(126, 160, 216, 0.12)',
    text: '#b7ccf8',
  };
}

function MetricSkeleton() {
  return (
    <div className="h-9 w-24 rounded bg-white/[0.07] animate-pulse" />
  );
}

function PanelShell({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-lg border border-white/[0.08] bg-[#10141c]/95 shadow-[0_24px_80px_rgba(0,0,0,0.24)] ${className}`}>
      {children}
    </section>
  );
}

export default function CommandDashboardScreen() {
  const [activeTimeframe, setActiveTimeframe] = useState<Timeframe>('30d');
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictCrimeData | null>(null);
  const [currentTime, setCurrentTime] = useState('');
  const [mapZoom, setMapZoom] = useState(1);
  const [mapPan, setMapPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all');
  const [sortBy, setSortBy] = useState<SortMode>('newest');
  const [searchQuery, setSearchQuery] = useState('');
  const mapContainerRef = useRef<HTMLDivElement>(null);

  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
  } = useQuery({
    queryKey: ['stats'],
    queryFn: dashboardService.getStats,
  });

  const {
    data: districts = [],
    isLoading: mapLoading,
    isError: mapError,
  } = useQuery<DistrictCrimeData[]>({
    queryKey: ['district-crimes', activeTimeframe],
    queryFn: () => dashboardService.getDistrictCrimes(activeTimeframe),
  });

  const {
    data: fetchedAlerts = [],
    isLoading: alertsLoading,
    isError: alertsError,
  } = useQuery<AlertItem[]>({
    queryKey: ['alerts'],
    queryFn: () => dashboardService.getAlerts(10),
    refetchInterval: 60_000,
  });

  const {
    data: trends = [],
    isLoading: trendsLoading,
    isError: trendsError,
  } = useQuery<TrendData[]>({
    queryKey: ['trends'],
    queryFn: dashboardService.getTrends,
  });

  const apiAlerts: AlertItem[] = fetchedAlerts.length > 0 ? fetchedAlerts : fallbackAlerts;
  const criticalAlertCount = apiAlerts.filter((alert) => alert.level === 'CRITICAL').length;
  const warningAlertCount = apiAlerts.filter((alert) => alert.level === 'WARNING').length;
  const maxDistrictFirs = Math.max(...districts.map((district: DistrictCrimeData) => district.total_firs), 1);
  const hasAnyError = statsError || mapError || alertsError || trendsError;

  const filteredAlerts = useMemo(() => {
    return apiAlerts
      .filter((alert) => {
        if (severityFilter === 'critical' && alert.level !== 'CRITICAL') return false;
        if (severityFilter === 'warning' && alert.level !== 'WARNING') return false;

        if (!searchQuery.trim()) return true;
        const query = searchQuery.toLowerCase();
        return (
          alert.district_name.toLowerCase().includes(query) ||
          alert.crime_type.toLowerCase().includes(query) ||
          alert.title.toLowerCase().includes(query)
        );
      })
      .sort((a, b) => {
        if (sortBy === 'oldest') {
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        }

        if (sortBy === 'district') {
          return a.district_name.localeCompare(b.district_name);
        }

        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
  }, [apiAlerts, searchQuery, severityFilter, sortBy]);

  const activeFilterCount = [
    severityFilter !== 'all',
    sortBy !== 'newest',
    Boolean(searchQuery.trim()),
  ].filter(Boolean).length;

  const topDistricts = useMemo(() => {
    return [...districts]
      .sort((a, b) => b.total_firs - a.total_firs)
      .slice(0, 4);
  }, [districts]);

  const metricCards = [
    {
      label: 'Total FIRs',
      value: formatNumber(stats?.total_firs),
      icon: 'description',
      note: selectedDistrict ? `${selectedDistrict.district_name} selected` : 'Statewide register',
      tone: 'text-[#d8e5ff]',
      border: 'border-[#78a8ff]/35',
      loading: statsLoading,
      onClick: () => setSelectedDistrict(null),
    },
    {
      label: 'Active cases',
      value: formatNumber(stats?.active_cases),
      icon: 'folder_open',
      note: 'Open investigations',
      tone: 'text-[#9fe5ce]',
      border: 'border-[#6fd1a9]/25',
      loading: statsLoading,
    },
    {
      label: 'High-risk offenders',
      value: formatNumber(stats?.high_risk_offender_count),
      icon: 'person_alert',
      note: 'Prioritized watchlist',
      tone: 'text-[#ffd27a]',
      border: 'border-[#d9a751]/30',
      loading: statsLoading,
    },
    {
      label: 'Active alerts',
      value: formatNumber(apiAlerts.length),
      icon: 'release_alert',
      note: `${criticalAlertCount} critical, ${warningAlertCount} warning`,
      tone: 'text-[#ff9a91]',
      border: 'border-[#ff6b66]/30',
      loading: alertsLoading && fetchedAlerts.length === 0,
    },
  ];

  useEffect(() => {
    const mapContainer = mapContainerRef.current;
    if (!mapContainer) return;

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      const delta = event.deltaY > 0 ? -0.1 : 0.1;
      setMapZoom((prev) => Math.max(0.65, Math.min(4, prev + delta)));
    };

    mapContainer.addEventListener('wheel', handleWheel, { passive: false });
    return () => mapContainer.removeEventListener('wheel', handleWheel);
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const dateStr = now.toLocaleDateString('en-IN', {
        month: 'short',
        day: '2-digit',
        year: 'numeric',
      });
      const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
      setCurrentTime(`${dateStr} / ${timeStr} IST`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleMouseDown = (event: React.MouseEvent) => {
    if (event.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: event.clientX - mapPan.x, y: event.clientY - mapPan.y });
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (!isDragging) return;
    event.preventDefault();
    setMapPan({ x: event.clientX - dragStart.x, y: event.clientY - dragStart.y });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetMap = () => {
    setMapZoom(1);
    setMapPan({ x: 0, y: 0 });
  };

  const resetFilters = () => {
    setSeverityFilter('all');
    setSortBy('newest');
    setSearchQuery('');
  };

  return (
    <main className="flex-1 overflow-hidden bg-[#080b10] text-on-surface">
      <div className="h-full overflow-y-auto custom-scrollbar">
        <div className="relative min-h-full px-4 py-4 sm:px-6 lg:px-8">
          <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_18%_8%,rgba(59,111,232,0.14),transparent_28%),radial-gradient(circle_at_82%_18%,rgba(217,167,81,0.08),transparent_24%),linear-gradient(180deg,#080b10_0%,#0b1018_54%,#080b10_100%)]" />
          <div
            className="pointer-events-none fixed inset-0 opacity-[0.07]"
            style={{
              backgroundImage:
                'linear-gradient(rgba(255,255,255,0.7) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.7) 1px, transparent 1px)',
              backgroundSize: '44px 44px',
            }}
          />

          <div className="relative mx-auto flex max-w-[1520px] flex-col gap-4">
            <header className="rounded-lg border border-white/[0.08] bg-[#10141c]/90 px-4 py-4 shadow-[0_24px_80px_rgba(0,0,0,0.25)] sm:px-5">
              <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                <div>
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="rounded border border-[#78a8ff]/30 bg-[#78a8ff]/10 px-2 py-1 font-mono text-[11px] font-semibold text-[#d8e5ff]">
                      PRISM COMMAND
                    </span>
                    <span className="rounded border border-white/[0.08] bg-white/[0.04] px-2 py-1 font-mono text-[11px] text-[#9aa4b8]">
                      {activeTimeframe.toUpperCase()} WINDOW
                    </span>
                  </div>
                  <h1 className="text-[30px] font-semibold leading-tight tracking-[0] text-[#f4f7fb] sm:text-[36px]">
                    Situation Overview
                  </h1>
                  <p className="mt-1 max-w-2xl text-sm leading-6 text-[#9aa4b8]">
                    Statewide FIR pressure, live alert triage, and district-level operational density.
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-3 xl:min-w-[520px]">
                  <div className="rounded border border-white/[0.08] bg-[#080b10]/70 px-3 py-3">
                    <div className="font-mono text-[11px] text-[#778196]">SYNC TIME</div>
                    <div className="mt-1 font-mono text-[12px] font-semibold text-[#eef3fb]">
                      {currentTime || 'Syncing clock'}
                    </div>
                  </div>
                  <div className="rounded border border-white/[0.08] bg-[#080b10]/70 px-3 py-3">
                    <div className="font-mono text-[11px] text-[#778196]">SYSTEM STATE</div>
                    <div className="mt-1 flex items-center gap-2 font-mono text-[12px] font-semibold text-[#9fe5ce]">
                      <span className="h-2 w-2 rounded-sm bg-[#6fd1a9] shadow-[0_0_18px_rgba(111,209,169,0.65)]" />
                      Online
                    </div>
                  </div>
                  <div className="rounded border border-white/[0.08] bg-[#080b10]/70 px-3 py-3">
                    <div className="font-mono text-[11px] text-[#778196]">ALERT LOAD</div>
                    <div className="mt-1 font-mono text-[12px] font-semibold text-[#ffb0aa]">
                      {criticalAlertCount} critical / {warningAlertCount} warning
                    </div>
                  </div>
                </div>
              </div>
            </header>

            {hasAnyError && (
              <div className="rounded-lg border border-[#ff6b66]/30 bg-[#2a1113] px-4 py-3 text-sm text-[#ffb0aa]">
                Some live services did not respond. The dashboard is showing available data and local fallbacks.
              </div>
            )}

            <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
              {metricCards.map((metric) => (
                <button
                  key={metric.label}
                  onClick={metric.onClick}
                  className={`group min-h-[138px] rounded-lg border ${metric.border} bg-[#10141c]/95 p-4 text-left shadow-[0_18px_50px_rgba(0,0,0,0.2)] transition duration-200 hover:-translate-y-0.5 hover:bg-[#121824] focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70 active:translate-y-0`}
                  type="button"
                >
                  <div className="flex items-start justify-between">
                    <span className="font-mono text-[11px] font-semibold text-[#8792a8]">
                      {metric.label}
                    </span>
                    <span className={`material-symbols-outlined text-[22px] ${metric.tone}`}>
                      {metric.icon}
                    </span>
                  </div>
                  <div className={`mt-4 font-mono text-[34px] font-bold leading-none tracking-[0] ${metric.tone}`}>
                    {metric.loading ? <MetricSkeleton /> : metric.value}
                  </div>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <span className="text-xs text-[#9aa4b8]">{metric.note}</span>
                    <span className="h-px flex-1 bg-white/[0.08] transition-colors group-hover:bg-white/[0.18]" />
                  </div>
                </button>
              ))}
            </section>

            <section className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(360px,0.8fr)]">
              <PanelShell className="overflow-hidden">
                <div className="flex flex-col gap-3 border-b border-white/[0.08] px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-[20px] text-[#78a8ff]">
                        travel_explore
                      </span>
                      <h2 className="text-sm font-semibold text-[#eef3fb]">
                        Karnataka crime density
                      </h2>
                    </div>
                    <p className="mt-1 text-xs text-[#8792a8]">
                      Drag to pan. Use the wheel to inspect district pressure.
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <div className="rounded border border-white/[0.08] bg-[#080b10] p-1">
                      {(['24h', '7d', '30d'] as const).map((timeframe) => (
                        <button
                          key={timeframe}
                          onClick={() => setActiveTimeframe(timeframe)}
                          className={`rounded px-3 py-1.5 font-mono text-[11px] font-semibold transition focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70 ${
                            activeTimeframe === timeframe
                              ? 'bg-[#d8e5ff] text-[#07101f]'
                              : 'text-[#9aa4b8] hover:bg-white/[0.06] hover:text-[#eef3fb]'
                          }`}
                          type="button"
                        >
                          {timeframe}
                        </button>
                      ))}
                    </div>
                    <button
                      onClick={resetMap}
                      className="rounded border border-white/[0.08] bg-white/[0.04] px-3 py-2 font-mono text-[11px] font-semibold text-[#d8e5ff] transition hover:bg-white/[0.08] focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70 active:translate-y-px"
                      type="button"
                    >
                      Reset map
                    </button>
                  </div>
                </div>

                <div
                  ref={mapContainerRef}
                  className="relative min-h-[520px] overflow-hidden bg-[#070a0f]"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                  style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
                >
                  <div
                    className="absolute inset-0 opacity-[0.16]"
                    style={{
                      backgroundImage:
                        'radial-gradient(circle at center, rgba(120,168,255,0.55) 1px, transparent 1px)',
                      backgroundSize: '22px 22px',
                    }}
                  />

                  <div
                    className="absolute inset-0 flex items-center justify-center p-8 transition-transform duration-100 ease-out"
                    style={{
                      transform: `translate(${mapPan.x}px, ${mapPan.y}px) scale(${mapZoom})`,
                      transformOrigin: 'center center',
                    }}
                  >
                    <img
                      alt="High contrast digital outline map of Karnataka"
                      className="h-full w-full object-contain opacity-[0.72] mix-blend-screen pointer-events-none"
                      src={process.env.PUBLIC_URL + '/map.svg'}
                      style={{ imageRendering: 'crisp-edges' }}
                    />

                    {!mapLoading &&
                      districts.map((district: DistrictCrimeData) => {
                        const coords = districtCoordinates[district.district_name];
                        if (!coords) return null;

                        const isActive = selectedDistrict?.district_id === district.district_id;
                        const ratio = district.total_firs / maxDistrictFirs;
                        const tone = getDistrictTone(ratio, isActive);
                        const pos = {
                          left: (coords.cx / SVG_WIDTH) * 100,
                          top: (coords.cy / SVG_HEIGHT) * 100,
                        };

                        return (
                          <button
                            key={district.district_id}
                            aria-label={`Select ${district.district_name}`}
                            onClick={() => setSelectedDistrict(isActive ? null : district)}
                            className="map-marker focus:outline-none"
                            style={{ left: `${pos.left}%`, top: `${pos.top}%` }}
                            title={district.district_name}
                            type="button"
                          >
                            <span
                              className="absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-sm border transition duration-200 hover:scale-125"
                              style={{
                                backgroundColor: tone.dot,
                                borderColor: tone.border,
                                boxShadow: tone.glow,
                              }}
                            />
                            <span
                              className="map-marker-tooltip"
                              style={{
                                transform: `scale(${1 / mapZoom})`,
                                transformOrigin: 'left center',
                              }}
                            >
                              <span className="block font-mono text-[11px] font-bold" style={{ color: tone.text }}>
                                {district.district_name}
                              </span>
                              <span className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[10px] text-[#c5cfdf]">
                                <span>FIRs</span>
                                <strong className="text-right text-white">{district.total_firs}</strong>
                                <span>Active</span>
                                <strong className="text-right text-white">{district.active_cases}</strong>
                                <span>Risk</span>
                                <strong className="text-right text-white">{district.high_risk_count}</strong>
                              </span>
                            </span>
                          </button>
                        );
                      })}
                  </div>

                  {mapLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-[#070a0f]/70">
                      <div className="w-[min(520px,80%)] space-y-3 rounded-lg border border-white/[0.08] bg-[#10141c]/90 p-4">
                        <div className="h-4 w-44 rounded bg-white/[0.08] animate-pulse" />
                        <div className="h-48 rounded bg-white/[0.06] animate-pulse" />
                      </div>
                    </div>
                  )}

                  {!mapLoading && districts.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center p-6 text-center">
                      <div className="max-w-sm rounded-lg border border-white/[0.08] bg-[#10141c]/95 p-5">
                        <div className="font-semibold text-[#eef3fb]">No district data available</div>
                        <p className="mt-2 text-sm text-[#9aa4b8]">
                          The selected time window has no mapped FIR records yet.
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="absolute bottom-4 left-4 rounded-lg border border-white/[0.08] bg-[#080b10]/90 p-3">
                    <div className="mb-2 font-mono text-[10px] font-semibold text-[#8792a8]">
                      DENSITY RANGE
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-8 rounded-sm bg-[#7ea0d8]" />
                      <span className="h-2 w-8 rounded-sm bg-[#d9a751]" />
                      <span className="h-2 w-8 rounded-sm bg-[#ff6b66]" />
                    </div>
                  </div>

                  <div className="absolute right-4 top-4 rounded border border-white/[0.08] bg-[#080b10]/90 px-3 py-2 font-mono text-[11px] text-[#9aa4b8]">
                    Zoom {Math.round(mapZoom * 100)}%
                  </div>
                </div>
              </PanelShell>

              <PanelShell className="flex max-h-[680px] flex-col overflow-hidden">
                <div className="border-b border-white/[0.08] px-4 py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[20px] text-[#ff9a91]">
                          emergency_home
                        </span>
                        <h2 className="text-sm font-semibold text-[#eef3fb]">
                          Active alert queue
                        </h2>
                      </div>
                      <p className="mt-1 text-xs text-[#8792a8]">
                        {filteredAlerts.length} of {apiAlerts.length} visible
                      </p>
                    </div>
                    <span className="rounded border border-[#ff6b66]/25 bg-[#ff6b66]/10 px-2 py-1 font-mono text-[11px] font-semibold text-[#ffb0aa]">
                      {criticalAlertCount}
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-2">
                    <select
                      aria-label="Filter alerts by severity"
                      className="rounded border border-white/[0.08] bg-[#080b10] px-2 py-2 font-mono text-[11px] text-[#dce5f3] outline-none transition focus:border-[#78a8ff]"
                      onChange={(event) => setSeverityFilter(event.target.value as SeverityFilter)}
                      value={severityFilter}
                    >
                      <option value="all">All severity</option>
                      <option value="critical">Critical only</option>
                      <option value="warning">Warning only</option>
                    </select>
                    <select
                      aria-label="Sort alerts"
                      className="rounded border border-white/[0.08] bg-[#080b10] px-2 py-2 font-mono text-[11px] text-[#dce5f3] outline-none transition focus:border-[#78a8ff]"
                      onChange={(event) => setSortBy(event.target.value as SortMode)}
                      value={sortBy}
                    >
                      <option value="newest">Newest first</option>
                      <option value="oldest">Oldest first</option>
                      <option value="district">District A-Z</option>
                    </select>
                  </div>

                  <div className="mt-2 flex gap-2">
                    <div className="relative flex-1">
                      <span className="material-symbols-outlined pointer-events-none absolute left-2 top-1/2 -translate-y-1/2 text-[16px] text-[#778196]">
                        search
                      </span>
                      <input
                        className="w-full rounded border border-white/[0.08] bg-[#080b10] py-2 pl-8 pr-3 text-xs text-[#eef3fb] outline-none transition placeholder:text-[#687386] focus:border-[#78a8ff]"
                        onChange={(event) => setSearchQuery(event.target.value)}
                        placeholder="Search district or crime"
                        type="text"
                        value={searchQuery}
                      />
                    </div>
                    {activeFilterCount > 0 && (
                      <button
                        className="rounded border border-white/[0.08] bg-white/[0.04] px-3 font-mono text-[11px] font-semibold text-[#d8e5ff] transition hover:bg-white/[0.08] focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70"
                        onClick={resetFilters}
                        type="button"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
                  {alertsLoading && fetchedAlerts.length === 0 ? (
                    <div className="space-y-2">
                      {Array.from({ length: 5 }).map((_, index) => (
                        <div key={index} className="h-24 rounded-lg border border-white/[0.08] bg-white/[0.04] animate-pulse" />
                      ))}
                    </div>
                  ) : filteredAlerts.length === 0 ? (
                    <div className="rounded-lg border border-white/[0.08] bg-[#080b10]/70 p-5 text-center">
                      <div className="font-semibold text-[#eef3fb]">No matching alerts</div>
                      <p className="mt-2 text-sm text-[#9aa4b8]">
                        Adjust the filters to bring incidents back into the queue.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {filteredAlerts.map((alert) => {
                        const isCritical = alert.level === 'CRITICAL';
                        return (
                          <article
                            key={alert.alert_id}
                            className={`group rounded-lg border bg-[#080b10]/72 p-3 transition duration-200 hover:-translate-y-0.5 ${
                              isCritical
                                ? 'border-[#ff6b66]/22 hover:border-[#ff6b66]/50'
                                : 'border-[#d9a751]/22 hover:border-[#d9a751]/45'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <h3 className="text-sm font-semibold leading-5 text-[#eef3fb]">
                                  {alert.title}
                                </h3>
                                <p className={`mt-1 font-mono text-[12px] font-semibold ${isCritical ? 'text-[#ff9a91]' : 'text-[#ffd27a]'}`}>
                                  {alert.details}
                                </p>
                              </div>
                              <span className={`rounded border px-2 py-1 font-mono text-[10px] font-semibold ${
                                isCritical
                                  ? 'border-[#ff6b66]/30 bg-[#ff6b66]/10 text-[#ffb0aa]'
                                  : 'border-[#d9a751]/30 bg-[#d9a751]/10 text-[#ffd27a]'
                              }`}>
                                {alert.level}
                              </span>
                            </div>
                            <div className="mt-3 grid grid-cols-2 gap-2 border-t border-white/[0.07] pt-3 font-mono text-[10px] text-[#8792a8]">
                              <span>{alert.district_name}</span>
                              <span className="text-right">{alert.time_ago}</span>
                              <span>{alert.crime_type}</span>
                              <span className="text-right">x{alert.spike_ratio.toFixed(1)}</span>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  )}
                </div>
              </PanelShell>
            </section>

            <section className="grid grid-cols-1 gap-4 xl:grid-cols-[0.82fr_1.18fr]">
              <PanelShell className="overflow-hidden">
                <div className="border-b border-white/[0.08] px-4 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <h2 className="text-sm font-semibold text-[#eef3fb]">
                        District focus
                      </h2>
                      <p className="mt-1 text-xs text-[#8792a8]">
                        {selectedDistrict ? 'Selected map jurisdiction' : 'Highest FIR pressure'}
                      </p>
                    </div>
                    {selectedDistrict && (
                      <button
                        className="rounded border border-white/[0.08] px-3 py-2 font-mono text-[11px] font-semibold text-[#d8e5ff] transition hover:bg-white/[0.06] focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70"
                        onClick={() => setSelectedDistrict(null)}
                        type="button"
                      >
                        Statewide
                      </button>
                    )}
                  </div>
                </div>

                <div className="p-4">
                  {selectedDistrict ? (
                    <div>
                      <div className="rounded-lg border border-[#78a8ff]/25 bg-[#78a8ff]/10 p-4">
                        <div className="font-mono text-[11px] text-[#9aa4b8]">SELECTED DISTRICT</div>
                        <div className="mt-2 text-2xl font-semibold tracking-[0] text-[#eef3fb]">
                          {selectedDistrict.district_name}
                        </div>
                        <div className="mt-4 grid grid-cols-3 gap-3">
                          <div>
                            <div className="font-mono text-[10px] text-[#8792a8]">FIRs</div>
                            <div className="mt-1 font-mono text-xl font-bold text-[#d8e5ff]">
                              {selectedDistrict.total_firs}
                            </div>
                          </div>
                          <div>
                            <div className="font-mono text-[10px] text-[#8792a8]">Active</div>
                            <div className="mt-1 font-mono text-xl font-bold text-[#9fe5ce]">
                              {selectedDistrict.active_cases}
                            </div>
                          </div>
                          <div>
                            <div className="font-mono text-[10px] text-[#8792a8]">Risk</div>
                            <div className="mt-1 font-mono text-xl font-bold text-[#ffd27a]">
                              {selectedDistrict.high_risk_count}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 rounded border border-white/[0.08] bg-[#080b10]/70 px-3 py-3 text-sm text-[#c5cfdf]">
                        Dominant pattern: <strong className="font-semibold text-[#eef3fb]">{selectedDistrict.dominant_crime_type || 'Not classified'}</strong>
                      </div>
                    </div>
                  ) : topDistricts.length === 0 ? (
                    <div className="rounded-lg border border-white/[0.08] bg-[#080b10]/70 p-5 text-sm text-[#9aa4b8]">
                      No district ranking is available for this time window.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {topDistricts.map((district, index) => {
                        const percent = Math.max(8, Math.round((district.total_firs / maxDistrictFirs) * 100));
                        return (
                          <button
                            key={district.district_id}
                            className="w-full rounded-lg border border-white/[0.08] bg-[#080b10]/72 p-3 text-left transition hover:border-[#78a8ff]/35 hover:bg-[#111722] focus:outline-none focus:ring-2 focus:ring-[#78a8ff]/70"
                            onClick={() => setSelectedDistrict(district)}
                            type="button"
                          >
                            <div className="flex items-center justify-between gap-4">
                              <div className="flex items-center gap-3">
                                <span className="flex h-7 w-7 items-center justify-center rounded border border-white/[0.08] bg-white/[0.04] font-mono text-[11px] text-[#9aa4b8]">
                                  {index + 1}
                                </span>
                                <div>
                                  <div className="text-sm font-semibold text-[#eef3fb]">{district.district_name}</div>
                                  <div className="mt-0.5 text-xs text-[#8792a8]">{district.dominant_crime_type}</div>
                                </div>
                              </div>
                              <span className="font-mono text-sm font-bold text-[#d8e5ff]">{district.total_firs}</span>
                            </div>
                            <div className="mt-3 h-1.5 rounded-sm bg-white/[0.06]">
                              <div
                                className="h-full rounded-sm bg-[#78a8ff]"
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </PanelShell>

              <PanelShell className="overflow-hidden">
                <div className="flex flex-col gap-2 border-b border-white/[0.08] px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-[#eef3fb]">
                      30-day crime trend analytics
                    </h2>
                    <p className="mt-1 text-xs text-[#8792a8]">
                      Weekly movement across major crime categories.
                    </p>
                  </div>
                  <span className="font-mono text-[11px] text-[#8792a8]">
                    LIVE CACHE
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 xl:grid-cols-6">
                  {trendsLoading ? (
                    Array.from({ length: 5 }).map((_, index) => (
                      <div
                        key={index}
                        className={`min-h-[188px] rounded-lg border border-white/[0.08] bg-[#080b10]/72 p-4 ${
                          index < 2 ? 'xl:col-span-3' : 'xl:col-span-2'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex flex-col gap-2">
                            <Skeleton className="h-4 w-28 bg-white/[0.08]" />
                            <Skeleton className="h-3 w-20 bg-white/[0.06]" />
                          </div>
                          <Skeleton className="h-5 w-14 rounded-md bg-white/[0.08]" />
                        </div>
                        <Skeleton className="mt-5 h-20 w-full bg-white/[0.05]" />
                        <div className="mt-4 grid grid-cols-2 gap-2">
                          <Skeleton className="h-9 w-full bg-white/[0.05]" />
                          <Skeleton className="h-9 w-full bg-white/[0.05]" />
                        </div>
                      </div>
                    ))
                  ) : trends.length === 0 ? (
                    <div className="col-span-full flex min-h-[188px] flex-col items-center justify-center rounded-lg border border-dashed border-white/[0.12] bg-[#080b10]/70 p-6 text-center">
                      <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#6d7890]">
                        Analytics pending
                      </span>
                      <p className="mt-2 text-sm font-medium text-[#cbd6e8]">
                        Trend data is not available yet.
                      </p>
                    </div>
                  ) : (
                    trends.slice(0, 5).map((trend: TrendData, index: number) => {
                      const tone = getTrendTone(trend);
                      const change = `${trend.change_pct > 0 ? '+' : ''}${trend.change_pct}%`;
                      const path = buildSparkPath(trend.bar_heights);
                      const areaPath = buildAreaPath(trend.bar_heights);
                      const badgeVariant = trend.trend === 'up'
                        ? 'destructive'
                        : trend.trend === 'down'
                          ? 'default'
                          : 'outline';

                      return (
                        <article
                          key={trend.crime_category}
                          className={`min-h-[188px] rounded-lg border border-white/[0.08] bg-[#080b10]/72 p-4 transition-colors hover:border-[#78a8ff]/35 hover:bg-[#0b1018]/82 ${
                            index < 2 ? 'xl:col-span-3' : 'xl:col-span-2'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <h3 className="text-sm font-semibold text-[#eef3fb]">
                                {trend.crime_category}
                              </h3>
                              <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8792a8]">
                                30-day category movement
                              </p>
                            </div>
                            <Badge
                              variant={badgeVariant}
                              className={`rounded-md border-white/[0.1] bg-white/[0.04] font-mono text-[11px] ${tone.text}`}
                            >
                              <span className="material-symbols-outlined text-[14px]" data-icon="inline-start">
                                {tone.icon}
                              </span>
                              {change}
                            </Badge>
                          </div>

                          <div className="mt-5 h-20 rounded-md border border-white/[0.06] bg-[#05070b]/60 p-2">
                            <svg className="h-full w-full" preserveAspectRatio="none" viewBox="0 0 100 44">
                              <defs>
                                <linearGradient id={`trendFill-${index}`} x1="0" x2="0" y1="0" y2="1">
                                  <stop offset="0%" stopColor={tone.fill} />
                                  <stop offset="100%" stopColor="rgba(0,0,0,0)" />
                                </linearGradient>
                              </defs>
                              {areaPath && <path d={areaPath} fill={`url(#trendFill-${index})`} />}
                              {path && (
                                <path
                                  d={path}
                                  fill="none"
                                  stroke={tone.stroke}
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth="2.4"
                                />
                              )}
                            </svg>
                          </div>

                          <div className="mt-4 grid grid-cols-2 gap-2">
                            <div className="rounded-md border border-white/[0.06] bg-white/[0.035] px-3 py-2">
                              <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#69758a]">
                                Current
                              </p>
                              <p className="mt-1 font-mono text-sm font-semibold text-[#eef3fb]">
                                {formatNumber(trend.total_current)}
                              </p>
                            </div>
                            <div className="rounded-md border border-white/[0.06] bg-white/[0.025] px-3 py-2">
                              <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-[#69758a]">
                                Prior
                              </p>
                              <p className="mt-1 font-mono text-sm font-semibold text-[#aebbd0]">
                                {formatNumber(trend.total_prior)}
                              </p>
                            </div>
                          </div>
                        </article>
                      );
                    })
                  )}
                </div>
              </PanelShell>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
