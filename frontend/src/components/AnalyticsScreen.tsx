/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { EMERGING_CLUSTERS, MOCK_SUSPECTS } from '../data/mockData';
import { ClusterItem } from '../types';
import { 
  ZoomIn, 
  ZoomOut, 
  Flame, 
  Clock, 
  Eye, 
  Activity, 
  TrendingUp, 
  User, 
  Filter,
  CheckCircle,
  FileSpreadsheet,
  X
} from 'lucide-react';

export default function AnalyticsScreen() {
  const [activeTab, setActiveTab] = useState<'hotspot' | 'trends' | 'offenders'>('hotspot');
  
  // Hotspot states
  const [sliderVal, setSliderVal] = useState(22); // Oct 2024
  const [selectedCluster, setSelectedCluster] = useState<ClusterItem>(EMERGING_CLUSTERS[1]); // House Break-in
  const [showLogDialog, setShowLogDialog] = useState(false);
  
  // Offenders search query
  const [offenderSearch, setOffenderSearch] = useState('');

  // Months map for slider values
  const getSliderMonth = (val: number) => {
    const months = [
      'JAN 2023', 'FEB 2023', 'MAR 2023', 'APR 2023', 'MAY 2023', 'JUN 2023',
      'JUL 2023', 'AUG 2023', 'SEP 2023', 'OCT 2023', 'NOV 2023', 'DEC 2023',
      'JAN 2024', 'FEB 2024', 'MAR 2024', 'APR 2024', 'MAY 2024', 'JUN 2024',
      'JUL 2024', 'AUG 2024', 'SEP 2024', 'OCT 2024', 'NOV 2024', 'DEC 2024',
      'JAN 2025', 'FEB 2025', 'MAR 2025', 'APR 2025', 'MAY 2025', 'JUN 2025',
      'JUL 2025', 'AUG 2025', 'SEP 2025', 'OCT 2025', 'NOV 2025', 'DEC 2025'
    ];
    return months[val - 1] || 'OCT 2024';
  };

  // Adjust hotspot blur position based on slider input
  const getHotspotPositions = () => {
    const shiftX = (sliderVal - 22) * 2;
    const shiftY = (sliderVal - 22) * 1.5;

    return [
      { id: 1, top: 30 + shiftY, left: 40 + shiftX, size: 190, color: 'rgba(220,38,38,0.5)' },
      { id: 2, top: 20 - shiftY, left: 50 - shiftX, size: 130, color: 'rgba(234,88,12,0.5)' },
      { id: 3, top: 50 + shiftY, left: 25 - shiftX, size: 250, color: 'rgba(220,38,38,0.45)' },
      { id: 4, top: 60 - shiftY, left: 60 + shiftX, size: 160, color: 'rgba(234,88,12,0.45)' }
    ];
  };

  // Detailed cluster simulated logs
  const getSimulatedLogs = () => {
    if (selectedCluster.name === 'Vehicle Theft') {
      return [
        { time: '2023-10-24 02:15', loc: 'JP Nagar 4th Phase', desc: 'Lock compromised on heavy duty transport vehicle' },
        { time: '2023-10-23 23:45', loc: 'BTM Layout Stage 2', desc: 'Keyless signal relay attack on parked sedan' },
        { time: '2023-10-22 01:10', loc: 'Banashankari near temple', desc: 'Steering column bypassed, ignition forced' }
      ];
    }
    if (selectedCluster.name === 'House Break-in') {
      return [
        { time: '2023-10-24 03:30', loc: 'Gokulam 3rd Stage', desc: 'Primary utility lines tampered. Entry forced via window.' },
        { time: '2023-10-22 02:45', loc: 'Mysore West Layout B', desc: 'Tampered circuit board, disabled sirens. Stole safe contents.' },
        { time: '2023-10-19 04:15', loc: 'Jayalakshmipuram Lane 4', desc: 'Utility box bypass lock cut. Glass glides removed silently.' }
      ];
    }
    return [
      { time: '2023-10-24 19:15', loc: 'Hubballi Central Junction', desc: 'Forceful snatching of gold necklace from pedestrian' },
      { time: '2023-10-21 18:30', loc: 'Keshwapur Extension Lane', desc: 'Snatching by two offenders operating high powered bike' }
    ];
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] overflow-hidden select-none">
      {/* Top tab headers */}
      <header className="px-6 pt-6 pb-0 border-b border-white/10 flex-shrink-0 bg-black">
        <h2 className="text-xl font-black text-white tracking-tighter mb-4 uppercase leading-none">
          ANALYTICS &amp; PREDICTIVE PATTERNS
        </h2>
        
        <div className="flex gap-6 text-[10px] font-mono font-bold tracking-wider">
          {[
            { id: 'hotspot', label: 'HOTSPOT INTENSITY MAP' },
            { id: 'trends', label: 'HISTORICAL TREND ANALYSIS' },
            { id: 'offenders', label: 'OFFENDER RISK MATRIX' }
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`pb-3 border-b-2 font-black transition-all tracking-[0.15em] cursor-pointer ${
                activeTab === t.id
                  ? 'border-[#00F0FF] text-[#00F0FF]'
                  : 'border-transparent text-white/40 hover:text-white/80'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Tab content container */}
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-[#0A0C10]">
        <AnimatePresence mode="wait">
          {/* TAB 1: Hotspot Map */}
          {activeTab === 'hotspot' && (
            <motion.div 
              key="hotspot"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col xl:flex-row gap-6 h-full"
            >
              {/* Map Canvas Left side */}
              <div className="flex-1 xl:w-[70%] flex flex-col gap-4">
                <div className="flex-1 bg-black border border-white/10 relative overflow-hidden flex flex-col rounded-none min-h-[400px]">
                  {/* Styled satellite canvas */}
                  <div className="flex-1 relative bg-black overflow-hidden">
                    <div 
                      className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-luminosity grayscale"
                      style={{
                        backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuBC6RgexodwX06JxrK6CFVtTutT9lHZIM2zd2Vmy5vPURgfV22mHeZ9viC8pL9zd3CChiNTh5E_ZNOVWpzk7fZL9VnG9DR6-u-YXlq4wL4vKbYw7EaOzwbZ4V80vLblW-k9I3O8YxqRx_2X4GdTN3dqzvIqLSogMn9FT7pXmXgOwumZUJ1Wa8OkBD22rwEEWzHErH_RyNv1-j0BupCh0_SAfCRkrUY77PdEejlDuTbL-a8Fh6ZIjF4ted3uqIa6En2TJhKplKh9TCE')`
                      }}
                    ></div>

                    {/* Gradient black map vignette mask */}
                    <div className="absolute inset-0 bg-radial-gradient from-transparent to-[#0A0C10]/95 pointer-events-none"></div>

                    {/* Glow heat circle halos layers */}
                    {getHotspotPositions().map((spot) => (
                      <div
                        key={spot.id}
                        className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full blur-xl transition-all duration-700 ease-out"
                        style={{
                          top: `${spot.top}%`,
                          left: `${spot.left}%`,
                          width: `${spot.size}px`,
                          height: `${spot.size}px`,
                          background: `radial-gradient(circle, ${spot.color} 0%, rgba(0,0,0,0) 70%)`
                        }}
                      ></div>
                    ))}

                    {/* Zoom coordinates overlay controls */}
                    <div className="absolute top-4 right-4 flex flex-col gap-1 z-10">
                      <button className="w-8 h-8 bg-black border border-white/10 hover:border-[#00F0FF] transition-colors flex items-center justify-center text-white rounded-none cursor-pointer">
                        <ZoomIn className="w-4 h-4 text-white/40" />
                      </button>
                      <button className="w-8 h-8 bg-black border border-white/10 hover:border-[#00F0FF] transition-colors flex items-center justify-center text-white rounded-none cursor-pointer">
                        <ZoomOut className="w-4 h-4 text-white/40" />
                      </button>
                    </div>

                    <div className="absolute top-4 left-4 bg-black border border-white/10 p-2.5 rounded-none font-mono text-[9px] font-black text-white/40 tracking-[0.15em] uppercase">
                      CAMERA GRID ACTIVE // ANPR_LINKED
                    </div>
                  </div>

                  {/* Timeline sliding seek bar */}
                  <div className="p-4 border-t border-white/10 bg-black select-none font-mono">
                    <div className="flex justify-between text-[10px] font-mono font-bold uppercase mb-2">
                      <span className="text-white/40">JAN 2023</span>
                      <span className="text-[#00F0FF] font-black tracking-[0.15em]">
                        CURRENT WINDOW: {getSliderMonth(sliderVal)}
                      </span>
                      <span className="text-white/40">DEC 2025</span>
                    </div>

                    {/* slider input */}
                    <input 
                      type="range"
                      min={1}
                      max={36}
                      value={sliderVal}
                      onChange={(e) => setSliderVal(Number(e.target.value))}
                      className="w-full h-1 bg-white/10 rounded-none appearance-none cursor-pointer focus:outline-none accent-[#00F0FF]"
                    />

                    <div className="flex justify-between w-full mt-1 px-1 select-none">
                      {Array.from({ length: 6 }).map((_, idx) => (
                        <div key={idx} className="w-px h-1.5 bg-white/20"></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Cluster Detail panels side columns */}
              <div className="w-full xl:w-[30%] flex flex-col gap-6 select-none shrink-0">
                {/* Panel 1: Emerging Clusters list */}
                <div className="bg-black border border-white/10 rounded-none flex flex-col overflow-hidden">
                  <div className="p-3 border-b border-white/10 bg-black">
                    <h3 className="text-[10px] font-mono font-black text-white/40 uppercase tracking-[0.15em]">
                      Emerging Crime Clusters
                    </h3>
                  </div>

                  <div className="divide-y divide-white/10">
                    {EMERGING_CLUSTERS.map((cl) => {
                      const isActive = selectedCluster.id === cl.id;
                      return (
                        <div 
                          key={cl.id}
                          onClick={() => setSelectedCluster(cl)}
                          className={`p-4 border-l-2 transition-all cursor-pointer flex flex-col gap-1 ${
                            isActive
                              ? 'bg-white/5 border-l-[#00F0FF]'
                              : 'border-l-transparent hover:bg-white/5'
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <span className="text-xs font-black text-white uppercase tracking-tight">
                              {cl.name}
                            </span>
                            <span className="text-xs font-mono font-black text-[#ff4d4d]">
                              {cl.change}
                            </span>
                          </div>
                          <span className="text-[9px] font-mono font-bold text-white/40 uppercase tracking-wider mt-0.5">
                            {cl.location}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Panel 2: Stats breakdown distribution */}
                <div className="bg-black border border-white/10 rounded-none flex flex-col overflow-hidden flex-1 min-h-[280px]">
                  <div className="p-3 border-b border-white/10 bg-black flex justify-between items-center">
                    <h3 className="text-[10px] font-mono font-black text-white/40 uppercase tracking-[0.15em]">
                      Cluster Details
                    </h3>
                    <span className="text-[9px] text-[#00F0FF] border border-[#00F0FF] px-1.5 py-0.5 font-mono font-black">
                      {selectedCluster.location.replace(' ', '_')}_01
                    </span>
                  </div>

                  <div className="p-4 flex flex-col gap-4 flex-1">
                    <div className="grid grid-cols-2 gap-4 border-b border-white/10 pb-4 font-mono text-xs">
                      <div>
                        <div className="text-[9px] text-white/40 font-black uppercase">Incidents</div>
                        <div className="text-xl font-black text-white mt-1">{selectedCluster.incidents}</div>
                      </div>
                      <div>
                        <div className="text-[9px] text-white/40 font-black uppercase">Range</div>
                        <div className="text-xs font-black text-white mt-2">{selectedCluster.rangeDays} Days</div>
                      </div>
                    </div>

                    <div className="border-b border-white/10 pb-4">
                      <div className="text-[9px] font-mono text-white/40 font-black uppercase">Primary Threat Type</div>
                      <div className="text-xs font-black text-[#ff4d4d] flex items-center gap-1.5 mt-1.5 font-mono uppercase tracking-wider">
                        <Flame className="w-3.5 h-3.5" />
                        {selectedCluster.primaryType}
                      </div>
                    </div>

                    {/* Hourly timeline mini bars layout */}
                    <div className="flex-1 flex flex-col">
                      <div className="text-[9px] font-mono text-white/40 font-black uppercase mb-1">
                        Hourly occurrence Distribution (24H)
                      </div>
                      <div className="flex-1 flex items-end justify-between gap-0.5 h-20 pt-2 border-b border-white/10">
                        {selectedCluster.hourlyDistribution.map((hVal, idx) => (
                          <div 
                            key={idx}
                            title={`Hour ${idx}: ${hVal} occurrence`}
                            className={`w-full hover:bg-white transition-colors rounded-none ${
                              hVal > 30 ? 'bg-[#00F0FF]' : 'bg-white/10'
                            }`}
                            style={{ height: `${Math.min(hVal, 100)}%` }}
                          ></div>
                        ))}
                      </div>
                      <div className="flex justify-between text-[9px] font-mono font-bold text-white/40 mt-1">
                        <span>00:00</span>
                        <span>12:00</span>
                        <span>23:59</span>
                      </div>
                    </div>

                    <button 
                      onClick={() => setShowLogDialog(true)}
                      className="w-full bg-black border border-white/10 hover:border-[#00F0FF] hover:text-[#00F0FF] text-white font-mono font-black text-xs py-2 transition-colors flex items-center justify-center gap-1.5 mt-2 rounded-none cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>VIEW DETAILED LOG</span>
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 2: Trend Analysis */}
          {activeTab === 'trends' && (
            <motion.div 
              key="trends"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6 select-none"
            >
              {/* historical rates grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-black border border-white/10 p-5 rounded-none">
                  <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
                    Monthly Crime Clearance Rates (%)
                  </h3>
                  <div className="h-44 flex items-end justify-between gap-2 border-b border-white/10 pb-2 font-mono text-[9px] font-bold">
                    {[
                      { m: 'Jan', rate: 42 }, { m: 'Feb', rate: 45 }, { m: 'Mar', rate: 48 },
                      { m: 'Apr', rate: 52 }, { m: 'May', rate: 50 }, { m: 'Jun', rate: 58 },
                      { m: 'Jul', rate: 64 }, { m: 'Aug', rate: 62 }, { m: 'Sep', rate: 68 },
                      { m: 'Oct', rate: 75 }
                    ].map((item, idx) => (
                      <div key={idx} className="w-full flex flex-col items-center">
                        <span className="text-[#00F0FF] font-black mb-1">{item.rate}%</span>
                        <div className="w-8 bg-[#00F0FF] rounded-none" style={{ height: `${item.rate * 1.5}px` }}></div>
                        <span className="text-white/40 mt-1.5 uppercase font-black tracking-wider text-[8px]">{item.m}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-black border border-white/10 p-5 rounded-none">
                  <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
                    Weekly crime Occurrence Peak Times (Days)
                  </h3>
                  <div className="h-44 flex items-end justify-between gap-3 border-b border-white/10 pb-2 font-mono text-[9px] font-bold">
                    {[
                      { d: 'MON', crime: 30 }, { d: 'TUE', crime: 28 }, { d: 'WED', crime: 35 },
                      { d: 'THU', crime: 45 }, { d: 'FRI', crime: 72 }, { d: 'SAT', crime: 88 },
                      { d: 'SUN', crime: 64 }
                    ].map((item, idx) => (
                      <div key={idx} className="w-full flex flex-col items-center">
                        <span className="text-[#ff4d4d] font-black mb-1">{item.crime}</span>
                        <div className={`w-10 rounded-none ${item.crime > 60 ? 'bg-[#ff4d4d]' : 'bg-[#ff4d4d]/30'}`} style={{ height: `${item.crime * 1.3}px` }}></div>
                        <span className="text-white/40 mt-1.5 uppercase font-black tracking-wider text-[8px]">{item.d}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 3: Offender Risk Board */}
          {activeTab === 'offenders' && (
            <motion.div 
              key="offenders"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4 select-none"
            >
              {/* Search bar offenders filter */}
              <div className="max-w-md relative border border-white/10 bg-black flex items-center px-3 py-2 rounded-none">
                <Filter className="w-4 h-4 text-white/40 mr-2 shrink-0" />
                <input 
                  type="text"
                  placeholder="FILTER REPEAT OFFENDERS..."
                  value={offenderSearch}
                  onChange={(e) => setOffenderSearch(e.target.value)}
                  className="bg-transparent border-none p-0 text-xs text-white placeholder-white/20 w-full outline-none focus:ring-0 font-mono font-bold"
                />
              </div>

              {/* Grid suspect cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {MOCK_SUSPECTS.filter(s => s.name.toLowerCase().includes(offenderSearch.toLowerCase())).map((sus) => (
                  <div key={sus.id} className="bg-black border border-white/10 p-4 rounded-none flex flex-col justify-between group hover:border-[#00F0FF]/50 transition-all">
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-black text-white uppercase tracking-tight text-sm">{sus.name}</h4>
                          <span className="text-[9px] font-mono text-white/40 font-black tracking-wider uppercase">
                            ID: {sus.id} // AGE: {sus.age}
                          </span>
                        </div>
                        <span className={`text-[8px] font-mono font-black border px-1.5 py-0.5 rounded-none uppercase tracking-wider ${
                          sus.status === 'HIGH-RISK' ? 'border-[#ff4d4d] text-[#ff4d4d]' : 'border-[#ff9f0a] text-[#ff9f0a]'
                        }`}>
                          {sus.status}
                        </span>
                      </div>

                      <p className="text-xs text-white/70 leading-relaxed font-sans mb-4 pt-1.5 border-t border-white/10">
                        {sus.bio}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-white/10 font-mono text-[9px] font-black uppercase tracking-wider">
                      <span className="text-white/40">Risk Score: <strong className="text-white">{sus.riskScore}%</strong></span>
                      <span className="text-[#00F0FF] tracking-wider font-black uppercase">
                        {sus.recentCrime}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* DETAILED CLUSTER LOG OVERLAY DIALOG */}
      <AnimatePresence>
        {showLogDialog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-black border border-white/10 rounded-none shadow-2xl max-w-lg w-full overflow-hidden"
            >
              <div className="p-4 border-b border-white/10 bg-black flex justify-between items-center select-none font-mono">
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-[#00F0FF]" />
                  <span className="text-[10px] font-mono font-black tracking-[0.15em] text-[#00F0FF] uppercase">
                    INCIDENT LOGS // {selectedCluster.name.toUpperCase()}
                  </span>
                </div>
                <button 
                  onClick={() => setShowLogDialog(false)}
                  className="text-white/40 hover:text-white transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* logs body */}
              <div className="p-5 max-h-[350px] overflow-y-auto custom-scrollbar bg-black space-y-3 font-mono text-xs">
                {getSimulatedLogs().map((log, idx) => (
                  <div key={idx} className="p-3 border border-white/10 rounded-none bg-black/40 space-y-1.5">
                    <div className="flex justify-between text-[9px] text-white/40 font-black uppercase">
                      <span>{log.time}</span>
                      <span className="text-[#00F0FF]">{log.loc}</span>
                    </div>
                    <p className="text-white/80 text-xs leading-snug font-sans">
                      {log.desc}
                    </p>
                  </div>
                ))}
              </div>

              <div className="p-4 border-t border-white/10 bg-black flex justify-end">
                <button 
                  onClick={() => setShowLogDialog(false)}
                  className="px-4 py-2 bg-[#00F0FF] hover:bg-[#00D8EE] text-black text-[10px] font-black rounded-none font-mono tracking-wider transition-colors cursor-pointer uppercase"
                >
                  CLOSE LOGS
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
