import { useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Your Royalty DNA Profile maps exactly where your money comes from — every platform, every territory, every royalty type — and surfaces patterns you've likely never seen before. It shows where you're earning without knowing it, where you should be earning but aren't registered, how dependent you are on a single platform or market, and which parts of your catalog are carrying the weight. Think of it as an X-ray of your earnings genome.";

type PlatformEntry = { platform: string; amount: number; pct: number; trend: string };
type RoyaltyEntry = { type: string; amount: number; pct: number; trend: string };
type Insight = { headline: string; explanation: string; recommended_action: string };
type DNAStrand = { segment: string; value: number; pct: number; color: string };

type Result = {
  platform_breakdown: PlatformEntry[];
  territory_gaps: string[];
  royalty_type_breakdown: RoyaltyEntry[];
  revenue_concentration_score: number;
  top3_platform_concentration_pct: number;
  catalog_long_tail_ratio_pct: number;
  dna_strand: DNAStrand[];
  insights: Insight[];
  chain_of_custody_hash: string;
};

type Props = { artistId: string };

export function RoyaltyDNAProfileCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function generate() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/profile/dna`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  const trendArrow = (t: string) => t === "GROWING" ? " ↑" : t === "DECLINING" ? " ↓" : "";

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Royalty DNA Profile</span>
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
            Generate your personal earnings fingerprint across platform, territory, and royalty type.
          </p>
          <button
            onClick={generate}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Generate My DNA Profile
          </button>
        </div>
      )}

      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>🧬 Mapping your earnings genome…</div>
      )}
      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && result && (
        <div>
          {/* DNA Strand */}
          <div style={{ display: "flex", height: 24, borderRadius: 6, overflow: "hidden", marginBottom: 16 }}>
            {result.dna_strand.map((seg) => (
              <div
                key={seg.segment}
                title={`${seg.segment}: ${seg.pct}%`}
                style={{ width: `${seg.pct}%`, background: seg.color, minWidth: 2 }}
              />
            ))}
          </div>

          {/* Platform bar chart */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, color: textSecondary, marginBottom: 6 }}>Platform Breakdown</div>
            {result.platform_breakdown.slice(0, 5).map((p) => (
              <div key={p.platform} style={{ marginBottom: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                  <span>{p.platform}{trendArrow(p.trend)}</span>
                  <span style={{ color: amber }}>{p.pct.toFixed(1)}%</span>
                </div>
                <div style={{ background: "#1F2937", borderRadius: 4, height: 6, overflow: "hidden" }}>
                  <div style={{ width: `${p.pct}%`, height: "100%", background: amber }} />
                </div>
              </div>
            ))}
          </div>

          {/* Royalty type donut summary */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, color: textSecondary, marginBottom: 6 }}>Royalty Type Breakdown</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {result.royalty_type_breakdown.filter((r) => r.amount > 0).map((r) => (
                <span
                  key={r.type}
                  style={{
                    background: "#1F2937", borderRadius: 4, padding: "3px 8px",
                    fontSize: 11, color: "#D1D5DB",
                  }}
                >
                  {r.type}: <span style={{ color: amber }}>{r.pct.toFixed(1)}%</span>{trendArrow(r.trend)}
                </span>
              ))}
            </div>
          </div>

          {/* Concentration score */}
          <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
            <div style={{ background: "#111827", borderRadius: 8, padding: 10, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: result.revenue_concentration_score > 0.5 ? "#F87171" : "#10B981" }}>
                {Math.round(result.revenue_concentration_score * 100)}
              </div>
              <div style={{ fontSize: 11, color: textSecondary }}>HHI Concentration</div>
            </div>
            <div style={{ background: "#111827", borderRadius: 8, padding: 10, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: amber }}>
                {result.catalog_long_tail_ratio_pct}%
              </div>
              <div style={{ fontSize: 11, color: textSecondary }}>Top 10 works</div>
            </div>
          </div>

          {/* Territory gaps */}
          {result.territory_gaps.length > 0 && (
            <div style={{ background: "#451A03", border: "1px solid #92400E", borderRadius: 8, padding: 10, marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: "#FCD34D", marginBottom: 4 }}>⚠️ Territory Gaps Detected</div>
              <div style={{ fontSize: 12, color: "#FDE68A" }}>
                {result.territory_gaps.join(", ")} — catalog active but no registration/payout
              </div>
            </div>
          )}

          {/* AI Insight cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {result.insights.map((insight, i) => (
              <div key={i} style={{ background: "#111827", border: "1px solid #1F2937", borderRadius: 8, padding: 12 }}>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{insight.headline}</div>
                <div style={{ fontSize: 12, color: textSecondary, marginBottom: 6 }}>{insight.explanation}</div>
                <div style={{ fontSize: 12, color: amber }}>→ {insight.recommended_action}</div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12, alignItems: "center" }}>
            <div style={{ fontSize: 11, color: "#6B7280" }}>
              Trust hash: {result.chain_of_custody_hash?.slice(0, 16)}…
            </div>
            <button
              onClick={() => alert("PNG export feature — generates a shareable branded summary card")}
              style={{ background: "transparent", border: `1px solid ${amber}`, color: amber, borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer" }}
            >
              Share / Export
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
