/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import HotspotMap from './HotspotMap';
import TrendAnalysis from './TrendAnalysis';
import OffenderRiskBoard from './OffenderRiskBoard';

type ActiveTab = 'hotspot' | 'trends' | 'offenders';

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('hotspot');

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      {/* Header */}
      <header className="px-margin-desktop pt-margin-desktop pb-0 border-b border-outline-variant flex-shrink-0">
        <h2 className="font-headline-md text-display-lg text-on-surface mb-lg">
          Analytics &amp; Patterns
        </h2>
        {/* Tabs */}
        <div className="flex gap-lg font-body-sm text-body-sm font-semibold">
          <button
            onClick={() => setActiveTab('hotspot')}
            className={`pb-sm border-b-2 transition-colors cursor-pointer ${
              activeTab === 'hotspot' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Hotspot Map
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={`pb-sm border-b-2 transition-colors cursor-pointer ${
              activeTab === 'trends' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Trend Analysis
          </button>
          {/* <button
            onClick={() => setActiveTab('offenders')}
            className={`pb-sm border-b-2 transition-colors cursor-pointer ${
              activeTab === 'offenders' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Offender Risk Board
          </button> */}
        </div>
      </header>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-margin-desktop custom-scrollbar">
        {activeTab === 'hotspot' && <HotspotMap />}

        <AnimatePresence mode="wait">
          {/* TAB 2: Trend Analysis */}
          {activeTab === 'trends' && (
            <motion.div
              key="trends"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <TrendAnalysis />
            </motion.div>
          )}

          {/* TAB 3: Offender Risk Board */}
          {activeTab === 'offenders' && (
            <motion.div
              key="offenders"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <OffenderRiskBoard />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
