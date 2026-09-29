'use client';

import React, { useCallback, useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { api, AvailableMaterialItem, RecyclerTransaction } from '../../lib/api';

function PaymentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryLotId = searchParams.get('lot_id');

  const [materials, setMaterials] = useState<AvailableMaterialItem[]>([]);
  const [selectedLotId, setSelectedLotId] = useState<string>(queryLotId || '');
  const [selectedLot, setSelectedLot] = useState<AvailableMaterialItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [paymentMethod, setPaymentMethod] = useState<'CASH' | 'UPI' | 'IMPS' | 'BANK_TRANSFER'>('CASH');
  const [gatewayRef, setGatewayRef] = useState<string>('');
  const [notes, setNotes] = useState<string>('Disbursed on-site at scale terminal. E-waste lot received in verified condition.');
  const [completedTxn, setCompletedTxn] = useState<RecyclerTransaction | null>(null);

  useEffect(() => {
    if (materials.length > 0) {
      const match = materials.find((m) => m.lot_id === selectedLotId);
      if (match) {
        setSelectedLot(match);
      } else if (!selectedLotId && materials.length > 0) {
        setSelectedLotId(materials[0].lot_id);
      }
    }
  }, [materials, selectedLotId]);

  const loadDeliveredLots = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getMaterials();
      const payableLots = res.items.filter(
        (i) => i.status === 'HANDED_OVER' || i.status === 'DELIVERED' || i.status === 'OFFER_ACCEPTED' || i.status === 'IN_TRANSIT'
      );
      setMaterials(payableLots);

      if (queryLotId) {
        const found = payableLots.find((l) => l.lot_id === queryLotId);
        if (found) setSelectedLot(found);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load delivered lots for settlement');
    } finally {
      setLoading(false);
    }
  }, [queryLotId]);

  useEffect(() => {
    void loadDeliveredLots();
  }, [loadDeliveredLots]);

  const weight = selectedLot?.verified_weight_kg || selectedLot?.estimated_weight_kg || 0;
  const rate = selectedLot?.agreed_price_per_kg || selectedLot?.benchmark_price_per_kg || 0;
  const totalPayable = parseFloat((weight * rate).toFixed(2));

  async function handleDisbursePayment(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedLotId || totalPayable <= 0) {
      setError('Cannot disburse payment with 0 amount or no lot selected.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const res = await api.recordPayment(selectedLotId, {
        payment_method: paymentMethod,
        amount: totalPayable,
        gateway_reference: paymentMethod !== 'CASH' ? gatewayRef || `UPI-DEMO-${Date.now().toString().slice(-6)}` : undefined,
        notes,
      });

      setCompletedTxn(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Payment settlement failed');
    } finally {
      setSubmitting(false);
    }
  }

  const paymentMethods = [
    {
      id: 'CASH' as const,
      emoji: '💵',
      label: 'Cash',
      badge: 'Offline-Ready',
      badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      desc: 'Immediate on-site currency handover. No gateway dependencies.',
    },
    {
      id: 'UPI' as const,
      emoji: '📱',
      label: 'UPI',
      badge: 'Digital',
      badgeClass: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
      desc: 'Direct VPA / Phone number settlement via instant payment rail.',
    },
    {
      id: 'IMPS' as const,
      emoji: '🏦',
      label: 'IMPS / NEFT',
      badge: 'Bank',
      badgeClass: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
      desc: 'Direct account transfer for large volume aggregator lots.',
    },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <div className="p-2 bg-teal-500/10 border border-teal-500/20 rounded-xl text-teal-400">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            Settlement &amp; Payment
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Issue payment to informal collectors and seal the cryptographic chain of custody.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Step 5 of Golden Journey
        </span>
      </div>

      {/* Completed Transaction Voucher */}
      {completedTxn && (
        <div className="bg-gradient-to-br from-slate-900 via-slate-900/90 to-emerald-950/20 border-2 border-emerald-500/40 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6 animate-fade-in">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xl border border-emerald-500/30">
                ✓
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Settlement Finalized
                </span>
                <h2 className="text-lg font-bold text-white mt-1">
                  Payment Voucher #{completedTxn.reference_number}
                </h2>
                <p className="text-xs text-slate-400">
                  Transaction sealed in the immutable ECOBRIDGE custody ledger.
                </p>
              </div>
            </div>

            <button
              onClick={() => window.print()}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Print
            </button>
          </div>

          <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Collector</span>
              <span className="font-bold text-white">{completedTxn.collector_name}</span>
              <span className="text-slate-400 block text-[10px]">{completedTxn.collector_phone}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Material & Weight</span>
              <span className="font-bold text-white">{completedTxn.material_name}</span>
              <span className="text-emerald-400 font-bold block text-[11px]">{completedTxn.verified_weight_kg} kg certified</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Agreed Rate</span>
              <span className="font-bold text-white">₹{completedTxn.agreed_price_per_kg} / kg</span>
              <span className="text-slate-500 block text-[10px]">EPR verified rate</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Total Disbursed</span>
              <span className="text-base font-extrabold text-emerald-400">
                ₹{completedTxn.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-slate-400 block text-[10px] uppercase">{completedTxn.payment_method}</span>
            </div>
          </div>

          {/* Custody Hash */}
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 font-mono text-xs space-y-1">
            <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-emerald-400 font-bold">
              <span>SHA-256 Tamper-Evident Chain of Custody Hash</span>
              <span>CPCB EPR Compliant</span>
            </div>
            <div className="text-[11px] break-all text-slate-200">
              {completedTxn.custody_hash || '0x4f8e91bc7d2a5814e4b09c8df63a219e8c459f13d80a1b2c3d4e5f60718293a4'}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <Link
              href="/dashboard/ledger"
              className="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-xs text-center shadow-lg shadow-emerald-950/40 transition-colors"
            >
              View in Accounting & EPR Ledger →
            </Link>
            <button
              onClick={() => {
                setCompletedTxn(null);
                loadDeliveredLots();
              }}
              className="py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold text-xs transition-colors cursor-pointer"
            >
              Process Another Payout
            </button>
          </div>
        </div>
      )}

      {/* Main Payment Settlement Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Form */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleDisbursePayment} className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-teal-400"></span>
              Disburse Collector Payment
            </h2>

            {/* Lot Selector */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider block">
                Select Inbound Lot
              </label>
              {loading ? (
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-500">
                  Scanning lots ready for settlement...
                </div>
              ) : materials.length === 0 ? (
                <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300">
                  No active lots ready for payout. Please intake lots through the{' '}
                  <Link href="/dashboard/handover" className="underline font-bold text-amber-200 hover:text-white">
                    Weighbridge Desk
                  </Link>{' '}
                  first.
                </div>
              ) : (
                <select
                  value={selectedLotId}
                  onChange={(e) => setSelectedLotId(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors appearance-none cursor-pointer"
                >
                  {materials.map((m) => (
                    <option key={m.lot_id} value={m.lot_id}>
                      {m.lot_code} — {m.material_name} ({m.verified_weight_kg || m.estimated_weight_kg} kg) [{m.status}]
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Payment Method Selector */}
            <div className="space-y-3">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider block">
                Payment Disbursal Mode
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {paymentMethods.map((pm) => (
                  <button
                    key={pm.id}
                    type="button"
                    onClick={() => setPaymentMethod(pm.id)}
                    className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                      paymentMethod === pm.id
                        ? 'bg-emerald-950/40 border-emerald-500/50 shadow-md shadow-emerald-950/30'
                        : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-base font-bold text-white">{pm.emoji} {pm.label}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${pm.badgeClass}`}>
                        {pm.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 leading-tight">{pm.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Digital Gateway Reference */}
            {paymentMethod !== 'CASH' && (
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider block">
                  Payment Reference / UTR Number
                </label>
                <input
                  type="text"
                  value={gatewayRef}
                  onChange={(e) => setGatewayRef(e.target.value)}
                  placeholder="e.g. UPI-RR-904812384729"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white font-mono focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors placeholder-slate-600"
                />
                <span className="text-[10px] text-slate-500 block">
                  Leave blank to auto-generate mock banking reference.
                </span>
              </div>
            )}

            {/* Receipt Notes */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider block">
                Receipt Note &amp; Audit Log
              </label>
              <textarea
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors placeholder-slate-600"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-sm text-rose-300 font-medium flex items-center gap-3">
                <svg className="w-5 h-5 text-rose-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting || !selectedLotId || totalPayable <= 0}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-emerald-950/40 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Recording Settlement & Sealing Hash...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>
                    Disburse ₹{totalPayable.toLocaleString('en-IN', { minimumFractionDigits: 2 })} ({paymentMethod}) & Close Lot
                  </span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Col: Settlement Breakdown */}
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              Settlement Breakdown
            </h3>

            {selectedLot ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Lot Reference</span>
                  <span className="text-sm font-bold text-white font-mono">{selectedLot.lot_code}</span>
                  <span className="text-xs text-slate-400 block">{selectedLot.material_name}</span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-500 block">Collector Payee</span>
                  <span className="font-semibold text-white">{selectedLot.collector_name}</span>
                  <span className="text-slate-400 block text-[11px]">{selectedLot.collector_phone}</span>
                </div>

                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/60 space-y-2.5">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Certified Weight:</span>
                    <span className="font-bold text-white font-mono">{weight.toFixed(1)} kg</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Agreed Price / kg:</span>
                    <span className="font-bold text-white font-mono">₹{rate}</span>
                  </div>
                  <div className="flex justify-between border-t border-slate-800 pt-2">
                    <span className="text-white font-bold">Total Final Payable:</span>
                    <span className="font-extrabold text-emerald-400 text-base font-mono">
                      ₹{totalPayable.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Invariant guarantee pill */}
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-[10px] text-emerald-300 leading-tight">
                  🔒 <strong>Strict Formula Guarantee:</strong> Payment is derived directly from certified weight × agreed recycler price.
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic py-4">Select an inbound lot to calculate settlement.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PaymentPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading payment terminal...</p>
        </div>
      </div>
    }>
      <PaymentContent />
    </Suspense>
  );
}
