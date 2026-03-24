import { useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Contract Drift Monitor watches every contract you've ever signed and measures whether what actually came in matches what was agreed on paper. Every quarter it computes the gap — the contracted rate versus the actual effective rate — flags the ones that are silently decaying, and tells you when you're close to having a legitimate breach claim. Most artists never know their rates are drifting because no-one adds it up.";

type QuarterPoint = { quarter: string; contracted_rate: number; actual_rate: number; drift_pct: number };

type ContractResult = {
  contract_id: string;
  payer_name: string;
  classification: string;
  current_drift_pct: number;
  cumulative_underpayment: number;
  drift_trend: string;
  quarterly_timeline: QuarterPoint[];
  anomaly_id?: string;
};

type Props = { artistId: string };

const classColor = (c: string) => {
  if (c === "WITHIN_VARIANCE") return "#10B981";
  if (c === "SOFT_DRIFT") return "#FCD34D";
  if (c === "HARD_DRIFT") return "#F97316";
  return "#F87171";
};

const trendIcon = (t: string) => t === "WIDENING" ? "↗" : t === "NARROWING" ? "↘" : "→";

function DriftSparkline({ data }: { data: QuarterPoint[] }) {
  if (!data || data.length < 2) return null;
  const w = 120, h = 40;
  const maxR = Math.max(...data.map((d) => d.contracted_rate), 1);
  const pts = (arr: number[]) =>
    arr.map((v, i) => `${(i / (arr.length - 1)) * w},${h - (v / maxR) * h}`).join(" ");
  const contracted = data.map((d) => d.contracted_rate);
  const actual = data.map((d) => d.actual_rate);
  const areaTop = actual.map((v, i) => `${(i / (actual.length - 1)) * w},${h - (v / maxR) * h}`).join(" ");
  const areaBottom = [...actual].reverse().map((v, i) => {
    const idx = actual.length - 1 - i;
    return `${(idx / (actual.length - 1)) * w},${h - (contracted[idx] / maxR) * h}`;
  }).join(" ");

  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polygon points={`${areaTop} ${areaBottom}`} fill="#F97316" opacity="0.15" />
      <polyline points={pts(contracted)} fill="none" stroke="#C89B3C" strokeWidth={1.5} strokeDasharray="4 2" />
      <polyline points={pts(actual)} fill="none" stroke="#60A5FA" strokeWidth={1.5} />
    </svg>
  );
}

export function ContractDriftMonitorCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [contracts, setContracts] = useState<ContractResult[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [disputing, setDisputing] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function load() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/contracts/drift`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setContracts(data.contracts ?? []);
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  async function initiateDispute(contractId: string) {
    setDisputing(contractId);
    try {
      await fetch(`${BASE}/artists/${artistId}/contracts/${contractId}/drift/dispute`, { method: "POST" });
    } finally {
      setDisputing(null);
    }
  }

  const totalUnderpaid = contracts.reduce((s, c) => s + c.cumulative_underpayment, 0);

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Contract Drift Monitor</span>
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
            Monitor whether your contracted rates and actual payouts are in sync — every quarter.
          </p>
          <button
            onClick={load}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Monitor My Contracts
          </button>
        </div>
      )}
      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>📋 Analysing contracts…</div>
      )}
      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && (
        <div>
          {contracts.length === 0 ? (
            <div style={{ textAlign: "center", padding: "24px 0" }}>
              <div style={{ color: textSecondary, marginBottom: 8 }}>No contracts found.</div>
              <div style={{ fontSize: 12, color: "#6B7280" }}>Upload a contract under Settings to begin monitoring.</div>
            </div>
          ) : (
            <>
              {totalUnderpaid > 0 && (
                <div style={{ background: "#491A03", border: "1px solid #92400E", borderRadius: 8, padding: 12, marginBottom: 16, textAlign: "center" }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: "#F87171" }}>
                    ${totalUnderpaid.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </div>
                  <div style={{ fontSize: 12, color: "#FDE68A" }}>Total cumulative underpayment across all contracts</div>
                </div>
              )}

              {contracts.map((c) => (
                <div key={c.contract_id} style={{ marginBottom: 8, border: "1px solid #2D2D4E", borderRadius: 8, overflow: "hidden" }}>
                  <div
                    style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", cursor: "pointer", background: "#111827" }}
                    onClick={() => setExpanded(expanded === c.contract_id ? null : c.contract_id)}
                  >
                    <div
                      style={{
                        width: 10, height: 10, borderRadius: "50%",
                        background: classColor(c.classification), flexShrink: 0,
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>{c.payer_name}</div>
                      <span style={{
                        color: classColor(c.classification), fontSize: 11,
                      }}>
                        {c.classification.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div style={{ textAlign: "right", flexShrink: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: c.current_drift_pct > 5 ? "#F87171" : "#FCD34D" }}>
                        −{c.current_drift_pct.toFixed(1)}%
                      </div>
                      <div style={{ fontSize: 11, color: textSecondary }}>{trendIcon(c.drift_trend)} {c.drift_trend}</div>
                    </div>
                    <span style={{ color: textSecondary, fontSize: 12 }}>{expanded === c.contract_id ? "▲" : "▼"}</span>
                  </div>

                  {expanded === c.contract_id && (
                    <div style={{ background: "#0F172A", padding: "10px 14px" }}>
                      <DriftSparkline data={c.quarterly_timeline} />
                      <div style={{ display: "flex", gap: 16, fontSize: 11, marginTop: 6 }}>
                        <span style={{ color: amber }}>── Contracted</span>
                        <span style={{ color: "#60A5FA" }}>── Actual</span>
                      </div>
                      <div style={{ marginTop: 8, fontSize: 12, color: textSecondary }}>
                        Cumulative underpayment:{" "}
                        <span style={{ color: "#F87171", fontWeight: 700 }}>
                          ${c.cumulative_underpayment.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </span>
                      </div>
                      {(c.classification === "BREACH_RISK" || c.classification === "HARD_DRIFT") && (
                        <button
                          onClick={() => initiateDispute(c.contract_id)}
                          disabled={disputing === c.contract_id}
                          style={{
                            marginTop: 10, background: "#7F1D1D", color: "#FCA5A5",
                            border: "1px solid #991B1B", borderRadius: 6, padding: "6px 14px",
                            fontSize: 12, cursor: "pointer",
                          }}
                        >
                          {disputing === c.contract_id ? "Filing…" : "Initiate Dispute"}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
