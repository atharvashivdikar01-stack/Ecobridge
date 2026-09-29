'use client';

import { useEffect, useState } from 'react';
import { api, AvailableMaterialItem } from '../../lib/api';

export default function HandoverPage() {
  const [lots, setLots] = useState<AvailableMaterialItem[]>([]);
  const [lotId, setLotId] = useState('');
  const [weight, setWeight] = useState('');
  const [slip, setSlip] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMaterials()
      .then((r) => setLots(r.items.filter((x) => ['OFFER_ACCEPTED', 'ACCEPTED', 'IN_TRANSIT'].includes(x.status))))
      .catch(() => setLots([]))
      .finally(() => setLoading(false));
  }, []);

  const selectedLot = lots.find((l) => l.lot_id === lotId);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!lotId || Number(weight) <= 0 || !slip) {
      setMessage('Select a lot, slip number, and positive verified weight.');
      setMessageType('error');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      await api.handover(lotId, {
        weighbridge_slip_number: slip,
        weighbridge_gross_kg: Number(weight),
        weighbridge_tare_kg: 0,
        verified_weight_kg: Number(weight),
        scale_calibration_id: 'PORTAL-SCALE',
      });
      setMessage('Handover recorded successfully. The lot is ready for settlement.');
      setMessageType('success');
      setLotId('');
      setWeight('');
      setSlip('');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to record handover.');
      setMessageType('error');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading accepted lots...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
            </div>
            Weighbridge &amp; Handover
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Record certified scale intake and custody transfer before settlement.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 border border-slate-800 px-4 py-2 rounded-xl">
          <svg className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span>{lots.length} lot{lots.length !== 1 ? 's' : ''} awaiting intake</span>
        </div>
      </div>

      {/* Handover Form Card */}
      <form
        onSubmit={submit}
        className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 sm:p-8 backdrop-blur-xl space-y-6"
      >
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          Record Certified Handover
        </h2>

        {/* Lot Selector */}
        <div className="space-y-2">
          <label htmlFor="lot-select" className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Accepted Lot
          </label>
          <select
            id="lot-select"
            value={lotId}
            onChange={(e) => setLotId(e.target.value)}
            className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors appearance-none cursor-pointer"
          >
            <option value="">— Select an accepted lot —</option>
            {lots.map((lot) => (
              <option key={lot.lot_id} value={lot.lot_id}>
                {lot.lot_code} — {lot.material_name} ({lot.estimated_weight_kg} kg est.)
              </option>
            ))}
          </select>
        </div>

        {/* Selected Lot Details Mini Card */}
        {selectedLot && (
          <div className="p-4 bg-slate-950/60 border border-slate-800/60 rounded-xl grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-500 uppercase tracking-wider block">Material</span>
              <span className="text-white font-semibold mt-0.5 block">{selectedLot.material_name}</span>
            </div>
            <div>
              <span className="text-slate-500 uppercase tracking-wider block">Collector</span>
              <span className="text-white font-semibold mt-0.5 block">{selectedLot.collector_name}</span>
            </div>
            <div>
              <span className="text-slate-500 uppercase tracking-wider block">Est. Weight</span>
              <span className="text-white font-semibold mt-0.5 block">{selectedLot.estimated_weight_kg} kg</span>
            </div>
            <div>
              <span className="text-slate-500 uppercase tracking-wider block">Hazard</span>
              {selectedLot.detected_hazard === 'NORMAL' ? (
                <span className="text-slate-300 font-medium mt-0.5 block">Standard</span>
              ) : (
                <span className="text-rose-300 font-bold mt-0.5 block">⚠️ {selectedLot.detected_hazard}</span>
              )}
            </div>
          </div>
        )}

        {/* Weight and Slip Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label htmlFor="weight-input" className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Verified Net Weight (kg)
            </label>
            <input
              id="weight-input"
              required
              type="number"
              min="0.01"
              step="0.01"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder="e.g. 12.5"
              className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white font-mono focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors placeholder-slate-600"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="slip-input" className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Weighbridge Slip Number
            </label>
            <input
              id="slip-input"
              required
              value={slip}
              onChange={(e) => setSlip(e.target.value)}
              placeholder="e.g. WB-2026-00145"
              className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white font-mono focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors placeholder-slate-600"
            />
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div
            className={`rounded-xl p-4 text-sm font-medium flex items-center gap-3 ${
              messageType === 'success'
                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
            }`}
          >
            {messageType === 'success' ? (
              <svg className="w-5 h-5 text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-rose-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            )}
            <span>{message}</span>
          </div>
        )}

        {/* Submit */}
        <div className="flex items-center justify-between pt-2">
          <p className="text-[11px] text-slate-500">
            Custody hash will be appended to the SHA-256 tamper-evident ledger upon confirmation.
          </p>
          <button
            disabled={saving}
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-emerald-950/40 transition-all border border-emerald-400/20 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Recording…</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Record Certified Handover</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
