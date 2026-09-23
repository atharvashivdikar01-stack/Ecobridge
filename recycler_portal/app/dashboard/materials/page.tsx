'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { api, AvailableMaterialItem } from '../../lib/api';

export default function MaterialsMarketplacePage() {
  const [materials, setMaterials] = useState<AvailableMaterialItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [hazardousOnly, setHazardousOnly] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  const loadMaterials = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params: { status?: string; hazardous_only?: boolean } = {};
      if (statusFilter !== 'ALL') params.status = statusFilter;
      if (hazardousOnly) params.hazardous_only = true;

      const res = await api.getMaterials(params);
      setMaterials(res.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load materials catalog');
    } finally {
      setLoading(false);
    }
  }, [hazardousOnly, statusFilter]);

  useEffect(() => {
    void loadMaterials();
  }, [loadMaterials]);

  const filteredMaterials = materials.filter((item) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.lot_code.toLowerCase().includes(q) ||
      item.material_name.toLowerCase().includes(q) ||
      item.category_name.toLowerCase().includes(q) ||
      item.collector_name.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Available E-Waste Lots</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Live Feed
            </span>
          </div>
          <p className="text-sm text-slate-600 mt-1">
            Browse verified inbound collections from certified informal aggregators with AI material classification.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* View mode toggle */}
          <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                viewMode === 'grid' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Grid View
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                viewMode === 'table' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Table View
            </button>
          </div>

          <button
            onClick={() => loadMaterials()}
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search by lot code (e.g. EB-202609), material name, or collector..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white text-slate-900 transition-all"
            />
          </div>

          {/* Hazardous Filter Toggle */}
          <label className="flex items-center gap-2.5 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors">
            <input
              type="checkbox"
              checked={hazardousOnly}
              onChange={(e) => setHazardousOnly(e.target.checked)}
              className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
            />
            <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              Hazardous Items Only
            </span>
          </label>
        </div>

        {/* Status Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-medium">
          <span className="text-slate-500 font-semibold uppercase tracking-wider text-[10px] mr-1">Status:</span>
          {[
            { id: 'ALL', label: 'All Lots' },
            { id: 'COLLECTED', label: 'Available (Collected)' },
            { id: 'OFFER_ACCEPTED', label: 'Offer Accepted' },
            { id: 'IN_TRANSIT', label: 'In Transit' },
            { id: 'DELIVERED', label: 'Delivered (At Scale)' },
            { id: 'COMPLETED', label: 'Completed' },
          ].map((status) => (
            <button
              key={status.id}
              onClick={() => setStatusFilter(status.id)}
              className={`px-3 py-1.5 rounded-full whitespace-nowrap transition-colors ${
                statusFilter === status.id
                  ? 'bg-slate-900 text-white font-semibold shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-3 text-sm text-slate-500 font-medium">Scanning live material manifests...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-center">
          <div className="w-10 h-10 mx-auto text-red-500 mb-2">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-red-800">{error}</p>
          <button
            onClick={() => loadMaterials()}
            className="mt-3 px-4 py-1.5 text-xs font-semibold bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      ) : filteredMaterials.length === 0 ? (
        <div className="p-12 bg-white border border-slate-200 rounded-xl text-center shadow-sm">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center mb-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-slate-800">No matching e-waste lots found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
            Try adjusting your search criteria or resetting status filters to discover available collector manifests.
          </p>
          <button
            onClick={() => {
              setStatusFilter('ALL');
              setSearchQuery('');
              setHazardousOnly(false);
            }}
            className="mt-4 px-4 py-2 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100"
          >
            Reset Filters
          </button>
        </div>
      ) : viewMode === 'grid' ? (
        /* GRID VIEW */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredMaterials.map((item) => {
            const isHazardous = item.detected_hazard && item.detected_hazard !== 'NONE';
            const weight = item.verified_weight_kg || item.estimated_weight_kg;
            const isAvailable = item.status === 'COLLECTED';
            const isAccepted = item.status === 'OFFER_ACCEPTED' || item.status === 'IN_TRANSIT';
            const isDelivered = item.status === 'DELIVERED';
            const isCompleted = item.status === 'COMPLETED';

            return (
              <div
                key={item.lot_id}
                className="bg-white rounded-xl border border-slate-200 hover:border-emerald-500 hover:shadow-md transition-all flex flex-col justify-between overflow-hidden group"
              >
                {/* Header preview & Status bar */}
                <div>
                  <div className="p-4 border-b border-slate-100 flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[11px] font-mono font-bold text-slate-500 tracking-wider">
                        {item.lot_code}
                      </span>
                      <h2 className="text-base font-bold text-slate-900 group-hover:text-emerald-700 transition-colors line-clamp-1 mt-0.5">
                        {item.material_name}
                      </h2>
                      <span className="text-xs text-slate-500">{item.category_name}</span>
                    </div>

                    {/* Status badge */}
                    <span
                      className={`px-2.5 py-1 rounded-full text-[11px] font-bold whitespace-nowrap ${
                        isAvailable
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : isAccepted
                          ? 'bg-blue-100 text-blue-800 border border-blue-200'
                          : isDelivered
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}
                    >
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>

                  {/* Hazard Advisory Banner (if hazardous) */}
                  {isHazardous && (
                    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0 animate-pulse"></span>
                      <p className="text-xs font-semibold text-amber-900 truncate">
                        ⚠️ Hazard: {item.detected_hazard.replace(/_/g, ' ')} ({item.hazard_severity})
                      </p>
                    </div>
                  )}

                  {/* Body Specs */}
                  <div className="p-4 space-y-3">
                    {/* Weight & Benchmark Price */}
                    <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      <div>
                        <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
                          {item.verified_weight_kg ? 'Verified Weight' : 'Est. Weight'}
                        </span>
                        <span className="text-sm font-bold text-slate-900 flex items-center gap-1 mt-0.5">
                          <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                          </svg>
                          {weight.toFixed(1)} kg
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
                          Benchmark Band
                        </span>
                        <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                          ₹{item.min_price_per_kg} - ₹{item.max_price_per_kg}
                          <span className="text-[10px] font-normal text-slate-500"> /kg</span>
                        </span>
                      </div>
                    </div>

                    {/* AI Tag */}
                    <div className="flex items-center justify-between text-xs py-1 border-b border-slate-100">
                      <span className="text-slate-500">AI Classification</span>
                      <span className="font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                        {item.ai_classification}
                        {item.ai_confidence_score && (
                          <span className="text-emerald-700 ml-1">
                            ({Math.round(item.ai_confidence_score * 100)}%)
                          </span>
                        )}
                      </span>
                    </div>

                    {/* Collector Info */}
                    <div className="flex items-center justify-between text-xs py-1">
                      <span className="text-slate-500">Collector</span>
                      <span className="font-semibold text-slate-800 flex items-center gap-1">
                        <svg className="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {item.collector_name}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Footer Action */}
                <div className="p-4 bg-slate-50 border-t border-slate-100">
                  <Link
                    href={`/dashboard/materials/${item.lot_id}`}
                    className="w-full py-2 px-3 bg-white hover:bg-emerald-600 hover:text-white text-emerald-800 border border-emerald-300 rounded-lg text-xs font-bold text-center flex items-center justify-center gap-1.5 shadow-sm transition-all"
                  >
                    <span>Inspect Lot & Review AI</span>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* TABLE VIEW */
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Lot Code</th>
                  <th className="py-3 px-4">Material & Category</th>
                  <th className="py-3 px-4">AI Classification</th>
                  <th className="py-3 px-4">Weight</th>
                  <th className="py-3 px-4">Benchmark Band</th>
                  <th className="py-3 px-4">Collector</th>
                  <th className="py-3 px-4">Hazard Check</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {filteredMaterials.map((item) => {
                  const isHazardous = item.detected_hazard && item.detected_hazard !== 'NONE';
                  const weight = item.verified_weight_kg || item.estimated_weight_kg;

                  return (
                    <tr key={item.lot_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-slate-900">
                        {item.lot_code}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-900">{item.material_name}</div>
                        <div className="text-[11px] text-slate-400">{item.category_name}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="bg-slate-100 px-2 py-0.5 rounded font-medium text-slate-800">
                          {item.ai_classification}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-900">
                        {weight.toFixed(1)} kg
                      </td>
                      <td className="py-3 px-4">
                        ₹{item.min_price_per_kg} - ₹{item.max_price_per_kg}/kg
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-medium text-slate-800">{item.collector_name}</div>
                        <div className="text-[11px] text-slate-400">{item.collector_phone}</div>
                      </td>
                      <td className="py-3 px-4">
                        {isHazardous ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                            ⚠️ {item.hazard_severity}
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700">
                            Clear
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                          {item.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          href={`/dashboard/materials/${item.lot_id}`}
                          className="px-3 py-1 bg-emerald-50 hover:bg-emerald-600 hover:text-white text-emerald-800 border border-emerald-300 rounded font-semibold text-xs transition-colors"
                        >
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
