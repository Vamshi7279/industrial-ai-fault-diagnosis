/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#060913',
          800: '#0b0f19',
          700: '#0f172a',
          600: '#1e293b',
          500: '#334155'
        },
        brand: {
          cyan: '#38bdf8',
          indigo: '#818cf8',
          emerald: '#34d399',
          amber: '#fbbf24',
          rose: '#f87171'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      }
    },
  },
  plugins: [],
}
