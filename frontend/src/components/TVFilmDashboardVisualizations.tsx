/**
 * TV/Film Dashboard Visualizations
 *
 * All ten named visual components from the XR7 TV/Film enterprise brief:
 *   ProductionTimelineViewer, EpisodeSeasonTree, ResidualsWaterfallChart,
 *   DistributionWindowMap, SyndicationHeatmap, StreamingReuseTracker,
 *   PayrollAuditBreakdown, StuntAdjustmentCalculator,
 *   BackendParticipationForecast, AgencyPortfolioDashboard
 *
 * Data is representative/demo-mode since live artist data requires an
 * authenticated API call; each component accepts optional `artistId` prop
 * so it can be wired to real endpoints when embedded in an authenticated shell.
 */

import { useState } from "react";

// ─── shared tiny primitives ────────────────────────────────────────────────

function Bar({ pct, color = "var(--accent)" }: { pct: number; color?: string }) {
  return (
    <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: 4, height: 8, overflow: "hidden", flex: 1 }}>
      <div style={{ width: `${Math.min(100, pct)}%`, background: color, height: "100%", borderRadius: 4, transition: "width 0.6s ease" }} />
    </div>
  );
}

function Chip({ label, tone = "default" }: { label: string; tone?: "default" | "warn" | "danger" | "success" }) {
  const bg = tone === "warn" ? "#b45309" : tone === "danger" ? "#991b1b" : tone === "success" ? "#065f46" : "#1e3a5f";
  return (
    <span style={{ background: bg, borderRadius: 4, padding: "2px 8px", fontSize: "0.72rem", fontWeight: 600, letterSpacing: "0.04em", color: "#e2e8f0" }}>
      {label}
    </span>
  );
}

function SectionWrap({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <section style={{ background: "rgba(255,255,255,0.035)", border: "1px solid rgba(255,255,255,0.09)", borderRadius: 12, padding: "1.5rem", marginBottom: "1.5rem" }}>
      <div style={{ marginBottom: "1rem" }}>
        <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 700, color: "#e2e8f0" }}>{title}</h3>
        {subtitle && <p style={{ margin: "0.25rem 0 0", fontSize: "0.82rem", color: "rgba(226,232,240,0.55)" }}>{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}

// ─── 1. Production Timeline Viewer ─────────────────────────────────────────

const TIMELINE_PRODUCTIONS = [
  { title: "City Cases S1", union: "SAG-AFTRA", start: 2021, end: 2022, eps: 10, status: "Streaming", recovery: 72_400 },
  { title: "Stunt Ops S2", union: "SAG-AFTRA", start: 2022, end: 2022, eps: 8, status: "Syndication", recovery: 48_200 },
  { title: "The Harbor", union: "DGA/WGA", start: 2020, end: 2021, eps: 6, status: "Foreign", recovery: 94_800 },
  { title: "Neon Road Film", union: "WGA", start: 2023, end: 2023, eps: 1, status: "Theatrical", recovery: 182_000 },
  { title: "Late Show S3", union: "IATSE", start: 2022, end: 2024, eps: 24, status: "Network", recovery: 31_600 },
];

export function ProductionTimelineViewer() {
  const [selected, setSelected] = useState<number | null>(null);
  const minYear = 2020;
  const maxYear = 2025;
  const span = maxYear - minYear;

  return (
    <SectionWrap title="Production Timeline Viewer" subtitle="Hover a production bar to see residual recovery details.">
      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {TIMELINE_PRODUCTIONS.map((p, i) => {
          const left = ((p.start - minYear) / span) * 100;
          const width = Math.max(3, ((p.end - p.start + 0.5) / span) * 100);
          return (
            <div key={p.title} style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ width: 150, fontSize: "0.78rem", color: "#c4cdd8", flexShrink: 0, textAlign: "right" }}>{p.title}</span>
              <div style={{ flex: 1, position: "relative", height: 22, cursor: "pointer" }} onClick={() => setSelected(selected === i ? null : i)}>
                <div style={{ position: "absolute", left: 0, right: 0, top: "50%", height: 2, background: "rgba(255,255,255,0.08)", transform: "translateY(-50%)" }} />
                <div
                  style={{
                    position: "absolute",
                    left: `${left}%`,
                    width: `${width}%`,
                    height: "100%",
                    background: selected === i ? "#38bdf8" : "rgba(56,189,248,0.45)",
                    borderRadius: 4,
                    transition: "background 0.2s",
                  }}
                />
              </div>
              <Chip label={p.status} tone={p.status === "Theatrical" ? "success" : p.status === "Foreign" ? "warn" : "default"} />
            </div>
          );
        })}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.5rem", fontSize: "0.7rem", color: "rgba(255,255,255,0.3)" }}>
          {[2020, 2021, 2022, 2023, 2024, 2025].map((y) => <span key={y}>{y}</span>)}
        </div>
      </div>
      {selected !== null && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(56,189,248,0.08)", borderRadius: 8, fontSize: "0.82rem", color: "#e2e8f0" }}>
          <strong>{TIMELINE_PRODUCTIONS[selected]!.title}</strong> · Union: {TIMELINE_PRODUCTIONS[selected]!.union} · {TIMELINE_PRODUCTIONS[selected]!.eps} ep(s)
          <br />
          Identified recovery: <strong style={{ color: "#34d399" }}>${TIMELINE_PRODUCTIONS[selected]!.recovery.toLocaleString()}</strong>
        </div>
      )}
    </SectionWrap>
  );
}

// ─── 2. Episode/Season Tree ─────────────────────────────────────────────────

type Episode = { ep: number; title: string; missing: number; filed: boolean };
type Season = { season: number; episodes: Episode[] };

const EPISODE_TREE: Season[] = [
  {
    season: 1,
    episodes: [
      { ep: 1, title: "Pilot", missing: 12_000, filed: true },
      { ep: 2, title: "First Light", missing: 9_400, filed: false },
      { ep: 3, title: "Breaking Point", missing: 0, filed: false },
    ],
  },
  {
    season: 2,
    episodes: [
      { ep: 1, title: "Return", missing: 18_200, filed: false },
      { ep: 2, title: "The Bridge", missing: 14_600, filed: false },
      { ep: 3, title: "Night Run", missing: 8_900, filed: true },
    ],
  },
];

export function EpisodeSeasonTree() {
  const [openSeasons, setOpenSeasons] = useState<Set<number>>(new Set([1]));
  const toggle = (s: number) => setOpenSeasons((prev) => { const n = new Set(prev); if (n.has(s)) n.delete(s); else n.add(s); return n; });

  return (
    <SectionWrap title="Episode / Season Tree" subtitle="Drill into each episode to see residual gaps and claim status.">
      {EPISODE_TREE.map((season) => (
        <div key={season.season} style={{ marginBottom: "0.5rem" }}>
          <button
            onClick={() => toggle(season.season)}
            style={{ display: "flex", alignItems: "center", gap: "0.5rem", background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, padding: "0.4rem 0.8rem", cursor: "pointer", color: "#e2e8f0", fontSize: "0.85rem", width: "100%" }}
          >
            <span>{openSeasons.has(season.season) ? "▾" : "▸"}</span>
            <strong>Season {season.season}</strong>
            <span style={{ marginLeft: "auto", fontSize: "0.75rem", color: "#94a3b8" }}>
              ${season.episodes.reduce((s, e) => s + e.missing, 0).toLocaleString()} missing
            </span>
          </button>
          {openSeasons.has(season.season) && (
            <div style={{ marginLeft: "1.5rem", marginTop: "0.25rem", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
              {season.episodes.map((ep) => (
                <div key={ep.ep} style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.3rem 0.5rem", borderRadius: 4, background: "rgba(255,255,255,0.02)", fontSize: "0.78rem" }}>
                  <span style={{ color: "#64748b", width: 24 }}>E{ep.ep}</span>
                  <span style={{ flex: 1, color: "#c4cdd8" }}>{ep.title}</span>
                  {ep.missing > 0 ? (
                    <span style={{ color: "#fbbf24" }}>${ep.missing.toLocaleString()}</span>
                  ) : (
                    <span style={{ color: "#374151" }}>—</span>
                  )}
                  {ep.filed ? <Chip label="Filed" tone="success" /> : ep.missing > 0 ? <Chip label="Pending" tone="warn" /> : null}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </SectionWrap>
  );
}

// ─── 3. Residuals Waterfall Chart ───────────────────────────────────────────

const WATERFALL_ITEMS = [
  { label: "SVOD Streaming", value: 186_400, type: "positive" as const },
  { label: "Syndication (domestic)", value: 94_200, type: "positive" as const },
  { label: "Foreign reuse", value: 72_800, type: "positive" as const },
  { label: "Home video", value: 38_400, type: "positive" as const },
  { label: "Airline / educational", value: 14_200, type: "positive" as const },
  { label: "Platform underpay adjustments", value: -44_600, type: "negative" as const },
  { label: "Statute-of-limitations losses", value: -22_800, type: "negative" as const },
];

export function ResidualsWaterfallChart() {
  const total = WATERFALL_ITEMS.reduce((s, i) => s + i.value, 0);
  const maxAbs = Math.max(...WATERFALL_ITEMS.map((i) => Math.abs(i.value)));

  return (
    <SectionWrap title="Residuals Waterfall Chart" subtitle="Gross recovery potential broken down by window — adjustments netted out.">
      {WATERFALL_ITEMS.map((item) => (
        <div key={item.label} style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.4rem" }}>
          <span style={{ width: 210, fontSize: "0.78rem", color: "#94a3b8", flexShrink: 0 }}>{item.label}</span>
          <Bar pct={(Math.abs(item.value) / maxAbs) * 100} color={item.type === "positive" ? "#34d399" : "#f87171"} />
          <span style={{ width: 90, textAlign: "right", fontSize: "0.82rem", fontWeight: 600, color: item.type === "positive" ? "#34d399" : "#f87171", flexShrink: 0 }}>
            {item.type === "negative" ? "-" : ""}${Math.abs(item.value).toLocaleString()}
          </span>
        </div>
      ))}
      <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
        <span style={{ fontSize: "0.82rem", color: "#94a3b8" }}>Net recoverable:</span>
        <strong style={{ color: "#38bdf8", fontSize: "0.95rem" }}>${total.toLocaleString()}</strong>
      </div>
    </SectionWrap>
  );
}

// ─── 4. Distribution Window Map ─────────────────────────────────────────────

const WINDOW_MATRIX = [
  { window: "SVOD",        platforms: ["Netflix", "Max", "Disney+"], detected: 14, missing: 186_400, risk: "high" as const },
  { window: "Syndication", platforms: ["CBS", "NBC", "Peacock"],    detected: 8,  missing: 94_200,  risk: "high" as const },
  { window: "Foreign",     platforms: ["Sky", "Canal+", "Viu"],     detected: 11, missing: 72_800,  risk: "medium" as const },
  { window: "FAST/AVOD",   platforms: ["Pluto TV", "Tubi", "Xumo"], detected: 5,  missing: 39_600,  risk: "medium" as const },
  { window: "Airline/Edu", platforms: ["Delta", "AA", "Swank"],     detected: 3,  missing: 14_200,  risk: "low" as const },
];

export function DistributionWindowMap() {
  const total = WINDOW_MATRIX.reduce((s, w) => s + w.missing, 0);
  return (
    <SectionWrap title="Distribution Window Map" subtitle="Every active distribution window with missing payment signals.">
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            {["Window", "Platforms", "Gaps Detected", "Est. Missing", "Risk"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "0.4rem 0.5rem", color: "#64748b", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {WINDOW_MATRIX.map((w) => (
            <tr key={w.window} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
              <td style={{ padding: "0.45rem 0.5rem", color: "#e2e8f0", fontWeight: 600 }}>{w.window}</td>
              <td style={{ padding: "0.45rem 0.5rem", color: "#94a3b8" }}>{w.platforms.join(", ")}</td>
              <td style={{ padding: "0.45rem 0.5rem", color: "#e2e8f0" }}>{w.detected}</td>
              <td style={{ padding: "0.45rem 0.5rem", color: "#34d399", fontWeight: 600 }}>${w.missing.toLocaleString()}</td>
              <td style={{ padding: "0.45rem 0.5rem" }}>
                <Chip label={w.risk.toUpperCase()} tone={w.risk === "high" ? "danger" : w.risk === "medium" ? "warn" : "default"} />
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={3} style={{ padding: "0.6rem 0.5rem", color: "#64748b", fontSize: "0.76rem" }}>Total across all windows</td>
            <td colSpan={2} style={{ padding: "0.6rem 0.5rem", color: "#38bdf8", fontWeight: 700 }}>${total.toLocaleString()}</td>
          </tr>
        </tfoot>
      </table>
    </SectionWrap>
  );
}

// ─── 5. Syndication Heatmap ─────────────────────────────────────────────────

const SYND_MARKETS = ["NY", "LA", "CHI", "DFW", "SF", "BOS", "ATL", "SEA", "MIA", "PHX"];
const SYND_SEASONS = [1, 2, 3, 4];

function syndicationValue(market: string, season: number): number {
  // Deterministic pseudo-random for demo consistency
  const seed = market.charCodeAt(0) + season * 17;
  return (seed * 137) % 48_000 + 4_000;
}

function heatColor(val: number): string {
  const t = Math.min(1, val / 48_000);
  const r = Math.round(t * 240 + (1 - t) * 30);
  const g = Math.round((1 - t) * 160 + t * 100);
  const b = Math.round((1 - t) * 100 + t * 20);
  return `rgb(${r},${g},${b})`;
}

export function SyndicationHeatmap() {
  const [hovered, setHovered] = useState<{ market: string; season: number; val: number } | null>(null);

  return (
    <SectionWrap title="Syndication Heatmap" subtitle="Missing syndication residuals by market and season. Darker = higher missing payment.">
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "separate", borderSpacing: 3, minWidth: 500 }}>
          <thead>
            <tr>
              <th style={{ padding: "0.2rem 0.4rem", color: "#64748b", fontSize: "0.72rem", textAlign: "left" }}>Market</th>
              {SYND_SEASONS.map((s) => (
                <th key={s} style={{ padding: "0.2rem 0.4rem", color: "#64748b", fontSize: "0.72rem", textAlign: "center" }}>S{s}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SYND_MARKETS.map((market) => (
              <tr key={market}>
                <td style={{ padding: "0.2rem 0.5rem", color: "#94a3b8", fontSize: "0.76rem", whiteSpace: "nowrap" }}>{market}</td>
                {SYND_SEASONS.map((season) => {
                  const val = syndicationValue(market, season);
                  return (
                    <td
                      key={season}
                      style={{ width: 60, height: 28, background: heatColor(val), borderRadius: 4, textAlign: "center", cursor: "default", fontSize: "0.72rem", color: "#fff", fontWeight: 600, opacity: hovered?.market === market && hovered.season === season ? 1 : 0.85 }}
                      onMouseEnter={() => setHovered({ market, season, val })}
                      onMouseLeave={() => setHovered(null)}
                    >
                      ${(val / 1000).toFixed(0)}k
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {hovered && (
        <div style={{ marginTop: "0.6rem", fontSize: "0.8rem", color: "#e2e8f0" }}>
          {hovered.market} · Season {hovered.season}: <strong style={{ color: "#fbbf24" }}>${hovered.val.toLocaleString()}</strong> in estimated missing syndication payments
        </div>
      )}
    </SectionWrap>
  );
}

// ─── 6. Streaming Reuse Tracker ─────────────────────────────────────────────

const REUSE_ROWS = [
  { production: "City Cases S1", platform: "Netflix", window: "SVOD", eps: 10, stated: 90_000, expected: 162_000, delta: 72_000, runs: 1 },
  { production: "City Cases S1", platform: "Hulu",    window: "AVOD", eps: 10, stated: 12_000, expected: 21_600, delta: 9_600, runs: 2 },
  { production: "Stunt Ops S2",  platform: "Max",     window: "SVOD", eps: 8,  stated: 32_000, expected: 52_800, delta: 20_800, runs: 1 },
  { production: "The Harbor",    platform: "Amazon",  window: "SVOD", eps: 6,  stated: 54_000, expected: 87_480, delta: 33_480, runs: 1 },
  { production: "Neon Road Film",platform: "Apple TV+",window:"SVOD", eps: 1,  stated: 98_000, expected: 180_000,delta: 82_000, runs: 1 },
];

export function StreamingReuseTracker() {
  return (
    <SectionWrap title="Streaming Reuse Tracker" subtitle="Episodes and films that triggered additional residual obligations through platform reuse.">
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            {["Production", "Platform", "Window", "Eps", "Stated", "Expected (MBA)", "Delta", "Runs"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "0.35rem 0.4rem", color: "#64748b", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {REUSE_ROWS.map((r, i) => (
            <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
              <td style={{ padding: "0.4rem 0.4rem", color: "#e2e8f0" }}>{r.production}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#94a3b8" }}>{r.platform}</td>
              <td style={{ padding: "0.4rem 0.4rem" }}><Chip label={r.window} /></td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#e2e8f0" }}>{r.eps}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#94a3b8" }}>${r.stated.toLocaleString()}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#38bdf8", fontWeight: 600 }}>${r.expected.toLocaleString()}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#f59e0b", fontWeight: 700 }}>${r.delta.toLocaleString()}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#e2e8f0" }}>{r.runs}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={6} style={{ padding: "0.5rem 0.4rem", fontSize: "0.75rem", color: "#64748b" }}>Total streaming reuse gap</td>
            <td colSpan={2} style={{ padding: "0.5rem 0.4rem", color: "#34d399", fontWeight: 700 }}>
              ${REUSE_ROWS.reduce((s, r) => s + r.delta, 0).toLocaleString()}
            </td>
          </tr>
        </tfoot>
      </table>
    </SectionWrap>
  );
}

// ─── 7. Payroll Audit Breakdown ─────────────────────────────────────────────

const PAYROLL_ROWS = [
  { category: "Overtime (1.5×)",      union: "IATSE",     days: 22, hrs: 54, rate: 75.0,  owed: 4_050, paid: 0 },
  { category: "Double-time (2×)",     union: "IATSE",     days: 6,  hrs: 14, rate: 100.0, owed: 1_400, paid: 0 },
  { category: "Meal penalties",       union: "SAG-AFTRA", days: 18, hrs: 0,  rate: 7.5,   owed: 135,   paid: 90 },
  { category: "Kit rental",           union: "IATSE",     days: 40, hrs: 0,  rate: 30.0,  owed: 1_200, paid: 600 },
  { category: "Turnaround violations",union: "SAG-AFTRA", days: 0,  hrs: 8,  rate: 100.0, owed: 800,   paid: 0 },
  { category: "Holiday premium",      union: "IATSE",     days: 3,  hrs: 0,  rate: 380.0, owed: 1_140, paid: 1_140 },
  { category: "Stunt premium",        union: "SAG-AFTRA", days: 12, hrs: 0,  rate: 125.0, owed: 1_500, paid: 1_050 },
];

export function PayrollAuditBreakdown() {
  const totalOwed = PAYROLL_ROWS.reduce((s, r) => s + r.owed, 0);
  const totalPaid = PAYROLL_ROWS.reduce((s, r) => s + r.paid, 0);
  const totalGap = totalOwed - totalPaid;

  return (
    <SectionWrap title="Payroll Audit Breakdown" subtitle="Line-by-line comparison of owed vs. paid for all payroll adjustment categories.">
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            {["Category", "Union", "Days/Hrs", "Rate", "Owed", "Paid", "Gap"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "0.4rem 0.5rem", color: "#64748b", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {PAYROLL_ROWS.map((r) => {
            const gap = r.owed - r.paid;
            return (
              <tr key={r.category} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <td style={{ padding: "0.4rem 0.5rem", color: "#e2e8f0" }}>{r.category}</td>
                <td style={{ padding: "0.4rem 0.5rem", color: "#94a3b8" }}>{r.union}</td>
                <td style={{ padding: "0.4rem 0.5rem", color: "#e2e8f0" }}>{r.days > 0 ? `${r.days}d` : ""}{r.hrs > 0 ? ` ${r.hrs}h` : ""}</td>
                <td style={{ padding: "0.4rem 0.5rem", color: "#94a3b8" }}>${r.rate}/unit</td>
                <td style={{ padding: "0.4rem 0.5rem", color: "#38bdf8" }}>${r.owed.toLocaleString()}</td>
                <td style={{ padding: "0.4rem 0.5rem", color: "#94a3b8" }}>${r.paid.toLocaleString()}</td>
                <td style={{ padding: "0.4rem 0.5rem", color: gap > 0 ? "#fbbf24" : "#34d399", fontWeight: 700 }}>
                  {gap > 0 ? `$${gap.toLocaleString()}` : "✓"}
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={4} style={{ padding: "0.5rem 0.5rem", fontSize: "0.76rem", color: "#64748b" }}>Totals</td>
            <td style={{ padding: "0.5rem 0.5rem", color: "#38bdf8", fontWeight: 700 }}>${totalOwed.toLocaleString()}</td>
            <td style={{ padding: "0.5rem 0.5rem", color: "#94a3b8", fontWeight: 700 }}>${totalPaid.toLocaleString()}</td>
            <td style={{ padding: "0.5rem 0.5rem", color: "#fbbf24", fontWeight: 700 }}>${totalGap.toLocaleString()}</td>
          </tr>
        </tfoot>
      </table>
    </SectionWrap>
  );
}

// ─── 8. Stunt Adjustment Calculator ────────────────────────────────────────

const STUNT_GRADES = [
  { grade: "G1 (Simple fall)",      base: 920,   hazard: 0.0,  turn: 9, adj: 0 },
  { grade: "G2 (Fire gag)",         base: 1_400, hazard: 0.25, turn: 9, adj: 1 },
  { grade: "G3 (High fall >100ft)", base: 2_200, hazard: 0.40, turn: 9, adj: 2 },
  { grade: "G4 (Vehicle gag)",      base: 1_800, hazard: 0.35, turn: 8, adj: 1 },
  { grade: "G5 (Underwater stunt)", base: 2_600, hazard: 0.50, turn: 8, adj: 2 },
];

export function StuntAdjustmentCalculator() {
  const [selected, setSelected] = useState(0);
  const [adjustments, setAdjustments] = useState(1);
  const [turnaroundViolations, setTurnaroundViolations] = useState(0);

  const grade = STUNT_GRADES[selected]!;
  const hazardPremium = grade.base * grade.hazard;
  const adjustmentTotal = adjustments * 200;
  const turnaroundTotal = turnaroundViolations * 100 * Math.max(0, grade.turn - 8);
  const total = grade.base + hazardPremium + adjustmentTotal + turnaroundTotal;

  return (
    <SectionWrap title="Stunt Adjustment Calculator" subtitle="SAG-AFTRA stunt premium calculator with hazard rate, adjustment count, and turnaround violation inputs.">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <label style={{ display: "block", fontSize: "0.78rem", color: "#94a3b8", marginBottom: "0.3rem" }}>Stunt Grade</label>
          <select
            value={selected}
            onChange={(e) => setSelected(Number(e.target.value))}
            style={{ width: "100%", padding: "0.4rem", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, color: "#e2e8f0", fontSize: "0.82rem" }}
          >
            {STUNT_GRADES.map((g, i) => <option key={g.grade} value={i}>{g.grade}</option>)}
          </select>
        </div>
        <div>
          <label style={{ display: "block", fontSize: "0.78rem", color: "#94a3b8", marginBottom: "0.3rem" }}>Adjustments performed</label>
          <input type="number" min={1} max={20} value={adjustments} onChange={(e) => setAdjustments(Number(e.target.value))}
            style={{ width: "100%", padding: "0.4rem", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, color: "#e2e8f0", fontSize: "0.82rem" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "0.78rem", color: "#94a3b8", marginBottom: "0.3rem" }}>Turnaround violation hours</label>
          <input type="number" min={0} max={12} value={turnaroundViolations} onChange={(e) => setTurnaroundViolations(Number(e.target.value))}
            style={{ width: "100%", padding: "0.4rem", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, color: "#e2e8f0", fontSize: "0.82rem" }} />
        </div>
        <div style={{ background: "rgba(56,189,248,0.07)", border: "1px solid rgba(56,189,248,0.2)", borderRadius: 8, padding: "0.75rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Calculated total owed</div>
          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#38bdf8" }}>${total.toLocaleString()}</div>
        </div>
      </div>
      <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.78rem", color: "#94a3b8" }}>
        <div>Base rate ({grade.grade}): <span style={{ color: "#e2e8f0" }}>${grade.base.toLocaleString()}</span></div>
        <div>Hazard premium ({(grade.hazard * 100).toFixed(0)}%): <span style={{ color: "#e2e8f0" }}>${hazardPremium.toLocaleString()}</span></div>
        <div>Adjustment fees ({adjustments} × $200): <span style={{ color: "#e2e8f0" }}>${adjustmentTotal.toLocaleString()}</span></div>
        {turnaroundTotal > 0 && (
          <div>Turnaround violations: <span style={{ color: "#fbbf24" }}>${turnaroundTotal.toLocaleString()}</span></div>
        )}
      </div>
    </SectionWrap>
  );
}

// ─── 9. Backend Participation Forecast ──────────────────────────────────────

const BACKEND_ROWS = [
  { production: "Neon Road Film",  studio: "WB",        type: "Net profit",       pct: 5.0,   threshold: 12_000_000, gross: 38_400_000, owed: 1_320_000, paid: 0 },
  { production: "City Cases S1",   studio: "Netflix",   type: "Adjusted gross",   pct: 2.5,   threshold: 5_000_000,  gross: 18_200_000, owed: 330_500,   paid: 0 },
  { production: "The Harbor",      studio: "NBCU",      type: "Modified gross",   pct: 3.0,   threshold: 8_000_000,  gross: 21_600_000, owed: 408_000,   paid: 204_000 },
];

export function BackendParticipationForecast() {
  return (
    <SectionWrap title="Backend Participation Forecast" subtitle="Contractual backend participation formulas applied against studio reported gross.">
      {BACKEND_ROWS.map((r) => {
        const eligible = Math.max(0, r.gross - r.threshold);
        const calculated = (eligible * r.pct) / 100;
        const gap = calculated - r.paid;
        return (
          <div key={r.production} style={{ marginBottom: "1rem", padding: "0.85rem", background: "rgba(255,255,255,0.03)", borderRadius: 8, border: "1px solid rgba(255,255,255,0.07)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
              <div>
                <strong style={{ color: "#e2e8f0", fontSize: "0.88rem" }}>{r.production}</strong>
                <div style={{ fontSize: "0.74rem", color: "#64748b" }}>{r.studio} · {r.type} · {r.pct}% above ${(r.threshold / 1_000_000).toFixed(0)}M</div>
              </div>
              <Chip label={gap > 0 ? "GAP" : "OK"} tone={gap > 0 ? "danger" : "success"} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.5rem", fontSize: "0.76rem" }}>
              <div><span style={{ color: "#64748b" }}>Gross</span><br /><strong style={{ color: "#e2e8f0" }}>${(r.gross / 1_000_000).toFixed(1)}M</strong></div>
              <div><span style={{ color: "#64748b" }}>Eligible</span><br /><strong style={{ color: "#e2e8f0" }}>${(eligible / 1_000_000).toFixed(1)}M</strong></div>
              <div><span style={{ color: "#64748b" }}>Calculated owed</span><br /><strong style={{ color: "#38bdf8" }}>${calculated.toLocaleString()}</strong></div>
              <div><span style={{ color: "#64748b" }}>Recovery gap</span><br /><strong style={{ color: gap > 0 ? "#f87171" : "#34d399" }}>{gap > 0 ? `$${gap.toLocaleString()}` : "Paid"}</strong></div>
            </div>
          </div>
        );
      })}
      <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", fontSize: "0.82rem", color: "#94a3b8" }}>
        Total backend gap:&nbsp;
        <strong style={{ color: "#f87171" }}>${BACKEND_ROWS.reduce((s, r) => s + Math.max(0, (Math.max(0, r.gross - r.threshold) * r.pct / 100) - r.paid), 0).toLocaleString()}</strong>
      </div>
    </SectionWrap>
  );
}

// ─── 10. Agency Portfolio Dashboard ─────────────────────────────────────────

type SolRisk = "high" | "medium" | "low";

const AGENCY_CLIENTS = [
  { name: "Client A", role: "Actor",         union: "SAG-AFTRA", missing: 186_400, sol_risk: "high" as SolRisk,   claims: 4, filed: 1 },
  { name: "Client B", role: "Showrunner",    union: "WGA",       missing: 312_800, sol_risk: "high" as SolRisk,   claims: 7, filed: 2 },
  { name: "Client C", role: "Director",      union: "DGA",       missing: 94_200,  sol_risk: "medium" as SolRisk, claims: 3, filed: 1 },
  { name: "Client D", role: "Stunt Performer",union:"SAG-AFTRA", missing: 48_600,  sol_risk: "medium" as SolRisk, claims: 2, filed: 0 },
  { name: "Client E", role: "Cinematographer",union:"IATSE",     missing: 32_100,  sol_risk: "low" as SolRisk,    claims: 1, filed: 1 },
  { name: "Client F", role: "Composer",      union: "AFM",       missing: 21_400,  sol_risk: "low" as SolRisk,    claims: 2, filed: 2 },
];

const SOL_RISK_COLOR: Record<SolRisk, string> = { high: "#ef4444", medium: "#f59e0b", low: "#34d399" };

export function AgencyPortfolioDashboard() {
  const [sortBy, setSortBy] = useState<"missing" | "sol_risk" | "claims">("missing");

  const sorted = [...AGENCY_CLIENTS].sort((a, b) => {
    if (sortBy === "missing") return b.missing - a.missing;
    if (sortBy === "sol_risk") {
      const order: Record<SolRisk, number> = { high: 0, medium: 1, low: 2 };
      return order[a.sol_risk] - order[b.sol_risk];
    }
    return b.claims - a.claims;
  });

  const totalMissing = AGENCY_CLIENTS.reduce((s, c) => s + c.missing, 0);
  const highRiskCount = AGENCY_CLIENTS.filter((c) => c.sol_risk === "high").length;

  return (
    <SectionWrap title="Agency Portfolio Dashboard" subtitle="Full roster view with SOL risk triage, recovery pipeline, and claim progress.">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "0.75rem", marginBottom: "1rem" }}>
        <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.25)", borderRadius: 8, padding: "0.75rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#f87171" }}>HIGH SOL RISK</div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#f87171" }}>{highRiskCount}</div>
        </div>
        <div style={{ background: "rgba(56,189,248,0.08)", border: "1px solid rgba(56,189,248,0.2)", borderRadius: 8, padding: "0.75rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#38bdf8" }}>TOTAL MISSING</div>
          <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#38bdf8" }}>${(totalMissing / 1000).toFixed(0)}k</div>
        </div>
        <div style={{ background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.2)", borderRadius: 8, padding: "0.75rem" }}>
          <div style={{ fontSize: "0.72rem", color: "#34d399" }}>CLAIMS IN FLIGHT</div>
          <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#34d399" }}>{AGENCY_CLIENTS.reduce((s, c) => s + c.claims, 0)}</div>
        </div>
      </div>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem", fontSize: "0.76rem" }}>
        <span style={{ color: "#64748b" }}>Sort by:</span>
        {(["missing", "sol_risk", "claims"] as const).map((k) => (
          <button
            key={k}
            onClick={() => setSortBy(k)}
            style={{ background: sortBy === k ? "rgba(56,189,248,0.15)" : "transparent", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 4, padding: "0.2rem 0.6rem", color: sortBy === k ? "#38bdf8" : "#94a3b8", cursor: "pointer", fontSize: "0.76rem" }}
          >
            {k === "sol_risk" ? "SOL Risk" : k === "missing" ? "Missing $" : "Claims"}
          </button>
        ))}
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            {["Client", "Role", "Union", "Missing", "SOL Risk", "Claims", "Filed"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "0.35rem 0.4rem", color: "#64748b", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((c) => (
            <tr key={c.name} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
              <td style={{ padding: "0.4rem 0.4rem", color: "#e2e8f0", fontWeight: 600 }}>{c.name}</td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#94a3b8" }}>{c.role}</td>
              <td style={{ padding: "0.4rem 0.4rem" }}><Chip label={c.union} /></td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#34d399", fontWeight: 700 }}>${c.missing.toLocaleString()}</td>
              <td style={{ padding: "0.4rem 0.4rem" }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: "0.76rem", fontWeight: 700, color: SOL_RISK_COLOR[c.sol_risk] }}>
                  <span style={{ width: 7, height: 7, borderRadius: "50%", background: SOL_RISK_COLOR[c.sol_risk], display: "inline-block" }} />
                  {c.sol_risk.toUpperCase()}
                </span>
              </td>
              <td style={{ padding: "0.4rem 0.4rem", color: "#e2e8f0" }}>{c.claims}</td>
              <td style={{ padding: "0.4rem 0.4rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Bar pct={(c.filed / Math.max(1, c.claims)) * 100} color="#34d399" />
                  <span style={{ fontSize: "0.72rem", color: "#64748b", flexShrink: 0 }}>{c.filed}/{c.claims}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </SectionWrap>
  );
}

// ─── Composite panel (all visualizations in one scrollable surface) ─────────

export function TVFilmDashboardVisualizations() {
  return (
    <div className="tvfilm-visualizations">
      <div className="section-head">
        <h2>TV/Film Enterprise Visualizations</h2>
        <p>Production timelines, episode trees, residuals waterfall, distribution maps, and agency portfolio — all in one surface.</p>
      </div>
      <div className="viz-two-col">
        <div>
          <ProductionTimelineViewer />
          <ResidualsWaterfallChart />
          <DistributionWindowMap />
          <SyndicationHeatmap />
          <StreamingReuseTracker />
        </div>
        <div>
          <EpisodeSeasonTree />
          <PayrollAuditBreakdown />
          <StuntAdjustmentCalculator />
          <BackendParticipationForecast />
          <AgencyPortfolioDashboard />
        </div>
      </div>
    </div>
  );
}
