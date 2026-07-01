/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Screen } from '../types';
import { 
  Shield, 
  LayoutDashboard, 
  MessageSquare, 
  Network, 
  BarChart2, 
  User, 
  Settings as SettingsIcon,
  LogOut,
  ChevronRight
} from 'lucide-react';

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
      icon: LayoutDashboard,
      description: 'Situation overview and tactical map'
    },
    {
      screen: Screen.CHAT,
      label: 'Intelligence Chat',
      icon: MessageSquare,
      description: 'AI query and case search'
    },
    {
      screen: Screen.NETWORK,
      label: 'Network Explorer',
      icon: Network,
      description: 'Suspect linkages and associations'
    },
    {
      screen: Screen.ANALYTICS,
      label: 'Analytics',
      icon: BarChart2,
      description: 'Pattern and hotspot discovery'
    }
  ];

  return (
    <nav className="hidden md:flex flex-col h-full bg-black border-r border-white/10 w-64 flex-shrink-0 relative z-30 select-none">
      {/* Brand Header */}
      <div className="p-6 border-b border-white/10 flex items-center gap-3">
        <div className="w-10 h-10 bg-[#00F0FF]/10 border border-[#00F0FF]/30 flex items-center justify-center text-[#00F0FF]">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="text-3xl font-black tracking-tighter leading-none text-white">
            PRISM<span className="text-[#00F0FF]">.</span>
          </div>
          <div className="text-white/40 text-[9px] uppercase font-bold tracking-[0.2em] mt-1.5">
            Intel Division
          </div>
        </div>
      </div>

      {/* Operator Status bar */}
      <div className="px-6 py-3 bg-white/5 border-b border-white/10 flex items-center justify-between text-[10px] font-mono">
        <span className="text-white/50 font-medium">OP_ID: KSP-724</span>
        <span className="flex items-center gap-1.5 text-[#00F0FF] font-bold tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00F0FF] animate-pulse"></span>
          ACTIVE
        </span>
      </div>

      {/* Navigation Menu */}
      <ul className="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto custom-scrollbar">
        {menuItems.map((item, idx) => {
          const isActive = currentScreen === item.screen;
          const Icon = item.icon;
          return (
            <li key={item.screen}>
              <button
                onClick={() => onNavigate(item.screen)}
                className={`w-full flex items-center justify-between px-3.5 py-3 transition-all group ${
                  isActive
                    ? 'bg-[#00F0FF] text-black font-black border-l-4 border-white'
                    : 'text-white/70 hover:bg-white/5 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4.5 h-4.5 shrink-0 transition-transform group-hover:scale-105 ${
                    isActive ? 'text-black' : 'text-white/40 group-hover:text-[#00F0FF]'
                  }`} />
                  <div>
                    <span className="text-xs uppercase font-bold tracking-[0.15em]">
                      {idx + 1}. {item.label}
                    </span>
                  </div>
                </div>
                {isActive && (
                  <ChevronRight className="w-4 h-4 text-black shrink-0" />
                )}
              </button>
            </li>
          );
        })}
      </ul>

      {/* User Actions Profile & Logout */}
      <div className="p-4 border-t border-white/10 bg-white/5 space-y-1">
        <button className="w-full flex items-center gap-3 px-3.5 py-2.5 text-white/60 hover:bg-white/5 text-[10px] font-mono font-bold tracking-wider">
          <User className="w-4 h-4 text-white/30" />
          <span>PROFILE // SAHIL.V</span>
        </button>
        <button className="w-full flex items-center gap-3 px-3.5 py-2.5 text-white/60 hover:bg-white/5 text-[10px] font-mono font-bold tracking-wider">
          <SettingsIcon className="w-4 h-4 text-white/30" />
          <span>CONFIGURATION</span>
        </button>
        <button 
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3.5 py-2.5 text-[#ff4d4d] hover:bg-red-500/10 text-[10px] font-mono font-bold tracking-wider mt-1"
        >
          <LogOut className="w-4 h-4 text-[#ff4d4d]" />
          <span>TERMINATE SESSION</span>
        </button>
      </div>
    </nav>
  );
}
