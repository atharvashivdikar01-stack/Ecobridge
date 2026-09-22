'use client';

import React, { useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { api, AvailableMaterialItem } from '../../lib/api';

function HandoverContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryLotId = searchParams.get('lot_id');

  const [materials, setMaterials] = useState<AvailableMaterialItem[]>([]);
  const [selectedLotId, setSelectedLotId] = useState<string>(queryLotId || '');
  const [selectedLot, setSelectedLot] = useState<AvailableMaterialItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<AvailableMaterialItem | null>(null);

  // Form inputs
  const [slipNumber, setSlipNumber] = useState<string>('WB-2026-9042');
  const [scaleMode, setScaleMode] = useState<'gross_tare' | 'direct'>('gross_tare');
  const [grossWeight, setGrossWeight] = useState<number>(35.4);
  const [tareWeight, setTareWeight] = useState<number>(20.0);
  const [directWeight, setDirectWeight] = useState<number>(15.4);
  const [scaleId, setScaleId] = useState<string>('SCALE-CALIB-MH-092');

  // Computed net weight
  const netWeight =
    scaleMode === 'gross_tare'
      ? Math.max(0, parseFloat((grossWeight - tareWeight).toFixed(2)))
      : directWeight;

  useEffect(() => {
    loadMaterials();
  }, []);

  useEffect(() => {
    if (materials.length > 0) {
      const match = materials.find((m) => m.lot_id === selectedLotId);
      if (match) {
        setSelectedLot(match);
        const baseW = match.verified_weight_kg || match.estimated_weight_kg || 15.0;
        setDirectWeight(baseW);
        setGrossWeight(parseFloat((baseW + 20.0).toFixed(2)));
        setTareWeight(20.0);
      } else if (!selectedLotId && materials.length > 0) {
        setSelectedLotId(materials[0].lot_id);
      }
    }
  }, [materials, selectedLotId]);

  async function loadMaterials() {
    try {
      setLoading(true);
      setError(null);
      // Fetch lots that are in OFFER_ACCEPTED, IN_TRANSIT, or COLLECTED state
      const res = await api.getMaterials();
      const validLots = res.items.filter(
        (i) => i.status === 'OFFER_ACCEPTED' || i.status === 'IN_TRANSIT' || i.status === 'COLLECTED'
      );
      setMaterials(validLots);

      if (queryLotId) {
        const found = validLots.find((l) => l.lot_id === queryLotId);
        if (found) setSelectedLot(found);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load inbound lots');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedLotId || netWeight <= 0) {
      alert('Please enter valid scale weights resulting in net weight > 0.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const res = await api.confirmHandover(selectedLotId, {
        weighbridge_slip_number: slipNumber,
        verified_weight_kg: netWeight,
        weighbridge_gross_kg: scaleMode === 'gross_tare' ? grossWeight : undefined,
        weighbridge_tare_kg: scaleMode === 'gross_tare' ? tareWeight : undefined,
        scale_calibration_id: scaleId,
      });

      setSuccessData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to confirm weighbridge handover');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Weighbridge Intake & Scale Verification
          </h1>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
            Step 3 of Golden Journey
          </span>
        </div>
        <p className="text-sm text-slate-600 mt-1">
          Perform certified physical weight calibration, generate tamper-evident gate pass, and advance lot to settlement.
        </p>
      </div>

      {/* Success Notification Modal / Card */}
      {successData && (
        <div className="bg-white rounded-xl border-2 border-emerald-500 p-6 shadow-md animate-fade-in space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              ✓
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Weighbridge Intake Confirmed — Gate Pass #{slipNumber}
              </h2>
              <p className="text-xs text-slate-600">
                Certified weight recorded at <strong className="font-semibold text-emerald-800">{successData.verified_weight_kg} kg</strong>. Lot status updated to <strong className="font-semibold text-blue-800">DELIVERED</strong>.
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Lot Code:</span>
              <span className="font-bold text-slate-800">{successData.lot_code}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Material:</span>
              <span className="font-bold text-slate-800">{successData.material_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Verified Net Weight:</span>
              <span className="font-bold text-emerald-700">{successData.verified_weight_kg} kg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Agreed Price:</span>
              <span className="font-bold text-slate-800">₹{successData.agreed_price_per_kg}/kg</span>
            </div>
            <div className="flex justify-between border-t border-slate-200 pt-2">
              <span className="text-slate-700 font-bold">Final Settlement Payable:</span>
              <span className="font-bold text-emerald-800 text-sm">
                ₹{((successData.verified_weight_kg || 0) * (successData.agreed_price_per_kg || 0)).toFixed(2)}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <Link
              href={`/dashboard/payment?lot_id=${successData.lot_id}`}
              className="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs text-center shadow-sm transition-colors"
            >
              Proceed to Step 4: Record Payout Settlement →
            </Link>
            <button
              onClick={() => {
                setSuccessData(null);
                loadMaterials();
              }}
              className="py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold text-xs transition-colors"
            >
              Intake Another Inbound Lot
            </button>
          </div>
        </div>
      )}

      {/* Main Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Form */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
            {/* Step 1: Select Lot */}
            <div>
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1.5">
                Select Pending Collection Lot:
              </label>
              {loading ? (
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-500">
                  Scanning active manifests...
                </div>
              ) : materials.length === 0 ? (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
                  No active lots awaiting intake. Visit the{' '}
                  <Link href="/dashboard/materials" className="underline font-bold text-amber-800">
                    Materials Catalog
                  </Link>{' '}
                  to discover and accept new lots first.
                </div>
              ) : (
                <select
                  value={selectedLotId}
                  onChange={(e) => setSelectedLotId(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-900 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                >
                  {materials.map((m) => (
                    <option key={m.lot_id} value={m.lot_id}>
                      {m.lot_code} — {m.material_name} ({m.estimated_weight_kg} kg) [Status: {m.status}]
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Step 2: Weighbridge Slip Number & Device ID */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Weighbridge Slip / Serial Number:
                </label>
                <input
                  type="text"
                  required
                  value={slipNumber}
                  onChange={(e) => setSlipNumber(e.target.value)}
                  placeholder="e.g. WB-2026-9042"
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono text-slate-900 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">Physical scale ticket barcode/ID</span>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Scale Calibration Device ID:
                </label>
                <input
                  type="text"
                  required
                  value={scaleId}
                  onChange={(e) => setScaleId(e.target.value)}
                  placeholder="e.g. SCALE-CALIB-MH-092"
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-mono text-slate-900 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">CPCB certified scale verification token</span>
              </div>
            </div>

            {/* Step 3: Weighing Mode & Calculations */}
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Weight Determination Mode
                </span>
                <div className="flex bg-white p-1 rounded-lg border border-slate-200 text-xs font-medium">
                  <button
                    type="button"
                    onClick={() => setScaleMode('gross_tare')}
                    className={`px-3 py-1 rounded transition-colors ${
                      scaleMode === 'gross_tare' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600'
                    }`}
                  >
                    Vehicle / Bin (Gross - Tare)
                  </button>
                  <button
                    type="button"
                    onClick={() => setScaleMode('direct')}
                    className={`px-3 py-1 rounded transition-colors ${
                      scaleMode === 'direct' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600'
                    }`}
                  >
                    Direct Platform Net
                  </button>
                </div>
              </div>

              {scaleMode === 'gross_tare' ? (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                      Gross Weight (kg):
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      value={grossWeight}
                      onChange={(e) => setGrossWeight(parseFloat(e.target.value) || 0)}
                      className="w-full p-2 text-xs bg-white border border-slate-300 rounded-lg font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500"
                    />
                    <span className="text-[10px] text-slate-400 mt-0.5 block">Vehicle/Bin + Waste</span>
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                      Tare Weight (kg):
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      value={tareWeight}
                      onChange={(e) => setTareWeight(parseFloat(e.target.value) || 0)}
                      className="w-full p-2 text-xs bg-white border border-slate-300 rounded-lg font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500"
                    />
                    <span className="text-[10px] text-slate-400 mt-0.5 block">Empty Vehicle/Bin</span>
                  </div>

                  <div className="bg-emerald-100/70 p-2.5 rounded-lg border border-emerald-300 flex flex-col justify-center">
                    <span className="text-[10px] font-bold uppercase text-emerald-800">
                      Certified Net Weight:
                    </span>
                    <span className="text-base font-extrabold text-emerald-900 mt-0.5">
                      {netWeight} kg
                    </span>
                    <span className="text-[9px] text-emerald-700">Calculated automatically</span>
                  </div>
                </div>
              ) : (
                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                    Direct Platform Certified Weight (kg):
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={directWeight}
                    onChange={(e) => setDirectWeight(parseFloat(e.target.value) || 0)}
                    className="w-full p-2.5 text-sm bg-white border border-slate-300 rounded-lg font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500"
                  />
                  <span className="text-[10px] text-slate-400 mt-0.5 block">Certified platform scale readout</span>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs font-semibold text-red-800">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting || !selectedLotId || netWeight <= 0}
              className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-bold text-xs shadow-sm transition-all flex items-center justify-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Confirming Physical Handover & Sealing Scale Token...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Confirm Inward Scale Intake & Generate Gate Pass</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right 1 Col: Lot Summary & Live Settlement Preview */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider border-b border-slate-100 pb-2">
              Inbound Lot Manifest
            </h3>

            {selectedLot ? (
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-[10px] font-mono text-slate-400 block">Lot Code</span>
                  <span className="text-sm font-bold text-slate-900 font-mono">{selectedLot.lot_code}</span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 block">Material</span>
                  <span className="font-semibold text-slate-800">{selectedLot.material_name}</span>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 block">Collector</span>
                  <span className="font-semibold text-slate-800">{selectedLot.collector_name}</span>
                  <span className="text-slate-500 block text-[11px]">{selectedLot.collector_phone}</span>
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Agreed Price:</span>
                    <span className="font-bold text-slate-800">
                      ₹{selectedLot.agreed_price_per_kg || selectedLot.benchmark_price_per_kg} / kg
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Certified Weight:</span>
                    <span className="font-bold text-emerald-700">{netWeight} kg</span>
                  </div>
                </div>

                {/* Final calculated amount */}
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <span className="text-[10px] font-bold uppercase text-emerald-800 block">
                    Settlement Payable:
                  </span>
                  <span className="text-lg font-extrabold text-emerald-900 block mt-0.5">
                    ₹
                    {(
                      netWeight *
                      (selectedLot.agreed_price_per_kg || selectedLot.benchmark_price_per_kg || 0)
                    ).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                  <span className="text-[9px] text-emerald-700 block mt-1">
                    Formula: {netWeight} kg × ₹{selectedLot.agreed_price_per_kg || selectedLot.benchmark_price_per_kg}/kg
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">Select an inbound lot to view manifest details.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HandoverPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading weighbridge desk...</div>}>
      <HandoverContent />
    </Suspense>
  );
}
