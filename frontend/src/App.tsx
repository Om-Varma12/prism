/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Authentication flow (Clerk):
 * 1. ClerkProvider (in index.tsx) wraps the entire app.
 * 2. useAuth() provides isLoaded + isSignedIn.
 * 3. If not signed in → show ClerkAuthPage (our custom branded page).
 * 4. If signed in → show the full app shell.
 * 5. Logout is handled via useClerk().signOut() in Sidebar.
 */

import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuth, AuthenticateWithRedirectCallback } from '@clerk/clerk-react';
import { COLORS } from './constants/colors';
import { Screen } from './types';
import ClerkAuthPage from './components/ClerkAuthPage';
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
      gcTime: 10 * 60 * 1000,   // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { isLoaded, isSignedIn } = useAuth();

  const getInitialScreen = (): Screen => {
    const params = new URLSearchParams(window.location.search);
    const page = params.get('page');
    switch (page) {
      case 'dashboard': return Screen.DASHBOARD;
      case 'chat':      return Screen.CHAT;
      case 'network':   return Screen.NETWORK;
      case 'analytics': return Screen.ANALYTICS;
      default:          return Screen.DASHBOARD;
    }
  };

  const [currentScreen, setCurrentScreen] = useState<Screen>(getInitialScreen);

  // Set the page URL param once authenticated
  useEffect(() => {
    if (!isSignedIn) return;
    const params = new URLSearchParams(window.location.search);
    if (!params.has('page')) {
      const url = new URL(window.location.href);
      url.searchParams.set('page', 'dashboard');
      window.history.replaceState({}, '', url.pathname + url.search);
    }
  }, [isSignedIn]);

  // Handle back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const page = params.get('page');
      if (page) {
        switch (page) {
          case 'dashboard': setCurrentScreen(Screen.DASHBOARD); break;
          case 'chat':      setCurrentScreen(Screen.CHAT);      break;
          case 'network':   setCurrentScreen(Screen.NETWORK);   break;
          case 'analytics': setCurrentScreen(Screen.ANALYTICS); break;
          default:          setCurrentScreen(Screen.DASHBOARD);
        }
      } else {
        setCurrentScreen(Screen.DASHBOARD);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleNavigate = (screen: Screen) => {
    setCurrentScreen(screen);

    const url = new URL(window.location.href);
    let screenName = 'dashboard';
    switch (screen) {
      case Screen.DASHBOARD: screenName = 'dashboard'; break;
      case Screen.CHAT:      screenName = 'chat';      break;
      case Screen.NETWORK:   screenName = 'network';   break;
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
      case Screen.DASHBOARD: return <CommandDashboardScreen />;
      case Screen.CHAT:      return <ChatScreen onNavigate={handleNavigate} />;
      case Screen.NETWORK:   return <NetworkExplorerScreen />;
      case Screen.ANALYTICS: return <AnalyticsPage />;
      default:               return <CommandDashboardScreen />;
    }
  };

  // Dedicated SSO Callback Route
  if (window.location.pathname === '/sso-callback') {
    return <AuthenticateWithRedirectCallback afterSignInUrl="/" afterSignUpUrl="/" />;
  }

  // Splash while Clerk is loading
  if (!isLoaded) {
    return (
      <div
        className="flex h-screen items-center justify-center"
        style={{
          backgroundColor: COLORS.background.dark,
          backgroundImage: `
            linear-gradient(rgba(180, 225, 235, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(180, 225, 235, 0.07) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
        }}
      >
        <div className="flex flex-col items-center gap-4">
          <span
            className="w-3 h-3 rounded-full animate-ping"
            style={{ backgroundColor: COLORS.primary.main }}
          />
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '10px',
              color: COLORS.text.muted,
              letterSpacing: '0.2em',
            }}
          >
            INITIALIZING...
          </span>
        </div>
      </div>
    );
  }

  // Not signed in — show Clerk auth page
  if (!isSignedIn) {
    return <ClerkAuthPage />;
  }

  // Signed in — show the full app shell
  return (
    <QueryClientProvider client={queryClient}>
      <div
        className="flex h-screen overflow-hidden"
        style={{ backgroundColor: COLORS.background.dark }}
      >
        <Sidebar
          currentScreen={currentScreen}
          onNavigate={handleNavigate}
        />
        <div className="flex-1 flex flex-col overflow-hidden md:ml-64">
          {renderScreen()}
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
