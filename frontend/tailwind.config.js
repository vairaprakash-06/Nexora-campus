/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        campus: {
          bg: "#0B0F17",
          card: "#111827",
          cardHover: "#1E293B",
          surface: "#182234",
          border: "#1E293B",
          borderLight: "#334155",
          accent: "#38BDF8",
          accentHover: "#0EA5E9",
          primary: "#6366F1",
          primaryHover: "#4F46E5",
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#EF4444",
          text: "#F8FAFC",
          muted: "#94A3B8"
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
