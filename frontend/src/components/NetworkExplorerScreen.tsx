/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MOCK_SUSPECTS } from '../data/mockData';
import { SuspectProfile } from '../types';
import { useNetworkGraph, useAccusedProfile, useSearchAccused } from '../hooks/useNetworkGraph';
import { NetworkGraphFilters, NetworkGraphView, NetworkGraphNode } from '../types/network';
import { NetworkGraph } from './network/NetworkGraph';

export default function NetworkExplorerScreen() {
  const [activeSegment, setActiveSegment] = useState<NetworkGraphView>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [selectedDistrict, setSelectedDistrict] = useState('All Districts');
  const [selectedCrimeType, setSelectedCrimeType] = useState('All Types');
  const [selectedDateRange, setSelectedDateRange] = useState('Last 30 Days');
  
  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  
  // Search for accused
  const { data: searchResults, isLoading: searchLoading, error: searchError } = useSearchAccused(debouncedSearchQuery);

  // Convert date range to actual dates
  const getDateRange = () => {
    const now = new Date();
    const toDate = now.toISOString().split('T')[0];
    
    let fromDate: string | null = null;
    
    if (selectedDateRange === 'Last 30 Days') {
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      fromDate = thirtyDaysAgo.toISOString().split('T')[0];
    } else if (selectedDateRange === 'Last 6 Months') {
      const sixMonthsAgo = new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000);
      fromDate = sixMonthsAgo.toISOString().split('T')[0];
    } else if (selectedDateRange === 'Year to Date') {
      const yearStart = new Date(now.getFullYear(), 0, 1);
      fromDate = yearStart.toISOString().split('T')[0];
    }
    
    return { date_from: fromDate, date_to: toDate };
  };

  // Network graph filters
  const [filters, setFilters] = useState<NetworkGraphFilters>({
    view: 'all',
  });

  // Update filters when filter values change
  React.useEffect(() => {
    const { date_from, date_to } = getDateRange();
    
    setFilters({
      view: activeSegment,
      crime_type: selectedCrimeType === 'All Types' ? null : selectedCrimeType,
      district: selectedDistrict === 'All Districts' ? null : selectedDistrict,
      date_from,
      date_to,
    });
  }, [selectedDistrict, selectedCrimeType, selectedDateRange, activeSegment]);
  
  // Selected Profile state
  const [selectedProfile, setSelectedProfile] = useState<SuspectProfile | null>(null);
  const [showBriefingDialog, setShowBriefingDialog] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedAccusedId, setSelectedAccusedId] = useState<number | null>(null);
  
  // Fetch live graph data
  const { data: graphData, isLoading, error } = useNetworkGraph(filters);

  // Use live API data when available, fallback to mock for empty/error states
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  // Fetch accused profile when a node is selected
  const { data: profileData, isLoading: profileLoading, error: profileError } = useAccusedProfile(selectedAccusedId);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    // Find corresponding node data
    const node = nodes.find((n: NetworkGraphNode) => n.id === nodeId);
    if (node && node.type === 'accused') {
      // Extract accused_id from node and fetch real profile
      if (node.accused_id) {
        setSelectedAccusedId(node.accused_id);
      } else {
        // Fallback to mock if no accused_id
        const suspect = MOCK_SUSPECTS.find(s => s.name === node.label);
        if (suspect) {
          setSelectedProfile(suspect);
        }
      }
    }
  };

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
        <NetworkGraph
          nodes={nodes}
          edges={edges}
          selectedNodeId={selectedNodeId}
          onNodeClick={handleNodeClick}
        />

        {/* LEFT FLOATING PANEL: Filters */}
        <div className="absolute left-lg top-lg w-72 bg-[#111318] panel-border rounded-lg shadow-xl flex flex-col z-20 max-h-[calc(100%-48px)] overflow-y-auto">
          <div className="p-4 border-b border-[#252830]">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">
              Filters
            </h3>
          </div>
          <div className="p-4 flex flex-col gap-4">
            {/* Search */}
            <div className="relative">
              <div className="relative input-border rounded-DEFAULT bg-[#0A0C10] flex items-center px-3 py-2">
                <span className="material-symbols-outlined text-outline text-[18px] mr-2">search</span>
                <input
                  className="bg-transparent border-none p-0 text-sm text-on-surface placeholder:text-outline w-full focus:ring-0 outline-none"
                  placeholder="Search by name..."
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setShowSearchResults(e.target.value.length >= 2);
                  }}
                  onFocus={() => setShowSearchResults(searchQuery.length >= 2)}
                  onBlur={() => setTimeout(() => setShowSearchResults(false), 200)}
                />
              </div>
              
              {/* Search Results Dropdown */}
              <AnimatePresence>
                {showSearchResults && searchQuery.length >= 2 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full left-0 right-0 mt-2 bg-[#111318] border border-[#252830] rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto"
                  >
                    {searchLoading ? (
                      <div className="p-3 text-center text-on-surface-variant text-sm">Searching...</div>
                    ) : searchError ? (
                      <div className="p-3 text-center text-error text-sm">
                        Error: {String(searchError)}
                      </div>
                    ) : searchResults && searchResults.results.length > 0 ? (
                      searchResults.results.map((result: any) => (
                        <div
                          key={result.accused_id}
                          className="p-3 hover:bg-[#1A1D24] cursor-pointer border-b border-[#252830] last:border-b-0"
                          onClick={() => {
                            setSearchQuery(result.name);
                            setShowSearchResults(false);
                            setSelectedAccusedId(result.accused_id);
                            // Find and select the node in the graph
                            const node = nodes.find((n: NetworkGraphNode) => n.accused_id === result.accused_id);
                            if (node) {
                              setSelectedNodeId(node.id);
                            }
                          }}
                        >
                          <div className="text-sm text-on-surface font-medium">{result.name}</div>
                          <div className="text-xs text-on-surface-variant mt-1">
                            {result.fir_count} FIRs • Risk: {result.risk_score}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-3 text-center text-on-surface-variant text-sm">No results found</div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
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
                <option>Bengaluru North</option>
                <option>Bengaluru South</option>
                <option>Mysuru Central</option>
                <option>Belagavi</option>
                <option>Mangalore</option>
                <option>Dharwad</option>
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
                <option>Murder</option>
                <option>Robbery</option>
                <option>Chain Snatching</option>
                <option>Vehicle Theft</option>
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
        {(selectedProfile || profileData) && (
          <div className="absolute right-lg top-lg w-80 bg-[#111318] panel-border rounded-lg shadow-xl flex flex-col z-20">
            {profileLoading && (
              <div className="p-4 text-center text-on-surface-variant text-sm">Loading profile...</div>
            )}
            {profileError && (
              <div className="p-4 text-center text-error text-sm">Error loading profile</div>
            )}
            {!profileLoading && !profileError && (
              <>
                <div className="p-4 border-b border-[#252830] flex justify-between items-start">
                  <div>
                    <div className="text-xs text-error font-label-mono mb-1 uppercase tracking-wider">
                      Selected Profile
                    </div>
                    <h3 className="font-headline-md text-[20px] font-bold text-on-surface leading-tight">
                      {profileData?.name || selectedProfile?.name}
                    </h3>
                    <p className="text-sm text-on-surface-variant mt-1">
                      Age: {profileData?.age || selectedProfile?.age} | Gender: {profileData?.gender || selectedProfile?.gender}
                    </p>
                  </div>
                  <button 
                    onClick={() => {
                      setSelectedProfile(null);
                      setSelectedAccusedId(null);
                    }}
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
                      <span className="text-error font-data-mono-bold">
                        {profileData?.risk_score || selectedProfile?.riskScore}/100
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-[#0A0C10] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-error rounded-full"
                        style={{ width: `${profileData?.risk_score || selectedProfile?.riskScore}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* Stats */}
                  <div className="bg-[#0A0C10] p-3 rounded-DEFAULT border border-[#252830]">
                    <p className="text-sm text-on-surface">
                      Appears in{' '}
                      <span className="font-data-mono-bold text-primary">
                        {profileData?.fir_count || selectedProfile?.firsCount} FIRs
                      </span>
                      {' '}across{' '}
                      {profileData?.firs && profileData.firs.length > 0 && (
                        <span className="font-data-mono-bold text-primary">
                          {new Set(profileData.firs.map((f: any) => f.district)).size} districts
                        </span>
                      )}
                      {!profileData?.firs && selectedProfile && (
                        <span className="font-data-mono-bold text-primary">
                          {selectedProfile.districtsCount} districts
                        </span>
                      )}
                    </p>
                  </div>
                  {/* Connections */}
                  <div>
                    <h4 className="text-xs font-semibold text-on-surface-variant mb-2 uppercase tracking-wider border-b border-[#252830] pb-1">
                      Connected to
                    </h4>
                    <ul className="flex flex-col gap-2">
                      {profileData?.co_accused && profileData.co_accused.length > 0 ? (
                        profileData.co_accused.map((conn: any, idx: number) => (
                          <li key={idx} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-[#ffb4ab]"></div>
                              <span className="text-on-surface">{conn.name}</span>
                            </div>
                            <span className="text-xs text-outline font-label-mono border border-[#252830] px-1 rounded-sm">
                              {conn.times_together} FIRs
                            </span>
                          </li>
                        ))
                      ) : selectedProfile?.connections ? (
                        selectedProfile.connections.map((conn, idx) => (
                          <li key={idx} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-[#ffb4ab]"></div>
                              <span className="text-on-surface">{conn.name}</span>
                            </div>
                            <span className="text-xs text-outline font-label-mono border border-[#252830] px-1 rounded-sm">
                              {conn.type}
                            </span>
                          </li>
                        ))
                      ) : (
                        <li className="text-sm text-on-surface-variant">No connections data</li>
                      )}
                    </ul>
                  </div>
                  {/* Crime Types */}
                  {profileData?.crime_types && profileData.crime_types.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-on-surface-variant mb-2 uppercase tracking-wider border-b border-[#252830] pb-1">
                        Crime Types
                      </h4>
                      <ul className="flex flex-col gap-2">
                        {profileData.crime_types.map((ct: any, idx: number) => (
                          <li key={idx} className="flex items-center justify-between text-sm">
                            <span className="text-on-surface">{ct.name}</span>
                            <span className="text-xs text-outline font-label-mono">{ct.count}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </>
            )}
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
