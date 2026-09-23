import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ECOBRIDGE COMMAND CENTER | Platform Admin & Regulatory Console',
  description: 'Real-time telemetry, chain of custody audit, and statutory ledger for informal e-waste formalization.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#070b14] text-slate-100 min-h-screen selection:bg-emerald-500/30 selection:text-emerald-200">
        {children}
      </body>
    </html>
  );
}
