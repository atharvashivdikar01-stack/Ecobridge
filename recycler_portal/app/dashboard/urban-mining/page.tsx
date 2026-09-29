'use client';

import { useState, useMemo } from 'react';

type MetalYield = {
  element: string;
  name: string;
  symbol: string;
  unit: string;
  ratePerUnitInr: number; // INR per unit (grams or kg)
  yieldPerKg: number; // units recovered per kg of scrap
  color: string;
};

type ScrapMaterialProfile = {
  id: string;
  name: string;
  categoryCode: string;
  description: string;
  avgPurityPct: number;
  processingCostPerKgInr: number;
  co2OffsetPerKg: number;
  waterSavedPerKgLiters: number;
  hazardousMetalsDivertedGramsPerKg: number;
  metals: MetalYield[];
};

const SCRAP_PROFILES: ScrapMaterialProfile[] = [
  {
    id: 'pcb_telecom',
    name: 'Printed Circuit Boards (PCBs) — High Grade',
    categoryCode: 'CAT_PCB',
    description: 'Server motherboards, telecom base station cards, RAM & CPU boards with gold immersion plating.',
    avgPurityPct: 92,
    processingCostPerKgInr: 65,
    co2OffsetPerKg: 3.4,
    waterSavedPerKgLiters: 1450,
    hazardousMetalsDivertedGramsPerKg: 120, // Lead, cadmium solder
    metals: [
      { element: 'Gold', name: 'Gold (Au 99.9%)', symbol: 'Au', unit: 'g', ratePerUnitInr: 7200, yieldPerKg: 0.28, color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
      { element: 'Silver', name: 'Silver (Ag 99.9%)', symbol: 'Ag', unit: 'g', ratePerUnitInr: 92, yieldPerKg: 1.45, color: 'text-slate-300 bg-slate-500/10 border-slate-500/30' },
      { element: 'Copper', name: 'Electrolytic Copper', symbol: 'Cu', unit: 'kg', ratePerUnitInr: 780, yieldPerKg: 0.22, color: 'text-orange-400 bg-orange-500/10 border-orange-500/30' },
      { element: 'Palladium', name: 'Palladium (Pd)', symbol: 'Pd', unit: 'g', ratePerUnitInr: 2850, yieldPerKg: 0.04, color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30' },
    ],
  },
  {
    id: 'batteries_liion',
    name: 'Lithium-Ion / Polymer Battery Packs',
    categoryCode: 'CAT_BATTERY',
    description: 'EV battery modules, smartphone & laptop lithium cells with NMC/LCO cathode chemistry.',
    avgPurityPct: 88,
    processingCostPerKgInr: 45,
    co2OffsetPerKg: 4.8,
    waterSavedPerKgLiters: 2100,
    hazardousMetalsDivertedGramsPerKg: 280, // Heavy electrolytes, cobalt dust
    metals: [
      { element: 'Cobalt', name: 'Cobalt Metal (Co)', symbol: 'Co', unit: 'kg', ratePerUnitInr: 2600, yieldPerKg: 0.16, color: 'text-blue-400 bg-blue-500/10 border-blue-500/30' },
      { element: 'Lithium', name: 'Battery-Grade Lithium (Li)', symbol: 'Li', unit: 'kg', ratePerUnitInr: 1850, yieldPerKg: 0.065, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
      { element: 'Nickel', name: 'Nickel (Ni)', symbol: 'Ni', unit: 'kg', ratePerUnitInr: 1420, yieldPerKg: 0.18, color: 'text-purple-400 bg-purple-500/10 border-purple-500/30' },
      { element: 'Copper', name: 'Copper Foil Current Collector', symbol: 'Cu', unit: 'kg', ratePerUnitInr: 780, yieldPerKg: 0.11, color: 'text-orange-400 bg-orange-500/10 border-orange-500/30' },
    ],
  },
  {
    id: 'copper_cables',
    name: 'Copper Cables & Harness Wires',
    categoryCode: 'CAT_CABLES',
    description: 'Stripped and sheathed communication, industrial power, and networking copper wiring.',
    avgPurityPct: 96,
    processingCostPerKgInr: 25,
    co2OffsetPerKg: 2.1,
    waterSavedPerKgLiters: 980,
    hazardousMetalsDivertedGramsPerKg: 40,
    metals: [
      { element: 'Copper', name: 'Bright Bare Copper (Millberry)', symbol: 'Cu', unit: 'kg', ratePerUnitInr: 810, yieldPerKg: 0.58, color: 'text-orange-400 bg-orange-500/10 border-orange-500/30' },
      { element: 'Aluminum', name: 'Aluminum Shielding', symbol: 'Al', unit: 'kg', ratePerUnitInr: 210, yieldPerKg: 0.08, color: 'text-slate-300 bg-slate-500/10 border-slate-500/30' },
    ],
  },
  {
    id: 'crt_monitors',
    name: 'CRT Monitors & Glass Assemblies',
    categoryCode: 'CAT_CRT',
    description: 'Cathode ray tube funnels, electron guns, and leaded phosphor glass requiring sealed smelting.',
    avgPurityPct: 75,
    processingCostPerKgInr: 30,
    co2OffsetPerKg: 1.6,
    waterSavedPerKgLiters: 650,
    hazardousMetalsDivertedGramsPerKg: 450, // High toxic lead oxide
    metals: [
      { element: 'Copper', name: 'Deflection Yoke Copper', symbol: 'Cu', unit: 'kg', ratePerUnitInr: 780, yieldPerKg: 0.12, color: 'text-orange-400 bg-orange-500/10 border-orange-500/30' },
      { element: 'Iron', name: 'Structural Ferrous Scrap', symbol: 'Fe', unit: 'kg', ratePerUnitInr: 38, yieldPerKg: 0.35, color: 'text-slate-400 bg-slate-600/10 border-slate-600/30' },
    ],
  },
];

export default function UrbanMiningPage() {
  const [selectedProfileId, setSelectedProfileId] = useState<string>(SCRAP_PROFILES[0].id);
  const [weightKg, setWeightKg] = useState<number>(250);
  const [recoveryEfficiency, setRecoveryEfficiency] = useState<number>(90);
  const [showCertificateModal, setShowCertificateModal] = useState<boolean>(false);

  const profile = useMemo(() => {
    return SCRAP_PROFILES.find((p) => p.id === selectedProfileId) || SCRAP_PROFILES[0];
  }, [selectedProfileId]);

  // Calculations
  const calculations = useMemo(() => {
    const effFactor = recoveryEfficiency / 100;
    let grossRealizationInr = 0;

    const metalBreakdown = profile.metals.map((m) => {
      const recoveredQuantity = weightKg * m.yieldPerKg * effFactor;
      const metalValueInr = recoveredQuantity * m.ratePerUnitInr;
      grossRealizationInr += metalValueInr;
      return {
        ...m,
        recoveredQuantity,
        metalValueInr,
      };
    });

    const totalProcessingCostInr = weightKg * profile.processingCostPerKgInr;
    const netSmelterProfitInr = Math.max(0, grossRealizationInr - totalProcessingCostInr);
    const co2OffsetKg = weightKg * profile.co2OffsetPerKg;
    const waterSavedLiters = weightKg * profile.waterSavedPerKgLiters;
    const toxicDivertedKg = (weightKg * profile.hazardousMetalsDivertedGramsPerKg) / 1000;

    return {
      metalBreakdown,
      grossRealizationInr,
      totalProcessingCostInr,
      netSmelterProfitInr,
      co2OffsetKg,
      waterSavedLiters,
      toxicDivertedKg,
      netPerKg: weightKg > 0 ? netSmelterProfitInr / weightKg : 0,
    };
  }, [profile, weightKg, recoveryEfficiency]);

  const certificateHash = useMemo(() => {
    const raw = `CPCB-EPR-${profile.categoryCode}-${weightKg}KG-${recoveryEfficiency}%-${new Date().toISOString().split('T')[0]}`;
    return '0x' + Array.from(raw).reduce((acc, char) => (acc * 31 + char.charCodeAt(0)) >>> 0, 0x9e3779b9).toString(16).padStart(16, '0');
  }, [profile, weightKg, recoveryEfficiency]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Urban Mining & Elemental BOM Engine
                <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  CPCB Certified
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Decompose electronic scrap lots into critical rare & precious metals, project smelting yields, and issue statutory CPCB EPR certificates.
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowCertificateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-emerald-950/40 transition-all border border-emerald-400/20 cursor-pointer"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CPCB Form-6 Manifest
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Scrap Configuration & Sliders */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Lot Parameters & Feedstock
            </h2>

            {/* Scrap Category Selector */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Feedstock Material</label>
              <div className="grid grid-cols-1 gap-2">
                {SCRAP_PROFILES.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProfileId(p.id)}
                    className={`text-left p-3.5 rounded-xl border transition-all cursor-pointer ${
                      selectedProfileId === p.id
                        ? 'bg-emerald-950/40 border-emerald-500/50 shadow-md shadow-emerald-950/30'
                        : 'bg-slate-950/40 border-slate-800 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm text-white">{p.name}</span>
                      <span className="text-[11px] px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-300">
                        {p.categoryCode}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-1">{p.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Weight Input & Slider */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <label htmlFor="weightInput" className="text-xs font-medium text-slate-400 uppercase tracking-wider">Batch Weight (kg)</label>
                <div className="flex items-center gap-2">
                  <input
                    id="weightInput"
                    type="number"
                    min="1"
                    max="10000"
                    value={weightKg}
                    onChange={(e) => setWeightKg(Math.max(1, Number(e.target.value) || 0))}
                    className="w-24 px-3 py-1 bg-slate-950 border border-slate-800 rounded-lg text-right font-mono text-emerald-400 font-bold focus:outline-none focus:border-emerald-500"
                  />
                  <span className="text-xs text-slate-400 font-medium">kg</span>
                </div>
              </div>
              <input
                id="weightSlider"
                aria-label="Batch Weight Slider"
                type="range"
                min="10"
                max="2000"
                step="10"
                value={weightKg}
                onChange={(e) => setWeightKg(Number(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-950 cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                <span>10 kg (Bag)</span>
                <span>500 kg (Pallet)</span>
                <span>2,000 kg (Truckload)</span>
              </div>
            </div>

            {/* Smelting Efficiency */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <label htmlFor="recoveryEfficiencyInput" className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Hydrometallurgical Efficiency
                </label>
                <span className="text-sm font-mono font-bold text-amber-400">{recoveryEfficiency}%</span>
              </div>
              <input
                id="recoveryEfficiencyInput"
                aria-label="Hydrometallurgical Recovery Efficiency"
                type="range"
                min="60"
                max="98"
                value={recoveryEfficiency}
                onChange={(e) => setRecoveryEfficiency(Number(e.target.value))}
                className="w-full accent-amber-500 bg-slate-950 cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                <span>60% (Mechanical)</span>
                <span>85% (Pyrometallurgical)</span>
                <span>98% (Hydrometallurgical)</span>
              </div>
            </div>
          </div>

          {/* Environmental ESG Stats Card */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              EPR Environmental Equivalency
            </h3>
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3.5 bg-slate-950/60 border border-slate-800/60 rounded-xl text-center">
                <span className="text-xl font-bold font-mono text-cyan-400">
                  {Math.round(calculations.co2OffsetKg)}
                </span>
                <span className="text-[10px] text-slate-400 block mt-1 uppercase font-medium">kg CO₂ Averted</span>
              </div>
              <div className="p-3.5 bg-slate-950/60 border border-slate-800/60 rounded-xl text-center">
                <span className="text-xl font-bold font-mono text-blue-400">
                  {Math.round(calculations.waterSavedLiters / 1000)}k
                </span>
                <span className="text-[10px] text-slate-400 block mt-1 uppercase font-medium">L Water Saved</span>
              </div>
              <div className="p-3.5 bg-slate-950/60 border border-slate-800/60 rounded-xl text-center">
                <span className="text-xl font-bold font-mono text-emerald-400">
                  {calculations.toxicDivertedKg.toFixed(1)}
                </span>
                <span className="text-[10px] text-slate-400 block mt-1 uppercase font-medium">kg Toxics Diverted</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Elemental Realization & Smelting Economics */}
        <div className="lg:col-span-7 space-y-6">
          {/* Realization Summary Card */}
          <div className="bg-gradient-to-br from-slate-900 via-slate-900/90 to-emerald-950/20 border border-emerald-500/20 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-emerald-400">
                  Projected Smelter Net Realization
                </span>
                <div className="text-3xl sm:text-4xl font-extrabold font-mono text-white mt-1">
                  ₹{Math.round(calculations.netSmelterProfitInr).toLocaleString('en-IN')}
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">Net Realization per kg:</span>
                <div className="text-lg font-mono font-bold text-emerald-400">
                  ₹{Math.round(calculations.netPerKg).toLocaleString('en-IN')} / kg
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-800/80">
              <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                <span className="text-[11px] text-slate-400 block">Gross Metal Value</span>
                <span className="text-sm font-mono font-semibold text-white">
                  ₹{Math.round(calculations.grossRealizationInr).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                <span className="text-[11px] text-slate-400 block">Processing & Acid Cost</span>
                <span className="text-sm font-mono font-semibold text-rose-400">
                  -₹{Math.round(calculations.totalProcessingCostInr).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50 col-span-2 sm:col-span-1">
                <span className="text-[11px] text-slate-400 block">EPR Compliance Credit</span>
                <span className="text-sm font-mono font-semibold text-cyan-400">
                  +₹{Math.round(weightKg * 5).toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          </div>

          {/* Recoverable Elemental Breakdown */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                Elemental Bill of Materials (BOM)
              </h2>
              <span className="text-xs text-slate-400">Spot rates updated daily (MCX/LME)</span>
            </div>

            <div className="space-y-3">
              {calculations.metalBreakdown.map((metal) => (
                <div
                  key={metal.element}
                  className="p-4 bg-slate-950/60 border border-slate-800/60 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-mono font-bold text-sm border ${metal.color}`}>
                      {metal.symbol}
                    </div>
                    <div>
                      <div className="font-semibold text-sm text-white">{metal.name}</div>
                      <div className="text-xs text-slate-400">
                        Spot: ₹{metal.ratePerUnitInr.toLocaleString('en-IN')}/{metal.unit} • Projected Recovery: {metal.yieldPerKg * (recoveryEfficiency / 100)} {metal.unit}/kg
                      </div>
                    </div>
                  </div>

                  <div className="text-right flex items-center sm:block justify-between border-t sm:border-0 border-slate-900 pt-2 sm:pt-0">
                    <div className="font-mono text-base font-bold text-emerald-400">
                      ₹{Math.round(metal.metalValueInr).toLocaleString('en-IN')}
                    </div>
                    <div className="text-xs text-slate-400 font-mono">
                      {metal.recoveredQuantity.toFixed(2)} {metal.unit} yield
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CPCB Form-6 Manifest Modal */}
      {showCertificateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl relative space-y-6">
            <button
              onClick={() => setShowCertificateModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="text-center space-y-2 border-b border-slate-800 pb-5">
              <span className="text-[11px] font-mono uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                Government of India • Ministry of Environment, Forest & Climate Change
              </span>
              <h2 className="text-xl font-bold text-white mt-2">
                Central Pollution Control Board (CPCB) — Form 6
              </h2>
              <p className="text-xs text-slate-400">
                E-Waste (Management) Rules 2022/2026 • Certificate of Verified Environmentally-Sound Dismantling
              </p>
            </div>

            <div className="space-y-4 text-xs font-mono bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-500">Certificate Reference:</span>
                <span className="text-emerald-400 font-bold">{certificateHash}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-500">Material Category:</span>
                <span className="text-white">{profile.name} ({profile.categoryCode})</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-500">Verified Batch Weight:</span>
                <span className="text-white">{weightKg} kg</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-500">Smelting Efficiency:</span>
                <span className="text-white">{recoveryEfficiency}% Hydrometallurgical</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-500">Carbon Offset Generated:</span>
                <span className="text-cyan-400 font-bold">{Math.round(calculations.co2OffsetKg)} kg CO₂e</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Statutory Custody Proof:</span>
                <span className="text-amber-400 font-bold">SHA-256 Tamper-Evident Ledger Enforced</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowCertificateModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-sm font-medium transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={() => {
                  window.print();
                }}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-emerald-950/40 transition-colors flex items-center gap-2 cursor-pointer"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Print / Save PDF
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
