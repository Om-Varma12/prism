/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Screen } from '../types';

interface SidebarProps {
  currentScreen: Screen;
  onNavigate: (screen: Screen) => void;
  onLogout: () => void;
}

export default function Sidebar({ currentScreen, onNavigate, onLogout }: SidebarProps) {
  const menuItems = [
    {
      screen: Screen.DASHBOARD,
      label: 'Dashboard',
      icon: 'dashboard',
    },
    {
      screen: Screen.CHAT,
      label: 'Intelligence Chat',
      icon: 'forum',
    },
    {
      screen: Screen.NETWORK,
      label: 'Network Explorer',
      icon: 'hub',
    },
    {
      screen: Screen.ANALYTICS,
      label: 'Analytics',
      icon: 'analytics',
    }
  ];

  return (
    <nav className="hidden md:flex flex-col h-full border-r border-outline-variant bg-surface w-64 fixed left-0 top-0 shrink-0 z-10 text-primary dark:text-primary font-body-md text-body-md font-label-mono text-label-mono select-none">
      {/* Brand Header */}
      <div className="p-6 border-b border-outline-variant flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center border border-outline-variant overflow-hidden shrink-0">
          <span
            className="material-symbols-outlined text-primary"
            style={{ fontVariationSettings: '"FILL" 1' }}
          >
            security
          </span>
        </div>
        <div>
          <h1 className="font-headline-sm text-headline-sm font-bold text-primary tracking-tight">
            PRISM
          </h1>
          <p className="font-label-mono text-label-mono text-on-surface-variant">
            Operator 724
          </p>
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="flex-1 py-4 overflow-y-auto">
        <ul className="space-y-1 px-2">
          {menuItems.map((item) => {
            const isActive = currentScreen === item.screen;
            return (
              <li key={item.screen}>
                <button
                  onClick={() => onNavigate(item.screen)}
                  className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-colors duration-150 cursor-pointer ${
                    isActive
                      ? 'text-primary border-l-2 border-primary bg-surface-container-high active:bg-surface-container-highest'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-variant active:bg-surface-container-highest'
                  }`}
                >
                  <span
                    className="material-symbols-outlined text-[20px]"
                    style={{ fontVariationSettings: isActive ? '"FILL" 1' : undefined }}
                  >
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      {/* Bottom Profile and Settings */}
      <div className="p-4 border-t border-outline-variant bg-surface">
        <ul className="space-y-1">
          <li>
            <button className="w-full text-left px-4 py-3 flex items-center gap-3 text-on-surface-variant hover:text-on-surface hover:bg-surface-variant transition-colors duration-150 active:bg-surface-container-highest cursor-pointer">
              <span className="material-symbols-outlined text-[20px]">account_circle</span>
              <span>Profile</span>
            </button>
          </li>
          <li>
            <button className="w-full text-left px-4 py-3 flex items-center gap-3 text-on-surface-variant hover:text-on-surface hover:bg-surface-variant transition-colors duration-150 active:bg-surface-container-highest cursor-pointer">
              <span className="material-symbols-outlined text-[20px]">settings</span>
              <span>Settings</span>
            </button>
          </li>
          <li>
            <button
              onClick={onLogout}
              className="w-full text-left px-4 py-3 flex items-center gap-3 text-error hover:bg-error/10 transition-colors duration-150 rounded-btn cursor-pointer font-bold"
            >
              <span className="material-symbols-outlined text-[20px]">logout</span>
              <span>Logout</span>
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
