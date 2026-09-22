'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, DashboardSummary, AvailableMaterialItem } from '../lib/api';

export default function DashboardOverviewPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentLots, setRecentLots] = useState<AvailableMaterialItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashData, matsData] = await Promise.all([
        api.getDashboard(),
        api.getMaterials(),
      ]);
      setSummary(dashData);
      setRecentLots(matsData.items.slice(0, 5));
    } catch (err) {
      console.error('Failed to load overview data', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COLLECTED':
      case 'AVAILABLE':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">AVAILABLE FOR INWARD</span>;
      case 'ACCEPTED':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">OFFER ACCEPTED</span>;
      case 'HANDED_OVER':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">SCALE WEIGHED • PENDING PAY</span>;
      case 'SETTLED':
      case 'COMPLETED':
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">COMPLETED & SETTLED</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-500/15 text-slate-300 border border-slate-500/30">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading recycler plant telemetry...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Operations & Procurement Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time material intake, weighbridge scale verification, and statutory accounting ledger.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/dashboard/materials')}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-lg shadow-emerald-600/20 transition-all flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Procure Available Lots</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Available Lots</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-extrabold text-white mt-3">{summary?.available_lots_count ?? 0}</p>
          <p className="text-[11px] text-slate-400 mt-1">Staged by informal collectors</p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending Handovers</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-extrabold text-amber-300 mt-3">{summary?.pending_handovers_count ?? 0}</p>
          <p className="text-[11px] text-slate-400 mt-1">Awaiting physical weighbridge intake</p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Recycled Volume</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-extrabold text-white mt-3">
            {summary?.total_weight_recycled_kg ? summary.total_weight_recycled_kg.toFixed(1) : '0.0'} <span className="text-base font-normal text-slate-400">kg</span>
          </p>
          <p className="text-[11px] text-emerald-400 mt-1">Certified scale weighed</p>
        </div>

        <div className="glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Disbursements</span>
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-400 flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-extrabold text-emerald-400 mt-3">
            ₹{summary?.total_payouts_inr ? summary.total_payouts_inr.toLocaleString('en-IN') : '0'}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">{summary?.completed_transactions_count ?? 0} settled transactions</p>
        </div>
      </div>

      {/* Traceable Lifecycle Progression Banner */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>Verified Recycler Golden Journey (SIH 2026 Core Flow)</span>
          </h2>
          <span className="text-[10px] text-slate-400 font-mono">Immutable Traceability Pipeline</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 pt-2">
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">1</div>
            <p className="text-xs font-semibold text-white">Discovery</p>
            <p className="text-[10px] text-slate-400 mt-0.5">View Available Material</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">2</div>
            <p className="text-xs font-semibold text-white">Review AI</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Classification & Hazards</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">3</div>
            <p className="text-xs font-semibold text-white">Agree Rate</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Verified Recycler Accept</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">4</div>
            <p className="text-xs font-semibold text-white">Scale Intake</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Weighbridge Slip & Net Kg</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">5</div>
            <p className="text-xs font-semibold text-white">Payout</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Cash / Digital Settlement</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center justify-center mx-auto mb-1.5">6</div>
            <p className="text-xs font-semibold text-white">Ledger</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Statutory Audit Record</p>
          </div>
        </div>
      </div>

      {/* Recent Collection Batches Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Recent E-Waste Collection Batches</h2>
            <p className="text-xs text-slate-400">Live incoming inventory from informal collectors in Mumbai Metropolitan Region.</p>
          </div>
          <button
            onClick={() => router.push('/dashboard/materials')}
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>View All Batches</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="pb-3 font-semibold">Lot Code</th>
                <th className="pb-3 font-semibold">Material & AI Tag</th>
                <th className="pb-3 font-semibold">Weight</th>
                <th className="pb-3 font-semibold">Hazard Condition</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {recentLots.map((lot) => (
                <tr key={lot.lot_id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3.5 font-mono font-bold text-white">{lot.lot_code}</td>
                  <td className="py-3.5">
                    <p className="font-semibold text-slate-200">{lot.material_name}</p>
                    <p className="text-[11px] text-slate-400">AI Confidence: {lot.ai_confidence_score ? `${(lot.ai_confidence_score * 100).toFixed(1)}%` : 'Advisory'}</p>
                  </td>
                  <td className="py-3.5">
                    <span className="font-bold text-white">
                      {lot.verified_weight_kg ? lot.verified_weight_kg.toFixed(1) : lot.estimated_weight_kg.toFixed(1)} kg
                    </span>
                    <span className="text-[10px] text-slate-400 block">{lot.verified_weight_kg ? 'Scale Verified' : 'Collector Approx'}</span>
                  </td>
                  <td className="py-3.5">
                    {lot.detected_hazard === 'NORMAL' ? (
                      <span className="text-[10px] text-slate-400 font-medium">Standard</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30 text-[10px] font-bold">
                        ⚠️ {lot.detected_hazard.replace('_', ' ')}
                      </span>
                    )}
                  </td>
                  <td className="py-3.5">{getStatusBadge(lot.status)}</td>
                  <td className="py-3.5 text-right">
                    <button
                      onClick={() => router.push(`/dashboard/materials/${lot.lot_id}`)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 hover:text-white text-slate-300 font-medium text-xs transition-colors"
                    >
                      Inspect Lot
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
