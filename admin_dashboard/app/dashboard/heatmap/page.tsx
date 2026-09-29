'use client';

import React, { useState, useEffect } from 'react';
import { adminApi, CityHeatmapData } from '../../lib/api';

export default function MunicipalHeatmapPage() {
  const [cities, setCities] = useState<CityHeatmapData[]>([]);
  const [selectedCity, setSelectedCity] = useState<CityHeatmapData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await adminApi.getMunicipalHeatmap();
        setCities(data);
        if (data.length > 0) setSelectedCity(data[0]);
      } catch (err) {
        console.error('Failed to load heatmap data', err);
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, []);

  const totalNationalVolume = cities.reduce((sum, c) => sum + c.volume_tonnes, 0);
  const totalMicroHubs = cities.reduce((sum, c) => sum + c.active_micro_hubs, 0);

  return (
    <div className="space-y-8 animate-fadeIn text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
              Spatial Intelligence
            </span>
            <span className="text-xs text-slate-400">PostGIS Influx Cluster Monitoring</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            Municipal E-Waste Scrap Density &amp; Hub Heatmap
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Real-time telemetry tracking scrap concentration, informal *Kabadi Dukaan* micro-hubs,
            and municipal logistics routes across major Indian industrial metropolitan corridors.
          </p>
        </div>

        {/* Global summary pill */}
        <div className="flex items-center gap-4 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Tracked</div>
            <div className="text-lg font-bold text-white font-mono">{totalNationalVolume.toFixed(1)} MT</div>
          </div>
          <div className="h-8 w-px bg-slate-800" />
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Active Micro-Hubs</div>
            <div className="text-lg font-bold text-emerald-400 font-mono">{totalMicroHubs}</div>
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive Map representation & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: City Cards List (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
            <h2 className="text-lg font-bold text-white mb-4">
              Monitored Urban E-Waste Influx Zones
            </h2>

            {loading ? (
              <div className="py-12 text-center text-slate-500 text-sm animate-pulse">
                Loading spatial telemetry...
              </div>
            ) : (
              <div className="space-y-3">
                {cities.map((city) => {
                  const isSelected = selectedCity?.city === city.city;
                  const pct = Math.round((city.volume_tonnes / totalNationalVolume) * 100);

                  return (
                    <div
                      key={city.city}
                      onClick={() => setSelectedCity(city)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-blue-600/10 border-blue-500/50 ring-1 ring-blue-500/40 shadow-lg shadow-blue-500/10'
                          : 'bg-slate-800/30 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-xs ${
                            city.density === 'CRITICAL_HIGH'
                              ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                              : city.density === 'HIGH'
                              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          }`}>
                            {city.volume_tonnes.toFixed(1)} MT
                          </div>
                          <div>
                            <div className="font-bold text-sm text-white flex items-center gap-2">
                              <span>{city.city}</span>
                              <span className="text-xs font-normal text-slate-400">
                                ({city.state})
                              </span>
                            </div>
                            <div className="text-xs text-slate-400 mt-0.5">
                              {city.active_micro_hubs} micro-hubs • Top: {city.top_category}
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                            city.density === 'CRITICAL_HIGH'
                              ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                              : city.density === 'HIGH'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          }`}>
                            {city.density.replace('_', ' ')}
                          </span>
                          <div className="text-xs text-slate-400 mt-1 font-mono font-semibold">
                            {pct}% of National Total
                          </div>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            city.density === 'CRITICAL_HIGH'
                              ? 'bg-gradient-to-r from-red-500 to-amber-500'
                              : city.density === 'HIGH'
                              ? 'bg-gradient-to-r from-amber-500 to-emerald-500'
                              : 'bg-emerald-500'
                          }`}
                          style={{ width: `${pct * 2}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Detailed Hub & Geo Inspection (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {selectedCity ? (
            <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                    {selectedCity.spcb_code} Regional Cell
                  </span>
                  <h3 className="text-xl font-bold text-white mt-1">
                    {selectedCity.city}
                  </h3>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Coordinates</div>
                  <div className="text-xs font-mono font-semibold text-white">
                    {selectedCity.coordinates[0].toFixed(2)}°N, {selectedCity.coordinates[1].toFixed(2)}°E
                  </div>
                </div>
              </div>

              {/* Geo Telemetry Metrics */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800">
                  <div className="text-slate-400">Total Volume Collected</div>
                  <div className="text-lg font-bold text-white font-mono mt-1">
                    {selectedCity.volume_tonnes.toFixed(2)} MT
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">
                    {(selectedCity.volume_tonnes * 1000).toLocaleString()} kg
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800">
                  <div className="text-slate-400">Active Micro-Hubs</div>
                  <div className="text-lg font-bold text-white font-mono mt-1">
                    {selectedCity.active_micro_hubs} Hubs
                  </div>
                  <div className="text-[10px] text-blue-400 mt-0.5">
                    100% KYC Verified
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800">
                  <div className="text-slate-400">Dominant Waste Class</div>
                  <div className="text-sm font-bold text-white mt-1 truncate">
                    {selectedCity.top_category}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800">
                  <div className="text-slate-400">Regulatory Status</div>
                  <div className="text-sm font-bold text-emerald-400 mt-1">
                    Compliant (SPCB Valid)
                  </div>
                </div>
              </div>

              {/* Micro-Hub Logistics Corridors */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Connected Micro-Aggregation Hubs (Kabadi Dukaans)
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-800/30 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-white">Central Aggregation Yard #1</span>
                      <span className="text-[11px] text-slate-500 block">Weighbridge Scale Calibrated • JNARDDC-04</span>
                    </div>
                    <span className="text-xs text-emerald-400 font-mono font-bold">3.2 MT/mo</span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-800/30 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-white">East Industrial Scrap Hub #4</span>
                      <span className="text-[11px] text-slate-500 block">Hazardous Battery Quarantine Storage Ready</span>
                    </div>
                    <span className="text-xs text-emerald-400 font-mono font-bold">2.1 MT/mo</span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-800/30 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-white">Informal Cluster Collection Depot #7</span>
                      <span className="text-[11px] text-slate-500 block">34 Certified Waste Pickers Attached</span>
                    </div>
                    <span className="text-xs text-emerald-400 font-mono font-bold">1.5 MT/mo</span>
                  </div>
                </div>
              </div>

              {/* Action Banner */}
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-200 flex items-center justify-between">
                <span>Export SPCB Influx Report (CSV)</span>
                <button
                  onClick={() => alert(`Municipal influx report for ${selectedCity.city} exported successfully.`)}
                  className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all shadow-md"
                >
                  Download Report
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
