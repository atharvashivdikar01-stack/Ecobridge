'use client';

import React from 'react';

interface DemoDisclaimerBannerProps {
  isDemoMode: boolean;
}

export const DemoDisclaimerBanner: React.FC<DemoDisclaimerBannerProps> = ({ isDemoMode }) => {
  if (!isDemoMode) {
    return (
      <div className="rounded-xl p-4 bg-emerald-950/40 border border-emerald-500/30 text-emerald-200 text-xs flex items-start gap-3 shadow-lg">
        <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-emerald-300">Live Production Sensor & Inward Node Active</p>
          <p className="text-emerald-400/80 mt-0.5 leading-relaxed">
            Connected to real-time physical scale weighbridges and verified recycler gateways. Note: Zero-fabrication policy is enforced. Unverified or staged intake lots are pending live hardware weighbridge slips.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl p-4 bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3 shadow-lg">
      <div className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 mt-0.5 font-bold">
        ⚠️
      </div>
      <div className="flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-bold text-amber-300 uppercase tracking-wider text-[11px] px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40">
            DEMO DATA NOTICE
          </span>
          <span className="text-amber-200/90 font-medium">
            Simulated Demonstration Telemetry (Non-Statutory / Non-Production)
          </span>
        </div>
        <p className="text-amber-300/80 mt-1 leading-relaxed">
          The metrics displayed below (<strong>12 Collectors Active</strong>, <strong>8 Verified Recyclers</strong>, <strong>47 Lots Created</strong>, <strong>32 Transactions</strong>, <strong>284 kg Formalized E-Waste</strong>, <strong>96% Traceable Lots</strong>) represent test fixtures created for platform demonstration, integration testing, and evaluation. In compliance with ECOBRIDGE data integrity standards, these figures are explicitly labeled as synthetic demo data and must not be presented as audited real-world field results.
        </p>
      </div>
    </div>
  );
};
