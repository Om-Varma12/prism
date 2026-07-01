/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MOCK_SUSPECTS } from '../data/mockData';
import { SuspectProfile } from '../types';
import { 
  Search, 
  X, 
  ArrowRight, 
  Grid, 
  ShieldAlert, 
  BookOpen, 
  Activity, 
  CheckCircle, 
  UserPlus 
} from 'lucide-react';

export default function NetworkExplorerScreen() {
  const [activeSegment, setActiveSegment] = useState<'all' | 'gang' | 'repeat'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('All Districts');
  const [selectedCrimeType, setSelectedCrimeType] = useState('All Types');
  const [selectedDateRange, setSelectedDateRange] = useState('Last 30 Days');
  
  // Selected Profile state
  const [selectedProfile, setSelectedProfile] = useState<SuspectProfile>(MOCK_SUSPECTS[0]);
  const [showBriefingDialog, setShowBriefingDialog] = useState(false);

  // Nodes simulation positions based on segment selected
  const getNodes = () => {
    // Standard coordinates (percentages)
    const baseNodes = [
      { id: 'SP-90210', name: 'Suresh Hegde', type: 'accused', cx: 60, cy: 50, isCentral: true },
      { id: 'SP-90211', name: 'K. Manjunath', type: 'accused', cx: 75, cy: 60 },
      { id: 'SP-90212', name: 'R. Ravi', type: 'accused', cx: 55, cy: 70 },
      { id: 'SP-90214', name: 'S. Kumar', type: 'accused', cx: 80, cy: 45 },
      
      // Crime incidents
      { id: 'CR-001', name: 'FIR-2023-BN-0847', type: 'crime', cx: 40, cy: 45 },
      { id: 'CR-002', name: 'FIR-2023-BN-0912', type: 'crime', cx: 70, cy: 30 },
      
      // Locations
      { id: 'LO-001', name: 'Yelahanka Industrial Area', type: 'location', cx: 35, cy: 55 },
      { id: 'LO-002', name: 'Hebbal Flyover camera', type: 'location', cx: 80, cy: 25 },
      
      // Distant Nodes
      { id: 'SP-90213', name: 'Ramesh Gowda', type: 'accused', cx: 20, cy: 30 },
      { id: 'CR-003', name: 'FIR-2023-MW-0502', type: 'crime', cx: 15, cy: 20 }
    ];

    if (activeSegment === 'gang') {
      // Pull nodes closer into distinct cluster groups
      return baseNodes.map(node => {
        if (node.id === 'SP-90210' || node.id === 'SP-90211' || node.id === 'SP-90212') {
          return { ...node, cx: node.cx - 5, cy: node.cy - 5 };
        }
        return node;
      });
    }

    if (activeSegment === 'repeat') {
      // Emphasize repeat offenders
      return baseNodes.map(node => {
        if (node.type === 'accused' && (node.id === 'SP-90210' || node.id === 'SP-90213')) {
          return { ...node, cy: node.cy - 10 }; // Lift repeat offenders
        }
        return node;
      });
    }

    return baseNodes;
  };

  const nodes = getNodes();

  // Draw lines connecting nodes based on relationships
  const getConnections = () => {
    return [
      { from: 'SP-90210', to: 'SP-90211', thick: true },
      { from: 'SP-90210', to: 'SP-90212', thick: true },
      { from: 'SP-90210', to: 'SP-90214', thick: true },
      { from: 'SP-90210', to: 'CR-001', thick: true },
      { from: 'SP-90211', to: 'LO-001', thick: false },
      { from: 'SP-90212', to: 'LO-001', thick: false },
      { from: 'CR-001', to: 'LO-001', thick: true },
      { from: 'SP-90214', to: 'CR-002', thick: false },
      { from: 'CR-002', to: 'LO-002', thick: true },
      { from: 'SP-90213', to: 'CR-003', thick: false }
    ];
  };

  const connections = getConnections();

  const handleNodeClick = (node: any) => {
    if (node.type === 'accused') {
      const suspect = MOCK_SUSPECTS.find(s => s.name === node.name);
      if (suspect) {
        setSelectedProfile(suspect);
      } else {
        // Create generic profile
        setSelectedProfile({
          id: node.id,
          name: node.name,
          age: 35,
          gender: 'Male',
          riskScore: 50,
          firsCount: 2,
          districtsCount: 1,
          connections: [
            { name: 'Suresh Hegde', type: 'ASSOC', status: 'HIGH-RISK' }
          ],
          recentCrime: 'Robbery',
          status: 'MONITORED',
          bio: 'Involved in active investigations. Status currently monitored under surveillance operations.'
        });
      }
    }
  };

  const filteredNodes = nodes.filter(node => {
    if (searchQuery) {
      return node.name.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] select-none relative">
      {/* Header section with segments */}
      <header className="h-16 border-b border-white/10 bg-black flex items-center justify-between px-6 shrink-0 z-10">
        <h2 className="text-xl font-black text-white tracking-tighter uppercase leading-none">
          NETWORK LINK EXPLORER
        </h2>
        
        {/* Segmented controls styling */}
        <div className="flex items-center bg-black p-1 border border-white/10 text-[10px] font-mono font-bold uppercase tracking-wider">
          <button 
            onClick={() => setActiveSegment('all')}
            className={`px-3.5 py-1.5 transition-colors ${
              activeSegment === 'all'
                ? 'bg-[#00F0FF] text-black font-black'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            All Connections
          </button>
          <button 
            onClick={() => setActiveSegment('gang')}
            className={`px-3.5 py-1.5 transition-colors ${
              activeSegment === 'gang'
                ? 'bg-[#00F0FF] text-black font-black'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Gang Clusters
          </button>
          <button 
            onClick={() => setActiveSegment('repeat')}
            className={`px-3.5 py-1.5 transition-colors ${
              activeSegment === 'repeat'
                ? 'bg-[#00F0FF] text-black font-black'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Repeat Offenders
          </button>
        </div>
      </header>

      {/* Main Workspace with canvas & side panes */}
      <div className="flex-1 relative overflow-hidden" id="network-canvas">
        {/* Dot background overlay for tactical mapping feel */}
        <div 
          className="absolute inset-0 pointer-events-none" 
          style={{
            backgroundSize: '24px 24px',
            backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)',
            opacity: 0.6
          }}
        ></div>

        {/* Bounding Cluster annotations */}
        <div className="absolute border border-dashed border-[#00F0FF]/30 rounded-full pointer-events-none bg-[#00F0FF]/5" 
          style={{ left: '22%', top: '35%', width: '26%', height: '26%' }}
        ></div>
        <div className="absolute text-[#00F0FF] text-[9px] font-mono font-black tracking-widest bg-black px-2 py-1 border border-[#00F0FF]/30 uppercase" 
          style={{ left: '25%', top: '32%' }}
        >
          CLUSTER #3 // SUSPECTED GANG
        </div>

        {/* SVG connection lines layer */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
          {connections.map((conn, idx) => {
            const fromNode = nodes.find(n => n.id === conn.from);
            const toNode = nodes.find(n => n.id === conn.to);
            if (!fromNode || !toNode) return null;

            return (
              <line 
                key={idx}
                x1={`${fromNode.cx}%`}
                y1={`${fromNode.cy}%`}
                x2={`${toNode.cx}%`}
                y2={`${toNode.cy}%`}
                stroke={fromNode.isCentral || toNode.isCentral ? '#00F0FF' : 'rgba(255,255,255,0.1)'}
                strokeWidth={conn.thick ? 2.5 : 1}
                strokeOpacity={fromNode.isCentral || toNode.isCentral ? 0.9 : 0.4}
                strokeDasharray={!conn.thick ? '4 4' : undefined}
              />
            );
          })}
        </svg>

        {/* Interactive nodes layer */}
        <div className="absolute inset-0 z-10 pointer-events-auto">
          {filteredNodes.map((node) => {
            const isSelected = selectedProfile && selectedProfile.name === node.name;
            return (
              <motion.div
                key={node.id}
                layout
                transition={{ duration: 0.5, ease: 'easeInOut' }}
                style={{ left: `${node.cx}%`, top: `${node.cy}%` }}
                onClick={() => handleNodeClick(node)}
                className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer flex flex-col items-center group"
              >
                {/* Visual node design */}
                {node.type === 'accused' ? (
                  <div className={`w-3.5 h-3.5 rounded-full border transition-all ${
                    node.isCentral 
                      ? 'bg-[#00F0FF] border-white w-5.5 h-5.5 shadow-[0_0_15px_rgba(0,240,255,0.6)] z-10 animate-pulse'
                      : isSelected
                      ? 'bg-[#00F0FF] border-white w-4.5 h-4.5 shadow-[0_0_8px_#00F0FF]'
                      : 'bg-[#00F0FF] border-black group-hover:scale-110'
                  }`}></div>
                ) : node.type === 'crime' ? (
                  <div className={`w-3 h-3 border transition-all ${
                    isSelected
                      ? 'bg-white border-[#00F0FF] w-4 h-4'
                      : 'bg-white/45 border-white/10 group-hover:scale-110'
                  }`}></div>
                ) : (
                  <div className={`w-3 h-3 rotate-45 border transition-all ${
                    isSelected
                      ? 'bg-[#00F0FF] border-white w-4 h-4'
                      : 'bg-white/20 border-white/10 group-hover:scale-110'
                  }`}></div>
                )}

                {/* Floating Node Title */}
                <span className={`mt-1.5 px-2 py-0.5 text-[9px] font-mono border whitespace-nowrap bg-black/95 transition-all uppercase tracking-wider ${
                  node.isCentral
                    ? 'border-[#00F0FF] text-[#00F0FF] font-black'
                    : isSelected
                    ? 'border-white text-white font-bold'
                    : 'border-white/10 text-white/60 opacity-85 group-hover:opacity-100'
                }`}>
                  {node.name}
                </span>
              </motion.div>
            );
          })}
        </div>

        {/* FLOATING FILTER PANEL (Left Column overlay) */}
        <div className="absolute left-6 top-6 w-72 bg-black/95 border border-white/10 rounded-none shadow-2xl flex flex-col z-20 max-h-[calc(100%-48px)]">
          <div className="p-4 border-b border-white/10">
            <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">
              Tactical Filters
            </h3>
          </div>
          
          <div className="p-4 flex flex-col gap-4">
            {/* Query Input */}
            <div className="relative border border-white/10 bg-black flex items-center px-3.5 py-2">
              <Search className="w-4 h-4 text-white/30 mr-2 shrink-0" />
              <input 
                type="text"
                placeholder="Search suspect name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent border-none p-0 text-xs text-white placeholder-white/20 w-full outline-none focus:ring-0"
              />
            </div>

            {/* District filter dropdown */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-mono font-black text-white/40 tracking-[0.2em] uppercase">District</label>
              <select 
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="w-full bg-black border border-white/10 text-xs text-white/80 p-2.5 focus:ring-0 focus:border-[#00F0FF] outline-none"
              >
                <option>All Districts</option>
                <option>Central</option>
                <option>North</option>
                <option>South</option>
              </select>
            </div>

            {/* Crime Type */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-mono font-black text-white/40 tracking-[0.2em] uppercase">Crime Type</label>
              <select 
                value={selectedCrimeType}
                onChange={(e) => setSelectedCrimeType(e.target.value)}
                className="w-full bg-black border border-white/10 text-xs text-white/80 p-2.5 focus:ring-0 focus:border-[#00F0FF] outline-none"
              >
                <option>All Types</option>
                <option>Assault</option>
                <option>Theft</option>
                <option>Robbery</option>
              </select>
            </div>

            {/* Date Range */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-mono font-black text-white/40 tracking-[0.2em] uppercase">Date Range</label>
              <select 
                value={selectedDateRange}
                onChange={(e) => setSelectedDateRange(e.target.value)}
                className="w-full bg-black border border-white/10 text-xs text-white/80 p-2.5 focus:ring-0 focus:border-[#00F0FF] outline-none"
              >
                <option>Last 30 Days</option>
                <option>Last 6 Months</option>
                <option>Year to Date</option>
              </select>
            </div>
          </div>

          {/* Legend indicator */}
          <div className="mt-auto p-4 border-t border-white/10 bg-white/5">
            <h4 className="text-[9px] font-mono font-black text-white/40 mb-3 uppercase tracking-[0.2em]">Legend</h4>
            <ul className="flex flex-col gap-2.5 text-xs text-white/80">
              <li className="flex items-center gap-2.5">
                <div className="w-3.5 h-3.5 rounded-full bg-[#00F0FF] border border-white"></div>
                <span className="font-mono text-[10px] uppercase font-bold tracking-wider">Accused</span>
              </li>
              <li className="flex items-center gap-2.5">
                <div className="w-3.5 h-3.5 bg-white border border-white/10"></div>
                <span className="font-mono text-[10px] uppercase font-bold tracking-wider">Crime Incident</span>
              </li>
              <li className="flex items-center gap-2.5">
                <div className="w-3.5 h-3.5 bg-white/20 border border-white/10 rotate-45"></div>
                <span className="font-mono text-[10px] uppercase font-bold tracking-wider">Location Node</span>
              </li>
            </ul>
          </div>
        </div>

        {/* FLOATING PROFILE DETAIL PANEL (Right Column overlay) */}
        {selectedProfile && (
          <div className="absolute right-6 top-6 w-80 bg-black/95 border border-white/10 rounded-none shadow-2xl flex flex-col z-20">
            {/* Profile heading details */}
            <div className="p-4 border-b border-white/10 flex justify-between items-start">
              <div>
                <div className="text-[9px] text-[#00F0FF] font-mono mb-1 uppercase tracking-[0.2em] font-black">
                  Selected Profile // Intel
                </div>
                <h3 className="text-lg font-black tracking-tight text-white uppercase">
                  {selectedProfile.name}
                </h3>
                <p className="text-xs text-white/50 mt-1.5 font-mono">
                  Age: {selectedProfile.age} | Gender: {selectedProfile.gender}
                </p>
              </div>
              <button 
                onClick={() => setSelectedProfile(MOCK_SUSPECTS[0])}
                className="text-white/40 hover:text-[#00F0FF] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Profile statistics */}
            <div className="p-4 flex flex-col gap-4">
              {/* Risk Score indicator */}
              <div>
                <div className="flex justify-between text-[10px] font-mono font-black tracking-wider mb-1">
                  <span className="text-white/40 uppercase">THREAT INDEX</span>
                  <span className="text-[#00F0FF] font-bold">{selectedProfile.riskScore}/100</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-[#00F0FF] rounded-full" 
                    style={{ width: `${selectedProfile.riskScore}%` }}
                  ></div>
                </div>
              </div>

              {/* Distrist count info */}
              <div className="bg-white/5 p-3 border border-white/10 text-xs leading-relaxed font-mono text-white/70">
                Appears in <span className="text-[#00F0FF] font-black">{selectedProfile.firsCount} FIRs</span> across <span className="text-[#00F0FF] font-black">{selectedProfile.districtsCount} districts</span>
              </div>

              {/* Connections list */}
              <div>
                <h4 className="text-[9px] font-mono font-black text-white/40 mb-2.5 uppercase tracking-[0.2em] border-b border-white/10 pb-1">
                  Connected To
                </h4>
                <ul className="space-y-2">
                  {selectedProfile.connections.map((conn, idx) => (
                    <li key={idx} className="flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#00F0FF]"></div>
                        <span className="text-white/80 font-bold">{conn.name}</span>
                      </div>
                      <span className="text-[9px] text-white/40 border border-white/10 px-1.5 py-0.5 uppercase tracking-wider font-bold">
                        {conn.type}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* View Profile brief detail button */}
            <div className="p-4 border-t border-white/10 bg-white/5">
              <button 
                onClick={() => setShowBriefingDialog(true)}
                className="w-full py-3 bg-[#00F0FF] hover:bg-white text-black font-black text-xs transition-colors flex items-center justify-center gap-2 font-mono uppercase tracking-[0.2em] cursor-pointer"
              >
                <span>View Full Profile</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* DETAILED LOG BRIEFING DIALOG */}
      <AnimatePresence>
        {showBriefingDialog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#050505] border border-white/10 rounded-none shadow-2xl max-w-md w-full overflow-hidden"
            >
              <div className="p-4 border-b border-white/10 bg-black flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-[#ff4d4d]" />
                  <span className="text-xs font-mono font-black tracking-[0.2em] text-[#ff4d4d] uppercase">
                    INTELLIGENCE BRIEFING
                  </span>
                </div>
                <button 
                  onClick={() => setShowBriefingDialog(false)}
                  className="text-white/40 hover:text-[#00F0FF] transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="p-5 space-y-4">
                <div>
                  <h4 className="text-xl font-black text-white uppercase tracking-tight">{selectedProfile.name}</h4>
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
                    <Activity className="w-4 h-4 text-[#00F0FF]" />
                    <div>
                      <div className="text-[9px] text-white/40 font-mono leading-none uppercase tracking-wider">RISK INDEX</div>
                      <div className="font-black text-white font-mono mt-1 text-sm">{selectedProfile.riskScore}%</div>
                    </div>
                  </div>
                  <div className="p-3 border border-white/10 bg-black flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-[#00F0FF]" />
                    <div>
                      <div className="text-[9px] text-white/40 font-mono leading-none uppercase tracking-wider">PRIMARY FOCUS</div>
                      <div className="font-black text-white font-mono mt-1 text-sm uppercase">{selectedProfile.recentCrime}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-white/10 bg-black flex justify-end gap-2">
                <button 
                  onClick={() => setShowBriefingDialog(false)}
                  className="px-5 py-3 bg-[#00F0FF] hover:bg-white text-black text-xs font-black font-mono transition-colors uppercase tracking-[0.2em] cursor-pointer"
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
