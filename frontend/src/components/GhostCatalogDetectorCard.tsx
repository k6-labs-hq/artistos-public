import { useState } from "react";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "This scan looks for works in your catalog that exist everywhere they should — registered with your PRO, live on streaming platforms — but have gone completely silent with zero dollars returned during periods when they should have been generating income. These aren't underpayments. They are works the system has completely forgotten about. Finding them is the first step to getting them paid.";

type GhostWork = {
  work_id: string;
  title: string;
  isrc: string | null;
  ghost_score: number;
  estimated_missing_value: number;
  ghost_start_date: string;
  suspected_cause: string;
  recommended_action: string;
  auto_escalate: boolean;
};

type Result = {
  ghost_works: GhostWork[];
  ghost_count: number;
  total_estimated_missing_value: number;
  chain_of_custody_hash: string;
};

type Props = { artistId: string };

const CAUSE_LABELS: Record<string, string> = {
  metadata_mismatch: "Metadata Mismatch",
  registration_gap: "Registration Gap",
  routing_failure: "Routing Failure",
  dsp_attribution_error: "DSP Attribution Error",
  unknown: "Unknown",
};

export function GhostCatalogDetectorCard({ artistId }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [tooltip, setTooltip] = useState(false);

  const amber = "#C89B3C";
  const textSecondary = "#9CA3AF";

  async function runScan() {
    setState("loading");
    try {
      const res = await fetch(`${BASE}/artists/${artistId}/catalog/ghost-scan`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
      setState("done");
    } catch (e) {
      setError(String(e));
      setState("error");
    }
  }

  function scoreColor(score: number) {
    if (score >= 0.85) return "#F87171";
    if (score >= 0.60) return "#FB923C";
    return amber;
  }

  return (
    <div style={{ background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 16 }}>Ghost Catalog Detector</span>
        {result && (
          <span style={{ background: "#F87171", color: "#fff", borderRadius: 999, padding: "2px 10px", fontSize: 12, fontWeight: 700 }}>
            {result.ghost_count} ghost{result.ghost_count !== 1 ? "s" : ""}
          </span>
        )}
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
            Scan for works present everywhere but paying nothing.
          </p>
          <button
            onClick={runScan}
            style={{ background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }}
          >
            Run Scan
          </button>
        </div>
      )}

      {state === "loading" && (
        <div style={{ textAlign: "center", padding: "24px 0", color: textSecondary }}>
          👻 Scanning your catalog for ghost works…
        </div>
      )}

      {state === "error" && <div style={{ color: "#F87171" }}>Error: {error}</div>}

      {state === "done" && result && (
        <div>
          <div style={{ background: "#111827", borderRadius: 8, padding: 12, marginBottom: 16, display: "flex", justifyContent: "space-between" }}>
            <span style={{ color: textSecondary, fontSize: 13 }}>Total missing value</span>
            <span style={{ color: amber, fontWeight: 700, fontSize: 18 }}>
              ${result.total_estimated_missing_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </span>
          </div>

          {result.ghost_works.length === 0 ? (
            <p style={{ color: textSecondary, textAlign: "center" }}>No ghost works detected. 👻</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {result.ghost_works.map((work) => (
                <div
                  key={work.work_id}
                  style={{
                    background: "#111827",
                    border: `1px solid ${work.auto_escalate ? "#F87171" : "#374151"}`,
                    borderRadius: 8,
                    padding: 12,
                    opacity: 0.9,
                    position: "relative",
                  }}
                >
                  {/* Ghost icon overlay for zero-income works */}
                  <div style={{ position: "absolute", top: 8, right: 10, opacity: 0.3, fontSize: 20 }}>👻</div>

                  <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#D1D5DB" }}>
                    {work.title}
                  </div>
                  {work.isrc && <div style={{ fontSize: 11, color: textSecondary }}>ISRC: {work.isrc}</div>}

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
                    {/* Ghost score */}
                    <span style={{
                      background: scoreColor(work.ghost_score) + "22",
                      color: scoreColor(work.ghost_score),
                      borderRadius: 4, padding: "2px 8px", fontSize: 11,
                    }}>
                      Score: {Math.round(work.ghost_score * 100)}%
                    </span>
                    {/* Cause */}
                    <span style={{ background: "#1F2937", color: textSecondary, borderRadius: 4, padding: "2px 8px", fontSize: 11 }}>
                      {CAUSE_LABELS[work.suspected_cause] || work.suspected_cause}
                    </span>
                    {/* Missing value */}
                    <span style={{ background: "#1F2937", color: amber, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700 }}>
                      ${work.estimated_missing_value.toLocaleString()}
                    </span>
                  </div>

                  <div style={{ fontSize: 12, color: "#6B7280", marginTop: 6 }}>
                    Silent since: {work.ghost_start_date.slice(0, 10)}
                  </div>

                  <button
                    style={{
                      marginTop: 10, background: "transparent", border: `1px solid ${amber}`,
                      color: amber, borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer",
                    }}
                    onClick={() => alert(`Draft claim for: ${work.title} — hands off to Claims Orchestration`)}
                  >
                    Draft Claim →
                  </button>
                </div>
              ))}
            </div>
          )}

          <div style={{ fontSize: 11, color: "#6B7280", marginTop: 12 }}>
            Trust hash: {result.chain_of_custody_hash?.slice(0, 16)}…
          </div>
        </div>
      )}
    </div>
  );
}
