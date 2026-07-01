/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';

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
    setPassword('demo1234');
  };

  return (
    <div className="flex flex-1 h-full overflow-hidden">
      {/* Left Half: Atmosphere / Map */}
      <div className="hidden lg:flex flex-none w-1/2 h-full relative bg-[#0A0C10] border-r border-[#252830]">
        {/* Animated SVG Map */}
        <div className="w-full h-full p-20 opacity-70">
          <svg style={{ background: '#0a0c10' }} viewBox="0 0 800 1000" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
            {/* Simplified Karnataka Boundary Path (Representative Silhouette) */}
            <path
              d="M400,50 L450,100 L500,150 L550,250 L580,400 L550,550 L500,750 L450,900 L350,950 L250,900 L200,800 L150,650 L100,500 L120,350 L180,200 L250,100 Z"
              fill="none"
              stroke="#3B6FE8"
              strokeOpacity="0.3"
              strokeWidth="1.5"
            >
              <animate attributeName="stroke-opacity" dur="4s" repeatCount="indefinite" values="0.2;0.4;0.2" />
            </path>
            {/* District Grid Lines */}
            <path
              d="M200,300 L500,300 M250,500 L550,500 M300,700 L500,700"
              stroke="#3B6FE8"
              strokeOpacity="0.1"
              strokeWidth="0.5"
            />
            {/* Pulsing Hotspot — Danger Red */}
            <circle cx="420" cy="350" fill="#E84040" r="4">
              <animate attributeName="r" dur="2s" repeatCount="indefinite" values="3;6;3" />
              <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.4;1" />
            </circle>
            <circle cx="420" cy="350" fill="none" opacity="0" r="12" stroke="#E84040" strokeWidth="1">
              <animate attributeName="r" dur="2s" repeatCount="indefinite" values="4;20" />
              <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="0.5;0" />
            </circle>
            {/* Pulsing Hotspot — Warning Orange */}
            <circle cx="320" cy="600" fill="#E8A030" r="4">
              <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="3;6;3" />
              <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="1;0.4;1" />
            </circle>
            <circle cx="320" cy="600" fill="none" opacity="0" r="12" stroke="#E8A030" strokeWidth="1">
              <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="4;18" />
              <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="0.5;0" />
            </circle>
            {/* Additional nodes */}
            <circle cx="480" cy="220" fill="#E84040" opacity="0.8" r="3">
              <animate attributeName="opacity" dur="3s" repeatCount="indefinite" values="0.8;0.2;0.8" />
            </circle>
            <circle cx="350" cy="150" fill="#E8A030" opacity="0.8" r="3">
              <animate attributeName="opacity" dur="3.5s" repeatCount="indefinite" values="0.8;0.2;0.8" />
            </circle>
          </svg>
        </div>
        {/* Overlay: Active status */}
        <div className="absolute top-8 left-8 flex items-center gap-2 text-on-surface-variant font-label-mono text-label-mono">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          SYS.OP.ACTIVE
        </div>
        {/* Overlay: Coordinates */}
        <div className="absolute bottom-8 left-8 flex flex-col gap-1 text-outline font-label-mono text-xs opacity-60">
          <span>SEC-A // GRID: 44.8291, -73.2910</span>
          <span>DATA FEED: ENCRYPTED // TIER-1</span>
        </div>
      </div>

      {/* Right Half: Login Form */}
      <div className="flex-1 h-full bg-[#0A0C10] flex flex-col justify-between px-8 py-8 lg:px-20 overflow-y-auto">
        {/* Header Branding */}
        <div className="mt-8 flex justify-between items-start">
          <div>
            <div className="font-label-mono text-label-mono tracking-[0.2em] text-on-surface-variant uppercase">
              PRISM
            </div>
            <div className="font-body-sm text-body-sm text-outline mt-1">
              Crime Intelligence &amp; Analytics Platform
            </div>
          </div>
          <button
            type="button"
            onClick={loadDemoCredentials}
            className="text-[10px] font-mono font-bold tracking-[0.15em] border border-primary-container px-3 py-1.5 text-primary-container bg-primary-container/10 hover:bg-primary-container/20 transition-colors uppercase rounded-btn shrink-0 cursor-pointer"
          >
            LOAD DEMO
          </button>
        </div>

        {/* Centered Login Container */}
        <div className="w-full flex flex-col justify-center py-16">
          <h1 className="font-headline-md text-headline-md text-on-surface mb-8">
            System Access
          </h1>

          {errorMessage && (
            <div className="mb-5 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 text-xs font-mono flex items-center gap-2.5">
              <span className="material-symbols-outlined text-[16px] text-red-400 shrink-0">lock</span>
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Employee ID Field */}
            <div className="space-y-2">
              <label className="block font-body-sm text-body-sm text-on-surface-variant" htmlFor="employee-id">
                Employee ID
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-outline text-[18px]">badge</span>
                </span>
                <input
                  className="input-field block w-full pl-10 pr-3 py-2 sm:text-sm font-data-mono-bold text-data-mono-bold rounded-none transition-colors duration-200 outline-none"
                  id="employee-id"
                  name="employee-id"
                  placeholder="e.g. KSP-90210"
                  required
                  type="text"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label className="block font-body-sm text-body-sm text-on-surface-variant" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-outline text-[18px]">lock</span>
                </span>
                <input
                  className="input-field block w-full pl-10 pr-3 py-2 sm:text-sm font-data-mono-bold text-data-mono-bold rounded-none transition-colors duration-200 outline-none"
                  id="password"
                  name="password"
                  placeholder="••••••••"
                  required
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {/* Helper Text */}
            <p className="font-body-sm text-[12px] text-outline leading-tight">
              Role is automatically assigned based on your credentials.
            </p>

            {/* Submit Button */}
            <button
              disabled={isSubmitting}
              className="btn-primary w-full flex justify-center items-center gap-2 py-3 px-4 rounded-btn font-body-md text-body-md font-semibold transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-[#0A0C10] cursor-pointer disabled:opacity-60"
              type="submit"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Authorizing...</span>
                </>
              ) : (
                <span>Sign In</span>
              )}
            </button>

            <div className="flex items-center justify-between mt-4">
              <button
                type="button"
                onClick={() => setErrorMessage('Access request requires supervisor approval.')}
                className="font-body-sm text-body-sm text-primary hover:text-primary-fixed transition-colors cursor-pointer"
              >
                Request Access
              </button>
              <button
                type="button"
                onClick={() => setErrorMessage('Password recovery is offline. Contact Intel Desk.')}
                className="font-body-sm text-body-sm text-primary hover:text-primary-fixed transition-colors cursor-pointer"
              >
                Forgot Password?
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="mb-4 text-center lg:text-left">
          <p className="font-body-sm text-[12px] text-outline">
            Karnataka State Police — Authorized Personnel Only
          </p>
        </div>
      </div>
    </div>
  );
}
