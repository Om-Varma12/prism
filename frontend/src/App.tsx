/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Screen } from './types';
import LoginScreen from './components/LoginScreen';
import Sidebar from './components/Sidebar';
import CommandDashboardScreen from './components/CommandDashboardScreen';
import ChatScreen from './components/ChatScreen';
import NetworkExplorerScreen from './components/NetworkExplorerScreen';
import AnalyticsScreen from './components/AnalyticsScreen';

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.LOGIN);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
    setCurrentScreen(Screen.DASHBOARD);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentScreen(Screen.LOGIN);
  };

  const handleNavigate = (screen: Screen) => {
    setCurrentScreen(screen);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case Screen.DASHBOARD:
        return <CommandDashboardScreen />;
      case Screen.CHAT:
        return <ChatScreen onNavigate={handleNavigate} />;
      case Screen.NETWORK:
        return <NetworkExplorerScreen />;
      case Screen.ANALYTICS:
        return <AnalyticsScreen />;
      default:
        return <CommandDashboardScreen />;
    }
  };

  // Show login screen when not authenticated
  if (!isLoggedIn) {
    return (
      <div className="flex h-screen bg-[#0A0C10] overflow-hidden">
        {/* Intercept the login redirect for local dev — clicking LOGIN logs in directly */}
        <div className="flex-1 flex flex-col" onClick={(e) => {
          // If the user clicks the LOGIN button we log in directly in local dev
          const target = e.target as HTMLElement;
          if (target.closest('button[type="button"]')) {
            e.preventDefault();
            handleLogin();
          }
        }}>
          <LoginScreen />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#0A0C10] overflow-hidden">
      {/* Persistent Sidebar */}
      <Sidebar
        currentScreen={currentScreen}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
      />

      {/* Main content area — offset by sidebar width on md+ */}
      <div className="flex-1 flex flex-col overflow-hidden md:ml-64">
        {renderScreen()}
      </div>
    </div>
  );
}

export default App;
