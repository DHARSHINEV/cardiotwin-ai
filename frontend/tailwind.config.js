/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        twin: {
          blue: "#0284c7",
          cyan: "#06b6d4",
          teal: "#0d9488",
          dark: "#0f172a",
          card: "#1e293b",
          border: "#334155",
          normal: "#10b981",
          watch: "#f59e0b",
          elevated: "#f97316",
          high: "#ef4444",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
