/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0A0B10",
        surface: "#12141C",
        card: "#1A1D2E",
        accent: "#6C63FF",
        "accent-light": "#A89FF0",
        mint: "#00D9A3",
        muted: "#9CA3AF",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      animation: {
        "fade-up": "fadeUp 0.6s ease-out forwards",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 8s linear infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "0% 50%" },
          "100%": { backgroundPosition: "200% 50%" },
        },
      },
      boxShadow: {
        glow: "0 0 40px rgba(108, 99, 255, 0.25)",
        "glow-lg": "0 0 80px rgba(108, 99, 255, 0.15)",
      },
    },
  },
  plugins: [],
};
