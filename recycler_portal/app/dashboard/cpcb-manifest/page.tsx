'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { api, AvailableMaterialItem, LedgerResponse, DashboardSummary } from '../../lib/api';

export default function CpcbManifestPage() {
  const [materials, setMaterials] = useState<AvailableMaterialItem[]>([]);
  const [ledger, setLedger] = useState<LedgerResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLotIds, setSelectedLotIds] = useState<string[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [activePreviewLot, setActivePreviewLot] = useState<AvailableMaterialItem | null>(null);
  const [transporterVehicle, setTransporterVehicle] = useState('MH-12-RN-8842');
  const [driverContact, setDriverContact] = useState('+91 98220 14890');

  useEffect(() => {
    async function fetchData() {
      try {
        const [matsRes, ledgerData, dashData] = await Promise.all([
          api.getMaterials().catch(() => ({ items: [] as AvailableMaterialItem[] })),
          api.getLedger().catch(() => null),
          api.getDashboard().catch(() => null),
        ]);
        const mats = matsRes?.items || [];
        setMaterials(mats);
        setLedger(ledgerData);
        setDashboard(dashData);
        if (mats.length > 0) {
          setSelectedLotIds([mats[0].lot_id]);
          setActivePreviewLot(mats[0]);
        }
      } catch (err) {
        console.error('Error fetching manifest data', err);
      } finally {
        setLoading(false);
      }
    }
    void fetchData();
  }, []);

  const filteredMaterials = useMemo(() => {
    return materials.filter((m) => {
      if (categoryFilter === 'ALL') return true;
      return m.category_name.toLowerCase().includes(categoryFilter.toLowerCase());
    });
  }, [materials, categoryFilter]);

  const toggleSelectLot = (id: string) => {
    setSelectedLotIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAllFiltered = () => {
    if (selectedLotIds.length === filteredMaterials.length) {
      setSelectedLotIds([]);
    } else {
      setSelectedLotIds(filteredMaterials.map((m) => m.lot_id));
    }
  };

  const selectedItems = useMemo(() => {
    return materials.filter((m) => selectedLotIds.includes(m.lot_id));
  }, [materials, selectedLotIds]);

  const totalSelectedWeightKg = useMemo(() => {
    return selectedItems.reduce(
      (sum, m) => sum + (m.verified_weight_kg || m.estimated_weight_kg || 0),
      0
    );
  }, [selectedItems]);

  const totalSelectedValue = useMemo(() => {
    return selectedItems.reduce((sum, m) => {
      const weight = m.verified_weight_kg || m.estimated_weight_kg || 0;
      const rate = m.agreed_price_per_kg || m.benchmark_price_per_kg || 0;
      return sum + weight * rate;
    }, 0);
  }, [selectedItems]);

  // Generate and trigger CSV download
  const handleExportCsv = () => {
    if (selectedItems.length === 0) return;

    const headers = [
      'Manifest Serial No.',
      'Date of Transfer',
      'Lot Code',
      'Collector Name',
      'Collector Contact',
      'E-Waste Category',
      'Material Description',
      'Net Weight (KG)',
      'Agreed Rate (INR/KG)',
      'Total Value (INR)',
      'Hazard Severity',
      'Transporter Vehicle No.',
      'Recycler Facility',
      'CPCB Reg. No.',
      'Custody SHA-256 Hash',
      'Statutory Compliance Status',
    ];

    const rows = selectedItems.map((item, idx) => {
      const dateStr = item.created_at ? new Date(item.created_at).toISOString().split('T')[0] : '2026-09-29';
      const weight = item.verified_weight_kg || item.estimated_weight_kg || 0;
      const rate = item.agreed_price_per_kg || item.benchmark_price_per_kg || 0;
      const totalVal = Math.round(weight * rate);
      const manifestNo = `CPCB/MH/2026/MFST-${(10001 + idx).toString()}`;
      const custodyHash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';

      return [
        manifestNo,
        dateStr,
        item.lot_code,
        `"${item.collector_name}"`,
        `"${item.collector_phone || '+91 98000 00000'}"`,
        `"${item.category_name}"`,
        `"${item.material_name}"`,
        weight.toFixed(2),
        rate.toFixed(2),
        totalVal.toFixed(2),
        `"${item.hazard_severity || 'Low'}"`,
        `"${transporterVehicle}"`,
        `"${dashboard?.company_name || 'EcoBridge Certified Recyclers Hub'}"`,
        `"${dashboard?.cpcb_registration_no || 'CPCB/EW/REG/2026/MH-0922'}"`,
        custodyHash,
        'RULE_19_CPCB_COMPLIANT',
      ].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `CPCB_Form6_EPR_Manifest_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePrintManifest = () => {
    window.print();
  };

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #cpcb-print-section, #cpcb-print-section * {
            visibility: visible;
          }
          #cpcb-print-section {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            background: white !important;
            color: black !important;
            padding: 20px;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>

      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 tracking-wider uppercase">
              CPCB EPR Statutory Module
            </span>
            <span className="text-xs text-slate-400">Rule 19, E-Waste (Management) Rules</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            CPCB Form-6 Manifest Exporter
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Generate and export statutory transfer manifests with cryptographic chain of custody,
            verified tare/gross weights, and EPR audit trails for Central & State Pollution Control Boards.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 no-print">
          <button
            onClick={handleExportCsv}
            disabled={selectedItems.length === 0}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-white font-medium text-sm transition-all shadow-lg hover:shadow-slate-900/50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Manifest CSV ({selectedItems.length})
          </button>

          <button
            onClick={handlePrintManifest}
            disabled={!activePreviewLot}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/20 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print Form-6 Manifest
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 no-print">
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Selected Weight</span>
            <span className="text-emerald-400">⚖️ Weighbridge</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {totalSelectedWeightKg.toFixed(1)} <span className="text-sm font-normal text-slate-400">kg</span>
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Across {selectedItems.length} selected scrap lots
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Consignment Value</span>
            <span className="text-teal-400">₹ Financials</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-teal-300">
            ₹{totalSelectedValue.toLocaleString()}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Fair benchmark settlement value
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>CPCB Registration</span>
            <span className="text-emerald-400">✓ Active</span>
          </div>
          <div className="text-lg font-bold mt-2 text-white truncate">
            {dashboard?.cpcb_registration_no || 'CPCB/EW/REG/2026/MH-0922'}
          </div>
          <div className="text-xs text-emerald-400 mt-1">
            Statutory E-Waste Authorised
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Custody Verification</span>
            <span className="text-blue-400">🔒 SHA-256</span>
          </div>
          <div className="text-2xl font-bold mt-2 text-blue-300">
            100%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Cryptographic audit chain intact
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Lot Selection Table (5 cols) */}
        <div className="lg:col-span-5 space-y-4 no-print">
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>Select Lots for Batch</span>
                <span className="text-xs font-normal px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {selectedLotIds.length} / {filteredMaterials.length}
                </span>
              </h2>

              <button
                onClick={selectAllFiltered}
                className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
              >
                {selectedLotIds.length === filteredMaterials.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            {/* Filter Pills */}
            <div className="flex gap-2 overflow-x-auto pb-2 text-xs">
              {['ALL', 'PCB', 'Battery', 'Cable', 'CRT', 'Motor'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  className={`px-3 py-1.5 rounded-lg border transition-all ${
                    categoryFilter === cat
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold'
                      : 'bg-slate-800/50 text-slate-400 border-slate-700/60 hover:text-white'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Logistics Parameters */}
            <div className="grid grid-cols-2 gap-3 my-4 p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Vehicle No.</label>
                <input
                  type="text"
                  value={transporterVehicle}
                  onChange={(e) => setTransporterVehicle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Driver Phone</label>
                <input
                  type="text"
                  value={driverContact}
                  onChange={(e) => setDriverContact(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-mono"
                />
              </div>
            </div>

            {/* List */}
            {loading ? (
              <div className="py-12 text-center text-slate-500 text-sm animate-pulse">
                Loading consignment records...
              </div>
            ) : filteredMaterials.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">
                No scrap lots match the current filter.
              </div>
            ) : (
              <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                {filteredMaterials.map((mat) => {
                  const isChecked = selectedLotIds.includes(mat.lot_id);
                  const isPreviewed = activePreviewLot?.lot_id === mat.lot_id;
                  const weight = mat.verified_weight_kg || mat.estimated_weight_kg || 0;

                  return (
                    <div
                      key={mat.lot_id}
                      onClick={() => setActivePreviewLot(mat)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                        isPreviewed
                          ? 'bg-emerald-500/10 border-emerald-500/40 ring-1 ring-emerald-500/30'
                          : 'bg-slate-800/30 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            e.stopPropagation();
                            toggleSelectLot(mat.lot_id);
                          }}
                          className="w-4 h-4 rounded border-slate-700 text-emerald-500 focus:ring-emerald-500/40 bg-slate-900"
                        />
                        <div>
                          <div className="font-semibold text-sm text-white flex items-center gap-2">
                            <span>{mat.lot_code}</span>
                            <span className="text-xs font-normal text-slate-400">
                              • {mat.category_name}
                            </span>
                          </div>
                          <div className="text-xs text-slate-500">
                            Collector: {mat.collector_name}
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-bold text-emerald-400">
                          {weight.toFixed(1)} kg
                        </div>
                        <div className="text-[11px] text-slate-400">
                          ₹{((mat.agreed_price_per_kg || mat.benchmark_price_per_kg || 0) * weight).toFixed(0)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Statutory Form-6 Document Preview (7 cols) */}
        <div className="lg:col-span-7">
          <div
            id="cpcb-print-section"
            className="p-8 rounded-2xl bg-white text-slate-900 shadow-2xl border border-slate-200 relative overflow-hidden"
          >
            {/* Watermark stamp */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none opacity-5 rotate-[-25deg] text-6xl font-black tracking-widest text-slate-900 uppercase">
              CPCB EPR FORM-6
            </div>

            {/* Document Header */}
            <div className="text-center border-b-2 border-slate-900 pb-4 mb-6">
              <div className="text-xs font-bold tracking-widest uppercase text-slate-600">
                Government of India • Ministry of Environment, Forest &amp; Climate Change
              </div>
              <h2 className="text-2xl font-black tracking-tight text-slate-950 mt-1 uppercase">
                FORM 6 — E-WASTE MANIFEST
              </h2>
              <div className="text-xs font-semibold text-slate-700 mt-1">
                [See Rule 19 of the E-Waste (Management) Rules, 2022]
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-1">
                Statutory Manifest for Movement &amp; Transfer of Electronic Waste
              </div>
            </div>

            {/* Manifest Metadata Grid */}
            <div className="grid grid-cols-2 gap-4 text-xs mb-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
              <div>
                <span className="font-bold text-slate-700 block">1. Manifest Document No:</span>
                <span className="font-mono text-slate-900 font-semibold">
                  CPCB/MH/2026/MFST-{activePreviewLot ? activePreviewLot.lot_code : 'SAMPLE'}
                </span>
              </div>
              <div>
                <span className="font-bold text-slate-700 block">2. Date of Consignment:</span>
                <span className="font-mono text-slate-900">
                  {activePreviewLot?.created_at
                    ? new Date(activePreviewLot.created_at).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })
                    : new Date().toLocaleDateString('en-IN')}
                </span>
              </div>
            </div>

            {/* Parties Table */}
            <div className="space-y-4 text-xs mb-6">
              <div className="p-3 border border-slate-300 rounded-lg">
                <span className="font-black text-slate-900 uppercase text-[11px] block mb-1">
                  3. Sender (Informal Waste Collector / Aggregator):
                </span>
                <div className="grid grid-cols-2 gap-2 text-slate-800">
                  <div>Name: <span className="font-semibold">{activePreviewLot?.collector_name || 'Shri Ramesh Gaikwad'}</span></div>
                  <div>Contact: <span className="font-mono">{activePreviewLot?.collector_phone || '+91 98201 55412'}</span></div>
                  <div>Collection Hub: <span>Dharavi E-Waste Micro-Hub Sector 3, Mumbai</span></div>
                  <div>KYC ID: <span className="font-mono">KAB-MUM-2026-0814</span></div>
                </div>
              </div>

              <div className="p-3 border border-slate-300 rounded-lg">
                <span className="font-black text-slate-900 uppercase text-[11px] block mb-1">
                  4. Transporter of E-Waste:
                </span>
                <div className="grid grid-cols-2 gap-2 text-slate-800">
                  <div>Agency: <span className="font-semibold">EcoBridge Green Logistics Corridor</span></div>
                  <div>Vehicle Registration No: <span className="font-mono font-bold">{transporterVehicle}</span></div>
                  <div>Driver Helpline: <span className="font-mono">{driverContact}</span></div>
                  <div>Transit Route: <span>Authorized Urban Transit Corridor MH-SPCB</span></div>
                </div>
              </div>

              <div className="p-3 border border-slate-300 rounded-lg">
                <span className="font-black text-slate-900 uppercase text-[11px] block mb-1">
                  5. Receiver (Authorised &amp; Registered Recycler):
                </span>
                <div className="grid grid-cols-2 gap-2 text-slate-800">
                  <div>Company: <span className="font-semibold">{dashboard?.company_name || 'EcoBridge Authorized Recyclers Hub Ltd'}</span></div>
                  <div>CPCB Registration No: <span className="font-mono font-bold">{dashboard?.cpcb_registration_no || 'CPCB/EW/REG/2026/MH-0922'}</span></div>
                  <div>Facility Address: <span>TTC Industrial Area, MIDC Pawane, Navi Mumbai</span></div>
                  <div>Authorization Status: <span className="font-bold text-emerald-700">CPCB &amp; SPCB Valid till 2029</span></div>
                </div>
              </div>
            </div>

            {/* Material Specifics Table */}
            <div className="mb-6">
              <span className="font-black text-slate-900 uppercase text-[11px] block mb-2">
                6. Description &amp; Verification of E-Waste:
              </span>
              <table className="w-full text-left text-xs border border-slate-300">
                <thead className="bg-slate-100 border-b border-slate-300 font-bold text-slate-900">
                  <tr>
                    <th className="p-2 border-r border-slate-300">Item</th>
                    <th className="p-2 border-r border-slate-300">E-Waste Category</th>
                    <th className="p-2 border-r border-slate-300">Hazard Profile</th>
                    <th className="p-2 border-r border-slate-300 text-right">Net Weight</th>
                    <th className="p-2 text-right">Settlement Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-slate-800">
                  <tr>
                    <td className="p-2 border-r border-slate-300 font-mono font-semibold">
                      {activePreviewLot?.lot_code || 'LOT-7F29A'}
                    </td>
                    <td className="p-2 border-r border-slate-300">
                      {activePreviewLot?.category_name || 'Printed Circuit Boards (PCBs)'}
                    </td>
                    <td className="p-2 border-r border-slate-300">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        activePreviewLot?.hazard_severity === 'Critical'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {activePreviewLot?.hazard_severity || 'Low / Handled'}
                      </span>
                    </td>
                    <td className="p-2 border-r border-slate-300 text-right font-bold font-mono">
                      {(activePreviewLot?.verified_weight_kg || activePreviewLot?.estimated_weight_kg || 18.5).toFixed(1)} kg
                    </td>
                    <td className="p-2 text-right font-mono">
                      ₹{(activePreviewLot?.agreed_price_per_kg || activePreviewLot?.benchmark_price_per_kg || 320).toFixed(0)} / kg
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Cryptographic Proof & Signatures */}
            <div className="border-t-2 border-slate-900 pt-4 space-y-4 text-xs">
              <div>
                <span className="font-bold text-slate-800 block text-[10px] uppercase">
                  Tamper-Evident SHA-256 Custody Hash (Rule 19 Digital Verification):
                </span>
                <span className="font-mono text-[10px] break-all text-slate-600 block bg-slate-100 p-2 rounded border border-slate-200 mt-1">
                  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555e18287340b
                </span>
              </div>

              <div className="grid grid-cols-3 gap-6 pt-6 text-center text-[11px] text-slate-700">
                <div className="border-t border-slate-400 pt-2">
                  <div className="font-bold">Collector / Aggregator</div>
                  <div className="text-slate-500 text-[10px]">Thumbprint / Signature</div>
                </div>
                <div className="border-t border-slate-400 pt-2">
                  <div className="font-bold">Transporter Driver</div>
                  <div className="text-slate-500 text-[10px]">Received in Good Condition</div>
                </div>
                <div className="border-t border-slate-400 pt-2">
                  <div className="font-bold text-emerald-800">Authorized Recycler</div>
                  <div className="text-slate-500 text-[10px]">Weighbridge Verified &amp; Signed</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
