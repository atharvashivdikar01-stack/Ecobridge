'use client';

import { useEffect, useState } from 'react';
import { api, LedgerResponse } from '../../lib/api';

export default function LedgerPage() {
  const [ledger, setLedger] = useState<LedgerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getLedger()
      .then(setLedger)
      .catch((e) => setError(e instanceof Error ? e.message : 'Unable to load ledger.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading statutory ledger records...</p>
        </div>
      </div>
    );
  }

  const summaryCards = [
    {
      label: 'Total Transactions',
      value: ledger?.total_transactions || 0,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      color: 'text-blue-400 bg-blue-500/10',
    },
    {
      label: 'Total Volume Recycled',
      value: `${(ledger?.total_volume_kg || 0).toFixed(1)} kg`,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
        </svg>
      ),
      color: 'text-emerald-400 bg-emerald-500/10',
    },
    {
      label: 'Total Disbursed',
      value: `₹${(ledger?.total_disbursed_inr || 0).toLocaleString('en-IN')}`,
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'text-teal-400 bg-teal-500/10',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          Accounting &amp; EPR Compliance Ledger
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Immutable settlement history — SHA-256 tamper-evident records for CPCB statutory audit.
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl p-4 bg-rose-500/10 border border-rose-500/30 text-sm text-rose-300 font-medium flex items-center gap-3">
          <svg className="w-5 h-5 text-rose-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {summaryCards.map((card) => (
          <div key={card.label} className="glass-card p-5 rounded-2xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{card.label}</span>
              <div className={`w-8 h-8 rounded-lg ${card.color} flex items-center justify-center`}>
                {card.icon}
              </div>
            </div>
            <p className="text-3xl font-extrabold text-white mt-3">{card.value}</p>
          </div>
        ))}
      </div>

      {/* Transactions Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Settlement Transaction Records</h2>
            <p className="text-xs text-slate-400">Statutory EPR custody chain for all settled lots.</p>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">
            {ledger?.total_transactions || 0} record{(ledger?.total_transactions || 0) !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="pb-3 font-semibold">Lot Reference</th>
                <th className="pb-3 font-semibold">Collector</th>
                <th className="pb-3 font-semibold">Material</th>
                <th className="pb-3 font-semibold">Verified Weight</th>
                <th className="pb-3 font-semibold">Rate</th>
                <th className="pb-3 font-semibold">Settlement</th>
                <th className="pb-3 font-semibold">Method</th>
                <th className="pb-3 font-semibold">Custody Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(ledger?.transactions || []).length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-2">
                      <svg className="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      <span className="text-sm">No settled transactions yet</span>
                      <span className="text-[11px] text-slate-600">Complete a handover and record payment to see records here.</span>
                    </div>
                  </td>
                </tr>
              ) : (
                (ledger?.transactions || []).map((tx) => (
                  <tr key={`${tx.lot_id}-${tx.reference_number}`} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3.5 font-mono font-bold text-white">{tx.lot_id.slice(0, 8).toUpperCase()}</td>
                    <td className="py-3.5">
                      <p className="font-semibold text-slate-200">{tx.collector_name}</p>
                      <p className="text-[11px] text-slate-500">{tx.collector_phone}</p>
                    </td>
                    <td className="py-3.5 text-slate-300">{tx.material_name}</td>
                    <td className="py-3.5 font-mono font-bold text-white">{tx.verified_weight_kg} kg</td>
                    <td className="py-3.5 font-mono text-slate-300">₹{tx.agreed_price_per_kg}/kg</td>
                    <td className="py-3.5">
                      <span className="font-mono font-bold text-emerald-400">₹{tx.total_amount.toLocaleString('en-IN')}</span>
                    </td>
                    <td className="py-3.5">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-semibold uppercase">
                        {tx.payment_method}
                      </span>
                    </td>
                    <td className="py-3.5">
                      <span className="font-mono text-[10px] text-slate-500 block max-w-[100px] truncate" title={tx.custody_hash}>
                        {tx.custody_hash ? `${tx.custody_hash.slice(0, 12)}…` : '—'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
