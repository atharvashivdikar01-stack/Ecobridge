'use client';

import React from 'react';
import { DEMO_RECYCLERS } from '../lib/demo-data';

export const RecyclerRegistryView: React.FC = () => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Verified Recycler Facilities (CPCB/SPCB Accredited)</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              8 Verified Plants
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Registered industrial smelters, hydrometallurgical processors, and material recovery facilities authorized under CPCB E-Waste Management Rules 2022.
          </p>
        </div>

        <span className="text-xs text-slate-400 font-mono">
          Combined Capacity: <strong className="text-white">138,000 kg / month</strong>
        </span>
      </div>

      {/* Grid of Recyclers */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {DEMO_RECYCLERS.map((recycler) => (
          <div
            key={recycler.id}
            className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-emerald-500/40 transition-all flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {recycler.cpcbRegistrationNo}
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-300 bg-emerald-500/15 px-2 py-0.5 rounded border border-emerald-500/30">
                  ✓ VERIFIED
                </span>
              </div>

              <h3 className="font-bold text-white text-sm mt-2.5 leading-snug">{recycler.companyName}</h3>
              <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <span>📍</span>
                <span>{recycler.location}</span>
              </p>
            </div>

            <div className="pt-3 border-t border-slate-800/80 space-y-2 text-xs">
              <div className="flex justify-between items-center text-slate-400">
                <span>Monthly Cap:</span>
                <span className="font-bold text-white font-mono">{recycler.monthlyCapacityKg.toLocaleString()} kg</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>Lots Inwarded:</span>
                <span className="font-bold text-emerald-400">{recycler.lotsReceived} batches</span>
              </div>
              <div className="flex justify-between items-center text-slate-400">
                <span>Weighbridge:</span>
                <span className="font-mono text-[10px] text-slate-300">{recycler.weighbridgeScaleId}</span>
              </div>
              <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
                <span>Last Activity:</span>
                <span>{recycler.lastIntake}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
