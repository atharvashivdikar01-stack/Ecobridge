'use client';

import React, { useState } from 'react';
import {
  DEMO_TRANSACTIONS,
  MATERIAL_VOLUME_BREAKDOWN,
  DEMO_SUMMARY_METRICS,
} from '../lib/demo-data';

export const ComplianceLedgerExport: React.FC = () => {
  const [downloadNotice, setDownloadNotice] = useState<string | null>(null);

  const handleExportJSON = () => {
    const payload = {
      exportMetadata: {
        format: 'CPCB_FORM_2_AUDIT_MANIFEST',
        version: '2026.1',
        exportTimestamp: new Date().toISOString(),
        disclaimer: 'DEMO DATA: Simulated compliance export for demonstration testing.',
      },
      summary: DEMO_SUMMARY_METRICS,
      materialComposition: MATERIAL_VOLUME_BREAKDOWN,
      settledTransactions: DEMO_TRANSACTIONS,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ecobridge-cpcb-demo-ledger-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    setDownloadNotice('CPCB Form 2 statutory audit ledger exported as JSON.');
    setTimeout(() => setDownloadNotice(null), 4000);
  };

  const handleExportCSV = () => {
    const headers = [
      'Reference No',
      'Lot Code',
      'Informal Collector',
      'Verified Recycler',
      'Verified Weight (kg)',
      'Agreed Rate (INR/kg)',
      'Total Disbursed (INR)',
      'Payment Method',
      'Weighbridge Slip',
      'Custody Hash',
      'Settlement Date',
    ];

    const rows = DEMO_TRANSACTIONS.map((t) => [
      t.referenceNo,
      t.lotCode,
      `"${t.collectorName}"`,
      `"${t.recyclerName}"`,
      t.verifiedWeightKg,
      t.agreedPricePerKg,
      t.totalAmountInr,
      t.paymentMethod,
      t.weighbridgeSlip,
      t.custodyHash,
      t.settledAt,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ecobridge-settled-transactions-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);

    setDownloadNotice('Settled weighbridge transactions exported as CSV.');
    setTimeout(() => setDownloadNotice(null), 4000);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Statutory Compliance & Regulatory Ledger</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              Form 2 / Form 3
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Immutable chain-of-custody ledger for environmental auditors (CPCB/SPCB) and voluntary corporate EPR buyers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Export CSV</span>
          </button>
          <button
            onClick={handleExportJSON}
            className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-lg shadow-emerald-600/20"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>Export JSON Manifest</span>
          </button>
        </div>
      </div>

      {downloadNotice && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2 animate-in fade-in">
          <span>✓</span>
          <span>{downloadNotice}</span>
        </div>
      )}

      {/* Material Composition Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {MATERIAL_VOLUME_BREAKDOWN.map((mat) => (
          <div key={mat.name} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white truncate">{mat.name}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {mat.sharePct}%
              </span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-black text-white">{mat.weightKg}</span>
              <span className="text-xs text-slate-400">kg</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${mat.sharePct}%`, backgroundColor: mat.color }} />
            </div>
            <span className="text-[10px] text-slate-400 block pt-1">{mat.badge}</span>
          </div>
        ))}
      </div>

      {/* Transactions Table Preview */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Settled Transactions (32 Total • ₹4,12,850 Disbursed)
          </h3>
          <span className="text-[10px] text-amber-300 font-mono">Demo Telemetry</span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4 font-semibold">Ref No</th>
                <th className="py-3 px-4 font-semibold">Lot Code</th>
                <th className="py-3 px-4 font-semibold">Collector</th>
                <th className="py-3 px-4 font-semibold">Recycler</th>
                <th className="py-3 px-4 font-semibold">Weighed Net</th>
                <th className="py-3 px-4 font-semibold">Rate</th>
                <th className="py-3 px-4 font-semibold">Disbursed</th>
                <th className="py-3 px-4 font-semibold">Method</th>
                <th className="py-3 px-4 font-semibold">Weighbridge Slip</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {DEMO_TRANSACTIONS.map((txn) => (
                <tr key={txn.id} className="hover:bg-slate-900/60 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-white">{txn.referenceNo}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400">{txn.lotCode}</td>
                  <td className="py-3 px-4 text-slate-300">{txn.collectorName}</td>
                  <td className="py-3 px-4 text-slate-300">{txn.recyclerName}</td>
                  <td className="py-3 px-4 font-bold text-white">{txn.verifiedWeightKg} kg</td>
                  <td className="py-3 px-4 text-slate-400">₹{txn.agreedPricePerKg}/kg</td>
                  <td className="py-3 px-4 font-bold text-emerald-300">₹{txn.totalAmountInr.toLocaleString('en-IN')}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {txn.paymentMethod.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[10px] text-slate-400">{txn.weighbridgeSlip}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
