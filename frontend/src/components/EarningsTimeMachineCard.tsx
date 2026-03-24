import { useEffect, useRef, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "This analysis reconstructs what you would have earned if your catalog had always been clean — every royalty correctly paid, every identifier properly registered, every split correct from day one. The gap between that number and what you actually received is your estimated lifetime leakage. This is not a guarantee of recovery — it is a map of what the system cost you.";

type Period = {
  period: string;
  actual_earned: number;
  estimated_clean_world_earned: number;
  delta: number;
  cumulative_leakage_to_date: number;
};

type Result = {
  time_series: Period[];
  total_actual_earned: number;
  total_clean_world_earned: number;
  total_lifetime_leakage: number;
  confidence_band: { low: number; expected: number; high: number };
  summary: string;
  chain_of_custody_hash: string;
};

type Props = { artistId: string };

export function EarningsTimeMachineCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  async function runAnalysis() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/earnings/time-machine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ granularity: "year" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  const amber = "#C89B3C";
  const amberFaded = "#C89B3C33";
  const textSecondary = "#9CA3AF";

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Earnings Time Machine</span>
        <span
          style={{ cursor: "pointer", color: textSecondary, userSelect: "none" }}
          onMouseEnter={() => setTooltip(true)}
          onMouseLeave={() => setTooltip(false)}
        >
          ⓘ
          {tooltip && (
            <span style={{
              position: "absolute", background: "#111827", border: "1px solid #374151",
              borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
              zIndex: 100, lineHeight: 1.5,
            }}>
              {TOOLTIP}
            </span>
          )}
        </span>
      </div>

      {state === "idle" && (
        <div style={{ textAlign: "center", padding: "24px 0" }}>
          <p style={{ color: textSecondary, marginBottom: 16, fontSize: 14 }}>
            Reconstruct your lifetime earnings as if the system had always worked correctly.
          </p>
          <button
            onClick={runAnalysis}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Run Analysis
          </button>
        </div>
      )}

      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>
          <div style={{ marginBottom: 8 }}>⏳ Analysing your earnings history…</div>
          <div style={{ fontSize: 13 }}>Estimated time: 10–30 seconds</div>
        </div>
      )}

      {state === "error" && (
        <div style={{ color: "#F87171", padding: "16px 0" }}>Error: {error}</div>
      )}

      {state === "done" && result && (
        <div>
          {/* Summary */}
          <p style={{ fontSize: 13, color: "#D1D5DB", marginBottom: 16, lineHeight: 1.5 }}>{result.summary}</p>

          {/* Hero leakage */}
          <div style={{ background: "#111827", borderRadius: 8, padding: 16, marginBottom: 16, textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: amber }}>
              ${result.total_lifetime_leakage.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 13, color: textSecondary }}>Estimated Lifetime Leakage</div>
            <div style={{ fontSize: 12, color: textSecondary, marginTop: 4 }}>
              Low: ${result.confidence_band.low.toLocaleString()} · Expected: ${result.confidence_band.expected.toLocaleString()} · High: ${result.confidence_band.high.toLocaleString()}
            </div>
          </div>

          {/* Diverging timeline chart (SVG) */}
          {result.time_series.length > 0 && (
            <DivergingTimeline timeSeries={result.time_series} />
          )}

          {/* Year-by-year table */}
          <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse", marginTop: 16 }}>
            <thead>
              <tr style={{ color: textSecondary }}>
                <th style={{ textAlign: "left", paddingBottom: 4 }}>Period</th>
                <th style={{ textAlign: "right" }}>Actual</th>
                <th style={{ textAlign: "right" }}>Clean World</th>
                <th style={{ textAlign: "right", color: amber }}>Leakage</th>
              </tr>
            </thead>
            <tbody>
              {result.time_series.map((row) => (
                <tr key={row.period} style={{ borderTop: "1px solid #1F2937" }}>
                  <td style={{ padding: "6px 0" }}>{row.period}</td>
                  <td style={{ textAlign: "right" }}>${row.actual_earned.toLocaleString()}</td>
                  <td style={{ textAlign: "right" }}>${row.estimated_clean_world_earned.toLocaleString()}</td>
                  <td style={{ textAlign: "right", color: amber }}>${row.delta.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ fontSize: 11, color: "#6B7280", marginTop: 12 }}>
            Trust hash: {result.chain_of_custody_hash?.slice(0, 16)}…
          </div>
        </div>
      )}
    </div>
  );
}

function DivergingTimeline({ timeSeries }: { timeSeries: Period[] }) {
  const width = 480;
  const height = 160;
  const pad = { top: 10, right: 10, bottom: 20, left: 40 };
  const W = width - pad.left - pad.right;
  const H = height - pad.top - pad.bottom;

  const maxVal = Math.max(...timeSeries.map((d) => d.estimated_clean_world_earned), 1);
  const xStep = W / Math.max(timeSeries.length - 1, 1);

  const px = (i: number) => pad.left + i * xStep;
  const py = (v: number) => pad.top + H - (v / maxVal) * H;

  const actualPath = timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.actual_earned)}`).join(" ");
  const cleanPath = timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.estimated_clean_world_earned)}`).join(" ");

  // Shaded area between actual and clean
  const areaPath = [
    ...timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.estimated_clean_world_earned)}`),
    ...[...timeSeries].reverse().map((d, i) => `L ${px(timeSeries.length - 1 - i)} ${py(d.actual_earned)}`),
    "Z",
  ].join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", maxWidth: width }}>
      <defs>
        <linearGradient id="leak-gradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C89B3C" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#C89B3C" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#leak-gradient)" />
      <path d={cleanPath} stroke="#C89B3C" strokeWidth="2" fill="none" />
      <path d={actualPath} stroke="#60A5FA" strokeWidth="2" fill="none" />
      {timeSeries.map((d, i) => (
        <text key={d.period} x={px(i)} y={height - 4} textAnchor="middle" fontSize="10" fill="#6B7280">
          {d.period}
        </text>
      ))}
      <text x={2} y={pad.top + 6} fontSize="9" fill="#C89B3C">Clean World</text>
      <text x={2} y={pad.top + 16} fontSize="9" fill="#60A5FA">Actual</text>
    </svg>
  );
}
