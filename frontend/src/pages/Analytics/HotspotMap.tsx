/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';
import { HotspotCluster, HotspotClusterResponse, HotspotFilters, CrimeAlert } from '../../types/analytics';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function HotspotMap() {
  // Hotspot filters
  const [filters, setFilters] = useState<HotspotFilters>({
    date_from: undefined,
    date_to: undefined,
    district: undefined,
  });

  // Selected cluster for details panel
  const [selectedCluster, setSelectedCluster] = useState<HotspotCluster | null>(null);

  // Fetch hotspots data
  const { data: hotspotsData, isLoading: hotspotsLoading } = useQuery({
    queryKey: ['hotspots', filters],
    queryFn: () => analyticsService.getHotspots(filters),
  });

  // Fetch emerging clusters
  const { data: emergingClustersData } = useQuery({
    queryKey: ['emerging-clusters'],
    queryFn: () => analyticsService.getEmergingClusters(),
  });

  // Handle date range slider change (debounced)
  const handleDateChange = useCallback((dateFrom: string, dateTo: string) => {
    setFilters(prev => ({
      ...prev,
      date_from: dateFrom,
      date_to: dateTo,
    }));
  }, []);

  // Handle district filter change
  const handleDistrictChange = useCallback((district: string) => {
    setFilters(prev => ({
      ...prev,
      district: district || undefined,
    }));
  }, []);

  // Handle cluster click
  const handleClusterClick = useCallback((cluster: HotspotCluster) => {
    setSelectedCluster(cluster);
  }, []);

  // Get cluster color based on point count (severity)
  const getClusterColor = (pointCount: number) => {
    if (pointCount >= 20) return '#ff4d4d'; // Red for high density
    if (pointCount >= 10) return '#ff9f0a'; // Orange for medium density
    return '#00F0FF'; // Cyan for low density
  };

  // Get cluster radius based on point count
  const getClusterRadius = (pointCount: number) => {
    return Math.min(Math.max(pointCount * 500, 2000), 15000); // Scale between 2km and 15km
  };

  return (
    <div className="flex flex-col xl:flex-row gap-lg h-full">
      {/* LEFT SIDE (70%) - Map */}
      <div className="flex-1 xl:w-[70%] flex flex-col gap-sm">
        <div className="flex-1 bg-surface border border-outline-variant relative overflow-hidden flex flex-col min-h-[400px]">
          {/* Map Container with Leaflet */}
          <div className="flex-1 relative bg-[#0A0C10]">
            {hotspotsLoading ? (
              <div className="absolute inset-0 flex items-center justify-center text-on-surface-variant">
                <span className="text-primary font-body-sm text-body-sm">Loading hotspots...</span>
              </div>
            ) : (
              <MapContainer
                key="hotspot-map"
                center={[15.3173, 76.4639]} // Center of Karnataka
                zoom={7}
                style={{ height: '100%', width: '100%' }}
                className="z-0"
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {hotspotsData?.clusters.map((cluster: HotspotCluster) => (
                  <CircleMarker
                    key={cluster.cluster_id}
                    center={[cluster.centroid_lat, cluster.centroid_lng]}
                    pathOptions={{
                      color: getClusterColor(cluster.point_count),
                      fillColor: getClusterColor(cluster.point_count),
                      weight: 2,
                      opacity: 0.8,
                      fillOpacity: 0.4,
                    }}
                    radius={getClusterRadius(cluster.point_count)}
                    eventHandlers={{
                      click: () => handleClusterClick(cluster),
                    }}
                  >
                    <Popup>
                      <div className="font-sans">
                        <div className="font-bold text-sm mb-1">
                          Cluster #{cluster.cluster_id}
                        </div>
                        <div className="text-xs">
                          <div><strong>Points:</strong> {cluster.point_count}</div>
                          <div><strong>Dominant Crime:</strong> {cluster.dominant_crime_type || 'N/A'}</div>
                          <div><strong>District:</strong> {cluster.district || 'N/A'}</div>
                          <div><strong>Radius:</strong> {cluster.radius_km.toFixed(2)} km</div>
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            )}

            {/* Map Controls Placeholder */}
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
          <div className="p-md border-t border-outline-variant bg-surface">
            <div className="flex justify-between font-label-mono text-label-mono text-on-surface-variant mb-xs">
              <span>JAN 2023</span>
              <span className="text-primary font-bold">
                CURRENT WINDOW: {filters.date_from || 'ALL TIME'}
              </span>
              <span>DEC 2025</span>
            </div>
            <div className="relative w-full h-4">
              <input
                className="w-full"
                max="36"
                min="1"
                type="range"
                defaultValue="22"
                onChange={(e) => {
                  // TODO: Convert slider value to date range
                  const val = Number(e.target.value);
                  const months = [
                    '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06',
                    '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
                    '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
                    '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
                    '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
                    '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12'
                  ];
                  handleDateChange(months[val - 1], months[val - 1]);
                }}
              />
            </div>
            <div className="flex justify-between w-full mt-1 px-1">
              <div className="w-px h-2 bg-outline-variant"></div>
              <div className="w-px h-2 bg-outline-variant"></div>
              <div className="w-px h-2 bg-outline-variant"></div>
              <div className="w-px h-2 bg-outline-variant"></div>
              <div className="w-px h-2 bg-outline-variant"></div>
              <div className="w-px h-2 bg-outline-variant"></div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE (30%) - Side Panels */}
      <div className="w-full xl:w-[30%] flex flex-col gap-lg shrink-0">
        {/* Panel 1: Emerging Clusters */}
        <div className="bg-surface border border-outline-variant flex flex-col rounded-none overflow-hidden">
          <div className="p-sm border-b border-outline-variant bg-surface-container-high">
            <h3 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
              Emerging Clusters
            </h3>
          </div>
          <div className="divide-y divide-outline-variant max-h-[200px] overflow-y-auto custom-scrollbar">
            {emergingClustersData?.alerts.length === 0 ? (
              <div className="p-md text-on-surface-variant font-body-sm text-body-sm">
                No emerging clusters detected
              </div>
            ) : (
              emergingClustersData?.alerts.map((alert: CrimeAlert) => (
                <div
                  key={alert.alert_id}
                  className="p-md border-l-2 border-l-transparent hover:bg-surface-variant cursor-pointer transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <span className="font-body-sm text-body-sm font-semibold text-on-surface">
                      {alert.crime_type}
                    </span>
                    <span className="font-data-mono-bold text-data-mono-bold text-error">
                      {alert.spike_ratio.toFixed(1)}x
                    </span>
                  </div>
                  <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">
                    {alert.district}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Panel 2: Cluster Details */}
        <div className="bg-surface border border-outline-variant flex flex-col flex-1 rounded-none overflow-hidden min-h-[300px]">
          <div className="p-sm border-b border-outline-variant bg-surface-container-high flex justify-between items-center">
            <h3 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
              Cluster Details
            </h3>
            {selectedCluster && (
              <span className="font-label-mono text-[10px] text-primary border border-primary px-1 font-bold">
                {selectedCluster.district?.replace(' ', '_') || 'UNKNOWN'}_CLUSTER
              </span>
            )}
          </div>
          {selectedCluster ? (
            <div className="p-md flex flex-col gap-md">
              <div className="grid grid-cols-2 gap-md border-b border-outline-variant pb-md font-mono text-xs">
                <div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mb-1">
                    INCIDENTS
                  </div>
                  <div className="font-data-mono-bold text-headline-sm text-on-surface">
                    {selectedCluster.point_count}
                  </div>
                </div>
                <div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mb-1">
                    RADIUS
                  </div>
                  <div className="font-data-mono-bold text-body-md text-on-surface mt-1">
                    {selectedCluster.radius_km.toFixed(1)} KM
                  </div>
                </div>
              </div>
              <div className="border-b border-outline-variant pb-md">
                <div className="font-label-mono text-[10px] text-on-surface-variant mb-1">
                  PRIMARY TYPE
                </div>
                <div className="font-body-sm text-body-sm font-semibold text-error flex items-center gap-2 uppercase tracking-wide">
                  <span className="material-symbols-outlined text-[16px]">warning</span>
                  {selectedCluster.dominant_crime_type || 'Unknown'}
                </div>
              </div>
              <div className="flex-1 flex flex-col">
                <div className="font-label-mono text-[10px] text-on-surface-variant mb-2">
                  HOURLY DISTRIBUTION (24H)
                </div>
                <div className="flex-1 flex items-end justify-between gap-1 h-24 pt-4 border-b border-outline-variant">
                  {/* Placeholder hourly distribution - would be calculated from actual data */}
                  {Array.from({ length: 24 }, (_, i) => Math.random() * 100).map((hVal, idx) => (
                    <div
                      key={idx}
                      title={`Hour ${idx}`}
                      className={`w-full transition-colors rounded-t-sm ${hVal > 25 ? 'bg-primary' : 'bg-outline-variant'}`}
                      style={{ height: `${hVal}%` }}
                    ></div>
                  ))}
                </div>
                <div className="flex justify-between font-label-mono text-[10px] text-on-surface-variant mt-1">
                  <span>00:00</span>
                  <span>12:00</span>
                  <span>23:59</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-md text-on-surface-variant font-body-sm text-body-sm flex-1 flex items-center justify-center">
              Select a cluster to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

