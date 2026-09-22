import './globals.css';

export const metadata = {
  title: 'ECOBRIDGE Recycler Portal',
  description: 'Operations and settlement portal for certified recyclers.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
