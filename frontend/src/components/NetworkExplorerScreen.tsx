/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MOCK_SUSPECTS } from '../data/mockData';
import { SuspectProfile } from '../types';
import { useNetworkGraph } from '../hooks/useNetworkGraph';
import { NetworkGraphFilters, NetworkGraphView } from '../types/network';

export default function NetworkExplorerScreen() {
  const [activeSegment, setActiveSegment] = useState<NetworkGraphView>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('All Districts');
  const [selectedCrimeType, setSelectedCrimeType] = useState('All Types');
  const [selectedDateRange, setSelectedDateRange] = useState('Last 30 Days');
  
  // Update filters when segment changes
  React.useEffect(() => {
    setFilters(prev => ({ ...prev, view: activeSegment }));
  }, [activeSegment]);
  
  // Selected Profile state
  const [selectedProfile, setSelectedProfile] = useState<SuspectProfile | null>(MOCK_SUSPECTS[0]);
  const [showBriefingDialog, setShowBriefingDialog] = useState(false);
  
  // Network graph filters
  const [filters, setFilters] = useState<NetworkGraphFilters>({
    view: 'all',
  });
  
  // Fetch live graph data
  const { data: graphData, isLoading, error } = useNetworkGraph(filters);

  // Use live API data when available, fallback to mock for empty/error states
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  
  // For now, keep mock positioning for visualization (will be replaced with D3 in Step 12)
  const getVisualNodes = () => {
    if (nodes.length === 0) {
      // Fallback to mock nodes when no data
      return [
        { id: 'SP-90210', name: 'Suresh Hegde', type: 'accused', cx: 60, cy: 50, isCentral: true },
        { id: 'SP-90211', name: 'K. Manjunath', type: 'accused', cx: 75, cy: 60 },
        { id: 'SP-90212', name: 'R. Ravi', type: 'accused', cx: 55, cy: 70 },
        { id: 'SP-90214', name: 'S. Kumar', type: 'accused', cx: 80, cy: 45 },
      ];
    }
    
    // Map API nodes to visual positions (simple circular layout for now)
    return nodes.map((node, index) => {
      const angle = (index / nodes.length) * 2 * Math.PI;
      const radius = 30;
      const cx = 50 + radius * Math.cos(angle);
      const cy = 50 + radius * Math.sin(angle);
      return {
        id: node.id,
        name: node.label,
        type: node.type === 'incident' ? 'crime' : node.type, // Map incident to crime for compatibility
        cx,
        cy,
        isCentral: node.centrality_score > 0.7,
      };
    });
  };

  const visualNodes = getVisualNodes();
  
  // Map API edges to visual connections
  const getVisualConnections = () => {
    if (edges.length === 0) {
      return [
        { from: 'SP-90210', to: 'SP-90211', thick: true },
        { from: 'SP-90210', to: 'SP-90212', thick: true },
        { from: 'SP-90210', to: 'SP-90214', thick: true },
      ];
    }
    
    return edges.map(edge => ({
      from: edge.source,
      to: edge.target,
      thick: edge.strength > 1,
    }));
  };

  const connections = getVisualConnections();

  const handleNodeClick = (node: any) => {
    if (node.type === 'accused') {
      const suspect = MOCK_SUSPECTS.find(s => s.name === node.name);
      if (suspect) {
        setSelectedProfile(suspect);
      }
    }
  };

  const filteredNodes = visualNodes.filter(node => {
    if (searchQuery) {
      return node.name.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  return (
    <div className="flex-1 flex flex-col relative h-screen bg-[#0A0C10]">
      {/* Header */}
      <header className="h-16 border-b border-[#252830] bg-[#111318] flex items-center justify-between px-lg shrink-0 z-40">
        <h2 className="font-headline-sm text-headline-sm text-on-surface">
          Network Explorer
        </h2>
        {isLoading && (
          <span className="text-xs text-on-surface-variant">Loading graph data...</span>
        )}
        {error && (
          <span className="text-xs text-error">Error loading graph</span>
        )}
        {/* Segmented Control */}
        <div className="flex items-center bg-[#0A0C10] p-1 rounded-DEFAULT border border-[#252830] text-sm font-medium">
          <button
            onClick={() => setActiveSegment('all')}
            className={`px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer ${
              activeSegment === 'all'
                ? 'bg-[#3B6FE8] text-white'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-[#1A1D24]'
            }`}
          >
            All Connections
          </button>
          <button
            onClick={() => setActiveSegment('clusters')}
            className={`px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer ${
              activeSegment === 'clusters'
                ? 'bg-[#3B6FE8] text-white'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-[#1A1D24]'
            }`}
          >
            Gang Clusters
          </button>
          <button
            onClick={() => setActiveSegment('repeat')}
            className={`px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer ${
              activeSegment === 'repeat'
                ? 'bg-[#3B6FE8] text-white'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-[#1A1D24]'
            }`}
          >
            Repeat Offenders
          </button>
        </div>
      </header>

      {/* Canvas Area */}
      <div className="flex-1 relative overflow-hidden" id="network-canvas">
        {/* Background Grid */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundSize: '24px 24px',
            backgroundImage:
              'linear-gradient(to right, #191b23 1px, transparent 1px), linear-gradient(to bottom, #191b23 1px, transparent 1px)',
            opacity: 0.3,
          }}
        ></div>

        {/* SVG Lines Layer */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
          {connections.map((conn, idx) => {
            const fromNode = filteredNodes.find(n => n.id === conn.from);
            const toNode = filteredNodes.find(n => n.id === conn.to);
            if (!fromNode || !toNode) return null;

            return (
              <line
                key={idx}
                className={conn.thick ? 'line-thick' : 'line-thin'}
                x1={`${fromNode.cx}%`}
                y1={`${fromNode.cy}%`}
                x2={`${toNode.cx}%`}
                y2={`${toNode.cy}%`}
                stroke={fromNode.isCentral || toNode.isCentral ? '#ffb4ab' : undefined}
                strokeOpacity={fromNode.isCentral || toNode.isCentral ? 0.5 : undefined}
              />
            );
          })}
        </svg>

        {/* Cluster Annotation */}
        {activeSegment === 'clusters' && (
          <>
            <div
              className="cluster-boundary"
              style={{ left: '20%', top: '35%', width: '25%', height: '25%' }}
            ></div>
            <div
              className="absolute text-primary text-xs font-label-mono bg-[#0A0C10] px-2 py-1 border border-[#003fa4] rounded-sm"
              style={{ left: '25%', top: '32%' }}
            >
              Cluster #3 — Suspected Gang
            </div>
          </>
        )}

        {/* Nodes Layer */}
        <div className="absolute inset-0 pointer-events-auto z-10">
          {filteredNodes.map((node) => {
            const isSelected = selectedProfile && selectedProfile.name === node.name;
            let nodeClass = '';
            if (node.type === 'accused') {
              nodeClass = node.isCentral ? 'node-accused node-high-centrality' : 'node-accused';
            } else if (node.type === 'crime') {
              nodeClass = 'node-crime';
            } else {
              nodeClass = 'node-location';
            }

            return (
              <div
                key={node.id}
                onClick={() => handleNodeClick(node)}
                className={`${nodeClass} transition-all duration-500 hover:scale-125 cursor-pointer`}
                style={{
                  left: `${node.cx}%`,
                  top: `${node.cy}%`,
                  transform: 'translate(-50%, -50%)',
                }}
                title={node.name}
              />
            );
          })}

          {/* Central Label for Suresh Hegde */}
          {filteredNodes.find(n => n.id === 'SP-90210') && (
            <div
              className="absolute text-error text-xs font-label-mono bg-[#111318] px-2 py-0.5 border border-[#93000a] rounded-sm whitespace-nowrap"
              style={{ left: 'calc(60% + 15px)', top: 'calc(50% - 10px)' }}
            >
              Suresh Hegde
            </div>
          )}
        </div>

        {/* LEFT FLOATING PANEL: Filters */}
        <div className="absolute left-lg top-lg w-72 bg-[#111318] panel-border rounded-lg shadow-xl flex flex-col z-20 max-h-[calc(100%-48px)] overflow-y-auto">
          <div className="p-4 border-b border-[#252830]">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">
              Filters
            </h3>
          </div>
          <div className="p-4 flex flex-col gap-4">
            {/* Search */}
            <div className="relative input-border rounded-DEFAULT bg-[#0A0C10] flex items-center px-3 py-2">
              <span className="material-symbols-outlined text-outline text-[18px] mr-2">search</span>
              <input
                className="bg-transparent border-none p-0 text-sm text-on-surface placeholder:text-outline w-full focus:ring-0 outline-none"
                placeholder="Search by name, location, case..."
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            {/* Dropdowns */}
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-on-surface-variant">District</label>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="bg-[#0A0C10] input-border text-sm text-on-surface rounded-DEFAULT p-2 focus:ring-0 focus:border-[#3b6fe8] outline-none"
              >
                <option>All Districts</option>
                <option>Central</option>
                <option>North</option>
                <option>South</option>
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-on-surface-variant">Crime Type</label>
              <select
                value={selectedCrimeType}
                onChange={(e) => setSelectedCrimeType(e.target.value)}
                className="bg-[#0A0C10] input-border text-sm text-on-surface rounded-DEFAULT p-2 focus:ring-0 focus:border-[#3b6fe8] outline-none"
              >
                <option>All Types</option>
                <option>Assault</option>
                <option>Theft</option>
                <option>Robbery</option>
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-on-surface-variant">Date Range</label>
              <select
                value={selectedDateRange}
                onChange={(e) => setSelectedDateRange(e.target.value)}
                className="bg-[#0A0C10] input-border text-sm text-on-surface rounded-DEFAULT p-2 focus:ring-0 focus:border-[#3b6fe8] outline-none"
              >
                <option>Last 30 Days</option>
                <option>Last 6 Months</option>
                <option>Year to Date</option>
              </select>
            </div>
          </div>
          {/* Legend */}
          <div className="mt-auto p-4 border-t border-[#252830] bg-[#0c0e15]">
            <h4 className="text-xs font-semibold text-on-surface-variant mb-3 uppercase tracking-wider">
              Legend
            </h4>
            <ul className="flex flex-col gap-2 text-sm text-on-surface">
              <li className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-[#ffb4ab] border border-[#93000a]"></div>
                <span>Accused</span>
              </li>
              <li className="flex items-center gap-3">
                <div className="w-3 h-3 bg-[#44474f] border border-[#191c22]"></div>
                <span>Crime Incident</span>
              </li>
              <li className="flex items-center gap-3">
                <div className="w-3 h-3 bg-[#b3c5ff] border border-[#003fa4] rotate-45"></div>
                <span>Location</span>
              </li>
            </ul>
          </div>
        </div>

        {/* RIGHT FLOATING PANEL: Entity Details */}
        {selectedProfile && (
          <div className="absolute right-lg top-lg w-80 bg-[#111318] panel-border rounded-lg shadow-xl flex flex-col z-20">
            <div className="p-4 border-b border-[#252830] flex justify-between items-start">
              <div>
                <div className="text-xs text-error font-label-mono mb-1 uppercase tracking-wider">
                  Selected Profile
                </div>
                <h3 className="font-headline-md text-[20px] font-bold text-on-surface leading-tight">
                  {selectedProfile.name}
                </h3>
                <p className="text-sm text-on-surface-variant mt-1">
                  Age: {selectedProfile.age} | Gender: {selectedProfile.gender}
                </p>
              </div>
              <button 
                onClick={() => setSelectedProfile(null)}
                className="text-outline hover:text-on-surface cursor-pointer"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div className="p-4 flex flex-col gap-5">
              {/* Risk Score */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-on-surface-variant">Risk Score</span>
                  <span className="text-error font-data-mono-bold">{selectedProfile.riskScore}/100</span>
                </div>
                <div className="h-1.5 w-full bg-[#0A0C10] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-error rounded-full"
                    style={{ width: `${selectedProfile.riskScore}%` }}
                  ></div>
                </div>
              </div>
              {/* Stats */}
              <div className="bg-[#0A0C10] p-3 rounded-DEFAULT border border-[#252830]">
                <p className="text-sm text-on-surface">
                  Appears in{' '}
                  <span className="font-data-mono-bold text-primary">{selectedProfile.firsCount} FIRs</span>
                  {' '}across{' '}
                  <span className="font-data-mono-bold text-primary">{selectedProfile.districtsCount} districts</span>
                </p>
              </div>
              {/* Connections */}
              <div>
                <h4 className="text-xs font-semibold text-on-surface-variant mb-2 uppercase tracking-wider border-b border-[#252830] pb-1">
                  Connected to
                </h4>
                <ul className="flex flex-col gap-2">
                  {selectedProfile.connections.map((conn, idx) => (
                    <li key={idx} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[#ffb4ab]"></div>
                        <span className="text-on-surface">{conn.name}</span>
                      </div>
                      <span className="text-xs text-outline font-label-mono border border-[#252830] px-1 rounded-sm">
                        {conn.type}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            {/* Footer Action */}
            <div className="p-4 border-t border-[#252830] bg-[#0c0e15] rounded-b-lg">
              <button
                onClick={() => setShowBriefingDialog(true)}
                className="w-full py-2 bg-transparent border border-[#252830] text-on-surface font-semibold text-sm hover:bg-[#191b23] transition-colors rounded-DEFAULT flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>View Full Profile</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* DETAILED BRIEFING DIALOG */}
      <AnimatePresence>
        {showBriefingDialog && selectedProfile && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#050505] border border-white/10 rounded-none shadow-2xl max-w-md w-full overflow-hidden"
            >
              <div className="p-4 border-b border-white/10 bg-black flex justify-between items-center select-none">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#ff4d4d] text-[18px]">warning</span>
                  <span className="text-xs font-mono font-black tracking-[0.2em] text-[#ff4d4d] uppercase">
                    INTELLIGENCE BRIEFING
                  </span>
                </div>
                <button
                  onClick={() => setShowBriefingDialog(false)}
                  className="text-white/40 hover:text-white transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">close</span>
                </button>
              </div>

              <div className="p-5 space-y-4">
                <div>
                  <h4 className="text-xl font-black text-white uppercase tracking-tight">
                    {selectedProfile.name}
                  </h4>
                  <div className="text-[10px] text-white/40 font-mono mt-1.5 uppercase tracking-wider">
                    TARGET ID: {selectedProfile.id} // Status: {selectedProfile.status}
                  </div>
                </div>

                <div className="space-y-2">
                  <h5 className="text-[9px] font-mono font-black text-white/40 uppercase tracking-[0.2em]">
                    EXECUTIVE PROFILE SUMMARY
                  </h5>
                  <p className="text-xs text-white/80 leading-relaxed font-mono bg-black p-3.5 border border-white/10">
                    {selectedProfile.bio || 'No executive brief logs on file for target ID.'}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 border border-white/10 bg-black flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[18px]">analytics</span>
                    <div>
                      <div className="text-[9px] text-white/40 font-mono leading-none uppercase tracking-wider">
                        RISK INDEX
                      </div>
                      <div className="font-black text-white font-mono mt-1 text-sm">
                        {selectedProfile.riskScore}%
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border border-white/10 bg-black flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[18px]">menu_book</span>
                    <div>
                      <div className="text-[9px] text-white/40 font-mono leading-none uppercase tracking-wider">
                        PRIMARY FOCUS
                      </div>
                      <div className="font-black text-white font-mono mt-1 text-sm uppercase">
                        {selectedProfile.recentCrime}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-white/10 bg-black flex justify-end gap-2">
                <button
                  onClick={() => setShowBriefingDialog(false)}
                  className="px-5 py-3 bg-[#3B6FE8] hover:bg-[#2b5bc2] text-white text-xs font-black font-mono transition-colors uppercase tracking-[0.2em] cursor-pointer"
                >
                  ACKNOWLEDGE BRIEFING
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
