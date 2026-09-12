/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          850: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        devlens: {
          bug: '#ef4444',
          feature: '#3b82f6',
          question: '#10b981',
          accent: '#6366f1',
          dark: '#0f172a'
        }
      }
    },
  },
  plugins: [],
}
