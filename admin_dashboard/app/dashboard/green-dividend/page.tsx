'use client';

import React, { useState } from 'react';

export default function GreenDividendPage() {
  const [selectedRate, setSelectedRate] = useState(4.2);

  const dividendTransactions = [
    {
      id: 'DIV-2026-9901',
      collector: 'Ramesh Gaikwad',
      hub: 'Dharavi Sector 3, Mumbai',
      material: 'Printed Circuit Boards (PCBs)',
      weightKg: 24.5,
      ratePerKg: 4.5,
      totalDividend: 110.25,
      eprSponsor: 'Croma Retail / Tata Electronics EPR Quota',
      utrNumber: 'UPI/20260929/9821849102',
      status: 'PAID_TO_UPI',
      timestamp: '2026-09-29 09:44:12',
    },
    {
      id: 'DIV-2026-9900',
      collector: 'Mohammad Ansari',
      hub: 'Seelampur Cluster 2, Delhi',
      material: 'Lithium-ion Batteries',
      weightKg: 18.0,
      ratePerKg: 5.0,
      totalDividend: 90.0,
      eprSponsor: 'Exide Battery EPR Producer Quota',
      utrNumber: 'UPI/20260929/1849104821',
      status: 'PAID_TO_UPI',
      timestamp: '2026-09-29 09:18:05',
    },
    {
      id: 'DIV-2026-9899',
      collector: 'Venkatesh Rao',
      hub: 'Peenya Industrial Area, Bengaluru',
      material: 'Copper Cables & Wires',
      weightKg: 32.0,
      ratePerKg: 4.0,
      totalDividend: 128.0,
      eprSponsor: 'Schneider Electric EPR Compliance',
      utrNumber: 'UPI/20260929/4910284918',
      status: 'PAID_TO_UPI',
      timestamp: '2026-09-29 08:52:19',
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/20 uppercase tracking-wider">
              Social Equity Mechanism
            </span>
            <span className="text-xs text-slate-400">Direct Producer Responsibility Pass-Through</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            Green Dividend Direct Payout Mechanism
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Automated statutory routing distributing ₹3.00 to ₹5.00 / kg of corporate EPR compliance credits
            directly to the digital wallets and UPI handles of informal waste pickers upon verified recycler handover.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-right">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Disbursed</div>
            <div className="text-lg font-bold text-teal-300 font-mono">₹77,490.00</div>
          </div>
        </div>
      </div>

      {/* Mechanism Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 font-bold">
            1
          </div>
          <h3 className="font-bold text-white text-base">Corporate EPR Credit Pool</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Registered electronics producers (OEMs) deposit statutory EPR compliance levies into escrow for every kg of certified e-waste channeled away from toxic dumping.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
            2
          </div>
          <h3 className="font-bold text-white text-base">Weighbridge Cryptographic Trigger</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upon gross/tare verification at an authorized recycler’s weighbridge, the tamper-evident SHA-256 custody block triggers an automated instant payout instruction.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            3
          </div>
          <h3 className="font-bold text-white text-base">100% Direct Collector UPI Settlement</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Zero intermediary deductions. The informal waste collector instantly receives ₹3–5/kg in addition to the base scrap scrap rate, elevating livelihoods by 18-25%.
          </p>
        </div>
      </div>

      {/* Live Disbursal Feed */}
      <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Live Green Dividend Settlement Feed</h2>
            <p className="text-xs text-slate-400">Direct pass-through ledger payments to informal collectors</p>
          </div>
          <button
            onClick={() => alert('Green dividend bank ledger export CSV generated.')}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white border border-slate-700"
          >
            Export Banking UTR Log
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Disbursal Ref &amp; Time</th>
                <th className="py-3 px-4">Recipient Collector</th>
                <th className="py-3 px-4">Material &amp; Net Weight</th>
                <th className="py-3 px-4">Corporate EPR Sponsor</th>
                <th className="py-3 px-4 text-right">Dividend Rate</th>
                <th className="py-3 px-4 text-right">Total Payout</th>
                <th className="py-3 px-4 text-center">Settlement Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {dividendTransactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-bold text-white font-mono">{tx.id}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{tx.utrNumber}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-white">{tx.collector}</div>
                    <div className="text-[10px] text-slate-400">{tx.hub}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-medium text-white">{tx.material}</div>
                    <div className="text-[10px] text-emerald-400 font-bold">{tx.weightKg.toFixed(1)} kg verified</div>
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-medium">
                    {tx.eprSponsor}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-teal-300">
                    ₹{tx.ratePerKg.toFixed(2)}/kg
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-white text-sm">
                    ₹{tx.totalDividend.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      PAID TO UPI
                    </span>
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
