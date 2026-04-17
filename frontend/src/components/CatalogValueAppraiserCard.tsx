import { useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DISCLAIMER = "This valuation is provided for informational purposes only and does not constitute a formal appraisal, legal advice, or a guarantee of sale or advance eligibility. Valuations are based on available data and proprietary models, which may not capture all factors affecting actual catalog market value. Consult qualified professionals before making financial decisions.";
const TOOLTIP = "Catalog Value Appraiser uses your net publishing share (NPS), performance and mechanical royalties, and a proprietary multiple that adjusts for catalog health, diversity, momentum, and recoverable upside. It gives you a real-world defensible estimate of what your catalog is worth today — and how much that number goes up once outstanding claims are collected.";

type WaterfallEntry = { label: string; impact: number; cumulative: number };

type Result = {
  base_nps_income: number;
  valuation_low: number;
  valuation_expected: number;
  valuation_high: number;
  multiple_applied_low: number;
  multiple_applied_high: number;
  recovery_upside_value: number;
  key_value_drivers: string[];
  key_value_risks: string[];
  waterfall: WaterfallEntry[];
  narrative: string;
  disclaimer: string;
  chain_of_custody_hash: string;
};

type Props = { artistId: string };

function WaterfallChart({ data }: { data: WaterfallEntry[] }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map((d) => Math.abs(d.cumulative)));
  const W = 280, barH = 22, gap = 6;
  const svgH = (barH + gap) * data.length + 10;

  return (
    <svg width={W} height={svgH}>
      {data.map((d, i) => {
        const isPositive = d.impact >= 0;
        const barLen = Math.abs(d.impact) / max * (W / 2 - 60);
        const baseX = W / 2;
        const barX = isPositive ? baseX : baseX - barLen;
        const y = i * (barH + gap);
        return (
          <g key={d.label}>
            <text x={baseX - 4} y={y + barH * 0.7} textAnchor="end" fill="#9CA3AF" fontSize={10}>
              {d.label.length > 16 ? d.label.slice(0, 14) + "…" : d.label}
            </text>
            <rect
              x={barX}
              y={y + 2}
              width={Math.max(barLen, 2)}
              height={barH - 4}
              fill={isPositive ? "#10B981" : "#F87171"}
              rx={3}
            />
            <text x={baseX + barLen + 4} y={y + barH * 0.7} fill={isPositive ? "#10B981" : "#F87171"} fontSize={10}>
              {isPositive ? "+" : "−"}${Math.abs(d.impact).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function CatalogValueAppraiserCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<Result | null>(null);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function appraise() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/catalog/value-appraisal`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  const fmt = (v?: number) =>
    v === undefined || v === null
      ? "—"
      : "$" + v.toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Catalog Value Appraiser</span>
        <span
          style={{ cursor: "pointer", color: textSecondary, marginLeft: "auto" }}
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
            Get a defensible market-value estimate for your catalog with recovery upside included.
          </p>
          <button
            type="button"
            aria-label="Appraise my catalog value"
            onClick={appraise}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Appraise My Catalog
          </button>
        </div>
      )}
      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>📐 Calculating catalog value…</div>
      )}
      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && result && (
        <div>
          {/* Hero valuation range */}
          <div style={{ background: "#111827", borderRadius: 10, padding: 16, marginBottom: 14, textAlign: "center" }}>
            <div style={{ fontSize: 11, color: textSecondary, marginBottom: 4 }}>Estimated Catalog Value</div>
            <div style={{ fontWeight: 800, fontSize: 26, color: amber, letterSpacing: -0.5 }}>
              {fmt(result.valuation_low)}–{fmt(result.valuation_high)}
            </div>
            <div style={{ fontSize: 13, color: textSecondary, marginTop: 4 }}>
              Expected: <span style={{ color: "#F1F1F3", fontWeight: 600 }}>{fmt(result.valuation_expected)}</span>
              {" "}&middot; Multiple: {result.multiple_applied_low}×–{result.multiple_applied_high}×
            </div>
          </div>

          {/* Recovery upside callout */}
          {result.recovery_upside_value > 0 && (
            <div style={{ background: "#064E3B", border: "1px solid #047857", borderRadius: 8, padding: 10, marginBottom: 14 }}>
              <div style={{ fontSize: 12, color: "#6EE7B7" }}>
                <b>+{fmt(result.recovery_upside_value)}</b> recovery upside included — {" "}
                once outstanding claims are collected, your catalog is worth that much more.
              </div>
            </div>
          )}

          {/* Waterfall */}
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 12, color: textSecondary, marginBottom: 6 }}>Value Bridge</div>
            <WaterfallChart data={result.waterfall} />
          </div>

          {/* Drivers & Risks */}
          <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, color: "#6EE7B7", marginBottom: 4 }}>Value Drivers</div>
              {result.key_value_drivers.map((d, i) => (
                <div key={i} style={{ fontSize: 11, color: "#D1D5DB", marginBottom: 3 }}>↑ {d}</div>
              ))}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, color: "#F87171", marginBottom: 4 }}>Value Risks</div>
              {result.key_value_risks.map((r, i) => (
                <div key={i} style={{ fontSize: 11, color: "#D1D5DB", marginBottom: 3 }}>↓ {r}</div>
              ))}
            </div>
          </div>

          {/* Narrative */}
          <div style={{ fontSize: 12, color: textSecondary, lineHeight: 1.6, marginBottom: 10 }}>
            {result.narrative}
          </div>

          {/* Footer */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #2D2D4E", paddingTop: 8 }}>
            <button
              type="button"
              aria-label={showDisclaimer ? "Hide catalog valuation disclaimer" : "Show catalog valuation disclaimer"}
              aria-expanded={showDisclaimer}
              onClick={() => setShowDisclaimer(!showDisclaimer)}
              style={{ background: "none", border: "none", color: "#6B7280", fontSize: 11, cursor: "pointer" }}
            >
              {showDisclaimer ? "Hide disclaimer" : "Disclaimer ⓘ"}
            </button>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                type="button"
                aria-label="Export catalog valuation summary"
                onClick={() => alert("PNG export —  generates a branded shareable summary")}
                style={{ background: "transparent", border: `1px solid ${amber}`, color: amber, borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer" }}
              >
                Share / Export
              </button>
            </div>
          </div>
          {showDisclaimer && (
            <div style={{ marginTop: 8, fontSize: 11, color: "#6B7280", lineHeight: 1.5 }}>
              {DISCLAIMER}
            </div>
          )}
          <div style={{ fontSize: 11, color: "#374151", marginTop: 4 }}>
            Trust hash: {result.chain_of_custody_hash?.slice(0, 16)}…
          </div>
        </div>
      )}
    </div>
  );
}
