'use client';

import React from 'react';
import { DEMO_COLLECTORS } from '../lib/demo-data';

export const CollectorNetworkView: React.FC = () => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Active Informal Collector Network</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              12 Active Collectors
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Waste pickers, scrap aggregators, and kabadiwalas using the offline-first mobile client (collector_app) across Mumbai Metropolitan Region.
          </p>
        </div>

        <span className="text-xs text-slate-400 font-mono">
          Total Staged: <strong className="text-cyan-400">318.9 kg</strong>
        </span>
      </div>

      {/* Grid of 12 Collectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {DEMO_COLLECTORS.map((collector) => (
          <div
            key={collector.id}
            className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col justify-between space-y-3"
          >
            <div>
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>{collector.name}</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                  {collector.kycDocType}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <span>📍</span>
                <span>{collector.hub}</span>
              </p>
              <p className="text-[10px] text-slate-500 mt-0.5 font-mono">{collector.phone}</p>
            </div>

            <div className="pt-3 border-t border-slate-800/80 space-y-1.5 text-xs">
              <div className="flex justify-between items-center text-slate-400">
                <span>Staged Volume:</span>
                <span className="font-bold text-white font-mono">{collector.totalKgStaged.toFixed(1)} kg</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>Batches Staged:</span>
                <span className="font-bold text-cyan-400">{collector.lotsCount} lots</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>Trust Score:</span>
                <span className="font-bold text-emerald-400">{collector.trustScore}%</span>
              </div>
              <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
                <span>Last Telemetry:</span>
                <span>{collector.lastActive}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
