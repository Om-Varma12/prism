/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useCallback } from 'react';
import { COLORS } from '../../constants/colors';

interface DateRangeSliderProps {
  dateFrom?: string;
  dateTo?: string;
  onChange: (dateFrom: string, dateTo: string) => void;
  onShowAllTime: () => void;
}

const MONTHS = [
  '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06',
  '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12',
  '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
  '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
  '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06',
  '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12',
  '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07'
];

export default function DateRangeSlider({ dateFrom, dateTo, onChange, onShowAllTime }: DateRangeSliderProps) {
  const [sliderValue, setSliderValue] = useState(31);

  const handleSliderChange = useCallback((val: number) => {
    setSliderValue(val);
    onChange(MONTHS[val - 1], MONTHS[val - 1]);
  }, [onChange]);

  return (
    <div className="p-4 border-t" style={{ backgroundColor: COLORS.surface.panel, borderColor: COLORS.border.default }}>
      <div className="flex justify-between items-center font-mono text-xs mb-2">
        <span style={{ color: COLORS.text.muted }}>JAN 2023</span>
        <div className="flex items-center gap-2">
          <span className="font-bold tracking-wide" style={{ color: COLORS.primary.main }}>
            CURRENT WINDOW: {dateFrom || 'ALL TIME'}
          </span>
          <button
            onClick={onShowAllTime}
            className="px-2 py-0.5 font-mono text-[10px] font-bold rounded transition-colors cursor-pointer"
            style={{ backgroundColor: COLORS.primary.main, color: COLORS.background.dark }}
          >
            ALL TIME
          </button>
        </div>
        <span style={{ color: COLORS.text.muted }}>JUL 2026</span>
      </div>
      <div className="relative w-full h-4 flex items-center">
        <input
          className="w-full cursor-pointer"
          max="43"
          min="1"
          type="range"
          value={sliderValue}
          onChange={(e) => handleSliderChange(Number(e.target.value))}
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
  );
}
