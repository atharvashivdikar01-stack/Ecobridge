'use client';

import React, { useState, useEffect } from 'react';
import { adminApi, BenchmarkRate } from '../../lib/api';

export default function BenchmarkPricesPage() {
  const [prices, setPrices] = useState<BenchmarkRate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await adminApi.getBenchmarkPrices();
        setPrices(data);
      } catch (err) {
        console.error('Failed to load benchmark prices', err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
              Market Intelligence
            </span>
            <span className="text-xs text-slate-400">8-Category Standardized Material Taxonomy</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            National E-Waste Benchmark Price Index &amp; Safety Protocols
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Regulated fair benchmark pricing bands per kilogram, empirical market averages, and mandatory PPE safety advisories broadcast to mobile collectors and certified recyclers.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Live Price Oracle Feed Active
        </div>
      </div>

      {/* Grid of Price & Hazard Cards */}
      {loading ? (
        <div className="py-16 text-center text-slate-500 text-sm animate-pulse">
          Loading national price index...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {prices.map((item) => (
            <div
              key={item.category_code}
              className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-all"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-slate-400 font-bold uppercase">
                    {item.category_code}
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                      item.hazard_level === 'CRITICAL'
                        ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                        : item.hazard_level === 'MEDIUM'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    }`}
                  >
                    {item.hazard_level} HAZARD
                  </span>
                </div>

                <h3 className="font-bold text-sm text-white mt-2 leading-snug">
                  {item.name}
                </h3>

                <div className="mt-4 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">
                    Benchmark Fair Rate
                  </div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-0.5">
                    ₹{item.benchmark_price_per_kg.toFixed(0)}{' '}
                    <span className="text-xs text-slate-400 font-normal">/ kg</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 flex justify-between font-mono">
                    <span>Min: ₹{item.min_price_per_kg}</span>
                    <span>Max: ₹{item.max_price_per_kg}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px]">
                <span className="text-slate-400 block font-semibold mb-0.5">Mandatory PPE:</span>
                <span className="text-slate-300">{item.required_ppe}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
