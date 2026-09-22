'use client';

import { useEffect, useState } from 'react';
import { api, AvailableMaterialItem } from '../../lib/api';

export default function HandoverPage() {
  const [lots, setLots] = useState<AvailableMaterialItem[]>([]);
  const [lotId, setLotId] = useState('');
  const [weight, setWeight] = useState('');
  const [slip, setSlip] = useState('');
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => { api.getMaterials().then((r) => setLots(r.items.filter((x) => ['OFFER_ACCEPTED', 'ACCEPTED', 'IN_TRANSIT'].includes(x.status)))).catch(() => setLots([])); }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!lotId || Number(weight) <= 0 || !slip) return setMessage('Select a lot, slip number, and positive verified weight.');
    setSaving(true); setMessage('');
    try {
      await api.handover(lotId, { weighbridge_slip_number: slip, weighbridge_gross_kg: Number(weight), weighbridge_tare_kg: 0, verified_weight_kg: Number(weight), scale_calibration_id: 'PORTAL-SCALE' });
      setMessage('Handover recorded. The lot is ready for settlement.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Unable to record handover.'); }
    finally { setSaving(false); }
  }

  return <div className="max-w-3xl mx-auto space-y-6">
    <header><h1 className="text-2xl font-bold text-slate-900">Weighbridge & Handover</h1><p className="text-sm text-slate-600 mt-1">Record certified scale intake before issuing payment.</p></header>
    <form onSubmit={submit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-5">
      <label className="block text-sm font-semibold text-slate-700">Accepted lot<select value={lotId} onChange={(e) => setLotId(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 text-sm"><option value="">Select a lot</option>{lots.map((lot) => <option key={lot.lot_id} value={lot.lot_id}>{lot.lot_code} — {lot.material_name}</option>)}</select></label>
      <label className="block text-sm font-semibold text-slate-700">Verified net weight (kg)<input required type="number" min="0.01" step="0.01" value={weight} onChange={(e) => setWeight(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 text-sm" /></label>
      <label className="block text-sm font-semibold text-slate-700">Weighbridge slip number<input required value={slip} onChange={(e) => setSlip(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 text-sm" /></label>
      {message && <p className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{message}</p>}
      <button disabled={saving} className="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{saving ? 'Recording…' : 'Record certified handover'}</button>
    </form>
  </div>;
}
