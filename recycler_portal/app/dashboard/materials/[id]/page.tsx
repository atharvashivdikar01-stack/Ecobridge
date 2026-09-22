'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { api, AvailableMaterialItem, DashboardSummary } from '../../../lib/api';

export default function MaterialDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lotId = params?.id as string;

  const [item, setItem] = useState<AvailableMaterialItem | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Offer form state
  const [agreedPrice, setAgreedPrice] = useState<number>(0);
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (lotId) {
      loadData();
    }
  }, [lotId]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      const [itemData, dashData] = await Promise.all([
        api.getMaterialDetail(lotId),
        api.getDashboard().catch(() => null),
      ]);
      setItem(itemData);
      setDashboard(dashData);

      // Initialize price with existing agreed price or benchmark
      if (itemData.agreed_price_per_kg) {
        setAgreedPrice(itemData.agreed_price_per_kg);
      } else {
        setAgreedPrice(itemData.benchmark_price_per_kg || itemData.min_price_per_kg);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load material details');
    } finally {
      setLoading(false);
    }
  }

  async function handleAcceptOffer() {
    if (!item) return;
    if (agreedPrice <= 0) {
      alert('Please enter a valid price per kg greater than 0.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const updated = await api.acceptOffer(item.lot_id, agreedPrice, notes);
      setItem(updated);
      setActionSuccess(`Offer successfully accepted at ₹${agreedPrice}/kg! Lot is now reserved.`);
    } catch (err: any) {
      setError(err.message || 'Failed to accept offer');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-slate-200">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-3 text-sm text-slate-500 font-medium">Fetching material manifest and AI telemetry...</p>
      </div>
    );
  }

  if (error && !item) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-center">
        <h2 className="text-base font-bold text-red-800">Error Loading Manifest</h2>
        <p className="text-sm text-red-600 mt-1">{error}</p>
        <Link
          href="/dashboard/materials"
          className="mt-4 inline-block px-4 py-2 text-xs font-semibold bg-white border border-red-300 rounded-lg text-red-700 hover:bg-red-100"
        >
          ← Back to Catalog
        </Link>
      </div>
    );
  }

  if (!item) return null;

  const isHazardous = item.detected_hazard && item.detected_hazard !== 'NONE';
  const isVerifiedRecycler = dashboard ? dashboard.is_verified : true;
  const weight = item.verified_weight_kg || item.estimated_weight_kg;
  const calculatedTotal = weight * agreedPrice;

  // Step status tracking
  const isAvailable = item.status === 'COLLECTED';
  const isAccepted = item.status === 'OFFER_ACCEPTED' || item.status === 'IN_TRANSIT';
  const isDelivered = item.status === 'DELIVERED';
  const isCompleted = item.status === 'COMPLETED';

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Back button & Breadcrumbs */}
      <div className="flex items-center justify-between">
        <Link
          href="/dashboard/materials"
          className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Materials Catalog
        </Link>

        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Manifest Status:</span>
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold ${
              isAvailable
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                : isAccepted
                ? 'bg-blue-100 text-blue-800 border border-blue-200'
                : isDelivered
                ? 'bg-amber-100 text-amber-800 border border-amber-200'
                : 'bg-slate-100 text-slate-800 border border-slate-200'
            }`}
          >
            {item.status.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Progress Journey Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <div className="grid grid-cols-4 gap-2 text-center text-xs font-semibold">
          <div className="p-2 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
            <span className="block text-[10px] uppercase font-bold tracking-wider">Step 1</span>
            1. Lot Discovered
          </div>
          <div
            className={`p-2 rounded-lg border transition-all ${
              item.status !== 'COLLECTED'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-emerald-600 text-white shadow-sm ring-2 ring-emerald-500/20'
            }`}
          >
            <span className="block text-[10px] uppercase font-bold tracking-wider">Step 2</span>
            2. Accept Offer
          </div>
          <div
            className={`p-2 rounded-lg border transition-all ${
              isDelivered || isCompleted
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : isAccepted
                ? 'bg-blue-600 text-white shadow-sm ring-2 ring-blue-500/20 font-bold'
                : 'bg-slate-50 text-slate-400 border-slate-200'
            }`}
          >
            <span className="block text-[10px] uppercase font-bold tracking-wider">Step 3</span>
            3. Scale Handover
          </div>
          <div
            className={`p-2 rounded-lg border transition-all ${
              isCompleted
                ? 'bg-emerald-600 text-white shadow-sm font-bold'
                : isDelivered
                ? 'bg-amber-500 text-white shadow-sm font-bold'
                : 'bg-slate-50 text-slate-400 border-slate-200'
            }`}
          >
            <span className="block text-[10px] uppercase font-bold tracking-wider">Step 4</span>
            4. Record Payout
          </div>
        </div>
      </div>

      {/* Success Notification */}
      {actionSuccess && (
        <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-xl flex items-center justify-between gap-3 text-emerald-900 shadow-sm animate-fade-in">
          <div className="flex items-center gap-2.5">
            <svg className="w-5 h-5 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-semibold">{actionSuccess}</span>
          </div>
          <Link
            href={`/dashboard/handover?lot_id=${item.lot_id}`}
            className="px-4 py-1.5 bg-emerald-700 text-white text-xs font-bold rounded-lg hover:bg-emerald-800 transition-colors shrink-0"
          >
            Proceed to Weighbridge Intake →
          </Link>
        </div>
      )}

      {/* Unverified Recycler Regulatory Warning Banner */}
      {!isVerifiedRecycler && (
        <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-xl flex items-start gap-3 shadow-sm">
          <div className="w-6 h-6 text-amber-600 shrink-0 mt-0.5">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-bold text-amber-900">
              CPCB Regulatory Authorization Pending — Bidding Restricted
            </h3>
            <p className="text-xs text-amber-800 mt-1 leading-relaxed">
              Your account is currently <strong className="font-semibold">UNVERIFIED</strong> under Central Pollution Control Board (CPCB) EPR Guidelines. Unverified facilities are prohibited from accepting e-waste lots or initiating chain-of-custody transfers.
            </p>
            <p className="text-xs text-amber-700 mt-1.5 font-medium">
              * To test the complete golden journey in demo mode, switch your account to <strong>Verified Recycler</strong> via the role switcher in the sidebar.
            </p>
          </div>
        </div>
      )}

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN: Material Details & AI Classification (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div>
                <span className="text-xs font-mono font-bold text-emerald-700 uppercase tracking-widest bg-emerald-50 px-2 py-0.5 rounded">
                  Lot: {item.lot_code}
                </span>
                <h1 className="text-2xl font-bold text-slate-900 mt-2">{item.material_name}</h1>
                <p className="text-sm text-slate-500 mt-0.5">{item.category_name}</p>
              </div>

              <div className="text-right">
                <span className="text-xs text-slate-500 block">Registered On</span>
                <span className="text-xs font-semibold text-slate-800">
                  {new Date(item.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </span>
              </div>
            </div>

            {/* Quick Spec Strip */}
            <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-lg border border-slate-100 text-xs">
              <div>
                <span className="text-slate-500 block text-[11px]">Weight</span>
                <span className="font-bold text-slate-900 text-sm">{weight.toFixed(1)} kg</span>
                <span className="text-[10px] text-slate-400 block">
                  {item.verified_weight_kg ? 'Verified Scale' : 'Collector Estimate'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Benchmark Band</span>
                <span className="font-bold text-slate-900 text-sm">
                  ₹{item.min_price_per_kg} - ₹{item.max_price_per_kg}
                </span>
                <span className="text-[10px] text-slate-400 block">Per kg standard</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Hazard Status</span>
                <span
                  className={`font-bold text-sm ${
                    isHazardous ? 'text-amber-700' : 'text-emerald-700'
                  }`}
                >
                  {isHazardous ? item.hazard_severity : 'Clean / Safe'}
                </span>
                <span className="text-[10px] text-slate-400 block">EPR Safety Protocol</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Agreed Rate</span>
                <span className="font-bold text-emerald-800 text-sm">
                  {item.agreed_price_per_kg ? `₹${item.agreed_price_per_kg}/kg` : 'Pending Bid'}
                </span>
                <span className="text-[10px] text-slate-400 block">
                  {item.final_value ? `Total ₹${item.final_value}` : 'Formula Bound'}
                </span>
              </div>
            </div>
          </div>

          {/* AI Material Classification & Hazard Analysis Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs">
                  AI
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">AI Vision Classification & Safety Inspection</h3>
                  <p className="text-xs text-slate-500">Autonomous Edge Material Recognition & Hazard Scan</p>
                </div>
              </div>

              {item.ai_confidence_score && (
                <div className="flex items-center gap-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1 rounded-full text-xs font-bold">
                  <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  {Math.round(item.ai_confidence_score * 100)}% Confidence
                </div>
              )}
            </div>

            {/* Mandatory Regulatory Advisory Disclaimer */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-start gap-2.5 text-xs text-slate-600 leading-relaxed">
              <svg className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong className="text-slate-800 font-semibold">Regulatory Notice:</strong> AI classification and weight estimates are advisory and do not establish final legal price or settlement. Recycler weighbridge intake scale readings determine verified transaction weights.
              </div>
            </div>

            {/* AI Classification Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                  Model Prediction
                </span>
                <span className="text-base font-bold text-slate-900 mt-1 block">
                  {item.ai_classification}
                </span>
                <span className="text-xs text-slate-600 mt-1 block">
                  Classified as {item.material_name} under e-waste schedule (Grade A recovery).
                </span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                  Hazard Protocol Check
                </span>
                <div className="mt-1 flex items-center gap-2">
                  <span
                    className={`w-2.5 h-2.5 rounded-full ${
                      isHazardous ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                  ></span>
                  <span className="text-base font-bold text-slate-900">
                    {item.detected_hazard}
                  </span>
                </div>
                <span className="text-xs text-slate-600 mt-1 block">
                  Severity: <strong className="font-semibold text-slate-800">{item.hazard_severity}</strong>
                </span>
              </div>
            </div>

            {/* Hazard Safety Advisory Details */}
            {isHazardous && (
              <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
                  <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Safety Advisory & Hazardous Handling Directive:</span>
                </div>

                {item.safety_advisory && (
                  <p className="text-xs text-amber-800 leading-relaxed font-medium">
                    {item.safety_advisory}
                  </p>
                )}

                {item.required_ppe && item.required_ppe.length > 0 && (
                  <div>
                    <span className="text-[11px] font-bold text-amber-900 uppercase tracking-wider block mb-1.5">
                      Mandatory PPE for Intake Personnel:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {item.required_ppe.map((ppe, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 bg-white border border-amber-300 text-amber-900 rounded-md text-xs font-semibold shadow-xs"
                        >
                          🛡️ {ppe}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Collector & Origin Information Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Collector & Origin Chain-of-Custody Manifest
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-1">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 space-y-1">
                <span className="text-slate-500 font-medium">Aggregator / Waste Picker</span>
                <p className="text-sm font-bold text-slate-900">{item.collector_name}</p>
                <p className="text-slate-600 flex items-center gap-1">
                  <svg className="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  {item.collector_phone}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 space-y-1">
                <span className="text-slate-500 font-medium">Pickup Location</span>
                <p className="text-sm font-bold text-slate-900 truncate">
                  {item.origin_address || 'Dharavi Aggregator Point, Mumbai'}
                </p>
                <p className="text-slate-500 font-mono text-[11px]">
                  Coords: {item.latitude?.toFixed(4) || '19.0432'}° N, {item.longitude?.toFixed(4) || '72.8561'}° E
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Pricing Formula & Offer Acceptance (1 col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5 sticky top-6">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 border-b border-slate-100 pb-3">
              <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Recycler Offer & Settlement
            </h3>

            {/* Invariant Pricing Formula Card */}
            <div className="p-3.5 bg-slate-900 text-white rounded-xl space-y-2 text-xs">
              <span className="text-[10px] uppercase font-mono tracking-wider text-emerald-400 font-bold block">
                Binding Pricing Invariant
              </span>
              <p className="font-mono text-xs text-slate-200 bg-slate-800/80 p-2 rounded border border-slate-700">
                Final Value = Verified Weight (kg) × Agreed Recycler Price (INR/kg)
              </p>
              <p className="text-[11px] text-slate-400 leading-snug">
                AI classification is strictly advisory and NEVER sets the final transaction value.
              </p>
            </div>

            {/* Price Range Reference */}
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs space-y-1">
              <div className="flex justify-between text-slate-600">
                <span>Benchmark Rate:</span>
                <span className="font-semibold text-slate-800">₹{item.benchmark_price_per_kg} / kg</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Fair Price Range:</span>
                <span className="font-semibold text-slate-800">
                  ₹{item.min_price_per_kg} - ₹{item.max_price_per_kg} / kg
                </span>
              </div>
            </div>

            {/* Pricing Input */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700 block">
                Agreed Recycler Price (INR / kg):
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center font-bold text-slate-400">
                  ₹
                </span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={agreedPrice}
                  onChange={(e) => setAgreedPrice(parseFloat(e.target.value) || 0)}
                  disabled={!isAvailable || !isVerifiedRecycler}
                  className="w-full pl-8 pr-12 py-2.5 bg-white border border-slate-300 rounded-lg text-slate-900 font-bold text-base focus:ring-2 focus:ring-emerald-500 focus:outline-none disabled:bg-slate-100 disabled:text-slate-400"
                />
                <span className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-xs font-semibold text-slate-400">
                  / kg
                </span>
              </div>
            </div>

            {/* Live Calculation Display */}
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-800 block">
                Estimated Settlement Value
              </span>
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-emerald-700">
                  {weight.toFixed(1)} kg × ₹{agreedPrice}/kg
                </span>
                <span className="text-xl font-extrabold text-emerald-900">
                  ₹{calculatedTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
              <span className="text-[10px] text-emerald-600 block">
                * Final payment will use certified weighbridge scale weight upon delivery.
              </span>
            </div>

            {/* Notes Input */}
            {isAvailable && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-700 block">
                  Intake Instructions / Notes (Optional):
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Schedule scale bay 2; inspect PCB solder integrity..."
                  className="w-full p-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:bg-white focus:ring-1 focus:ring-emerald-500 text-slate-800"
                />
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs font-semibold text-red-800">
                {error}
              </div>
            )}

            {/* Primary Action Button */}
            {isAvailable ? (
              <button
                onClick={handleAcceptOffer}
                disabled={submitting || !isVerifiedRecycler}
                className={`w-full py-3 px-4 rounded-xl text-sm font-bold shadow-sm transition-all flex items-center justify-center gap-2 ${
                  isVerifiedRecycler
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white hover:shadow-md'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
                }`}
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Committing Offer...</span>
                  </>
                ) : isVerifiedRecycler ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Accept Offer & Reserve Lot</span>
                  </>
                ) : (
                  <span>🔒 Verification Required to Bid</span>
                )}
              </button>
            ) : isAccepted ? (
              <div className="space-y-2">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-900 text-center font-semibold">
                  ✓ Offer Accepted at ₹{item.agreed_price_per_kg}/kg. Lot is queued for delivery.
                </div>
                <Link
                  href={`/dashboard/handover?lot_id=${item.lot_id}`}
                  className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold text-center block shadow-sm transition-colors"
                >
                  Proceed to Weighbridge Intake →
                </Link>
              </div>
            ) : isDelivered ? (
              <div className="space-y-2">
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 text-center font-semibold">
                  ✓ Inward Scale Verified ({item.verified_weight_kg} kg). Awaiting Payment.
                </div>
                <Link
                  href={`/dashboard/payment?lot_id=${item.lot_id}`}
                  className="w-full py-2.5 px-4 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold text-center block shadow-sm transition-colors"
                >
                  Record Payment Disbursal →
                </Link>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="p-3 bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-800 text-center font-semibold">
                  ✓ Lot Settled & Recorded in Custody Ledger
                </div>
                <Link
                  href="/dashboard/ledger"
                  className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold text-center block shadow-sm transition-colors"
                >
                  View in Accounting Ledger →
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
