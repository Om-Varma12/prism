/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { INITIAL_ALERTS } from '../data/mockData';
import { Alert } from '../types';

export default function CommandDashboardScreen() {
  const [activeTimeframe, setActiveTimeframe] = useState<'24h' | '7d' | '30d'>('30d');
  const [alerts, setAlerts] = useState<Alert[]>(INITIAL_ALERTS);
  const [activeDistrict, setActiveDistrict] = useState<string>('BENGALURU_N');
  const [currentTime, setCurrentTime] = useState('');

  // Clock ticks every second
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const months = ['OCT', 'NOV', 'DEC', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP']; // Representative month matching mockup format
      // We will construct "OCT 24, 2023 // 08:42:15 IST" dynamically
      const monthStr = months[now.getMonth() % 12];
      const day = String(now.getDate()).padStart(2, '0');
      const year = now.getFullYear();
      const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
      setCurrentTime(`OCT 24, 2023 // ${timeStr} IST`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // District KPIs data
  const getKpis = () => {
    switch (activeDistrict) {
      case 'HUBBALLI':
        return { totalFirs: '1,420', activeCases: '88', highRisk: '12', alerts: '2' };
      case 'MYSURU':
        return { totalFirs: '984', activeCases: '45', highRisk: '8', alerts: '1' };
      case 'BENGALURU_N':
      default:
        return { totalFirs: '5,847', activeCases: '312', highRisk: '47', alerts: '8' };
    }
  };

  const kpis = getKpis();

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

      {/* Scrollable Canvas */}
      <div className="flex-1 overflow-y-auto p-margin-desktop custom-scrollbar">
        {/* KPI Strip */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter mb-lg">
          {/* KPI 1 */}
          <div
            onClick={() => setActiveDistrict('BENGALURU_N')}
            className={`bg-panel border-tactical rounded flex flex-col p-md relative overflow-hidden group cursor-pointer transition-all duration-200 ${
              activeDistrict === 'BENGALURU_N' ? 'border-primary' : 'hover:border-primary-container/50'
            }`}
          >
            <div className="absolute top-0 left-0 w-1 h-full bg-outline-variant group-hover:bg-primary-container transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              TOTAL FIRs
            </span>
            <span className="font-display-lg text-display-lg text-on-surface font-data-mono-bold pl-2">
              {kpis.totalFirs}
            </span>
          </div>
          {/* KPI 2 */}
          <div className="bg-panel border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-outline-variant group-hover:bg-primary-container transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              ACTIVE CASES
            </span>
            <span className="font-display-lg text-display-lg text-on-surface font-data-mono-bold pl-2">
              {kpis.activeCases}
            </span>
          </div>
          {/* KPI 3 */}
          <div className="bg-panel border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-tertiary-container group-hover:bg-tertiary transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              HIGH-RISK OFFENDERS
            </span>
            <span className="font-display-lg text-display-lg text-tertiary font-data-mono-bold pl-2">
              {kpis.highRisk}
            </span>
          </div>
          {/* KPI 4 */}
          <div className="bg-panel border-tactical rounded flex flex-col p-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-error-container group-hover:bg-error transition-colors"></div>
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2 pl-2">
              ACTIVE ALERTS
            </span>
            <span className="font-display-lg text-display-lg text-error font-data-mono-bold pl-2">
              {kpis.alerts}
            </span>
          </div>
        </div>

        {/* Main Row (65/35) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter mb-lg min-h-[400px]">
          {/* Left: Map (8 cols) */}
          <div className="lg:col-span-8 bg-panel border-tactical rounded flex flex-col overflow-hidden">
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
            <div className="flex-1 relative bg-[#050608] min-h-[300px]">
              {/* Simulated Tactical Map */}
              <div
                className="absolute inset-0 opacity-20 pointer-events-none"
                style={{
                  backgroundImage: 'radial-gradient(#252830 1px, transparent 1px)',
                  backgroundSize: '20px 20px',
                }}
              ></div>
              <div className="absolute inset-0 flex items-center justify-center p-4">
                <img
                  className="w-full h-full object-contain opacity-60 mix-blend-screen grayscale"
                  alt="A tactical, high-contrast digital map of Karnataka state"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAHzq0WEhaL8_wtUyZPd5cih-cTu7AEGYoNL5_TJkfqobmOkPKANRwdyzgDRk3LV8-VeVdfuFrdse2Rwb-wx7fmXmBfrdtCHNukqm8FNS3OPEsA26p_aSb2xVkzlEgOcLrhnC6Nf9MM_JxPqYGexVA-8TwqJpOQI8dfAfiv6PoPquSOGVurIcEkB6gx2ESNgep6M_HJNAdLbhoOeQYfgZya9T21IBkUg6YM-ZMUUTe4l4AjDC_0TkifoZwomDxGp8nX-8cJYiSMLxE"
                />

                {/* Markers corresponding to Bengaluru, Mysore, Hubballi */}
                <button
                  onClick={() => setActiveDistrict('BENGALURU_N')}
                  className="absolute group cursor-pointer"
                  style={{ left: '55%', top: '65%' }}
                >
                  <span className={`absolute -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full border bg-red-500/30 border-red-500 flex items-center justify-center ${activeDistrict === 'BENGALURU_N' ? 'scale-125 shadow-[0_0_12px_rgba(239,68,68,0.8)]' : 'hover:scale-110'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></span>
                  </span>
                  <span className="absolute left-3 -top-3 bg-black border border-white/10 text-[9px] font-mono font-bold px-1.5 py-0.5 text-[#ff4d4d] whitespace-nowrap opacity-90 group-hover:opacity-100 transition-opacity uppercase tracking-wider">
                    Bengaluru North
                  </span>
                </button>

                <button
                  onClick={() => setActiveDistrict('MYSURU')}
                  className="absolute group cursor-pointer"
                  style={{ left: '46%', top: '78%' }}
                >
                  <span className={`absolute -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full border bg-orange-500/20 border-orange-500 flex items-center justify-center ${activeDistrict === 'MYSURU' ? 'scale-125 shadow-[0_0_12px_rgba(249,115,22,0.8)]' : 'hover:scale-110'}`}>
                    <span className="w-1 h-1 rounded-full bg-orange-500"></span>
                  </span>
                  <span className="absolute left-3 -top-3 bg-black border border-white/10 text-[9px] font-mono font-bold px-1.5 py-0.5 text-orange-400 whitespace-nowrap opacity-80 group-hover:opacity-100 transition-opacity uppercase tracking-wider">
                    Mysuru West
                  </span>
                </button>

                <button
                  onClick={() => setActiveDistrict('HUBBALLI')}
                  className="absolute group cursor-pointer"
                  style={{ left: '33%', top: '35%' }}
                >
                  <span className={`absolute -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full border bg-orange-500/20 border-orange-500 flex items-center justify-center ${activeDistrict === 'HUBBALLI' ? 'scale-125 shadow-[0_0_12px_rgba(249,115,22,0.8)]' : 'hover:scale-110'}`}>
                    <span className="w-1 h-1 rounded-full bg-orange-500"></span>
                  </span>
                  <span className="absolute left-3 -top-3 bg-black border border-white/10 text-[9px] font-mono font-bold px-1.5 py-0.5 text-orange-400 whitespace-nowrap opacity-80 group-hover:opacity-100 transition-opacity uppercase tracking-wider">
                    Hubballi Central
                  </span>
                </button>
              </div>

              {/* Map Legend */}
              <div className="absolute bottom-4 left-4 bg-panel border border-tactical rounded p-3 flex flex-col gap-2">
                <span className="font-label-mono text-[11px] text-on-surface-variant uppercase">
                  Intensity Legend
                </span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gradient-to-r from-[#050608] to-primary-container rounded-sm"></div>
                  <span className="font-label-mono text-[10px] text-primary">HIGH</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Active Alerts (4 cols) */}
          <div className="lg:col-span-4 bg-panel border-tactical rounded flex flex-col overflow-hidden">
            <div className="p-4 border-b border-tactical flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-error text-[20px]">
                  warning
                </span>
                <h3 className="font-body-md text-body-md font-semibold text-on-surface uppercase tracking-wide">
                  Active Alerts
                </h3>
              </div>
              <span className="w-5 h-5 rounded flex items-center justify-center bg-error-container text-on-error-container font-label-mono text-[11px]">
                {alerts.length}
              </span>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2 max-h-[400px] custom-scrollbar">
              {alerts.map((alert) => {
                const isCritical = alert.level === 'CRITICAL';
                return (
                  <div
                    key={alert.id}
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
                          {alert.time} // {alert.source}
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
        <div className="bg-panel border-tactical rounded flex flex-col overflow-hidden mb-xl">
          <div className="p-4 border-b border-tactical flex items-center justify-between">
            <h3 className="font-body-md text-body-md font-semibold text-on-surface uppercase tracking-wide">
              30-Day Crime Trend Analytics
            </h3>
            <span className="font-label-mono text-[11px] text-on-surface-variant">
              DATA SYNC: REAL-TIME
            </span>
          </div>
          <div className="p-md grid grid-cols-1 md:grid-cols-5 gap-4 divide-y md:divide-y-0 md:divide-x divide-tactical">
            {[
              { label: 'Robbery', change: '+12%', colorClass: 'text-error', isUp: true, bars: [25, 50, 35, 75, 60, 85, 100], animate: true },
              { label: 'Theft', change: '-2%', colorClass: 'text-on-surface-variant', isFlat: true, bars: [75, 65, 50, 55, 50, 45, 50], animate: false },
              { label: 'Assault', change: '+5%', colorClass: 'text-tertiary', isUp: true, bars: [25, 30, 25, 40, 35, 60, 70], animate: false },
              { label: 'Vehicle Crime', change: '-15%', colorClass: 'text-primary', isDown: true, bars: [100, 80, 70, 50, 40, 35, 25], animate: false },
              { label: 'Burglary', change: '0%', colorClass: 'text-on-surface-variant', isFlat: true, bars: [40, 45, 35, 50, 40, 45, 40], animate: false },
            ].map((trend, idx) => (
              <div key={idx} className="pt-2 md:pt-0 md:px-4 flex flex-col first:pl-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-label-mono text-[12px] text-on-surface-variant uppercase">
                    {trend.label}
                  </span>
                  <span className={`font-data-mono-bold text-[13px] ${trend.colorClass} flex items-center`}>
                    <span className="material-symbols-outlined text-[14px] mr-0.5">
                      {trend.isUp ? 'trending_up' : trend.isDown ? 'trending_down' : 'trending_flat'}
                    </span>
                    {trend.change}
                  </span>
                </div>
                <div className="h-12 w-full flex items-end gap-1 opacity-80">
                  {trend.bars.map((height, bIdx) => {
                    const isLast = bIdx === trend.bars.length - 1;
                    return (
                      <div
                        key={bIdx}
                        className={`w-full rounded-t-sm ${
                          isLast && trend.animate
                            ? 'bg-error animate-pulse'
                            : trend.isUp
                            ? 'bg-tertiary'
                            : 'bg-primary-container'
                        }`}
                        style={{ height: `${height}%` }}
                      ></div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
