/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cg: {
          bg: "#0f172a",
          card: "#1e293b",
          border: "#334155",
          accent: "#38bdf8",
          critical: "#ef4444",
          high: "#f97316",
          medium: "#eab308",
          low: "#3b82f6",
        }
      }
    },
  },
  plugins: [],
}
