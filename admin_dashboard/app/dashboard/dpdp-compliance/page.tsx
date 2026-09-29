'use client';

import React, { useState } from 'react';

export default function DpdpCompliancePage() {
  const [selectedAuditTab, setSelectedAuditTab] = useState<'safeguards' | 'consent' | 'dpo'>('safeguards');

  const collectorPrivacyAudits = [
    {
      id: 'KAB-MUM-0814',
      name: 'Ramesh Gaikwad',
      hub: 'Dharavi Sector 3, Mumbai',
      ageConfirmed: true,
      age: 38,
      consentRecorded: true,
      consentLocale: 'मराठी (mr)',
      dataStored: 'Phone, First Name, Scrap Weight, UPI ID',
      highRiskDataExcluded: 'Aadhaar / Biometrics / Iris: EXCLUDED (0%)',
      timestamp: '2026-09-29 07:14:22',
      status: 'DPDP_COMPLIANT',
    },
    {
      id: 'KAB-DEL-0419',
      name: 'Mohammad Ansari',
      hub: 'Seelampur Cluster 2, Delhi',
      ageConfirmed: true,
      age: 44,
      consentRecorded: true,
      consentLocale: 'हिंदी (hi)',
      dataStored: 'Phone, First Name, Scrap Weight, UPI ID',
      highRiskDataExcluded: 'Aadhaar / Biometrics / Iris: EXCLUDED (0%)',
      timestamp: '2026-09-29 08:32:10',
      status: 'DPDP_COMPLIANT',
    },
    {
      id: 'KAB-BLR-1184',
      name: 'Venkatesh Rao',
      hub: 'Peenya Industrial Area, Bengaluru',
      ageConfirmed: true,
      age: 29,
      consentRecorded: true,
      consentLocale: 'English (en)',
      dataStored: 'Phone, First Name, Scrap Weight, UPI ID',
      highRiskDataExcluded: 'Aadhaar / Biometrics / Iris: EXCLUDED (0%)',
      timestamp: '2026-09-29 09:12:45',
      status: 'DPDP_COMPLIANT',
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase tracking-wider">
              Statutory Privacy &amp; Human Rights
            </span>
            <span className="text-xs text-slate-400">Digital Personal Data Protection Act, 2023</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            DPDP Act (2023) &amp; Child Labor Safeguard Audit
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Independent regulatory verification enforcing non-collection of sensitive biometrics,
            mandatory affirmative consent in vernacular languages, and rigorous age gates to prohibit minor involvement in scrap handling.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          100% DPDP Act Compliant
        </div>
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Pillar 1 */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>High-Risk Data Prohibition</span>
            <span className="text-emerald-400">🛡️ Zero Leak</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-white font-mono">0% Stored</div>
          <div className="text-xs text-slate-400 mt-1">
            Strict exclusion of Aadhaar numbers, iris/fingerprint biometrics, and contacts.
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Child Labor Safeguard</span>
            <span className="text-blue-400">🚸 Age ≥ 18 Gate</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-blue-300 font-mono">100% Verified</div>
          <div className="text-xs text-slate-400 mt-1">
            Zero minors onboarded. Rigorous age validation before lot creation authorization.
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Vernacular Consent</span>
            <span className="text-teal-400">🗣️ Audio Readout</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-teal-300 font-mono">3 Languages</div>
          <div className="text-xs text-slate-400 mt-1">
            Affirmative consent in Marathi, Hindi, and English with voice readout for illiterate workers.
          </div>
        </div>

        {/* Pillar 4 */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Right to Erasure</span>
            <span className="text-indigo-400">⚖️ DPO Protocol</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-indigo-300 font-mono">Cryptographic</div>
          <div className="text-xs text-slate-400 mt-1">
            Anonymizes personal records while preserving immutable SHA-256 custody hashes for CPCB audits.
          </div>
        </div>
      </div>

      {/* Collector Audit Stream */}
      <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Collector Onboarding Privacy &amp; Consent Log</h2>
            <p className="text-xs text-slate-400">Auditable proof of affirmative consent and age verification compliance</p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded-lg bg-slate-800 text-slate-300">
            DPO Audit Token: DPDP-IN-2026-AUTH
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Collector ID &amp; Name</th>
                <th className="py-3 px-4">Cluster / Micro-Hub</th>
                <th className="py-3 px-4">Age Gate Validation</th>
                <th className="py-3 px-4">Consent Recording</th>
                <th className="py-3 px-4">Stored Attributes</th>
                <th className="py-3 px-4">Sensitive Biometrics</th>
                <th className="py-3 px-4 text-center">Compliance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {collectorPrivacyAudits.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-bold text-white">{item.name}</div>
                    <div className="font-mono text-[11px] text-blue-400">{item.id}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{item.hub}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      Age {item.age} (≥ 18 PASS)
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-medium text-white">{item.consentLocale}</div>
                    <div className="text-[10px] text-slate-500">{item.timestamp}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{item.dataStored}</td>
                  <td className="py-3 px-4">
                    <span className="font-mono text-[10px] text-emerald-400">
                      {item.highRiskDataExcluded}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      DPDP PASS
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
