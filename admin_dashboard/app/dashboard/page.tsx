'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { adminApi, PlatformStats, CityHeatmapData, EprComplianceRecord } from '../lib/api';

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [cities, setCities] = useState<CityHeatmapData[]>([]);
  const [audits, setAudits] = useState<EprComplianceRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, citiesData, auditData] = await Promise.all([
          adminApi.getPlatformStats(),
          adminApi.getMunicipalHeatmap(),
          adminApi.getAuditLedger(),
        ]);
        setStats(statsData);
        setCities(citiesData);
        setAudits(auditData);
      } catch (err) {
        console.error('Failed to load admin stats', err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title & Statutory Overview */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
              Central Regulatory Command
            </span>
            <span className="text-xs text-slate-400">CPCB E-Waste Portal Integration</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            National E-Waste Oversight &amp; EPR Command Center
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Real-time telemetry integrating informal collectors (*kabadiwalas*), aggregation micro-hubs,
            authorized recyclers, and statutory CPCB Form-6 transfer manifests across India.
          </p>
        </div>

        {/* Quick Links */}
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/heatmap"
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-500/20"
          >
            Open Municipal Heatmap →
          </Link>
          <Link
            href="/dashboard/cpcb-audit"
            className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-medium text-xs transition-all"
          >
            Audit Manifests
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Total E-Waste */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>Aggregated Scrap</span>
            <span className="text-emerald-400">⚖️ Verified</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {stats ? (stats.total_ewaste_collected_kg / 1000).toFixed(2) : '18.45'}{' '}
            <span className="text-sm font-normal text-slate-400">MT</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {stats?.total_ewaste_collected_kg.toLocaleString() || '18,450'} kg certified
          </div>
        </div>

        {/* Registered Kabadiwalas */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>Informal Collectors</span>
            <span className="text-blue-400">👥 Active</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-blue-300">
            {stats?.active_collectors_count || 342}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Formalized &amp; KYC Registered
          </div>
        </div>

        {/* Authorised Recyclers */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>Authorised Units</span>
            <span className="text-indigo-400">🏭 CPCB</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-indigo-300">
            {stats?.verified_recyclers_count || 28}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Registered Processing Centers
          </div>
        </div>

        {/* CO2 Offset */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>CO₂ Averted</span>
            <span className="text-emerald-400">🌱 ESG</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-emerald-400">
            {stats?.co2_offset_tonnes.toFixed(1) || '26.6'}{' '}
            <span className="text-sm font-normal text-slate-400">Tons</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Virgin mining carbon averted
          </div>
        </div>

        {/* Green Dividends Paid */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>Green Dividend</span>
            <span className="text-teal-400">₹ EPR</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-teal-300">
            ₹{stats ? (stats.green_dividends_paid_inr / 1000).toFixed(1) + 'k' : '77.5k'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Direct to collector wallets
          </div>
        </div>

        {/* Hazards Neutralized */}
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider flex items-center justify-between">
            <span>Critical Hazards</span>
            <span className="text-amber-400">⚠️ Neutralized</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-amber-300">
            {stats?.critical_hazards_neutralized || 1120}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Batteries &amp; CRT glass safe
          </div>
        </div>
      </div>

      {/* Urban Mining Precious Metals Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-blue-500/20 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-blue-400">
              National Urban Mining Yields (Circular Economy)
            </span>
            <h2 className="text-xl font-bold text-white mt-1">
              Recoverable Strategic Elements Extracted from Aggregated E-Waste
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Circumventing virgin mineral mining and import dependencies under the National Critical Minerals Mission.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs font-semibold text-amber-400">Gold (Au)</div>
              <div className="text-lg font-bold text-white mt-0.5 font-mono">
                {stats?.gold_recovered_grams || 1512} g
              </div>
              <div className="text-[10px] text-slate-400">from Telecom PCBs</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs font-semibold text-orange-400">Copper (Cu)</div>
              <div className="text-lg font-bold text-white mt-0.5 font-mono">
                {stats?.copper_recovered_kg || 2583} kg
              </div>
              <div className="text-[10px] text-slate-400">from Motors &amp; Wires</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs font-semibold text-blue-400">Lithium (Li)</div>
              <div className="text-lg font-bold text-white mt-0.5 font-mono">218 kg</div>
              <div className="text-[10px] text-slate-400">from Li-ion Packs</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs font-semibold text-slate-300">Silver (Ag)</div>
              <div className="text-lg font-bold text-white mt-0.5 font-mono">8.4 kg</div>
              <div className="text-[10px] text-slate-400">from Solders &amp; ICs</div>
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Municipal Hubs & Live Audit Ledger */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Top Municipal Hubs (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">Municipal E-Waste Intake</h2>
                <p className="text-xs text-slate-400">State Pollution Control Board regional clusters</p>
              </div>
              <Link
                href="/dashboard/heatmap"
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold"
              >
                View Full Heatmap →
              </Link>
            </div>

            <div className="space-y-3">
              {cities.slice(0, 5).map((city) => (
                <div
                  key={city.city}
                  className="p-3.5 rounded-xl bg-slate-800/30 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-bold text-xs">
                      {city.state.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">{city.city}</div>
                      <div className="text-xs text-slate-400">
                        {city.active_micro_hubs} micro-hubs • {city.top_category}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-sm font-bold text-white font-mono">
                      {city.volume_tonnes.toFixed(1)} MT
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                      {city.spcb_code}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Live Audit Ledger (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">CPCB Custody Audit Stream</h2>
                <p className="text-xs text-slate-400">SHA-256 tamper-evident consignment transitions</p>
              </div>
              <Link
                href="/dashboard/cpcb-audit"
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold"
              >
                Audit Records →
              </Link>
            </div>

            <div className="space-y-3">
              {audits.map((item) => (
                <div
                  key={item.manifest_id}
                  className="p-3.5 rounded-xl bg-slate-800/30 border border-slate-800 hover:border-slate-700 transition-all"
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-mono font-bold text-blue-300">{item.manifest_id}</span>
                    <span className="text-emerald-400 font-semibold flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      Tamper-Proof
                    </span>
                  </div>
                  <div className="text-xs text-white font-medium">
                    {item.collector_name} → {item.recycler_name}
                  </div>
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px] text-slate-400">
                    <span>{item.category} • <strong className="text-white">{item.weight_kg} kg</strong></span>
                    <span className="text-teal-400 font-semibold">₹{item.dividend_inr.toFixed(1)} Dividend</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
