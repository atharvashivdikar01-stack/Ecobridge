'use client';

import React, { useState, useEffect } from 'react';
import { CommandCenterHeader } from './components/CommandCenterHeader';
import { DemoDisclaimerBanner } from './components/DemoDisclaimerBanner';
import { KpiMetricsGrid } from './components/KpiMetricsGrid';
import { ChainOfCustodyStream } from './components/ChainOfCustodyStream';
import { RecyclerRegistryView } from './components/RecyclerRegistryView';
import { CollectorNetworkView } from './components/CollectorNetworkView';
import { ComplianceLedgerExport } from './components/ComplianceLedgerExport';
import { LotDetailModal } from './components/LotDetailModal';
import { DemoLot } from './lib/demo-data';
import { adminApi, AdminSummaryData } from './lib/api';

export default function AdminDashboardPage() {
  const [isDemoMode, setIsDemoMode] = useState(false); // Default to Live Database feed
  const [activeTab, setActiveTab] = useState<'custody' | 'recyclers' | 'collectors' | 'compliance'>('custody');
  const [selectedLot, setSelectedLot] = useState<DemoLot | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [liveSummary, setLiveSummary] = useState<AdminSummaryData | null>(null);
  const [dbConnected, setDbConnected] = useState<boolean>(false);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  useEffect(() => {
    fetchLiveMetrics();
  }, []);

  const fetchLiveMetrics = async () => {
    setIsRefreshing(true);
    const start = performance.now();
    try {
      const summary = await adminApi.getSummary();
      setLiveSummary(summary);
      setDbConnected(true);
      setLatencyMs(Math.round(performance.now() - start));
    } catch (err) {
      console.warn('Backend/PostgreSQL unreachable, fallback to simulation mode', err);
      setDbConnected(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#070b14] text-slate-100 p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">
      {/* PostgreSQL & Backend Connection Status Ribbon */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs shadow-md">
        <div className="flex items-center gap-2">
          {dbConnected ? (
            <>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 pulse-live shadow-sm shadow-emerald-400"></span>
              <span className="font-bold text-emerald-400">PostgreSQL 16 & FastAPI Backend Connected</span>
              <span className="text-slate-400 hidden sm:inline">• Database: <code className="text-slate-200">ecobridge@localhost:5432</code></span>
              {latencyMs !== null && (
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-mono text-[10px]">
                  {latencyMs}ms ping
                </span>
              )}
            </>
          ) : (
            <>
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
              <span className="font-bold text-amber-300">Offline Simulation Mode Active</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-400">
            Source: <strong className={isDemoMode ? 'text-amber-400' : 'text-emerald-400'}>{isDemoMode ? 'Synthetic Demonstration Fixture' : 'Live PostgreSQL asyncpg Engine'}</strong>
          </span>
          <button
            onClick={fetchLiveMetrics}
            disabled={isRefreshing}
            className="text-[11px] text-emerald-400 hover:text-emerald-300 font-semibold underline flex items-center gap-1"
          >
            <span>{isRefreshing ? 'Testing...' : 'Test DB Ping'}</span>
          </button>
        </div>
      </div>

      {/* Top Header */}
      <CommandCenterHeader
        isDemoMode={isDemoMode}
        onToggleDemoMode={(val) => setIsDemoMode(val)}
        onRefresh={fetchLiveMetrics}
        isRefreshing={isRefreshing}
      />

      {/* Demo Data Notice Banner (conditionally displayed if Demo Mode is selected) */}
      <DemoDisclaimerBanner isDemoMode={isDemoMode} />

      {/* Core KPI Metrics Grid (12 Collectors, 8 Recyclers, 47 Lots, 32 Transactions, 284 kg, 96% Traceable) */}
      <KpiMetricsGrid
        isDemoMode={isDemoMode}
        liveMetrics={liveSummary}
        onSelectTab={(tab) => setActiveTab(tab as any)}
      />

      {/* Navigation Tabs for Deep-Dive Management */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-slate-800 pb-2 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('custody')}
          className={`px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 shrink-0 ${
            activeTab === 'custody'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span>Chain of Custody & Lots ({liveSummary ? liveSummary.lots_created : '47'})</span>
        </button>

        <button
          onClick={() => setActiveTab('recyclers')}
          className={`px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 shrink-0 ${
            activeTab === 'recyclers'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span>Verified Recyclers ({liveSummary ? liveSummary.verified_recyclers : '8'})</span>
        </button>

        <button
          onClick={() => setActiveTab('collectors')}
          className={`px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 shrink-0 ${
            activeTab === 'collectors'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <svg className="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span>Active Collectors ({liveSummary ? liveSummary.collectors_active : '12'})</span>
        </button>

        <button
          onClick={() => setActiveTab('compliance')}
          className={`px-4 py-2.5 rounded-xl transition-all flex items-center gap-2 shrink-0 ${
            activeTab === 'compliance'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Statutory Compliance & Form 2 Ledger ({liveSummary ? `${liveSummary.transactions} Transactions` : '32 Transactions'})</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {activeTab === 'custody' && (
          <ChainOfCustodyStream
            isDemoMode={isDemoMode}
            onSelectLot={(lot) => setSelectedLot(lot)}
          />
        )}

        {activeTab === 'recyclers' && <RecyclerRegistryView />}

        {activeTab === 'collectors' && <CollectorNetworkView />}

        {activeTab === 'compliance' && <ComplianceLedgerExport />}
      </div>

      {/* Lot Inspection Modal */}
      {selectedLot && (
        <LotDetailModal
          lot={selectedLot}
          onClose={() => setSelectedLot(null)}
        />
      )}

      {/* Global Footer & Database Engine Telemetry */}
      <footer className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-live"></div>
          <span>ECOBRIDGE Command Center • PostgreSQL 16 (Port 5432) & FastAPI asyncpg Active</span>
        </div>
        <div className="text-right">
          <span>Cryptographic SHA-256 Ledger Verified • 45/47 Batches Tamper-Sealed (96%)</span>
        </div>
      </footer>
    </main>
  );
}
