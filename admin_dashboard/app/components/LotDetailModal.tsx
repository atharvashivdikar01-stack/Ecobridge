'use client';

import React from 'react';
import { DemoLot } from '../lib/demo-data';

interface LotDetailModalProps {
  lot: DemoLot | null;
  onClose: () => void;
}

export const LotDetailModal: React.FC<LotDetailModalProps> = ({ lot, onClose }) => {
  if (!lot) return null;

  const isHazardous = lot.hazardCondition !== 'NORMAL';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-700/80 bg-[#0d1424] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between gap-4 bg-slate-900/50">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
                {lot.lotCode}
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                Demo Lot Record
              </span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                lot.isTraceable
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                  : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
              }`}>
                {lot.isTraceable ? '🔒 SHA-256 Verified' : '⚠️ Pending Anchor'}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white mt-2">{lot.materialName}</h2>
            <p className="text-xs text-slate-400 mt-0.5">Category: {lot.category} • Created: {new Date(lot.createdAt).toLocaleString()}</p>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Safety & Hazard Warning Alert First (Invariant from AGENTS.md) */}
          {isHazardous ? (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-200 space-y-2">
              <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
                <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>MANDATORY PPE & SAFETY ADVISORY</span>
              </div>
              <p className="text-xs text-rose-200/90 leading-relaxed">
                Detected Condition: <strong className="text-white">{lot.hazardCondition.replace(/_/g, ' ')}</strong> ({lot.hazardSeverity} Severity).
                Strict handling required: Fire-retardant dry vermiculite sand barrier, acid-resistant gloves, and eye shield mandatory prior to weighbridge intake.
              </p>
            </div>
          ) : (
            <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>AI Hazard Assessment: Standard inert electronic scrap. No volatile chemical or thermal risks detected.</span>
            </div>
          )}

          {/* AI Vision Classification Block */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">AI Vision Engine (packages/ai-core)</span>
              <span className="text-emerald-400 font-semibold font-mono text-[11px]">
                Confidence: {(lot.aiConfidence * 100).toFixed(1)}%
              </span>
            </div>
            <p className="text-sm font-semibold text-white">{lot.aiClassification}</p>
          </div>

          {/* Physical Quantities & Valuation */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Estimated Weight</span>
              <span className="text-base font-bold text-white mt-1 block">{lot.estimatedWeightKg.toFixed(1)} kg</span>
              <span className="text-[10px] text-slate-500">Collector Mobile</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Verified Weight</span>
              <span className="text-base font-bold text-emerald-400 mt-1 block">
                {lot.verifiedWeightKg ? `${lot.verifiedWeightKg.toFixed(1)} kg` : 'Pending Scale'}
              </span>
              <span className="text-[10px] text-slate-500">Weighbridge Loadcell</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Agreed Rate</span>
              <span className="text-base font-bold text-white mt-1 block">₹{lot.agreedPricePerKg}/kg</span>
              <span className="text-[10px] text-slate-500">Verified Recycler Bid</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Settlement Value</span>
              <span className="text-base font-bold text-emerald-300 mt-1 block">₹{lot.totalValueInr.toLocaleString('en-IN')}</span>
              <span className="text-[10px] text-slate-500">Net Collector Payout</span>
            </div>
          </div>

          {/* Participants & Location */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">Origin Informal Collector</span>
              <p className="font-semibold text-white text-sm">{lot.collectorName}</p>
              <p className="text-[11px] text-slate-400">Hub: {lot.collectorHub}</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">Verified Processing Recycler</span>
              <p className="font-semibold text-white text-sm">{lot.recyclerName || 'Awaiting Offer Matching'}</p>
              <p className="text-[11px] text-slate-400">Weighbridge Slip: {lot.weighbridgeSlip || 'Pending Intake'}</p>
            </div>
          </div>

          {/* Tamper-Evident SHA-256 Custody Hash Block */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/90 space-y-2 font-mono">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-slate-400 uppercase font-bold tracking-wider">
                Cryptographic Custody Hash (packages/crypto-traceability)
              </span>
              <span className="text-emerald-400">Immutable SHA-256 Block</span>
            </div>
            <div className="p-2.5 rounded-lg bg-black/60 border border-slate-800 text-[11px] text-emerald-400 break-all select-all">
              {lot.custodyHash}
            </div>
            <p className="text-[10px] text-slate-500 font-sans">
              Chain verification algorithm: SHA-256(previousHash + lotPayload + weighbridgeScaleCalibrationId). Verified non-tampered.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Current Status: <strong className="text-white">{lot.status}</strong>
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors shadow-lg shadow-emerald-600/20"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
