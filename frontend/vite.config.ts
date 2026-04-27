import path from "node:path";

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@xr7-sdk": path.resolve(__dirname, "../sdk/typescript/src"),
    },
    // Resolve TypeScript first. Without this, an accidentally-checked-in or
    // locally-stale '.js' next to its source '.tsx' would shadow the .tsx —
    // Vite's default extension order puts '.js' before '.tsx'. We've been
    // bitten by this before; explicit ordering pins it.
    extensions: [".mjs", ".tsx", ".ts", ".jsx", ".js", ".json"],
  },
  server: {
    fs: {
      allow: [path.resolve(__dirname, "..")],
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/test/**", "src/main.tsx"],
      thresholds: {
        lines: 15,
        functions: 15,
        branches: 10,
        statements: 15,
      },
      reporter: ["text", "html", "json-summary"],
    },
  },
});
