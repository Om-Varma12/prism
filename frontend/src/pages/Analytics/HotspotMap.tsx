/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics.service';
import { HotspotCluster, HotspotClusterResponse, HotspotFilters, CrimeAlert } from '../../types/analytics';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import DateRangeSlider from '../../components/common/DateRangeSlider';
import DistrictFilter from '../../components/common/DistrictFilter';
import HotspotDetailsPanel from '../../components/analytics/HotspotDetailsPanel';

export default function HotspotMap() {
  // Unique map ID for container
  const [mapId] = useState(() => `map-${Date.now()}-${Math.random()}`);
  
  // Map refs for manual initialization
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Circle[]>([]);

  // Hotspot filters
  const [filters, setFilters] = useState<HotspotFilters>({
    date_from: undefined,
    date_to: undefined,
    district: undefined,
  });

  // Selected cluster for details panel
  const [selectedCluster, setSelectedCluster] = useState<HotspotCluster | null>(null);

  // Debounce timeout ref for slider
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Set new timeout
    debounceTimeoutRef.current = setTimeout(() => {
      setFilters(prev => ({
        ...prev,
        date_from: dateFrom,
        date_to: dateTo,
      }));
    }, 1000); // 1 second debounce
  }, []);

  // Handle district filter change
  const handleDistrictChange = useCallback((district: string) => {
    setFilters(prev => ({
      ...prev,
      district: district || undefined,
    }));
  }, []);

  // Handle show all time (reset date filters)
  const handleShowAllTime = useCallback(() => {
    setFilters(prev => ({
      ...prev,
      date_from: undefined,
      date_to: undefined,
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

  // Get cluster radius based on point count (in meters for L.circle)
  const getClusterRadius = (pointCount: number) => {
    // Scale between 1000m and 10000m based on point count
    return Math.min(Math.max(pointCount * 500, 3000), 30000);
  };
  // Initialize map on mount
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Check if map already exists (Strict Mode double-mount protection)
    if (mapInstanceRef.current) {
      return;
    }

    // Initialize map
    const map = L.map(mapContainerRef.current, {
      center: [15.3173, 76.4639], // Center of Karnataka
      zoom: 7,
    });

    // Add tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: ''
    }).addTo(map);

    mapInstanceRef.current = map;

    // Cleanup on unmount
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update markers when hotspots data changes
  useEffect(() => {
    if (!mapInstanceRef.current || !hotspotsData) return;

    // Clear existing markers
    markersRef.current.forEach(marker => {
      mapInstanceRef.current?.removeLayer(marker);
    });
    markersRef.current = [];

    // Add new markers
    hotspotsData.clusters.forEach((cluster: HotspotCluster) => {
      const marker = L.circle([cluster.centroid_lat, cluster.centroid_lng], {
        radius: getClusterRadius(cluster.point_count),
        color: getClusterColor(cluster.point_count),
        fillColor: getClusterColor(cluster.point_count),
        weight: 2,
        opacity: 0.8,
        fillOpacity: 0.4,
      });

      if (mapInstanceRef.current) {
        marker.addTo(mapInstanceRef.current);
      }

      marker.bindPopup(`
        <div class="font-sans">
          <div class="font-bold text-sm mb-1">Cluster #${cluster.cluster_id}</div>
          <div class="text-xs">
            <div><strong>Points:</strong> ${cluster.point_count}</div>
            <div><strong>Dominant Crime:</strong> ${cluster.dominant_crime_type || 'N/A'}</div>
            <div><strong>District:</strong> ${cluster.district || 'N/A'}</div>
            <div><strong>Radius:</strong> ${cluster.radius_km.toFixed(2)} km</div>
          </div>
        </div>
      `);

      marker.on('click', () => handleClusterClick(cluster));
      markersRef.current.push(marker);
    });
  }, [hotspotsData, handleClusterClick]);

  // Cleanup debounce timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col xl:flex-row gap-lg h-full">
      {/* LEFT SIDE (70%) - Map */}
      <div className="flex-1 xl:w-[70%] flex flex-col gap-sm">
        <div className="flex-1 bg-surface border border-outline-variant relative overflow-hidden flex flex-col min-h-[400px]">
          {/* Map Container with Leaflet */}
          <div className="flex-1 relative bg-[#0A0C10]">
            {hotspotsLoading && (
              <div className="absolute inset-0 flex items-center justify-center text-on-surface-variant z-10">
                <span className="text-primary font-body-sm text-body-sm">Loading hotspots...</span>
              </div>
            )}
            <div
              ref={mapContainerRef}
              id={mapId}
              className="h-full w-full z-0"
              style={{ height: '100%', width: '100%' }}
            />
          </div>

          <DateRangeSlider
            dateFrom={filters.date_from}
            dateTo={filters.date_to}
            onChange={handleDateChange}
            onShowAllTime={handleShowAllTime}
          />
        </div>
      </div>

      <div className="w-full xl:w-[30%] flex flex-col gap-lg shrink-0">
        <div className="bg-surface border border-outline-variant p-4">
          <DistrictFilter
            selectedDistrict={filters.district}
            onChange={handleDistrictChange}
          />
        </div>

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

        <HotspotDetailsPanel selectedCluster={selectedCluster} />
      </div>
    </div>
  );
}

