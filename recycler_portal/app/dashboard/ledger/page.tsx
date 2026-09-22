'use client';

import { useEffect, useState } from 'react';
import { api, LedgerResponse } from '../../lib/api';

export default function LedgerPage() {
  const [ledger, setLedger] = useState<LedgerResponse | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { api.getLedger().then(setLedger).catch((e) => setError(e instanceof Error ? e.message : 'Unable to load ledger.')); }, []);
  return <div className="max-w-6xl mx-auto space-y-6">
    <header><h1 className="text-2xl font-bold text-slate-900">Accounting & EPR Ledger</h1><p className="text-sm text-slate-600 mt-1">Immutable settlement history for this recycler facility.</p></header>
    {error && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-800">{error}</p>}
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">{[['Transactions', ledger?.total_transactions || 0], ['Volume', `${(ledger?.total_volume_kg || 0).toFixed(1)} kg`], ['Disbursed', `₹${(ledger?.total_disbursed_inr || 0).toLocaleString('en-IN')}`]].map(([label, value]) => <div key={String(label)} className="bg-white rounded-xl border border-slate-200 p-5"><p className="text-xs uppercase tracking-wide text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold text-slate-900">{value}</p></div>)}</div>
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="p-4">Lot</th><th className="p-4">Weight</th><th className="p-4">Rate</th><th className="p-4">Amount</th><th className="p-4">Method</th></tr></thead><tbody className="divide-y divide-slate-100">{(ledger?.transactions || []).map((tx) => <tr key={`${tx.lot_id}-${tx.reference_number}`}><td className="p-4 font-mono">{tx.lot_id}</td><td className="p-4">{tx.verified_weight_kg} kg</td><td className="p-4">₹{tx.agreed_price_per_kg}</td><td className="p-4 font-semibold">₹{tx.total_amount.toLocaleString('en-IN')}</td><td className="p-4">{tx.payment_method}</td></tr>)}</tbody></table></div>
  </div>;
}
