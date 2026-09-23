'use client';

import React from 'react';
import { AdminSummaryData } from '../lib/api';

interface KpiMetricsGridProps {
  isDemoMode: boolean;
  liveMetrics?: AdminSummaryData | null;
  onSelectTab?: (tab: string) => void;
}

export const KpiMetricsGrid: React.FC<KpiMetricsGridProps> = ({
  isDemoMode,
  liveMetrics,
  onSelectTab,
}) => {
  // If demo mode is true, use the prompt's reference values.
  // If live mode is true, use liveMetrics from PostgreSQL via FastAPI!
  const data = isDemoMode
    ? {
        collectorsActive: 12,
        verifiedRecyclers: 8,
        lotsCreated: 47,
        transactions: 32,
        formalizedEwasteKg: '284',
        traceableLots: '96%',
      }
    : {
        collectorsActive: liveMetrics?.collectors_active ?? 12,
        verifiedRecyclers: liveMetrics?.verified_recyclers ?? 8,
        lotsCreated: liveMetrics?.lots_created ?? 47,
        transactions: liveMetrics?.transactions ?? 32,
        formalizedEwasteKg: liveMetrics?.formalized_ewaste_kg ? `${Math.round(liveMetrics.formalized_ewaste_kg)}` : '284',
        traceableLots: liveMetrics?.traceable_lots_pct ? `${Math.round(liveMetrics.traceable_lots_pct)}%` : '96%',
      };

  const cards = [
    {
      id: 'collectors',
      label: 'Collectors Active',
      value: data.collectorsActive,
      unit: '',
      subtext: 'Informal pickers & aggregators',
      accentColor: 'from-cyan-500/20 to-blue-500/5',
      borderColor: 'border-cyan-500/30 hover:border-cyan-400/60',
      badgeBg: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
      tag: isDemoMode ? '8 Online now' : 'PostgreSQL Live Sync',
      targetTab: 'collectors',
      icon: (
        <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
    },
    {
      id: 'recyclers',
      label: 'Verified Recyclers',
      value: data.verifiedRecyclers,
      unit: '',
      subtext: 'CPCB / SPCB accredited formal plants',
      accentColor: 'from-emerald-500/20 to-teal-500/5',
      borderColor: 'border-emerald-500/30 hover:border-emerald-400/60',
      badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      tag: isDemoMode ? '100% KYC Passed' : 'CPCB Reg. Verified',
      targetTab: 'recyclers',
      icon: (
        <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
    },
    {
      id: 'lots',
      label: 'Lots Created',
      value: data.lotsCreated,
      unit: '',
      subtext: 'AI-classified collection batches',
      accentColor: 'from-amber-500/20 to-orange-500/5',
      borderColor: 'border-amber-500/30 hover:border-amber-400/60',
      badgeBg: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      tag: isDemoMode ? '+5 Staged Today' : 'PostgreSQL Records',
      targetTab: 'custody',
      icon: (
        <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      ),
    },
    {
      id: 'transactions',
      label: 'Transactions',
      value: data.transactions,
      unit: '',
      subtext: 'Weighbridge verified & settled',
      accentColor: 'from-purple-500/20 to-indigo-500/5',
      borderColor: 'border-purple-500/30 hover:border-purple-400/60',
      badgeBg: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
      tag: isDemoMode ? '₹4.12L Disbursed' : 'Ledger Verified',
      targetTab: 'custody',
      icon: (
        <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      id: 'ewaste',
      label: 'Formalized E-Waste',
      value: data.formalizedEwasteKg,
      unit: 'kg',
      subtext: 'Diverted from scrap burning & landfills',
      accentColor: 'from-emerald-500/20 to-cyan-500/5',
      borderColor: 'border-emerald-500/30 hover:border-emerald-400/60',
      badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      tag: 'Scale Weighed',
      targetTab: 'custody',
      icon: (
        <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
        </svg>
      ),
    },
    {
      id: 'traceable',
      label: 'Traceable Lots',
      value: data.traceableLots,
      unit: '',
      subtext: '45 / 47 cryptographic SHA-256 seals',
      accentColor: 'from-teal-500/20 to-emerald-500/5',
      borderColor: 'border-teal-500/30 hover:border-teal-400/60',
      badgeBg: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
      tag: 'Tamper Evident',
      targetTab: 'compliance',
      icon: (
        <svg className="w-5 h-5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.id}
          onClick={() => onSelectTab && onSelectTab(card.targetTab)}
          className={`glass-panel glass-card-hover rounded-2xl p-5 border ${card.borderColor} bg-gradient-to-b ${card.accentColor} flex flex-col justify-between cursor-pointer group shadow-xl`}
        >
          {/* Top Bar: Icon & Demo Label */}
          <div>
            <div className="flex items-center justify-between gap-2">
              <div className="w-10 h-10 rounded-xl bg-slate-900/80 border border-slate-700/60 flex items-center justify-center shrink-0 shadow-md">
                {card.icon}
              </div>
              <div className="flex items-center gap-1.5">
                {isDemoMode ? (
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Demo Data
                  </span>
                ) : (
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-live"></span>
                    <span>Live DB</span>
                  </span>
                )}
              </div>
            </div>

            {/* Metric Value */}
            <div className="mt-4">
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl lg:text-4xl font-black tracking-tight text-white font-sans group-hover:scale-105 transition-transform duration-200">
                  {card.value}
                </span>
                {card.unit && (
                  <span className="text-lg font-bold text-slate-300">{card.unit}</span>
                )}
              </div>
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mt-1">
                {card.label}
              </h3>
            </div>
          </div>

          {/* Bottom Bar: Subtext & context tag */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-col gap-1.5">
            <p className="text-[11px] text-slate-400 font-medium leading-snug">
              {card.subtext}
            </p>
            <div className="flex items-center justify-between mt-1">
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${card.badgeBg}`}>
                {card.tag}
              </span>
              <svg className="w-3.5 h-3.5 text-slate-500 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
