import { useEffect, useRef, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Every unmatched royalty has a deadline. After that deadline, the society redistributes the money to other rights holders — and it's gone forever. This clock shows exactly how much time remains for each of your open anomalies before that window closes. Green means you have time. Amber means act soon. Red means act now. Critical means today.";

type Countdown = {
  anomaly_id: string;
  society: string;
  redistribution_deadline: string;
  days_remaining: number;
  hours_remaining: number;
  urgency_tier: "CRITICAL" | "RED" | "AMBER" | "GREEN" | "EXPIRED";
  is_expired: boolean;
  estimated_at_risk_value: number;
  description: string | null;
};

type Result = {
  countdowns: Countdown[];
  critical_count: number;
  at_risk_value_next_30_days: number;
  chain_of_custody_hash: string;
};

type Props = { artistId: string };

const TIER_COLORS: Record<string, string> = {
  CRITICAL: "#EF4444",
  RED: "#EF4444",
  AMBER: "#C89B3C",
  GREEN: "#10B981",
  EXPIRED: "#6B7280",
};

const TIER_BORDER: Record<string, string> = {
  CRITICAL: "2px solid #EF4444",
  RED: "2px solid #EF4444",
  AMBER: "2px solid #C89B3C",
  GREEN: "none",
  EXPIRED: "none",
};

function formatCountdown(hours: number): string {
  const d = Math.floor(hours / 24);
  const h = hours % 24;
  return `${d}d ${h}h`;
}

export function BlackBoxCountdownCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function load() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/anomalies/countdown`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  // Live timer refresh every minute
  useEffect(() => {
    if (state === "done") {
      intervalRef.current = setInterval(() => {
        setResult((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            countdowns: prev.countdowns.map((c) => ({
              ...c,
              hours_remaining: Math.max(0, c.hours_remaining - 1),
              days_remaining: Math.max(0, Math.floor((c.hours_remaining - 1) / 24)),
            })),
          };
        });
      }, 60_000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [state]);

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Black Box Countdown</span>
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
            See exactly how much time remains before each royalty is redistributed and gone forever.
          </p>
          <button
            type="button"
            aria-label="Show black-box countdown deadlines"
            onClick={load}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Show Countdown
          </button>
        </div>
      )}

      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>⏰ Loading deadlines…</div>
      )}
      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && result && (
        <div>
          {/* Summary banner */}
          <div style={{
            background: result.critical_count > 0 ? "#450A0A" : "#111827",
            border: result.critical_count > 0 ? "1px solid #EF4444" : "1px solid #1F2937",
            borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13,
          }}>
            <span style={{ color: result.critical_count > 0 ? "#F87171" : textSecondary }}>
              <strong>{result.critical_count}</strong> anomal{result.critical_count !== 1 ? "ies" : "y"} at critical risk ·&nbsp;
            </span>
            <span style={{ color: amber }}>
              <strong>${result.at_risk_value_next_30_days.toLocaleString()}</strong> at risk in the next 30 days
            </span>
          </div>

          {/* Countdown list */}
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {result.countdowns.map((c) => (
              <div
                key={c.anomaly_id}
                style={{
                  background: "#111827",
                  borderLeft: TIER_BORDER[c.urgency_tier] || "none",
                  borderRadius: 8,
                  padding: 12,
                  animation: c.urgency_tier === "CRITICAL" ? "pulse-red 1.5s infinite" : undefined,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{
                    background: TIER_COLORS[c.urgency_tier] + "22",
                    color: TIER_COLORS[c.urgency_tier],
                    borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700,
                  }}>
                    {c.urgency_tier}
                  </span>
                  <span style={{ color: TIER_COLORS[c.urgency_tier], fontWeight: 700, fontSize: 15 }}>
                    {c.is_expired ? "EXPIRED" : formatCountdown(c.hours_remaining)}
                  </span>
                </div>
                <div style={{ marginTop: 6, fontSize: 13, color: "#D1D5DB" }}>{c.society}</div>
                {c.description && (
                  <div style={{ fontSize: 12, color: textSecondary, marginTop: 2 }}>
                    {c.description.slice(0, 80)}…
                  </div>
                )}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
                  <span style={{ color: amber, fontWeight: 600, fontSize: 13 }}>
                    ${c.estimated_at_risk_value.toLocaleString()} at risk
                  </span>
                  <button
                    type="button"
                    aria-label={`Draft claim for anomaly ${c.anomaly_id}`}
                    style={{
                      background: "transparent", border: `1px solid ${TIER_COLORS[c.urgency_tier]}`,
                      color: TIER_COLORS[c.urgency_tier], borderRadius: 6, padding: "3px 10px",
                      fontSize: 12, cursor: "pointer",
                    }}
                    onClick={() => alert(`Drafting claim for anomaly ${c.anomaly_id}`)}
                  >
                    Draft Claim Now
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ fontSize: 11, color: "#6B7280", marginTop: 12 }}>
            Trust hash: {result.chain_of_custody_hash?.slice(0, 16)}… · Updates automatically every minute
          </div>
        </div>
      )}

      <style>{`
        @keyframes pulse-red {
          0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
          50% { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
        }
      `}</style>
    </div>
  );
}
