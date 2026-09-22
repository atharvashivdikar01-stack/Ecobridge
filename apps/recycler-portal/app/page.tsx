'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getToken } from './lib/api';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (token) {
      router.replace('/dashboard');
    } else {
      router.replace('/login');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-950">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Loading ECOBRIDGE Recycler Portal...</p>
      </div>
    </div>
  );
}
