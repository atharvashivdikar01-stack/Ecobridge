'use client';

import React from 'react';

interface CommandCenterHeaderProps {
  isDemoMode: boolean;
  onToggleDemoMode: (val: boolean) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const CommandCenterHeader: React.FC<CommandCenterHeaderProps> = ({
  isDemoMode,
  onToggleDemoMode,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <header className="glass-panel rounded-2xl p-6 relative overflow-hidden border border-slate-800/80 shadow-2xl">
      {/* Background ambient glow effect */}
      <div className="absolute top-0 right-1/4 w-96 h-32 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -top-10 -left-10 w-72 h-32 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Brand & Title */}
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-slate-900 border border-emerald-500/40 flex items-center justify-center shadow-lg shadow-emerald-500/10 shrink-0">
            <svg className="w-8 h-8 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white uppercase font-sans">
                ECOBRIDGE COMMAND CENTER
              </h1>

              {/* Required Demo Data indicator badge */}
              {isDemoMode ? (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-amber-500/15 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/10">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>Demo Data</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-emerald-500/15 text-emerald-300 border border-emerald-500/40">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-live" />
                  <span>Live Network</span>
                </div>
              )}
            </div>

            <p className="text-xs sm:text-sm text-slate-400 mt-1 font-medium">
              National E-Waste Formalization Telemetry & Cryptographic Chain of Custody Node
            </p>
          </div>
        </div>

        {/* Telemetry controls and Data Source Switch */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Telemetry Mode Toggle */}
          <div className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => onToggleDemoMode(true)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                isDemoMode
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Demo Telemetry
            </button>
            <button
              onClick={() => onToggleDemoMode(false)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                !isDemoMode
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Live Feed
            </button>
          </div>

          {/* Refresh Pulse Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="px-3.5 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700/90 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
            title="Refresh active telemetry stream"
          >
            <svg
              className={`w-4 h-4 text-emerald-400 ${isRefreshing ? 'animate-spin' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span>{isRefreshing ? 'Syncing...' : 'Sync Telemetry'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
