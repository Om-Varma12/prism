/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { COLORS } from '../constants/colors';
import { EMERGING_CLUSTERS, MOCK_SUSPECTS } from '../data/mockData';
import { ClusterItem } from '../types';

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
    <div className="flex-1 flex flex-col h-full overflow-hidden check-bg" style={{ backgroundColor: COLORS.background.dark }}>
      {/* Header */}
      <header className="px-6 pt-5 pb-0 border-b flex-shrink-0" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
        <div className="flex items-center gap-2 mb-2">
          <span className="rounded border px-2 py-0.5 font-mono text-[11px] font-semibold" style={{ borderColor: `${COLORS.primary.main}4D`, backgroundColor: `${COLORS.primary.main}1A`, color: COLORS.primary.lightText }}>
            ANALYTICS ENGINE
          </span>
        </div>
        <h2 className="font-headline-md text-2xl font-bold mb-4" style={{ color: COLORS.text.heading }}>
          Analytics &amp; Patterns
        </h2>
        {/* Tabs */}
        <div className="flex gap-6 font-body-sm text-sm font-semibold">
          <button
            onClick={() => setActiveTab('hotspot')}
            className="pb-3 border-b-2 transition-colors cursor-pointer"
            style={{
              borderColor: activeTab === 'hotspot' ? COLORS.primary.main : 'transparent',
              color: activeTab === 'hotspot' ? COLORS.primary.light : COLORS.text.muted,
            }}
          >
            Hotspot Map
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className="pb-3 border-b-2 transition-colors cursor-pointer"
            style={{
              borderColor: activeTab === 'trends' ? COLORS.primary.main : 'transparent',
              color: activeTab === 'trends' ? COLORS.primary.light : COLORS.text.muted,
            }}
          >
            Trend Analysis
          </button>
          <button
            onClick={() => setActiveTab('offenders')}
            className="pb-3 border-b-2 transition-colors cursor-pointer"
            style={{
              borderColor: activeTab === 'offenders' ? COLORS.primary.main : 'transparent',
              color: activeTab === 'offenders' ? COLORS.primary.light : COLORS.text.muted,
            }}
          >
            Offender Risk Board
          </button>
        </div>
      </header>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-margin-desktop custom-scrollbar">
        <AnimatePresence mode="wait">
          {/* TAB 1: Hotspot Map */}
          {activeTab === 'hotspot' && (
            <motion.div
              key="hotspot"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col xl:flex-row gap-lg h-full"
            >
              {/* LEFT SIDE (70%) */}
              <div className="flex-1 xl:w-[70%] flex flex-col gap-sm">
                <div className="flex-1 bg-surface border border-outline-variant relative overflow-hidden flex flex-col min-h-[400px]">
                  {/* Map Container */}
                  <div className="flex-1 relative check-bg" style={{ backgroundColor: COLORS.background.dark }}>
                    <div
                      className="absolute inset-0 bg-cover bg-center opacity-40 mix-blend-luminosity grayscale pointer-events-none"
                      style={{
                        backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuBC6RgexodwX06JxrK6CFVtTutT9lHZIM2zd2Vmy5vPURgfV22mHeZ9viC8pL9zd3CChiNTh5E_ZNOVWpzk7fZL9VnG9DR6-u-YXlq4wL4vKbYw7EaOzwbZ4V80vLblW-k9I3O8YxqRx_2X4GdTN3dqzvIqLSogMn9FT7pXmXgOwumZUJ1Wa8OkBD22rwEEWzHErH_RyNv1-j0BupCh0_SAfCRkrUY77PdEejlDuTbL-a8Fh6ZIjF4ted3uqIa6En2TJhKplKh9TCE')`,
                      }}
                    ></div>
                    <div className="absolute inset-0 map-overlay pointer-events-none"></div>

                    {/* Heat Overlays */}
                    {getHotspotPositions().map((spot) => (
                      <div
                        key={spot.id}
                        className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full blur-xl transition-all duration-700 ease-out pointer-events-none"
                        style={{
                          top: `${spot.top}%`,
                          left: `${spot.left}%`,
                          width: `${spot.size}px`,
                          height: `${spot.size}px`,
                          background: `radial-gradient(circle, ${spot.color} 0%, rgba(0,0,0,0) 70%)`,
                        }}
                      ></div>
                    ))}

                    {/* Controls */}
                    <div className="absolute top-sm right-sm flex flex-col gap-xs z-10">
                      <button className="w-8 h-8 bg-surface border border-outline-variant flex items-center justify-center text-on-surface hover:border-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined text-[18px]">add</span>
                      </button>
                      <button className="w-8 h-8 bg-surface border border-outline-variant flex items-center justify-center text-on-surface hover:border-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined text-[18px]">remove</span>
                      </button>
                    </div>

                    <div className="absolute top-4 left-4 bg-black border border-white/10 p-2.5 rounded-none font-mono text-[9px] font-black text-white/40 tracking-[0.15em] uppercase">
                      CAMERA GRID ACTIVE // ANPR_LINKED
                    </div>
                  </div>

                  {/* Timeline Slider */}
                  <div className="p-4 border-t" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
                    <div className="flex justify-between font-mono text-xs mb-2">
                      <span style={{ color: COLORS.text.muted }}>JAN 2023</span>
                      <span className="font-bold tracking-wide" style={{ color: COLORS.primary.main }}>
                        CURRENT WINDOW: {getSliderMonth(sliderVal)}
                      </span>
                      <span style={{ color: COLORS.text.muted }}>DEC 2025</span>
                    </div>
                    <div className="relative w-full h-4 flex items-center">
                      <input
                        className="w-full cursor-pointer"
                        max="36"
                        min="1"
                        type="range"
                        value={sliderVal}
                        onChange={(e) => setSliderVal(Number(e.target.value))}
                        style={{ accentColor: COLORS.primary.main }}
                      />
                    </div>
                    <div className="flex justify-between w-full mt-1 px-1">
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                      <div className="w-px h-2" style={{ backgroundColor: COLORS.border.default }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT SIDE (30%) */}
              <div className="w-full xl:w-[30%] flex flex-col gap-4 shrink-0">
                {/* Panel 1: Emerging Clusters */}
                <div className="border flex flex-col rounded-lg overflow-hidden" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
                  <div className="p-3 border-b" style={{ borderColor: COLORS.border.default, backgroundColor: COLORS.background.dark }}>
                    <h3 className="font-mono text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.heading }}>
                      Emerging Clusters
                    </h3>
                  </div>
                  <div className="divide-y" style={{ borderColor: COLORS.border.default }}>
                    {EMERGING_CLUSTERS.map((cl) => {
                      const isActive = selectedCluster.id === cl.id;
                      return (
                        <div
                          key={cl.id}
                          onClick={() => setSelectedCluster(cl)}
                          className="p-3 border-l-2 transition-colors cursor-pointer flex flex-col gap-1"
                          style={{
                            borderLeftColor: isActive ? COLORS.primary.main : 'transparent',
                            backgroundColor: isActive ? `${COLORS.primary.main}12` : 'transparent',
                          }}
                        >
                          <div className="flex justify-between items-start">
                            <span className="text-sm font-semibold" style={{ color: COLORS.text.heading }}>
                              {cl.name}
                            </span>
                            <span className="font-mono text-xs font-bold" style={{ color: COLORS.status.errorSoft }}>
                              {cl.change}
                            </span>
                          </div>
                          <span className="font-mono text-xs uppercase" style={{ color: COLORS.text.muted }}>
                            {cl.location}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Panel 2: Cluster Details */}
                <div className="border flex flex-col flex-1 rounded-lg overflow-hidden min-h-[300px]" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
                  <div className="p-3 border-b flex justify-between items-center" style={{ borderColor: COLORS.border.default, backgroundColor: COLORS.background.dark }}>
                    <h3 className="font-mono text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.heading }}>
                      Cluster Details
                    </h3>
                    <span className="font-mono text-[10px] border px-1.5 py-0.5 rounded font-bold" style={{ color: COLORS.primary.lightText, borderColor: `${COLORS.primary.main}66`, backgroundColor: `${COLORS.primary.main}22` }}>
                      {selectedCluster.location.replace(' ', '_')}_02
                    </span>
                  </div>
                  <div className="p-4 flex flex-col gap-4">
                    <div className="grid grid-cols-2 gap-4 border-b pb-4 font-mono text-xs" style={{ borderColor: COLORS.border.default }}>
                      <div>
                        <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
                          INCIDENTS
                        </div>
                        <div className="font-mono text-xl font-bold" style={{ color: COLORS.text.heading }}>
                          {selectedCluster.incidents}
                        </div>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
                          RANGE
                        </div>
                        <div className="font-mono text-sm font-bold mt-1" style={{ color: COLORS.text.heading }}>
                          {selectedCluster.rangeDays} DAYS
                        </div>
                      </div>
                    </div>
                    <div className="border-b pb-4" style={{ borderColor: COLORS.border.default }}>
                      <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
                        PRIMARY TYPE
                      </div>
                      <div className="text-sm font-semibold flex items-center gap-2 uppercase tracking-wide" style={{ color: COLORS.status.errorSoft }}>
                        <span className="material-symbols-outlined text-[16px]">warning</span>
                        {selectedCluster.primaryType}
                      </div>
                    </div>
                    <div className="flex-1 flex flex-col">
                      <div className="font-mono text-[10px] mb-2" style={{ color: COLORS.text.muted }}>
                        HOURLY DISTRIBUTION (24H)
                      </div>
                      <div className="flex-1 flex items-end justify-between gap-1 h-24 pt-4 border-b" style={{ borderColor: COLORS.border.default }}>
                        {selectedCluster.hourlyDistribution.map((hVal, idx) => (
                          <div
                            key={idx}
                            title={`Hour ${idx}: ${hVal} occurrences`}
                            className="w-full transition-colors rounded-t-sm"
                            style={{ height: `${hVal}%`, backgroundColor: hVal > 25 ? COLORS.primary.main : COLORS.border.default }}
                          ></div>
                        ))}
                      </div>
                      <div className="flex justify-between font-mono text-[10px] mt-1" style={{ color: COLORS.text.muted }}>
                        <span>00:00</span>
                        <span>12:00</span>
                        <span>23:59</span>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowLogDialog(true)}
                      className="w-full border font-mono text-xs font-bold py-2 transition-colors flex items-center justify-center gap-2 mt-2 cursor-pointer rounded"
                      style={{ borderColor: COLORS.border.default, color: COLORS.text.heading, backgroundColor: `${COLORS.primary.main}12` }}
                    >
                      <span className="material-symbols-outlined text-[16px]">visibility</span>
                      VIEW DETAILED LOG
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
              className="space-y-6"
            >
              <div className="bg-surface border border-outline-variant p-5 rounded-none">
                <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
                  Monthly Resolution Rate Trajectory (2024)
                </h3>
                <div className="h-44 flex items-end justify-between gap-2 border-b border-white/10 pb-2 font-mono text-[9px] font-bold">
                  {[
                    { m: 'Jan', rate: 35, height: 52 },
                    { m: 'Feb', rate: 42, height: 63 },
                    { m: 'Mar', rate: 48, height: 72 },
                    { m: 'Apr', rate: 52, height: 78 },
                    { m: 'May', rate: 50, height: 75 },
                    { m: 'Jun', rate: 58, height: 87 },
                    { m: 'Jul', rate: 64, height: 96 },
                    { m: 'Aug', rate: 62, height: 93 },
                    { m: 'Sep', rate: 68, height: 102 },
                    { m: 'Oct', rate: 75, height: 112 }
                  ].map((item, idx) => (
                    <div key={idx} className="w-full flex flex-col items-center">
                      <span className="font-black mb-1" style={{ color: COLORS.accent.cyan }}>{item.rate}%</span>
                      <div
                        className="w-8 rounded-none transition-all duration-500"
                        style={{ height: `${item.height}px`, backgroundColor: COLORS.accent.cyan }}
                      ></div>
                      <span className="text-white/40 mt-1.5 uppercase font-black tracking-wider text-[8px]">
                        {item.m}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-surface border border-outline-variant p-5 rounded-none">
                <h3 className="text-[10px] font-mono font-black text-white/40 uppercase mb-4 tracking-[0.15em]">
                  Weekly crime Occurrence Peak Times (Days)
                </h3>
                <div className="h-44 flex items-end justify-between gap-3 border-b border-white/10 pb-2 font-mono text-[9px] font-bold">
                  {[
                    { d: 'MON', crime: 30, height: 39 },
                    { d: 'TUE', crime: 28, height: 36 },
                    { d: 'WED', crime: 35, height: 45 },
                    { d: 'THU', crime: 45, height: 58 },
                    { d: 'FRI', crime: 72, height: 93 },
                    { d: 'SAT', crime: 88, height: 114 },
                    { d: 'SUN', crime: 64, height: 83 }
                  ].map((item, idx) => (
                    <div key={idx} className="w-full flex flex-col items-center">
                      <span className="font-black mb-1" style={{ color: COLORS.status.error }}>{item.crime}</span>
                      <div
                        className="w-10 rounded-none transition-all duration-500"
                        style={{
                          height: `${item.height}px`,
                          backgroundColor: item.crime > 60 ? COLORS.status.error : `${COLORS.status.error}4D`
                        }}
                      ></div>
                      <span className="text-white/40 mt-1.5 uppercase font-black tracking-wider text-[8px]">
                        {item.d}
                      </span>
                    </div>
                  ))}
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
              className="space-y-4"
            >
              {/* Search bar offenders filter */}
              <div className="max-w-md relative border border-outline-variant flex items-center px-3 py-2 rounded-none" style={{ backgroundColor: COLORS.background.dark }}>
                <span className="material-symbols-outlined text-outline text-[18px] mr-2">filter_alt</span>
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
                {MOCK_SUSPECTS.filter((s) => s.name.toLowerCase().includes(offenderSearch.toLowerCase())).map((sus) => (
                  <div
                    key={sus.id}
                    className="bg-surface border border-outline-variant p-4 rounded-none flex flex-col justify-between group transition-all"
                    style={{ backgroundColor: COLORS.surface.panel }}
                  >
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-black text-white uppercase tracking-tight text-sm">{sus.name}</h4>
                          <span className="text-[9px] font-mono text-white/40 font-black tracking-wider uppercase">
                            ID: {sus.id} // AGE: {sus.age}
                          </span>
                        </div>
                        <span
                          className="text-[8px] font-mono font-black border px-1.5 py-0.5 rounded-none uppercase tracking-wider"
                          style={{
                            borderColor: sus.status === 'HIGH-RISK' ? COLORS.status.error : COLORS.status.amber,
                            color: sus.status === 'HIGH-RISK' ? COLORS.status.error : COLORS.status.amber,
                          }}
                        >
                          {sus.status}
                        </span>
                      </div>

                      <p className="text-xs text-white/70 leading-relaxed font-sans mb-4 pt-1.5 border-t border-outline-variant">
                        {sus.bio}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-outline-variant font-mono text-[9px] font-black uppercase tracking-wider">
                      <span className="text-white/40">
                        Risk Score: <strong className="text-white">{sus.riskScore}%</strong>
                      </span>
                      <span className="text-primary tracking-wider font-black uppercase">
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
              <div className="p-4 border-b border-white/10 bg-black flex justify-between items-center font-mono">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">table_chart</span>
                  <span className="text-[10px] font-mono font-black tracking-[0.15em] text-primary uppercase">
                    INCIDENT LOGS // {selectedCluster.name.toUpperCase()}
                  </span>
                </div>
                <button
                  onClick={() => setShowLogDialog(false)}
                  className="text-white/40 hover:text-white transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">close</span>
                </button>
              </div>

              {/* logs body */}
              <div className="p-5 max-h-[350px] overflow-y-auto custom-scrollbar bg-black space-y-3 font-mono text-xs">
                {getSimulatedLogs().map((log, idx) => (
                  <div key={idx} className="p-3 border border-white/10 rounded-none bg-black/40 space-y-1.5">
                    <div className="flex justify-between text-[9px] text-white/40 font-black uppercase">
                      <span>{log.time}</span>
                      <span style={{ color: COLORS.accent.cyan }}>{log.loc}</span>
                    </div>
                    <p className="text-white/80 text-xs leading-snug font-sans">{log.desc}</p>
                  </div>
                ))}
              </div>

              <div className="p-4 border-t border-white/10 bg-black flex justify-end">
                <button
                  onClick={() => setShowLogDialog(false)}
                  className="px-4 py-2 bg-primary hover:bg-inverse-primary text-white text-[10px] font-black rounded-none font-mono tracking-wider transition-colors cursor-pointer uppercase"
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
