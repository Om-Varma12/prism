/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardService, DistrictCrimeData, AlertItem, TrendData } from '../services/dashboard.service';
import { districtCoordinates } from '../constants/districtCoordinates';

export default function CommandDashboardScreen() {
  const [activeTimeframe, setActiveTimeframe] = useState<'24h' | '7d' | '30d'>('30d');
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictCrimeData | null>(null);
  const [currentTime, setCurrentTime] = useState('');
  const [mapZoom, setMapZoom] = useState(1);
  const [mapPan, setMapPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  // Alert filter states
  const [severityFilter, setSeverityFilter] = useState<'all' | 'HIGH' | 'LOW'>('all');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'district'>('newest');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Notification states
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [previousAlerts, setPreviousAlerts] = useState<AlertItem[]>([]);
  const [toasts, setToasts] = useState<Array<{ id: number; alert: AlertItem; timestamp: number }>>([]);

  // React Query hooks for data fetching
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: dashboardService.getStats,
  });

  const { data: districts = [], isLoading: mapLoading } = useQuery({
    queryKey: ['district-crimes', activeTimeframe],
    queryFn: () => dashboardService.getDistrictCrimes(activeTimeframe),
  });

  const { data: apiAlerts = [], isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => dashboardService.getAlerts(),
    refetchInterval: 60000, // Auto-refresh every 60s
  });

  const { data: trends = [], isLoading: trendsLoading } = useQuery({
    queryKey: ['trends'],
    queryFn: dashboardService.getTrends,
  });

  // Detect new alerts and trigger notifications
  useEffect(() => {
    if (apiAlerts.length > 0 && previousAlerts.length > 0) {
      const newAlerts = apiAlerts.filter(
        (alert: AlertItem) => !previousAlerts.some(prev => prev.alert_id === alert.alert_id)
      );
      
      // Only notify for HIGH severity alerts
      const highSeverityNewAlerts = newAlerts.filter((alert: AlertItem) => alert.level === 'CRITICAL');
      
      if (highSeverityNewAlerts.length > 0) {
        // Add toasts for new HIGH severity alerts
        const newToasts = highSeverityNewAlerts.map((alert: AlertItem) => ({
          id: Date.now() + Math.random(),
          alert,
          timestamp: Date.now()
        }));
        setToasts(prev => [...prev, ...newToasts]);
        
        // Play sound if enabled
        if (soundEnabled) {
          playNotificationSound();
        }
      }
    }
    
    setPreviousAlerts(apiAlerts);
  }, [apiAlerts, previousAlerts, soundEnabled]);

  // Auto-dismiss toasts after 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setToasts(prev => prev.filter(toast => now - toast.timestamp < 5000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Play notification sound
  const playNotificationSound = () => {
    try {
      // Simple beep sound using Web Audio API
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      gainNode.gain.value = 0.3;
      
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch (err) {
      console.log('Audio error:', err);
    }
  };

  // Filter and sort alerts
  const filteredAlerts = apiAlerts.filter((alert: AlertItem) => {
    // Severity filter
    if (severityFilter === 'HIGH' && alert.level !== 'CRITICAL') return false;
    if (severityFilter === 'LOW' && alert.level !== 'WARNING') return false;
    
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        alert.district_name.toLowerCase().includes(query) ||
        alert.crime_type.toLowerCase().includes(query) ||
        alert.title.toLowerCase().includes(query)
      );
    }
    
    return true;
  }).sort((a: AlertItem, b: AlertItem) => {
    // Sort logic
    switch (sortBy) {
      case 'newest':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'oldest':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      case 'district':
        return a.district_name.localeCompare(b.district_name);
      default:
        return 0;
    }
  });

  // Clock ticks every second
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const dateStr = now.toLocaleDateString('en-IN', {
        month: 'short', day: '2-digit', year: 'numeric'
      }).toUpperCase();
      const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
      setCurrentTime(`${dateStr} // ${timeStr} IST`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleMapWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setMapZoom(prev => Math.max(0.5, Math.min(10, prev + delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - mapPan.x, y: e.clientY - mapPan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      e.preventDefault();
      setMapPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };


  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#0A0C10] select-none">
      {/* Header */}
      <header className="h-[72px] shrink-0 border-b border-tactical bg-panel flex items-center justify-between px-margin-desktop z-10">
        <h2 className="font-headline-md text-headline-md text-on-surface">
          Situation Overview
        </h2>
        <div className="flex items-center gap-4">
          <span className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
            {currentTime || 'OCT 24, 2023 // 08:42:15 IST'}
          </span>
          <div className="h-6 w-px bg-outline-variant"></div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span>
            <span className="font-label-mono text-label-mono text-primary-container">
              SYSTEM ONLINE
            </span>
          </div>
        </div>
      </header>

      {/* Main Canvas */}
      <div className="flex-1 overflow-hidden p-margin-desktop">
        {/* KPI Strip */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter mb-lg">
          {/* KPI 1 */}
          <div
            onClick={() => setSelectedDistrict(null)}
            className="bg-panel border border-tactical rounded flex flex-col p-md relative overflow-hidden group cursor-pointer transition-all duration-200 hover:border-primary-container/50"
          >
            <div className="absolute top-0 left-0 w-1 h-full bg-outline-variant group-hover:bg-primary-container transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              TOTAL FIRs
            </span>
            {statsLoading ? (
              <span className="font-display-lg text-display-lg text-on-surface-variant animate-pulse pl-2">——</span>
            ) : (
              <span className="font-display-lg text-display-lg text-on-surface font-data-mono-bold pl-2">
                {stats?.total_firs.toLocaleString('en-IN') ?? '—'}
              </span>
            )}
          </div>
          {/* KPI 2 */}
          <div className="bg-panel border border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-outline-variant group-hover:bg-primary-container transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              ACTIVE CASES
            </span>
            {statsLoading ? (
              <span className="font-display-lg text-display-lg text-on-surface-variant animate-pulse pl-2">——</span>
            ) : (
              <span className="font-display-lg text-display-lg text-on-surface font-data-mono-bold pl-2">
                {stats?.active_cases.toLocaleString('en-IN') ?? '—'}
              </span>
            )}
          </div>
          {/* KPI 3 */}
          <div className="bg-panel border border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-tertiary-container group-hover:bg-tertiary transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              HIGH-RISK OFFENDERS
            </span>
            {statsLoading ? (
              <span className="font-display-lg text-display-lg text-on-surface-variant animate-pulse pl-2">——</span>
            ) : (
              <span className="font-display-lg text-display-lg text-tertiary font-data-mono-bold pl-2">
                {stats?.high_risk_offender_count.toLocaleString('en-IN') ?? '—'}
              </span>
            )}
          </div>
          {/* KPI 4 */}
          <div className="bg-panel border border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-error-container group-hover:bg-error transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              ACTIVE ALERTS
            </span>
            {statsLoading ? (
              <span className="font-display-lg text-display-lg text-on-surface-variant animate-pulse pl-2">——</span>
            ) : (
              <span className="font-display-lg text-display-lg text-error font-data-mono-bold pl-2">
                {stats?.active_alert_count.toLocaleString('en-IN') ?? '—'}
              </span>
            )}
          </div>
        </div>

        {/* Main Row (65/35) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter mb-lg min-h-[400px]">
          {/* Left: Map (8 cols) */}
          <div className="lg:col-span-8 bg-panel border border-tactical rounded flex flex-col overflow-hidden">
            <div className="p-4 border-b border-tactical flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
                  map
                </span>
                <h3 className="font-body-md text-body-md font-semibold text-on-surface uppercase tracking-wide">
                  Crime Density — Karnataka
                </h3>
              </div>
              <div className="flex bg-black border border-white/10 p-0.5 text-[10px] font-mono font-bold">
                {(['24h', '7d', '30d'] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setActiveTimeframe(t)}
                    className={`px-3 py-1 transition-colors uppercase cursor-pointer ${
                      activeTimeframe === t
                        ? 'bg-primary-container text-white font-bold'
                        : 'text-white/60 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div 
              className="flex-1 relative bg-[#050608] min-h-[300px] overflow-hidden"
              onWheel={handleMapWheel}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            >
              {/* Simulated Tactical Map */}
              <div
                className="absolute inset-0 opacity-20 pointer-events-none"
                style={{
                  backgroundImage: 'radial-gradient(#252830 1px, transparent 1px)',
                  backgroundSize: '20px 20px',
                }}
              ></div>
              <div 
                className="absolute inset-0 flex items-center justify-center p-4 transition-transform duration-100 ease-out"
                style={{ 
                  transform: `translate(${mapPan.x}px, ${mapPan.y}px) scale(${mapZoom})`,
                  transformOrigin: 'center center'
                }}
              >
                <img
                  className="w-full h-full object-contain opacity-60 mix-blend-screen pointer-events-none"
                  alt="A tactical, high-contrast digital map of Karnataka state"
                  src={process.env.PUBLIC_URL + '/map.svg'}
                  style={{ imageRendering: 'crisp-edges' }}
                />

                {/* Dynamic district markers from API */}
                {!mapLoading && districts.map((district: DistrictCrimeData) => {
                  const coords = districtCoordinates[district.district_name];
                  
                  // Only show marker if district has SVG coordinates
                  if (!coords) return null;
                  
                  // Convert SVG coordinates to percentage positions
                  // SVG viewBox: 0 0 4.12756 6.33471
                  const SVG_WIDTH = 4.12756;
                  const SVG_HEIGHT = 6.33471;
                  const pos = {
                    left: (coords.cx / SVG_WIDTH) * 100,
                    top: (coords.cy / SVG_HEIGHT) * 100,
                  };
                  
                  const maxFirs = Math.max(...districts.map((d: DistrictCrimeData) => d.total_firs), 1);
                  const ratio = district.total_firs / maxFirs;
                  const getIntensity = (r: number) => {
                    if (r > 0.7) return { dot: '#ef4444', border: '#ef4444', label: '#ff4d4d' };
                    if (r > 0.4) return { dot: '#f97316', border: '#f97316', label: '#fb923c' };
                    return { dot: '#eab308', border: '#eab308', label: '#facc15' };
                  };
                  const intensity = getIntensity(ratio);
                  const isActive = selectedDistrict?.district_id === district.district_id;
                  const tooltipScale = 1 / mapZoom;
                  return (
                    <button
                      key={district.district_id}
                      onClick={() => setSelectedDistrict(isActive ? null : district)}
                      className={`map-marker ${isActive ? 'active' : ''}`}
                      style={{ left: `${pos.left}%`, top: `${pos.top}%` }}
                    >
                      <span 
                        className="map-marker-dot"
                        style={{ 
                          backgroundColor: intensity.dot,
                          borderColor: intensity.border,
                        }}
                      >
                        <span className="map-marker-ping" />
                      </span>
                      
                      {/* Tooltip with district info */}
                      <div 
                        className="map-marker-tooltip"
                        style={{
                          transform: `scale(${tooltipScale})`,
                          transformOrigin: 'left center',
                          transition: 'transform 0.2s ease-out',
                        }}
                      >
                        <div style={{ 
                          fontSize: '12px', 
                          fontFamily: 'JetBrains Mono, monospace', 
                          fontWeight: 'bold', 
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                          marginBottom: '4px',
                          color: intensity.label 
                        }}>
                          {district.district_name}
                        </div>
                        <div style={{ fontSize: '10px', color: '#d1d5db', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>FIRs:</span>
                            <span style={{ color: '#ffffff', fontFamily: 'JetBrains Mono, monospace' }}>{district.total_firs}</span>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Active:</span>
                            <span style={{ color: '#ffffff', fontFamily: 'JetBrains Mono, monospace' }}>{district.active_cases}</span>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Risk:</span>
                            <span style={{ color: '#ffffff', fontFamily: 'JetBrains Mono, monospace' }}>{district.high_risk_count}</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Map Legend */}
              <div className="absolute bottom-4 left-4 bg-panel border border-tactical rounded p-3 flex flex-col gap-2">
                <span className="font-label-mono text-[11px] text-on-surface-variant uppercase">
                  Intensity Legend
                </span>
                <div className="flex items-center gap-2">
                  <span className="font-label-mono text-[10px] text-primary">LOW</span>
                  <div className="w-24 h-2 bg-gradient-to-r from-yellow-500 to-red-500 rounded-sm"></div>
                  <span className="font-label-mono text-[10px] text-primary">HIGH</span>
                </div>
              </div>

              {/* Zoom Indicator */}
              <div className="absolute top-4 right-4 bg-panel border border-tactical rounded px-2 py-1 font-mono text-xs text-on-surface-variant pointer-events-none">
                Zoom: {Math.round(mapZoom * 100)}%
              </div>
            </div>
          </div>

          {/* Right: Active Alerts (4 cols) */}
          <div className="lg:col-span-4 bg-panel border border-tactical rounded flex flex-col overflow-hidden">
            <div className="p-4 border-b border-tactical">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-error text-[20px]">
                    warning
                  </span>
                  <h3 className="font-body-md text-body-md font-semibold text-on-surface uppercase tracking-wide">
                    Active Alerts
                  </h3>
                  <span className="w-5 h-5 rounded flex items-center justify-center bg-error-container text-on-error-container font-label-mono text-[11px]">
                    {alertsLoading ? '—' : apiAlerts.length}
                  </span>
                  {apiAlerts.filter((a: AlertItem) => a.level === 'CRITICAL').length > 0 && (
                    <span className="w-5 h-5 rounded flex items-center justify-center bg-error text-on-error font-label-mono text-[11px]">
                      {apiAlerts.filter((a: AlertItem) => a.level === 'CRITICAL').length}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className={`p-1 rounded ${soundEnabled ? 'bg-primary-container text-primary' : 'bg-surface text-on-surface-variant'} hover:bg-surface-variant transition-colors`}
                  title={soundEnabled ? 'Disable sound' : 'Enable sound'}
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {soundEnabled ? 'volume_up' : 'volume_off'}
                  </span>
                </button>
              </div>
              
              {/* Filter Controls */}
              <div className="flex flex-wrap gap-2">
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value as 'all' | 'HIGH' | 'LOW')}
                  className="px-2 py-1 bg-surface border border-tactical rounded text-xs font-label-mono text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="all">All Severity</option>
                  <option value="HIGH">HIGH Only</option>
                  <option value="LOW">LOW Only</option>
                </select>
                
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest' | 'district')}
                  className="px-2 py-1 bg-surface border border-tactical rounded text-xs font-label-mono text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="district">District A-Z</option>
                </select>
                
                <input
                  type="text"
                  placeholder="Search district or crime..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 min-w-[120px] px-2 py-1 bg-surface border border-tactical rounded text-xs font-label-mono text-on-surface focus:outline-none focus:border-primary placeholder:text-on-surface-variant"
                />
                
                {(severityFilter !== 'all' || sortBy !== 'newest' || searchQuery) && (
                  <button
                    onClick={() => {
                      setSeverityFilter('all');
                      setSortBy('newest');
                      setSearchQuery('');
                    }}
                    className="px-2 py-1 bg-tertiary-container text-tertiary border border-tactical rounded text-xs font-label-mono hover:bg-tertiary transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
              
              {filteredAlerts.length !== apiAlerts.length && (
                <div className="mt-2 text-xs font-label-mono text-on-surface-variant">
                  Showing {filteredAlerts.length} of {apiAlerts.length} alerts
                </div>
              )}
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2 max-h-[400px] custom-scrollbar">
              {alertsLoading
                ? Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="h-16 bg-surface animate-pulse rounded border border-tactical" />
                  ))
                : filteredAlerts.map((alert: AlertItem) => {
                const isCritical = alert.level === 'CRITICAL';
                return (
                  <div
                    key={alert.alert_id}
                    className={`p-3 border border-tactical bg-surface transition-colors rounded relative overflow-hidden group cursor-pointer ${
                      isCritical ? 'hover:border-error-container' : 'hover:border-tertiary-container'
                    }`}
                  >
                    <div className={`absolute left-0 top-0 w-1 h-full ${isCritical ? 'bg-error' : 'bg-tertiary'}`}></div>
                    <div className="flex justify-between items-start mb-2 pl-2">
                      <h4 className="font-body-sm text-body-sm font-bold text-on-surface">
                        {alert.title}
                      </h4>
                      <span className={`font-label-mono text-[11px] ${isCritical ? 'text-error' : 'text-tertiary'}`}>
                        {alert.level}
                      </span>
                    </div>
                    <div className="pl-2 space-y-1">
                      <p className={`font-data-mono-bold text-[13px] ${isCritical ? 'text-error' : 'text-tertiary'}`}>
                        {alert.details}
                      </p>
                      <div className="flex items-center gap-2 text-on-surface-variant">
                        <span className="material-symbols-outlined text-[14px]">
                          schedule
                        </span>
                        <span className="font-label-mono text-[11px]">
                          {alert.time_ago} // {alert.district_name}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom Row: Sparklines */}
        <div className="bg-panel border border-tactical rounded flex flex-col overflow-hidden mb-xl">
          <div className="p-4 border-b border-tactical flex items-center justify-between">
            <h3 className="font-body-md text-body-md font-semibold text-on-surface uppercase tracking-wide">
              30-Day Crime Trend Analytics
            </h3>
            <span className="font-label-mono text-[11px] text-on-surface-variant">
              DATA SYNC: REAL-TIME
            </span>
          </div>
          <div className="p-md grid grid-cols-1 md:grid-cols-5 gap-4 divide-y md:divide-y-0 md:divide-x divide-tactical">
            {(trendsLoading ? [] : trends).map((trend: TrendData, idx: number) => {
              const isUp = trend.trend === 'up';
              const isDown = trend.trend === 'down';
              const changeStr = `${trend.change_pct > 0 ? '+' : ''}${trend.change_pct}%`;
              const colorClass = isUp ? 'text-error' : isDown ? 'text-primary' : 'text-on-surface-variant';
              const icon = isUp ? 'trending_up' : isDown ? 'trending_down' : 'trending_flat';
              return (
                <div key={idx} className="pt-2 md:pt-0 md:px-4 flex flex-col first:pl-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-label-mono text-[12px] text-on-surface-variant uppercase">
                      {trend.crime_category}
                    </span>
                    <span className={`font-data-mono-bold text-[13px] ${colorClass} flex items-center`}>
                      <span className="material-symbols-outlined text-[14px] mr-0.5">
                        {icon}
                      </span>
                      {changeStr}
                    </span>
                  </div>
                  <div className="h-12 w-full flex items-end gap-1 opacity-80">
                    {trend.bar_heights.map((height: number, bIdx: number) => {
                      const isLast = bIdx === trend.bar_heights.length - 1;
                      return (
                        <div
                          key={bIdx}
                          className={`w-full rounded-t-sm ${
                            isLast && isUp ? 'bg-error animate-pulse'
                              : isUp ? 'bg-tertiary'
                              : 'bg-primary-container'
                          }`}
                          style={{ height: `${height}%` }}
                        ></div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className="bg-panel border border-tactical rounded p-3 shadow-lg animate-slide-in flex items-start gap-3 min-w-[300px]"
          >
            <span className="material-symbols-outlined text-error text-[20px]">
              warning
            </span>
            <div className="flex-1">
              <div className="font-body-sm text-body-sm font-semibold text-on-surface mb-1">
                {toast.alert.title}
              </div>
              <div className="font-label-mono text-[11px] text-on-surface-variant">
                {toast.alert.district_name} • {toast.alert.time_ago}
              </div>
            </div>
            <button
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="text-on-surface-variant hover:text-on-surface"
            >
              <span className="material-symbols-outlined text-[18px]">
                close
              </span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
