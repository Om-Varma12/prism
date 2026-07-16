/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { HotspotCluster } from '../../types/analytics';

interface HotspotDetailsPanelProps {
  selectedCluster: HotspotCluster | null;
}

export default function HotspotDetailsPanel({ selectedCluster }: HotspotDetailsPanelProps) {
  const getDisplayDistrictName = (district: string | undefined | null) => {
    if (!district) return 'UNKNOWN';
    const districtMapping: Record<string, string> = {
      'Mysuru_Central': 'Bangalore',
      'Mysuru Central': 'Bangalore',
      'Mysuru': 'Bangalore',
    };
    return districtMapping[district] || district;
  };

  return (
    <div className="bg-surface border border-outline-variant flex flex-col flex-1 rounded-none overflow-hidden min-h-[300px]">
      <div className="p-sm border-b border-outline-variant bg-surface-container-high flex justify-between items-center">
        <h3 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
          Cluster Details
        </h3>
        {selectedCluster && (
          <span className="font-label-mono text-[10px] text-primary border border-primary px-1 font-bold">
            {getDisplayDistrictName(selectedCluster.district).replace(' ', '_')}_CLUSTER
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
  );
}
