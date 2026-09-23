'use client';

import React, { useState } from 'react';
import { DemoLot, DEMO_LOTS } from '../lib/demo-data';

interface ChainOfCustodyStreamProps {
  onSelectLot: (lot: DemoLot) => void;
  isDemoMode: boolean;
}

export const ChainOfCustodyStream: React.FC<ChainOfCustodyStreamProps> = ({
  onSelectLot,
  isDemoMode,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [onlyHazardous, setOnlyHazardous] = useState(false);

  const lots = isDemoMode ? DEMO_LOTS : [];

  const filteredLots = lots.filter((lot) => {
    const matchesSearch =
      lot.lotCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lot.materialName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lot.collectorName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lot.recyclerName && lot.recyclerName.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory = categoryFilter === 'ALL' || lot.category === categoryFilter;
    const matchesStatus = statusFilter === 'ALL' || lot.status === statusFilter;
    const matchesHazard = !onlyHazardous || lot.hazardCondition !== 'NORMAL';

    return matchesSearch && matchesCategory && matchesStatus && matchesHazard;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COLLECTED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">COLLECTED</span>;
      case 'ACCEPTED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">OFFER ACCEPTED</span>;
      case 'HANDED_OVER':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">SCALE WEIGHED</span>;
      case 'SETTLED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">SETTLED & SEALED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/15 text-slate-300">{status}</span>;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-5 shadow-2xl">
      {/* Title & Stats Ribbon */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Chain of Custody & Batch Manifest</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
              Demo Feed (47 Lots Total)
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time audit log of collection batches, AI hazard scans, weighbridge slips, and cryptographic SHA-256 seal records.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700/60 text-slate-300">
            Traceability Integrity: <strong className="text-emerald-400">96% (45/47)</strong>
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center gap-3 pt-2">
        {/* Search */}
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search lot code, material name, collector, or recycler..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
          <svg className="w-4 h-4 text-slate-500 absolute right-3.5 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Category Filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          aria-label="Filter lots by material category"
          className="bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
        >
          <option value="ALL">All Categories</option>
          <option value="PCBs">PCBs (High Grade)</option>
          <option value="Batteries">Batteries (Li-Ion)</option>
          <option value="Glass/CRTs">Glass & CRTs</option>
          <option value="Telecom">Telecom Relays</option>
          <option value="Mixed">Mixed Scrap</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Filter lots by workflow status"
          className="bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
        >
          <option value="ALL">All Statuses</option>
          <option value="COLLECTED">Collected (Staged)</option>
          <option value="ACCEPTED">Offer Accepted</option>
          <option value="HANDED_OVER">Scale Weighed</option>
          <option value="SETTLED">Settled & Paid</option>
        </select>

        {/* Hazardous Toggle */}
        <button
          onClick={() => setOnlyHazardous(!onlyHazardous)}
          className={`px-3.5 py-2.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
            onlyHazardous
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-sm shadow-rose-500/20'
              : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-slate-200'
          }`}
        >
          <span>⚠️</span>
          <span>Hazardous Only</span>
        </button>
      </div>

      {/* Table view */}
      <div className="overflow-x-auto rounded-xl border border-slate-800/80">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-3 px-4 font-semibold">Lot Code</th>
              <th className="py-3 px-4 font-semibold">Material & AI Scan</th>
              <th className="py-3 px-4 font-semibold">Weight</th>
              <th className="py-3 px-4 font-semibold">Collector Hub</th>
              <th className="py-3 px-4 font-semibold">Hazard Condition</th>
              <th className="py-3 px-4 font-semibold">Status</th>
              <th className="py-3 px-4 font-semibold">SHA-256 Custody</th>
              <th className="py-3 px-4 font-semibold text-right">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredLots.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  No collection lots match the current criteria.
                </td>
              </tr>
            ) : (
              filteredLots.map((lot) => (
                <tr
                  key={lot.id}
                  onClick={() => onSelectLot(lot)}
                  className="hover:bg-slate-900/70 transition-colors cursor-pointer group"
                >
                  <td className="py-3.5 px-4 font-mono font-bold text-white group-hover:text-emerald-400 transition-colors">
                    {lot.lotCode}
                  </td>
                  <td className="py-3.5 px-4 max-w-xs">
                    <p className="font-semibold text-slate-200 truncate">{lot.materialName}</p>
                    <p className="text-[11px] text-slate-400">
                      AI Conf: <span className="text-emerald-400">{(lot.aiConfidence * 100).toFixed(1)}%</span>
                    </p>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-white">
                      {lot.verifiedWeightKg ? `${lot.verifiedWeightKg.toFixed(1)} kg` : `${lot.estimatedWeightKg.toFixed(1)} kg`}
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      {lot.verifiedWeightKg ? 'Scale Verified' : 'Est. Collector'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <p className="text-slate-300 font-medium">{lot.collectorName}</p>
                    <p className="text-[10px] text-slate-500">{lot.collectorHub}</p>
                  </td>
                  <td className="py-3.5 px-4">
                    {lot.hazardCondition === 'NORMAL' ? (
                      <span className="text-[10px] text-slate-400 font-medium">Standard</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30 text-[10px] font-bold">
                        ⚠️ {lot.hazardCondition.replace(/_/g, ' ')}
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4">{getStatusBadge(lot.status)}</td>
                  <td className="py-3.5 px-4 font-mono text-[10px]">
                    {lot.isTraceable ? (
                      <span className="text-emerald-400 flex items-center gap-1 font-semibold" title={lot.custodyHash}>
                        <span>🔒</span>
                        <span>{lot.custodyHash.slice(0, 8)}...</span>
                      </span>
                    ) : (
                      <span className="text-rose-400 font-semibold flex items-center gap-1">
                        <span>⚠️</span>
                        <span>Pending</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectLot(lot);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-emerald-600 hover:text-white text-slate-300 text-[11px] font-medium transition-colors"
                    >
                      Audit
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
        <span>Showing {filteredLots.length} of {lots.length} simulated collection lots</span>
        <span className="font-mono text-[11px] text-emerald-400">Total Formalized Volume: 284 kg</span>
      </div>
    </div>
  );
};
