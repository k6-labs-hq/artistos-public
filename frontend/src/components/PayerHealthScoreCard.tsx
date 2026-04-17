import { useState, useEffect } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Your Payer Health Score turns every source of revenue into a rated counterparty. We look at how accurately they pay, how often they redistribute on time, whether rates are drifting lower than contracted, how they resolve disputes, and the quality of their data. The combined score tells you exactly who you can trust and who needs to be watched — before the money stops coming.";

type SubScores = {
  payment_accuracy: number;
  redistribution_timing: number;
  rate_drift: number;
  dispute_resolution: number;
  data_quality: number;
};

type PayerEntry = {
  payer_id: string;
  payer_name: string;
  total_score: number;
  risk_tier: string;
  sub_scores: SubScores;
  trend: number[];
  flags: string[];
};

type Props = { artistId: string };

const tierColor = (tier: string) => {
  if (tier === "TRUSTED") return "#10B981";
  if (tier === "RELIABLE") return "#6EE7B7";
  if (tier === "WATCH") return "#FCD34D";
  if (tier === "ELEVATED_RISK") return "#F97316";
  return "#F87171";
};

const subLabel: Record<string, string> = {
  payment_accuracy: "Payment Accuracy",
  redistribution_timing: "Redistribution Timing",
  rate_drift: "Rate Drift",
  dispute_resolution: "Dispute Resolution",
  data_quality: "Data Quality",
};

const subMax: Record<string, number> = {
  payment_accuracy: 25,
  redistribution_timing: 20,
  rate_drift: 20,
  dispute_resolution: 20,
  data_quality: 15,
};

export function PayerHealthScoreCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [payers, setPayers] = useState<PayerEntry[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function fetchScores() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/payers/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setPayers(data.payers ?? []);
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  function MiniSparkline({ data }: { data: number[] }) {
    if (!data || data.length < 2) return <span style={{ color: textSecondary, fontSize: 11 }}>—</span>;
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    const w = 48, h = 20;
    const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(" ");
    const first = data[0] ?? 0;
    const last = data[data.length - 1] ?? first;
    const trend = last - first;
    return (
      <svg width={w} height={h} style={{ display: "inline-block" }}>
        <polyline points={pts} fill="none" stroke={trend >= 0 ? "#10B981" : "#F87171"} strokeWidth={1.5} />
      </svg>
    );
  }

  function GaugeMini({ value }: { value: number }) {
    const pct = value / 100;
    const r = 16;
    const circ = 2 * Math.PI * r;
    const stroke = circ * pct;
    const color = value >= 80 ? "#10B981" : value >= 60 ? "#FCD34D" : value >= 40 ? "#F97316" : "#F87171";
    return (
      <svg width={40} height={40} viewBox="0 0 40 40">
        <circle cx={20} cy={20} r={r} fill="none" stroke="#1F2937" strokeWidth={4} />
        <circle
          cx={20} cy={20} r={r} fill="none" stroke={color} strokeWidth={4}
          strokeDasharray={`${stroke} ${circ - stroke}`}
          strokeLinecap="round" transform="rotate(-90 20 20)"
        />
        <text x={20} y={24} textAnchor="middle" fill={color} fontSize={10} fontWeight="bold">
          {Math.round(value)}
        </text>
      </svg>
    );
  }

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Payer Health Score</span>
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
            Rate every payer 0–100 on reliability, timing, accuracy, and data quality.
          </p>
          <button
            onClick={fetchScores}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Score My Payers
          </button>
        </div>
      )}
      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>📊 Scoring your payers…</div>
      )}
      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && (
        <div>
          {payers.length === 0 ? (
            <div style={{ color: textSecondary, textAlign: "center" }}>No payer data found.</div>
          ) : (
            payers.sort((a, b) => a.total_score - b.total_score).map((p) => (
              <div key={p.payer_id} style={{ marginBottom: 8, border: "1px solid #2D2D4E", borderRadius: 8, overflow: "hidden" }}>
                <div
                  style={{
                    display: "flex", alignItems: "center", gap: 10, padding: "10px 12px",
                    cursor: "pointer", background: "#111827",
                  }}
                  onClick={() => setExpanded(expanded === p.payer_id ? null : p.payer_id)}
                >
                  <GaugeMini value={p.total_score} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{p.payer_name}</div>
                    <span style={{
                      background: tierColor(p.risk_tier) + "22",
                      color: tierColor(p.risk_tier), fontSize: 11, borderRadius: 4, padding: "1px 7px",
                    }}>
                      {p.risk_tier.replace(/_/g, " ")}
                    </span>
                  </div>
                  <MiniSparkline data={p.trend} />
                  <span style={{ color: textSecondary, fontSize: 12 }}>{expanded === p.payer_id ? "▲" : "▼"}</span>
                </div>

                {expanded === p.payer_id && (
                  <div style={{ background: "#0F172A", padding: "10px 14px" }}>
                    {(Object.keys(subLabel) as (keyof SubScores)[]).map((k) => {
                      const val = p.sub_scores[k];
                      const max = subMax[k] ?? 1;
                      const pct = (val / max) * 100;
                      return (
                        <div key={k} style={{ marginBottom: 6 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
                            <span>{subLabel[k]}</span>
                            <span style={{ color: amber }}>{val}/{max}</span>
                          </div>
                          <div style={{ background: "#1F2937", borderRadius: 4, height: 5, overflow: "hidden" }}>
                            <div style={{
                              width: `${pct}%`, height: "100%",
                              background: pct >= 80 ? "#10B981" : pct >= 60 ? "#FCD34D" : "#F87171",
                            }} />
                          </div>
                        </div>
                      );
                    })}
                    {p.flags.length > 0 && (
                      <div style={{ marginTop: 8, fontSize: 11, color: "#F87171" }}>
                        {p.flags.map((f, i) => <div key={i}>⚠ {f}</div>)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
