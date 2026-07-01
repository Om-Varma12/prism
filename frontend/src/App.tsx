/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Screen } from './types';
import LoginScreen from './components/LoginScreen';
import Sidebar from './components/Sidebar';
import ChatScreen from './components/ChatScreen';
import NetworkExplorerScreen from './components/NetworkExplorerScreen';
import CommandDashboardScreen from './components/CommandDashboardScreen';
import AnalyticsScreen from './components/AnalyticsScreen';
import { AnimatePresence, motion } from 'motion/react';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.LOGIN);
  const [employeeId, setEmployeeId] = useState<string | null>(null);

  const handleLoginSuccess = (id: string) => {
    setEmployeeId(id);
    setCurrentScreen(Screen.DASHBOARD); // Go to situation overview dashboard upon login
  };

  const handleLogout = () => {
    setEmployeeId(null);
    setCurrentScreen(Screen.LOGIN);
  };

  return (
    <div className="w-full h-screen bg-[#0A0C10] text-[#e1e2ec] font-sans flex overflow-hidden">
      <div className="flex-1 h-full flex overflow-hidden">
      <AnimatePresence mode="wait">
        {currentScreen === Screen.LOGIN ? (
          <motion.div
            key="login"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="w-full h-full flex"
          >
            <LoginScreen onLoginSuccess={handleLoginSuccess} />
          </motion.div>
        ) : (
          <motion.div
            key="app-shell"
            initial={{ opacity: 0, scale: 0.99 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="w-full h-full flex overflow-hidden"
          >
            {/* Sidebar menu on left */}
            <Sidebar 
              currentScreen={currentScreen} 
              onNavigate={setCurrentScreen} 
              onLogout={handleLogout} 
            />

            {/* Right workspace panels based on navigation selection */}
            <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative md:ml-64 ml-0">
              {currentScreen === Screen.DASHBOARD && <CommandDashboardScreen />}
              {currentScreen === Screen.CHAT && <ChatScreen onNavigate={setCurrentScreen} />}
              {currentScreen === Screen.NETWORK && <NetworkExplorerScreen />}
              {currentScreen === Screen.ANALYTICS && <AnalyticsScreen />}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </div>
  );
}
