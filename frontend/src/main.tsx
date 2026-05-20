import React from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import "./styles.css";

// Sentry error monitoring. No-ops when VITE_SENTRY_DSN is unset. The
// dynamic import keeps @sentry/react out of bundles built without a
// DSN — Vite replaces import.meta.env.* at build time, so `if
// (undefined)` becomes dead code that gets tree-shaken.
const sentryDsn = import.meta.env.VITE_SENTRY_DSN as string | undefined;
if (sentryDsn) {
  void import("@sentry/react").then((Sentry) => {
    Sentry.init({
      dsn: sentryDsn,
      environment:
        (import.meta.env.VITE_SENTRY_ENVIRONMENT as string | undefined) ?? "development",
      // Free-tier friendly: catch every error (rare), sample 5% of
      // traces (well under the 10K perf-txn monthly budget at our
      // volumes). Replay + profiling intentionally not enabled — they
      // burn the budget fast and aren't needed yet.
      tracesSampleRate: 0.05,
      sendDefaultPii: false,
    });
  });
}

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("Root element not found");
}

createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
