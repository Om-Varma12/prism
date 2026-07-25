/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { HotspotCluster } from '../../types/analytics';
import { COLORS } from '../../constants/colors';

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
    <div className="border flex flex-col flex-1 rounded-lg overflow-hidden min-h-[300px]" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
      <div className="p-3 border-b flex justify-between items-center" style={{ borderColor: COLORS.border.default, backgroundColor: COLORS.background.dark }}>
        <h3 className="font-mono text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.heading }}>
          Cluster Details
        </h3>
        {selectedCluster && (
          <span className="font-mono text-[10px] border px-1.5 py-0.5 rounded font-bold" style={{ color: COLORS.primary.lightText, borderColor: `${COLORS.primary.main}66`, backgroundColor: `${COLORS.primary.main}22` }}>
            {getDisplayDistrictName(selectedCluster.district).replace(' ', '_')}_CLUSTER
          </span>
        )}
      </div>
      {selectedCluster ? (
        <div className="p-4 flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4 border-b pb-4 font-mono text-xs" style={{ borderColor: COLORS.border.default }}>
            <div>
              <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
                INCIDENTS
              </div>
              <div className="font-mono text-xl font-bold" style={{ color: COLORS.text.heading }}>
                {selectedCluster.point_count}
              </div>
            </div>
            <div>
              <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
                RADIUS
              </div>
              <div className="font-mono text-sm font-bold mt-1" style={{ color: COLORS.text.heading }}>
                {selectedCluster.radius_km.toFixed(1)} KM
              </div>
            </div>
          </div>
          <div className="border-b pb-4" style={{ borderColor: COLORS.border.default }}>
            <div className="font-mono text-[10px] mb-1" style={{ color: COLORS.text.muted }}>
              PRIMARY TYPE
            </div>
            <div className="text-sm font-semibold flex items-center gap-2 uppercase tracking-wide" style={{ color: COLORS.status.errorSoft }}>
              <span className="material-symbols-outlined text-[16px]">warning</span>
              {selectedCluster.dominant_crime_type || 'Unknown'}
            </div>
          </div>
          <div className="flex-1 flex flex-col">
            <div className="font-mono text-[10px] mb-2" style={{ color: COLORS.text.muted }}>
              HOURLY DISTRIBUTION (24H)
            </div>
            <div className="flex-1 flex items-end justify-between gap-1 h-24 pt-4 border-b" style={{ borderColor: COLORS.border.default }}>
              {Array.from({ length: 24 }, (_, i) => Math.random() * 100).map((hVal, idx) => (
                <div
                  key={idx}
                  title={`Hour ${idx}`}
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
        </div>
      ) : (
        <div className="p-4 font-mono text-xs flex-1 flex items-center justify-center" style={{ color: COLORS.text.muted }}>
          Select a cluster to view details
        </div>
      )}
    </div>
  );
}
