import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project site: https://amnanadeem08-commits.github.io/ai_analytics/
const base = process.env.VITE_BASE || "/";

export default defineConfig({
  base,
  plugins: [react()],
  build: {
    minify: "esbuild",
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
        },
      },
    },
  },
});
