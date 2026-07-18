/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Authentication flow (Zoho Catalyst Hosted Auth):
 * 1. User clicks LOGIN → redirected to /__catalyst/auth/login (Zoho SSO)
 * 2. After login, Catalyst sets a session cookie and redirects back to login_redirect (index.html)
 * 3. On reload, we check for the Catalyst session cookie to decide if the user is authenticated.
 * 4. If no session, show LoginScreen. If session exists, show the app shell.
 */

import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Screen } from './types';
import LoginScreen from './components/LoginScreen';
import Sidebar from './components/Sidebar';
import CommandDashboardScreen from './components/CommandDashboardScreen';
import ChatScreen from './components/ChatScreen';
import NetworkExplorerScreen from './components/NetworkExplorerScreen';
import AnalyticsPage from './pages/Analytics';

// Create QueryClient with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

/**
 * Checks if the app is running in local development mode.
 */
function isLocalDevelopment(): boolean {
  return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
}

/**
 * Checks if a Catalyst session cookie is present.
 * Catalyst sets `__zcsCookieSecurity` or `__z_cac` after a successful login.
 * On localhost this will always return false (no cookie), so the login screen
 * is shown and clicking LOGIN does the real Catalyst redirect.
 */
function isCatalystSessionActive(): boolean {
  return document.cookie
    .split(';')
    .some((c) => c.trim().startsWith('__zcsCookieSecurity=') || c.trim().startsWith('__z_cac='));
}

function App() {
  const getInitialScreen = (): Screen => {
    const params = new URLSearchParams(window.location.search);
    const page = params.get('page');
    switch (page) {
      case 'dashboard': return Screen.DASHBOARD;
      case 'chat': return Screen.CHAT;
      case 'network': return Screen.NETWORK;
      case 'analytics': return Screen.ANALYTICS;
      default: return Screen.DASHBOARD;
    }
  };

  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [currentScreen, setCurrentScreen] = useState<Screen>(getInitialScreen);
  const [checking, setChecking] = useState<boolean>(true);

  // On mount, check for an existing Catalyst session
  // Skip authentication check for local development
  useEffect(() => {
    // Bypass login screen - direct login
    setIsLoggedIn(true);
    setChecking(false);
    
    const params = new URLSearchParams(window.location.search);
    if (!params.has('page')) {
      const url = new URL(window.location.href);
      url.searchParams.set('page', 'dashboard');
      window.history.replaceState({}, '', url.pathname + url.search);
    }
  }, []);

  // Handle back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const page = params.get('page');
      if (page) {
        switch (page) {
          case 'dashboard':
            setCurrentScreen(Screen.DASHBOARD);
            break;
          case 'chat':
            setCurrentScreen(Screen.CHAT);
            break;
          case 'network':
            setCurrentScreen(Screen.NETWORK);
            break;
          case 'analytics':
            setCurrentScreen(Screen.ANALYTICS);
            break;
          default:
            setCurrentScreen(Screen.DASHBOARD);
        }
      } else {
        setCurrentScreen(Screen.DASHBOARD);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleLogout = () => {
    // Redirect to Catalyst logout endpoint which clears the session cookie
    window.location.href =
      'https://prism-60074849663.development.catalystserverless.in/__catalyst/auth/logout';
  };

  const handleNavigate = (screen: Screen) => {
    setCurrentScreen(screen);
    
    const url = new URL(window.location.href);
    let screenName = 'dashboard';
    switch (screen) {
      case Screen.DASHBOARD: screenName = 'dashboard'; break;
      case Screen.CHAT: screenName = 'chat'; break;
      case Screen.NETWORK: screenName = 'network'; break;
      case Screen.ANALYTICS: screenName = 'analytics'; break;
    }
    url.searchParams.set('page', screenName);
    if (screenName !== 'chat') {
      url.searchParams.delete('session_id');
    }
    window.history.pushState({}, '', url.pathname + url.search);
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
        return <AnalyticsPage />;
      default:
        return <CommandDashboardScreen />;
    }
  };

  // Splash while checking session
  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#0A0C10]">
        <span className="w-3 h-3 rounded-full bg-primary animate-ping" />
      </div>
    );
  }

  // Not authenticated — show login screen.
  // LoginScreen's button does window.location.href = '/__catalyst/auth/login'
  // which is the real Catalyst SSO redirect. We do NOT intercept it here.
  if (!isLoggedIn) {
    return (
      <div className="flex h-screen bg-[#0A0C10] overflow-hidden">
        <LoginScreen />
      </div>
    );
  }

  // Authenticated — show the full app shell
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen bg-[#0A0C10] overflow-hidden">
        <Sidebar
          currentScreen={currentScreen}
          onNavigate={handleNavigate}
          onLogout={handleLogout}
        />
        <div className="flex-1 flex flex-col overflow-hidden md:ml-64">
          {renderScreen()}
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
