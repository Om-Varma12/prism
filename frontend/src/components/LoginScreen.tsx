/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Badge, ShieldAlert, Lock, AtSign, Loader2, KeyRound } from 'lucide-react';

interface LoginScreenProps {
  onLoginSuccess: (employeeId: string) => void;
}

export default function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (!employeeId.trim()) {
      setErrorMessage('Employee ID is required');
      return;
    }
    if (!password) {
      setErrorMessage('Password is required');
      return;
    }

    setIsSubmitting(true);

    // Simulate database lookup/auth
    setTimeout(() => {
      setIsSubmitting(false);
      onLoginSuccess(employeeId);
    }, 1200);
  };

  const loadDemoCredentials = () => {
    setEmployeeId('KSP-90210');
    setPassword('••••••••');
  };

  return (
    <div className="min-h-screen w-full flex bg-[#050505] overflow-hidden select-none">
      {/* Left Half: Abstract Karnataka Intelligence Map */}
      <div className="hidden lg:flex w-1/2 h-screen relative bg-black border-r border-white/10 justify-center items-center overflow-hidden">
        {/* Animated tactical SVG map */}
        <div className="w-full h-full p-12 opacity-60 flex items-center justify-center">
          <svg style={{ background: '#000000' }} viewBox="0 0 800 1000" className="w-full h-full max-h-[85vh] object-contain">
            {/* Karnataka Boundary Path abstraction */}
            <path 
              d="M400,50 L450,100 L500,150 L550,250 L580,400 L550,550 L500,750 L450,900 L350,950 L250,900 L200,800 L150,650 L100,500 L120,350 L180,200 L250,100 Z" 
              fill="none" 
              stroke="#00F0FF" 
              strokeOpacity="0.3" 
              strokeWidth="2.5"
            >
              <animate attributeName="stroke-opacity" dur="4s" repeatCount="indefinite" values="0.2;0.6;0.2" />
            </path>
            
            {/* District grids */}
            <path 
              d="M200,300 L500,300 M250,500 L550,500 M300,700 L500,700 M350,200 L450,850 M250,350 L550,750" 
              stroke="#00F0FF" 
              strokeOpacity="0.1" 
              strokeWidth="1" 
            />
            
            {/* Active Nodes */}
            {/* Bengaluru Critical Hotspot */}
            <g>
              <circle cx="480" cy="720" fill="#ff4d4d" r="6">
                <animate attributeName="r" dur="2s" repeatCount="indefinite" values="5;10;5" />
                <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.4;1" />
              </circle>
              <circle cx="480" cy="720" fill="none" opacity="0" r="22" stroke="#ff4d4d" strokeWidth="1.5">
                <animate attributeName="r" dur="2s" repeatCount="indefinite" values="5;30" />
                <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="0.6;0" />
              </circle>
            </g>

            {/* Hubballi Warning Hotspot */}
            <g>
              <circle cx="320" cy="420" fill="#00F0FF" r="5">
                <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="4;8;4" />
                <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="1;0.4;1" />
              </circle>
              <circle cx="320" cy="420" fill="none" opacity="0" r="18" stroke="#00F0FF" strokeWidth="1.2">
                <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="4;24" />
                <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="0.5;0" />
              </circle>
            </g>

            {/* Mysuru warning */}
            <g>
              <circle cx="440" cy="850" fill="#00F0FF" r="4">
                <animate attributeName="opacity" dur="3s" repeatCount="indefinite" values="0.9;0.3;0.9" />
              </circle>
            </g>

            {/* Other minor coordinates */}
            <circle cx="520" cy="300" fill="#00F0FF" opacity="0.6" r="3" />
            <circle cx="280" cy="650" fill="#00F0FF" opacity="0.4" r="3" />
          </svg>
        </div>

        {/* Floating overlays */}
        <div className="absolute top-8 left-8 flex items-center gap-2 text-white/80 font-mono text-[10px] tracking-[0.2em] uppercase font-bold">
          <span className="w-2 h-2 rounded-full bg-[#00F0FF] animate-pulse"></span>
          SYS.OP.ACTIVE
        </div>
        
        <div className="absolute bottom-8 left-8 flex flex-col gap-1 text-white/40 font-mono text-[10px] tracking-wider opacity-75">
          <span>SEC-A // GRID: 44.8291, -73.2910</span>
          <span>DATA FEED: ENCRYPTED // TIER-1</span>
        </div>
      </div>

      {/* Right Half: Elegant Login credentials */}
      <div className="w-full lg:w-1/2 h-screen bg-[#050505] flex flex-col justify-between px-6 py-8 md:px-16 lg:px-24">
        {/* Top brand heading */}
        <div className="mt-4 flex justify-between items-center">
          <div>
            <div className="text-4xl font-black tracking-tighter text-white">
              PRISM<span className="text-[#00F0FF]">.</span>
            </div>
            <div className="text-white/40 text-[10px] uppercase font-bold tracking-[0.15em] mt-1.5">
              Crime Intelligence &amp; Analytics Platform
            </div>
          </div>

          <button 
            onClick={loadDemoCredentials}
            className="text-[10px] font-mono font-bold tracking-[0.15em] border border-[#00F0FF] px-3.5 py-1.5 text-[#00F0FF] bg-[#00F0FF]/5 hover:bg-[#00F0FF]/25 transition-colors uppercase"
          >
            LOAD_DEMO
          </button>
        </div>

        {/* Main form element */}
        <div className="w-full max-w-sm mx-auto flex flex-col justify-center h-full">
          <div className="mb-8">
            <h1 className="text-5xl font-black tracking-tighter text-white uppercase leading-none">
              SYSTEM<br />
              <span className="text-white/30">ACCESS</span>
            </h1>
            <p className="text-white/40 text-xs tracking-wider mt-2.5">
              Please provide credentials to initialize secure terminal connection.
            </p>
          </div>

          {errorMessage && (
            <div className="mb-5 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 text-xs font-mono flex items-center gap-2.5">
              <KeyRound className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Employee ID */}
            <div className="space-y-2">
              <label className="block text-[10px] font-bold text-white/60 tracking-[0.2em] uppercase" htmlFor="employee-id">
                EMPLOYEE ID
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-white/30">
                  <AtSign className="w-4 h-4" />
                </span>
                <input 
                  type="text"
                  id="employee-id"
                  name="employee-id"
                  placeholder="e.g. KSP-90210"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  className="bg-black border border-white/10 text-white block w-full pl-10 pr-4 py-2.5 font-mono text-sm placeholder-white/20 outline-none focus:border-[#00F0FF] focus:ring-1 focus:ring-[#00F0FF] transition-colors"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label className="block text-[10px] font-bold text-white/60 tracking-[0.2em] uppercase" htmlFor="password">
                PASSWORD
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-white/30">
                  <Lock className="w-4 h-4" />
                </span>
                <input 
                  type="password"
                  id="password"
                  name="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-black border border-white/10 text-white block w-full pl-10 pr-4 py-2.5 font-mono text-sm placeholder-white/20 outline-none focus:border-[#00F0FF] focus:ring-1 focus:ring-[#00F0FF] transition-colors"
                  required
                />
              </div>
            </div>

            {/* Details badge info */}
            <p className="text-[10px] tracking-wide text-white/40 leading-relaxed font-mono">
              Role is automatically assigned based on credentials. Terminal activity is fully monitored and audited.
            </p>

            {/* Submit */}
            <button 
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#00F0FF] text-black hover:bg-white transition-colors font-black uppercase text-xs tracking-[0.2em] py-3.5 flex justify-center items-center gap-2 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-black" />
                  <span>AUTHORIZING ENTRY...</span>
                </>
              ) : (
                <span>SIGN_IN_TERMINAL</span>
              )}
            </button>

            <div className="flex items-center justify-between pt-3 font-mono text-[10px] tracking-wider uppercase">
              <button 
                type="button" 
                onClick={() => setErrorMessage('Access request requires supervisor approval.')}
                className="text-[#00F0FF] hover:text-white transition-colors"
              >
                Request Access
              </button>
              <button 
                type="button"
                onClick={() => setErrorMessage('Password recovery is offline. Contact Intel Desk.')}
                className="text-[#00F0FF] hover:text-white transition-colors"
              >
                Forgot Password?
              </button>
            </div>
          </form>
        </div>

        {/* Bottom Footer block */}
        <div className="mb-2 text-center lg:text-left text-[10px] tracking-widest text-white/30 border-t border-white/10 pt-4 font-mono uppercase">
          KARNATAKA STATE POLICE — SECURE INTELLIGENCE PORTAL
        </div>
      </div>
    </div>
  );
}
