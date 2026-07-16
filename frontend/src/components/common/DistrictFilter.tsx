/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';

interface DistrictFilterProps {
  selectedDistrict?: string;
  onChange: (district: string) => void;
}

export default function DistrictFilter({ selectedDistrict, onChange }: DistrictFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <label className="font-label-mono text-label-mono text-on-surface-variant">District:</label>
      <input
        type="text"
        placeholder="All districts"
        value={selectedDistrict || ''}
        onChange={(e) => onChange(e.target.value)}
        className="bg-surface-variant border border-outline-variant text-on-surface px-3 py-1.5 font-body-sm text-body-sm rounded-none focus:outline-none focus:border-primary w-40"
      />
    </div>
  );
}
