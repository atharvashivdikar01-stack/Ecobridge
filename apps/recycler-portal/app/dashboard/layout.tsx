'use client';

import { useState, useEffect } from 'react';
import Link from 'next/navigation';
import { usePathname, useRouter } from 'next/navigation';
import { api, getStoredUser, logout, DashboardSummary } from '../lib/api';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [switchLoading, setSwitchLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await api.getDashboard();
      setDashboard(data);
    } catch (err) {
      console.error('Failed to load dashboard profile', err);
      // If unauthorized, redirect to login
      if (!api) router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleDemoRole = async () => {
    setSwitchLoading(true);
    try {
      const nextRole = dashboard?.is_verified ? 'UNVERIFIED_RECYCLER' : 'VERIFIED_RECYCLER';
      await api.demoLogin(nextRole);
      window.location.reload();
    } catch (err) {
      console.error('Failed to switch role', err);
    } finally {
      setSwitchLoading(false);
    }
  };

  const navItems = [
    {
      name: 'Overview',
      href: '/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      name: 'Available Materials',
      href: '/dashboard/materials',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
    },
    {
      name: 'Weighbridge & Handover',
      href: '/dashboard/handover',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
        </svg>
      ),
    },
    {
      name: 'Settlement & Payment',
      href: '/dashboard/payment',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
    },
    {
      name: 'Accounting Ledger',
      href: '/dashboard/ledger',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 bg-slate-900/80 border-r border-slate-800/80 flex flex-col justify-between">
        <div>
          {/* Brand Header */}
          <div className="p-6 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              </div>
              <div>
                <h2 className="font-bold text-base tracking-tight text-white flex items-center gap-2">
                  <span>ECOBRIDGE</span>
                </h2>
                <p className="text-[11px] font-medium text-emerald-400 tracking-wider uppercase">Recycler Portal</p>
              </div>
            </div>

            {/* Recycler Verification Card */}
            <div className="mt-4 p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs">
              <p className="text-[11px] text-slate-400 font-medium">Logged Facility</p>
              <p className="font-semibold text-white truncate mt-0.5">{dashboard?.company_name || 'Loading Company...'}</p>
              
              <div className="mt-2 flex items-center justify-between">
                {dashboard?.is_verified ? (
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 font-semibold text-[10px] tracking-wide">
                    <svg className="w-3 h-3 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    CPCB VERIFIED
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-amber-300 font-semibold text-[10px] tracking-wide">
                    <svg className="w-3 h-3 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    PENDING VERIFICATION
                  </span>
                )}
                
                <span className="text-[10px] text-slate-400 font-mono">
                  {dashboard?.cpcb_registration_no || ''}
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href));
              return (
                <button
                  key={item.href}
                  type="button"
                  onClick={() => router.push(item.href)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all text-left ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-300 font-semibold border border-emerald-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <span className={isActive ? 'text-emerald-400' : 'text-slate-400'}>{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer & Demo Switcher */}
        <div className="p-4 border-t border-slate-800/80 space-y-2">
          {/* Quick Demo Toggle */}
          <button
            type="button"
            onClick={handleToggleDemoRole}
            disabled={switchLoading}
            className="w-full py-2 px-3 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-800 text-[11px] font-medium text-slate-300 hover:text-white transition-all flex items-center justify-between"
          >
            <span>Toggle Demo Status</span>
            <span className="text-[10px] font-mono font-bold text-emerald-400">
              {dashboard?.is_verified ? 'Switch to Unverified' : 'Switch to Verified'}
            </span>
          </button>

          <button
            type="button"
            onClick={logout}
            className="w-full py-2 px-3 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 text-xs font-medium transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Notification Bar */}
        {!dashboard?.is_verified && (
          <div className="bg-amber-500/10 border-b border-amber-500/20 px-6 py-2.5 flex items-center justify-between text-xs text-amber-300">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-amber-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>
                <strong>Regulatory Notice:</strong> Your recycler permit is currently in <strong>PENDING_VERIFICATION</strong> status. You may browse lots in read-only mode, but offer acceptance and payment processing are restricted until CPCB accreditation is verified.
              </span>
            </div>
            <button
              onClick={handleToggleDemoRole}
              className="text-[11px] font-bold underline hover:text-white flex-shrink-0 ml-4"
            >
              Verify Now (Demo)
            </button>
          </div>
        )}

        {/* Scrollable View Content */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
