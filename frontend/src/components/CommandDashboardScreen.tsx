/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { INITIAL_ALERTS } from '../data/mockData';
import { Alert } from '../types';
import { 
  ShieldAlert, 
  Map, 
  Activity, 
  Clock, 
  TrendingUp, 
  TrendingDown, 
  ArrowRight,
  Info,
  Layers,
  Sparkles
} from 'lucide-react';

export default function CommandDashboardScreen() {
  const [activeTimeframe, setActiveTimeframe] = useState<'24h' | '7d' | '30d'>('30d');
  const [alerts, setAlerts] = useState<Alert[]>(INITIAL_ALERTS);
  const [activeDistrict, setActiveDistrict] = useState<string>('BENGALURU_N');
  
  // Dynamic Real-time IST Timestamp clock
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Format to "OCT 24, 2023 // 08:42:15 IST"
      const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
      const monthStr = months[now.getMonth()];
      const day = String(now.getDate()).padStart(2, '0');
      const year = now.getFullYear();
      const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
      setCurrentTime(`${monthStr} ${day}, ${year} // ${timeStr} IST`);
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

  // District marker selection handler
  const handleDistrictChange = (dist: string) => {
    setActiveDistrict(dist);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] overflow-y-auto custom-scrollbar select-none">
      {/* Top Header section */}
      <header className="h-[72px] shrink-0 border-b border-white/10 bg-black flex items-center justify-between px-6 z-10">
        <h2 className="text-xl font-black text-white tracking-tighter uppercase leading-none">
          SITUATION COMMAND OVERVIEW
        </h2>
        
        <div className="flex items-center gap-4 text-[10px] font-mono font-bold uppercase tracking-wider">
          <span className="text-white/60">{currentTime || 'OCT 24, 2023 // 08:42:15 IST'}</span>
          <div className="h-6 w-px bg-white/10"></div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-[#00F0FF] animate-pulse"></span>
            <span className="text-[#00F0FF] font-black">SYSTEM ONLINE</span>
          </div>
        </div>
      </header>

      {/* Main grid panels content */}
      <div className="p-6 space-y-6">
        {/* KPI strip banner */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'TOTAL FIRs', value: kpis.totalFirs, borderClass: 'border-l-4 border-white/20' },
            { label: 'ACTIVE CASES', value: kpis.activeCases, borderClass: 'border-l-4 border-[#00F0FF]' },
            { label: 'HIGH-RISK OFFENDERS', value: kpis.highRisk, borderClass: 'border-l-4 border-[#ff4d4d]', valueColor: 'text-[#ff4d4d]' },
            { label: 'ACTIVE ALERTS', value: kpis.alerts, borderClass: 'border-l-4 border-[#ff4d4d]', valueColor: 'text-[#ff4d4d]' }
          ].map((k, idx) => (
            <div key={idx} className={`bg-black border border-white/10 rounded-none p-4 relative overflow-hidden group hover:border-[#00F0FF]/30 transition-all ${k.borderClass}`}>
              <span className="block text-[9px] font-mono font-black text-white/40 mb-1 tracking-[0.2em] uppercase">
                {k.label}
              </span>
              <span className={`text-2xl font-mono font-black tracking-tight ${k.valueColor || 'text-white'}`}>
                {k.value}
              </span>
            </div>
          ))}
        </div>

        {/* Main interactive map / details split */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[420px]">
          {/* Left Column: Interactive State Map Density (65%) */}
          <div className="lg:col-span-8 bg-black border border-white/10 rounded-none flex flex-col overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-black">
              <div className="flex items-center gap-2">
                <Map className="w-4 h-4 text-white/40" />
                <h3 className="text-[10px] font-mono font-black text-white tracking-[0.2em] uppercase">
                  Crime Density // Karnataka State
                </h3>
              </div>
              
              <div className="flex bg-black border border-white/10 p-0.5 text-[10px] font-mono font-bold">
                {['24h', '7d', '30d'].map((t) => (
                  <button
                    key={t}
                    onClick={() => setActiveTimeframe(t as any)}
                    className={`px-3 py-1 transition-colors uppercase cursor-pointer ${
                      activeTimeframe === t
                        ? 'bg-[#00F0FF] text-black font-black'
                        : 'text-white/60 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Tactical SVG map display */}
            <div className="flex-1 relative bg-black min-h-[340px] flex items-center justify-center p-4">
              <div 
                className="absolute inset-0 opacity-10 pointer-events-none" 
                style={{
                  backgroundImage: 'radial-gradient(white 1px, transparent 1px)',
                  backgroundSize: '20px 20px'
                }}
              ></div>

              {/* Dynamic Map graphics representation */}
              <div className="w-full h-full max-h-[50vh] relative flex items-center justify-center">
                {/* Visual state illustration from Google resources */}
                <img 
                  alt="Karnataka tactical map density chart visualization"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAHzq0WEhaL8_wtUyZPd5cih-cTu7AEGYoNL5_TJkfqobmOkPKANRwdyzgDRk3LV8-VeVdfuFrdse2Rwb-wx7fmXmBfrdtCHNukqm8FNS3OPEsA26p_aSb2xVkzlEgOcLrhnC6Nf9MM_JxPqYGexVA-8TwqJpOQI8dfAfiv6PoPquSOGVurIcEkB6gx2ESNgep6M_HJNAdLbhoOeQYfgZya9T21IBkUg6YM-ZMUUTe4l4AjDC_0TkifoZwomDxGp8nX-8cJYiSMLxE"
                  className="w-full h-full object-contain opacity-40 mix-blend-screen grayscale"
                />

                {/* Clickable Overlay nodes markers for Bengaluru, Mysuru, Hubballi */}
                <button 
                  onClick={() => handleDistrictChange('BENGALURU_N')}
                  className={`absolute group cursor-pointer`}
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
                  onClick={() => handleDistrictChange('MYSURU')}
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
                  onClick={() => handleDistrictChange('HUBBALLI')}
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

              {/* Map Intensity details panel */}
              <div className="absolute bottom-4 left-4 bg-black border border-white/10 rounded-none p-3 flex flex-col gap-1.5 select-none font-mono">
                <span className="text-[9px] text-white/40 uppercase tracking-[0.15em] font-black">INTENSITY SPEC</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gradient-to-r from-black via-[#00F0FF]/40 to-[#00F0FF] border border-white/15 rounded-none"></div>
                  <span className="text-[9px] text-[#00F0FF] font-black tracking-wider">HIGH DENSITY</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Active Alerts Feed List (35%) */}
          <div className="lg:col-span-4 bg-black border border-white/10 rounded-none flex flex-col overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-black">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-[#ff4d4d]" />
                <h3 className="text-[10px] font-mono font-black text-white tracking-[0.2em] uppercase">
                  Active Alerts Feed
                </h3>
              </div>
              <span className="w-5 h-5 rounded-none flex items-center justify-center bg-[#ff4d4d]/10 border border-[#ff4d4d] text-[#ff4d4d] font-mono text-[10px] font-black">
                {alerts.length}
              </span>
            </div>

            {/* Scrolling alert items list */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2.5 max-h-[400px]">
              {alerts.map((al) => (
                <div 
                  key={al.id} 
                  className="p-3 border border-white/10 bg-black/50 relative overflow-hidden group hover:border-[#ff4d4d]/50 transition-all cursor-pointer rounded-none"
                >
                  <div className={`absolute left-0 top-0 w-1 h-full ${
                    al.level === 'CRITICAL' ? 'bg-[#ff4d4d]' : 'bg-[#ff9f0a]'
                  }`}></div>
                  
                  <div className="flex justify-between items-start mb-1.5 pl-2">
                    <h4 className="text-xs font-black text-white tracking-tight uppercase leading-snug pr-2">
                      {al.title}
                    </h4>
                    <span className={`text-[9px] font-mono font-black border px-1.5 py-0.5 tracking-wider ${
                      al.level === 'CRITICAL'
                        ? 'border-[#ff4d4d] text-[#ff4d4d]'
                        : 'border-[#ff9f0a] text-[#ff9f0a]'
                    }`}>
                      {al.level}
                    </span>
                  </div>

                  <div className="pl-2 space-y-1">
                    <p className={`text-xs font-mono font-bold ${
                      al.level === 'CRITICAL' ? 'text-[#ff4d4d]/90' : 'text-[#ff9f0a]/90'
                    }`}>
                      {al.details}
                    </p>
                    <div className="flex items-center gap-1.5 text-[9px] text-white/40 font-mono font-bold uppercase tracking-wider">
                      <Clock className="w-3 h-3 text-white/40" />
                      <span>{al.time} // {al.source}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Panel row: Sparklines tracking trends */}
        <div className="bg-black border border-white/10 rounded-none flex flex-col overflow-hidden">
          <div className="p-4 border-b border-white/10 bg-black flex items-center justify-between">
            <h3 className="text-[10px] font-mono font-black text-white tracking-[0.2em] uppercase">
              30-Day Crime Trend Analytics
            </h3>
            <span className="text-[9px] text-white/40 font-mono font-black tracking-wider uppercase">
              DATA SYNC: REAL-TIME SECURE
            </span>
          </div>

          <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 divide-y lg:divide-y-0 lg:divide-x divide-white/10 bg-black">
            {[
              { label: 'Robbery', value: '+12%', isUp: true, bars: [20, 45, 30, 70, 55, 80, 100], isHot: true },
              { label: 'Theft', value: '-2%', isUp: false, bars: [65, 50, 55, 45, 40, 35, 30], isHot: false },
              { label: 'Assault', value: '+5%', isUp: true, bars: [15, 25, 20, 35, 30, 55, 60], isHot: false },
              { label: 'Vehicle Crime', value: '-15%', isUp: false, bars: [90, 75, 65, 50, 40, 30, 25], isHot: false },
              { label: 'Burglary', value: '0%', isUp: undefined, bars: [40, 45, 35, 48, 42, 45, 40], isHot: false }
            ].map((trend, idx) => (
              <div key={idx} className="pt-4 lg:pt-0 lg:px-4 first:pl-0 border-white/10">
                <div className="flex justify-between items-center mb-2 font-mono text-xs font-bold">
                  <span className="text-white/60 uppercase tracking-wider font-black text-[10px]">
                    {trend.label}
                  </span>
                  
                  {trend.isUp !== undefined ? (
                    <span className={`font-black flex items-center gap-0.5 tracking-wider text-[10px] ${trend.isUp ? 'text-[#ff4d4d]' : 'text-emerald-400'}`}>
                      {trend.isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                      {trend.value}
                    </span>
                  ) : (
                    <span className="text-white/40 font-black text-[10px]">0%</span>
                  )}
                </div>

                {/* Simulated sparkbars diagram */}
                <div className="h-10 w-full flex items-end gap-1 select-none">
                  {trend.bars.map((h, bIdx) => {
                    const isLast = bIdx === trend.bars.length - 1;
                    return (
                      <div 
                        key={bIdx}
                        className={`w-full rounded-none transition-all ${
                          isLast && trend.isHot 
                            ? 'bg-[#ff4d4d] animate-pulse'
                            : trend.isUp === true
                            ? 'bg-[#00F0FF]'
                            : 'bg-[#00F0FF]/30 hover:bg-[#00F0FF]'
                        }`}
                        style={{ height: `${h}%` }}
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
