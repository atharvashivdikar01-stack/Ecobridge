/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#070b14',
          card: '#0f172a',
          emerald: '#10b981',
          cyan: '#06b6d4',
        },
      },
    },
  },
  plugins: [],
};
