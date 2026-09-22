'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState('+91 98111 11111');
  const [otp, setOtp] = useState('123456');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      // Direct demo login with verified recycler by default if standard phone entered
      await api.demoLogin('VERIFIED_RECYCLER');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to authenticate');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSwitch = async (role: 'VERIFIED_RECYCLER' | 'UNVERIFIED_RECYCLER') => {
    setError(null);
    setLoading(true);
    try {
      await api.demoLogin(role);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to switch demo account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4 shadow-lg shadow-emerald-500/5">
          <svg className="w-9 h-9 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v4" />
            <path d="m4.93 4.93 2.83 2.83" />
            <path d="M2 12h4" />
            <path d="m4.93 19.07 2.83-2.83" />
            <path d="M12 22v-4" />
            <path d="m19.07 19.07-2.83-2.83" />
            <path d="M22 12h-4" />
            <path d="m19.07 4.93-2.83 2.83" />
            <circle cx="12" cy="12" r="4" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">ECOBRIDGE</h1>
        <p className="mt-1 text-sm font-medium text-emerald-400 tracking-wide uppercase">
          Certified Recycler Operations Portal
        </p>
        <p className="mt-2 text-xs text-slate-400 max-w-sm mx-auto">
          Connecting informal waste aggregators with CPCB-authorized recycling facilities with transparent scale verification and immutable audit ledger.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg">
        <div className="glass-card rounded-2xl p-8 shadow-2xl space-y-6">
          {error && (
            <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 p-4 text-xs text-rose-300 flex items-center gap-3">
              <svg className="w-5 h-5 flex-shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          {/* Quick Demo Switcher */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
              Competition Demo Fast Access
            </label>
            <div className="grid grid-cols-1 gap-3">
              <button
                type="button"
                onClick={() => handleDemoSwitch('VERIFIED_RECYCLER')}
                disabled={loading}
                className="w-full text-left p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/30 hover:bg-emerald-900/40 hover:border-emerald-500/60 transition-all flex items-start gap-4 group"
              >
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:scale-105 transition-transform">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-emerald-300">Verified Recycler</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold tracking-wider">CPCB APPROVED</span>
                  </div>
                  <p className="text-xs text-slate-300 font-medium mt-0.5">EcoGreen E-Waste Recyclers Pvt Ltd</p>
                  <p className="text-[11px] text-slate-400 mt-1">Full access: Inspect e-waste, agree rates, verify weighbridge scale, settle cash/digital payouts.</p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleDemoSwitch('UNVERIFIED_RECYCLER')}
                disabled={loading}
                className="w-full text-left p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 hover:bg-amber-900/30 hover:border-amber-500/60 transition-all flex items-start gap-4 group"
              >
                <div className="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:scale-105 transition-transform">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-amber-300">Unverified Recycler</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-bold tracking-wider">PENDING CPCB</span>
                  </div>
                  <p className="text-xs text-slate-300 font-medium mt-0.5">Pending Scrap & Dismantling Co.</p>
                  <p className="text-[11px] text-slate-400 mt-1">Regulatory gate demonstration: Can browse listings but blocked from accepting offers or payouts.</p>
                </div>
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-900 px-3 text-slate-400 font-semibold">Or Sign In with Phone OTP</span>
            </div>
          </div>

          {/* Standard Phone/OTP Form */}
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div>
              <label htmlFor="phone" className="block text-xs font-medium text-slate-300 mb-1">
                Authorized Recycler Mobile Number
              </label>
              <input
                id="phone"
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 98111 11111"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label htmlFor="otp" className="block text-xs font-medium text-slate-300">
                  One-Time Password (OTP)
                </label>
                <span className="text-[11px] text-emerald-400 font-mono">Dev Test OTP: 123456</span>
              </div>
              <input
                id="otp"
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm tracking-widest font-mono text-center"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-sm text-white shadow-lg shadow-emerald-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>Sign In to Recycler Portal</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </form>

          <div className="pt-2 text-center text-[11px] text-slate-400">
            Compliant with E-Waste (Management) Rules 2022 • SIH 2026 PS 26229
          </div>
        </div>
      </div>
    </div>
  );
}
