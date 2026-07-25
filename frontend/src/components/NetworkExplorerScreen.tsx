/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { SuspectProfile } from '../types';
import { useNetworkGraph, useAccusedProfile, useSearchAccused } from '../hooks/useNetworkGraph';
import { NetworkGraphFilters, NetworkGraphView, NetworkGraphNode } from '../types/network';
import { NetworkGraph } from './network/NetworkGraph';
import { COLORS } from '../constants/colors';

export default function NetworkExplorerScreen() {
  const [activeSegment, setActiveSegment] = useState<NetworkGraphView>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [selectedDistrict, setSelectedDistrict] = useState('All Districts');
  const [selectedCrimeType, setSelectedCrimeType] = useState('All Types');
  const [selectedDateRange, setSelectedDateRange] = useState('Last 30 Days');
  
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

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  
  // Search for accused (pass current filters to search)
  const { data: searchResults, isLoading: searchLoading, error: searchError } = useSearchAccused(debouncedSearchQuery, filters);
  
  // Selected Profile state
  const [selectedProfile, setSelectedProfile] = useState<SuspectProfile | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedAccusedId, setSelectedAccusedId] = useState<number | null>(null);
  const [selectedRowId, setSelectedRowId] = useState<number | null>(null);
  const [showProfilePanel, setShowProfilePanel] = useState(false);
  
  // Fetch live graph data
  const { data: graphData, isLoading, error } = useNetworkGraph(filters);

  // Use live API data when available
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  // Fetch accused profile when a node or search result is selected
  const { data: profileData, isLoading: profileLoading, error: profileError } = useAccusedProfile(selectedAccusedId, selectedRowId);


  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    // Find corresponding node data
    const node = nodes.find((n: NetworkGraphNode) => n.id === nodeId);
    if (node && node.type === 'accused') {
      if (node.accused_id) {
        // Node has an AccusedMasterID — use it directly
        setSelectedAccusedId(node.accused_id);
        setSelectedRowId(null);
      } else {
        // No AccusedMasterID — parse the ROWID embedded in the node ID (format: accused_{ROWID})
        const rowIdStr = node.id.replace('accused_', '');
        const parsedRowId = parseInt(rowIdStr, 10);
        if (!isNaN(parsedRowId)) {
          setSelectedRowId(parsedRowId);
          setSelectedAccusedId(null);
        } else {
          setSelectedRowId(null);
          setSelectedAccusedId(null);
        }
      }
      setShowProfilePanel(true);
    }
  };

  return (
    <div className="flex-1 flex flex-col relative h-screen check-bg" style={{ backgroundColor: COLORS.background.dark }}>
      {/* Header */}
      <header className="h-16 border-b flex items-center justify-between px-lg shrink-0 z-40" style={{ borderColor: COLORS.border.default, backgroundColor: COLORS.surface.panel }}>
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
        <div className="flex items-center p-1 rounded-DEFAULT border text-sm font-medium" style={{ backgroundColor: COLORS.background.dark, borderColor: COLORS.border.default }}>
          <button
            onClick={() => setActiveSegment('all')}
            className="px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer"
            style={{
              backgroundColor: activeSegment === 'all' ? COLORS.primary.main : 'transparent',
              color: activeSegment === 'all' ? COLORS.background.dark : COLORS.text.primary,
            }}
          >
            All Connections
          </button>
          <button
            onClick={() => setActiveSegment('clusters')}
            className="px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer"
            style={{
              backgroundColor: activeSegment === 'clusters' ? COLORS.primary.main : 'transparent',
              color: activeSegment === 'clusters' ? COLORS.background.dark : COLORS.text.primary,
            }}
          >
            Gang Clusters
          </button>
          <button
            onClick={() => setActiveSegment('repeat')}
            className="px-4 py-1.5 rounded-DEFAULT transition-colors cursor-pointer"
            style={{
              backgroundColor: activeSegment === 'repeat' ? COLORS.primary.main : 'transparent',
              color: activeSegment === 'repeat' ? COLORS.background.dark : COLORS.text.primary,
            }}
          >
            Repeat Offenders
          </button>
        </div>
      </header>

      {/* Canvas Area */}
      <div className="flex-1 relative overflow-hidden check-bg" id="network-canvas" style={{ backgroundColor: COLORS.background.dark }}>
        <NetworkGraph
          nodes={nodes}
          edges={edges}
          selectedNodeId={selectedNodeId}
          onNodeClick={handleNodeClick}
        />

        {/* LEFT FLOATING PANEL: Filters */}
        <div className="absolute left-lg top-lg w-72 panel-border rounded-lg shadow-xl flex flex-col z-20 max-h-[calc(100%-48px)] overflow-y-auto" style={{ backgroundColor: COLORS.surface.panel }}>
          <div className="p-4 border-b" style={{ borderColor: COLORS.border.default }}>
            <h3 className="font-headline-sm text-headline-sm" style={{ color: COLORS.text.heading }}>
              Filters
            </h3>
          </div>
          <div className="p-4 flex flex-col gap-4">
            {/* Search */}
            <div className="relative">
              <div className="relative input-border rounded-DEFAULT flex items-center px-3 py-2" style={{ backgroundColor: COLORS.background.dark }}>
                <span className="material-symbols-outlined text-[18px] mr-2" style={{ color: COLORS.text.muted }}>search</span>
                <input
                  className="bg-transparent border-none p-0 text-sm placeholder:text-outline w-full focus:ring-0 outline-none"
                  style={{ color: COLORS.text.primary }}
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
                    className="absolute top-full left-0 right-0 mt-2 border rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto"
                    style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}
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
                          className="p-3 cursor-pointer border-b last:border-b-0"
                          style={{ borderColor: COLORS.border.default }}
                          onClick={() => {
                            setSearchQuery(result.name);
                            setShowSearchResults(false);

                            // Try to find and highlight the node in the graph
                            const foundNode = nodes.find((n: any) =>
                              (result.accused_id && n.accused_id === result.accused_id) ||
                              (result.row_id && n.id === `accused_${result.row_id}`)
                            );
                            setSelectedNodeId(foundNode ? foundNode.id : null);

                            // Set the correct identifiers for profile loading
                            if (result.accused_id) {
                              setSelectedAccusedId(result.accused_id);
                              setSelectedRowId(null);
                            } else if (result.row_id) {
                              setSelectedRowId(result.row_id);
                              setSelectedAccusedId(null);
                            }
                            setShowProfilePanel(true);
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
                className="input-border text-sm rounded-DEFAULT p-2 focus:ring-0 outline-none"
                style={{ backgroundColor: COLORS.background.dark, color: COLORS.text.primary }}
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
                className="input-border text-sm rounded-DEFAULT p-2 focus:ring-0 outline-none"
                style={{ backgroundColor: COLORS.background.dark, color: COLORS.text.primary }}
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
                className="input-border text-sm rounded-DEFAULT p-2 focus:ring-0 outline-none"
                style={{ backgroundColor: COLORS.background.dark, color: COLORS.text.primary }}
              >
                <option>Last 30 Days</option>
                <option>Last 6 Months</option>
                <option>Year to Date</option>
              </select>
            </div>
          </div>

        </div>

        {/* RIGHT FLOATING PANEL: Entity Details */}
        {showProfilePanel && (
          <div className="absolute right-lg top-lg w-80 panel-border rounded-lg shadow-xl flex flex-col z-20" style={{ backgroundColor: COLORS.surface.panel }}>
            {profileLoading && (
              <div className="p-4 text-center text-on-surface-variant text-sm">Loading profile...</div>
            )}
            {profileError && (
              <div className="p-4 text-center text-error text-sm">Error loading profile</div>
            )}
            {!profileLoading && !profileError && (
              <>
                <div className="p-4 border-b flex justify-between items-start" style={{ borderColor: COLORS.border.default }}>
                  <div>
                    <div className="text-xs text-error font-label-mono mb-1 uppercase tracking-wider">
                      Selected Profile
                    </div>
                    <h3 className="font-headline-md text-[20px] font-bold text-on-surface leading-tight">
                      {profileData?.name || selectedProfile?.name || (selectedNodeId ? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.label : 'Unknown')}
                    </h3>
                    <p className="text-sm text-on-surface-variant mt-1">
                      Age: {profileData?.age ?? selectedProfile?.age ?? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.age ?? 'Unknown'} | Gender: {profileData?.gender ?? selectedProfile?.gender ?? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.gender ?? 'Unknown'}
                    </p>
                  </div>
                  <button 
                    onClick={() => {
                      setSelectedProfile(null);
                      setSelectedAccusedId(null);
                      setSelectedRowId(null);
                      setShowProfilePanel(false);
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
                        {profileData?.risk_score ?? selectedProfile?.riskScore ?? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.risk_score ?? 0}/100
                      </span>
                    </div>
                    <div className="h-1.5 w-full rounded-full overflow-hidden" style={{ backgroundColor: COLORS.background.dark }}>
                      <div
                        className="h-full bg-error rounded-full"
                        style={{ width: `${profileData?.risk_score ?? selectedProfile?.riskScore ?? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.risk_score ?? 0}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* Stats */}
                  <div className="p-3 rounded-DEFAULT border" style={{ backgroundColor: COLORS.background.dark, borderColor: COLORS.border.default }}>
                    <p className="text-sm text-on-surface">
                      Appears in{' '}
                      <span className="font-data-mono-bold text-primary">
                        {profileData?.fir_count ?? selectedProfile?.firsCount ?? nodes.find((n: NetworkGraphNode) => n.id === selectedNodeId)?.fir_count ?? 0} FIRs
                      </span>
                    </p>
                  </div>
                  {/* Connections */}
                  <div>
                    <h4 className="text-xs font-semibold mb-2 uppercase tracking-wider border-b pb-1" style={{ color: COLORS.text.muted, borderColor: COLORS.border.default }}>
                      Connected to
                    </h4>
                    <ul className="flex flex-col gap-2">
                      {profileData?.co_accused && profileData.co_accused.length > 0 ? (
                        profileData.co_accused.map((conn: any, idx: number) => (
                          <li key={idx} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS.status.errorLight }}></div>
                              <span className="text-on-surface">{conn.name}</span>
                            </div>
                            <span className="text-xs font-label-mono border px-1 rounded-sm" style={{ color: COLORS.text.muted, borderColor: COLORS.border.default }}>
                              {conn.times_together} FIRs
                            </span>
                          </li>
                        ))
                      ) : selectedProfile?.connections ? (
                        selectedProfile.connections.map((conn, idx) => (
                          <li key={idx} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS.status.errorLight }}></div>
                              <span className="text-on-surface">{conn.name}</span>
                            </div>
                            <span className="text-xs font-label-mono border px-1 rounded-sm" style={{ color: COLORS.text.muted, borderColor: COLORS.border.default }}>
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
                      <h4 className="text-xs font-semibold mb-2 uppercase tracking-wider border-b pb-1" style={{ color: COLORS.text.muted, borderColor: COLORS.border.default }}>
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
          </div>
        )}
      </div>
    </div>
  );
}
