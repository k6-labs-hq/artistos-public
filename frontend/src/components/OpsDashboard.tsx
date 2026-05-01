import { useEffect, useMemo, useState } from "react";

import { ErrorBoundary } from "./ErrorBoundary";

type ClaimRow = {
  claim_id: string;
  artist_id: string;
  artist_name: string | null;
  payer_name: string | null;
  status: string;
  anomaly_subtype: string | null;
  estimated_recoverable: number | null;
  sol_days_remaining: number | null;
  communications_count: number;
  last_communication_at: string | null;
  created_at: string | null;
  proof_submitted_at: string | null;
};

type QueueResponse = {
  total: number;
  items: ClaimRow[];
};

type FilingResult = {
  success: boolean;
  message_id?: string | null;
  error?: string | null;
  stubbed?: boolean;
  payer_id?: string | null;
};

const STORAGE_ADMIN_KEY = "xr7-ops-admin-key";

const TABS: { label: string; status: string | null }[] = [
  { label: "All", status: null },
  { label: "Ready to file", status: "PREPARED" },
  { label: "Filed (awaiting reply)", status: "FILED" },
  { label: "In review", status: "IN_REVIEW" },
];

const basePath = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function fmtCurrency(n: number | null): string {
  if (n === null || n === undefined) return "—";
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function solBadge(days: number | null): { label: string; tone: string } {
  if (days === null) return { label: "—", tone: "muted" };
  if (days < 0) return { label: `Expired ${Math.abs(days)}d ago`, tone: "danger" };
  if (days <= 30) return { label: `${days}d left`, tone: "danger" };
  if (days <= 90) return { label: `${days}d left`, tone: "warn" };
  return { label: `${days}d left`, tone: "ok" };
}

export function OpsDashboard() {
  const [adminKey, setAdminKey] = useState("");
  const [activeTab, setActiveTab] = useState(0);
  const [rows, setRows] = useState<ClaimRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filingClaimId, setFilingClaimId] = useState<string | null>(null);
  const [previewingClaimId, setPreviewingClaimId] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<{ claim_id: string; result: FilingResult } | null>(
    null,
  );

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_ADMIN_KEY);
    if (saved) setAdminKey(saved);
  }, []);

  useEffect(() => {
    if (adminKey) window.localStorage.setItem(STORAGE_ADMIN_KEY, adminKey);
  }, [adminKey]);

  const headers = useMemo(() => ({ "X-Admin-Key": adminKey }), [adminKey]);

  const loadQueue = async () => {
    if (!adminKey.trim()) {
      setError("Admin key is required.");
      return;
    }
    setLoading(true);
    setError("");
    const params = new URLSearchParams();
    const status = TABS[activeTab]?.status;
    if (status) params.set("status", status);
    params.set("limit", "200");
    try {
      const res = await fetch(`${basePath}/admin/claims/queue?${params}`, { headers });
      const payload = (await res.json()) as QueueResponse | { detail?: string };
      if (!res.ok) {
        setRows([]);
        setTotal(0);
        setError((payload as { detail?: string }).detail || `Request failed (${res.status}).`);
        return;
      }
      const result = payload as QueueResponse;
      setRows(result.items || []);
      setTotal(result.total || 0);
    } catch (e) {
      setRows([]);
      setTotal(0);
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const previewPacket = async (claimId: string) => {
    if (!adminKey.trim()) {
      setError("Admin key is required.");
      return;
    }
    setPreviewingClaimId(claimId);
    setError("");
    try {
      const res = await fetch(`${basePath}/admin/claims/${claimId}/evidence.pdf`, { headers });
      if (!res.ok) {
        const text = await res.text();
        setError(`Preview failed (${res.status}): ${text.slice(0, 200)}`);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener");
      // Revoke after a delay so the new tab has time to load it.
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (e) {
      setError(String(e));
    } finally {
      setPreviewingClaimId(null);
    }
  };

  const fileClaim = async (claimId: string) => {
    if (!adminKey.trim()) {
      setError("Admin key is required.");
      return;
    }
    if (!window.confirm(`File claim ${claimId} via email? This sends a real dispute to the payer.`)) {
      return;
    }
    setFilingClaimId(claimId);
    setError("");
    setLastResult(null);
    try {
      const res = await fetch(`${basePath}/admin/claims/${claimId}/file-via-email`, {
        method: "POST",
        headers,
      });
      const result = (await res.json()) as FilingResult;
      setLastResult({ claim_id: claimId, result });
      if (!res.ok || !result.success) {
        setError(result.error || `Filing failed (${res.status}).`);
      } else {
        await loadQueue();
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setFilingClaimId(null);
    }
  };

  const counts = useMemo(() => {
    const byStatus: Record<string, number> = {};
    rows.forEach((r) => {
      byStatus[r.status] = (byStatus[r.status] || 0) + 1;
    });
    return byStatus;
  }, [rows]);

  return (
    <ErrorBoundary name="OpsDashboard">
      <main style={styles.page}>
        <section style={styles.shell}>
          <header style={styles.header}>
            <p style={styles.eyebrow}>K6 Labs · Operator Console</p>
            <h1 style={styles.h1}>Filing Queue</h1>
            <p style={styles.lede}>
              Cross-artist claim queue. Click <strong>File via email</strong> to send the dispute
              packet to the payer. Real action — not a preview.
            </p>
          </header>

          <section style={styles.card}>
            <div style={styles.row}>
              <label style={styles.field}>
                <span style={styles.fieldLabel}>Admin key</span>
                <input
                  type="password"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  placeholder="X-Admin-Key"
                  style={styles.input}
                  autoComplete="current-password"
                />
              </label>
              <button
                type="button"
                onClick={loadQueue}
                disabled={loading || !adminKey.trim()}
                style={{ ...styles.button, ...styles.buttonPrimary }}
              >
                {loading ? "Loading…" : "Load queue"}
              </button>
            </div>
            {error ? <p style={styles.error}>{error}</p> : null}
          </section>

          <section style={styles.card}>
            <div style={styles.tabs}>
              {TABS.map((tab, i) => (
                <button
                  key={tab.label}
                  type="button"
                  onClick={() => setActiveTab(i)}
                  style={{
                    ...styles.tab,
                    ...(i === activeTab ? styles.tabActive : {}),
                  }}
                >
                  {tab.label}
                  {tab.status && counts[tab.status] !== undefined ? (
                    <span style={styles.tabCount}>{counts[tab.status]}</span>
                  ) : null}
                </button>
              ))}
            </div>

            <div style={styles.summary}>
              {total} claim{total === 1 ? "" : "s"} loaded
            </div>

            {rows.length ? (
              <div style={styles.tableWrap}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Artist</th>
                      <th style={styles.th}>Payer</th>
                      <th style={styles.th}>Anomaly</th>
                      <th style={styles.thRight}>Est. recoverable</th>
                      <th style={styles.th}>SOL</th>
                      <th style={styles.th}>Status</th>
                      <th style={styles.th}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => {
                      const sol = solBadge(r.sol_days_remaining);
                      const canFile = r.status === "PREPARED";
                      return (
                        <tr key={r.claim_id} style={styles.tr}>
                          <td style={styles.td}>
                            <strong>{r.artist_name || r.artist_id}</strong>
                            <div style={styles.subtle}>{r.claim_id}</div>
                          </td>
                          <td style={styles.td}>{r.payer_name || "—"}</td>
                          <td style={styles.td}>{r.anomaly_subtype || "—"}</td>
                          <td style={styles.tdRight}>{fmtCurrency(r.estimated_recoverable)}</td>
                          <td style={styles.td}>
                            <span style={{ ...styles.badge, ...badgeTone(sol.tone) }}>
                              {sol.label}
                            </span>
                          </td>
                          <td style={styles.td}>
                            <span style={{ ...styles.badge, ...statusTone(r.status) }}>
                              {r.status}
                            </span>
                            {r.communications_count > 0 ? (
                              <div style={styles.subtle}>{r.communications_count} comm</div>
                            ) : null}
                          </td>
                          <td style={styles.td}>
                            <div style={styles.actions}>
                              <button
                                type="button"
                                onClick={() => previewPacket(r.claim_id)}
                                disabled={previewingClaimId === r.claim_id}
                                style={{ ...styles.button, ...styles.buttonGhost }}
                                title="Open the rendered evidence packet PDF in a new tab"
                              >
                                {previewingClaimId === r.claim_id ? "Loading…" : "Preview"}
                              </button>
                              <button
                                type="button"
                                onClick={() => fileClaim(r.claim_id)}
                                disabled={!canFile || filingClaimId === r.claim_id}
                                style={{
                                  ...styles.button,
                                  ...(canFile ? styles.buttonPrimary : styles.buttonDisabled),
                                }}
                                title={
                                  canFile
                                    ? "Send dispute email to payer"
                                    : "Only PREPARED claims can be filed"
                                }
                              >
                                {filingClaimId === r.claim_id ? "Filing…" : "File via email"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p style={styles.empty}>
                {loading
                  ? "Loading…"
                  : adminKey.trim()
                    ? "No claims to show. Click Load queue."
                    : "Enter the admin key to begin."}
              </p>
            )}

            {lastResult ? (
              <div
                style={{
                  ...styles.resultBox,
                  ...(lastResult.result.success ? styles.resultOk : styles.resultErr),
                }}
              >
                <strong>
                  {lastResult.result.success ? "Filed" : "Failed"}: {lastResult.claim_id}
                </strong>
                {lastResult.result.message_id ? (
                  <div style={styles.subtle}>MessageID: {lastResult.result.message_id}</div>
                ) : null}
                {lastResult.result.stubbed ? (
                  <div style={styles.subtle}>(stub — POSTMARK_API_TOKEN not set)</div>
                ) : null}
                {lastResult.result.error ? <div>{lastResult.result.error}</div> : null}
              </div>
            ) : null}
          </section>
        </section>
      </main>
    </ErrorBoundary>
  );
}

function badgeTone(tone: string): React.CSSProperties {
  switch (tone) {
    case "danger":
      return { background: "#3a1414", color: "#ff8585" };
    case "warn":
      return { background: "#3a2a14", color: "#f5b870" };
    case "ok":
      return { background: "#143a1f", color: "#7be3a3" };
    default:
      return { background: "#222", color: "#999" };
  }
}

function statusTone(status: string): React.CSSProperties {
  switch (status) {
    case "PREPARED":
      return { background: "#142a3a", color: "#7bb3e3" };
    case "FILED":
    case "SUBMITTED":
      return { background: "#3a2a14", color: "#f5b870" };
    case "IN_REVIEW":
      return { background: "#2a143a", color: "#c885ff" };
    case "ACCEPTED":
    case "FUNDS_RECEIVED":
    case "PAID":
      return { background: "#143a1f", color: "#7be3a3" };
    default:
      return { background: "#222", color: "#aaa" };
  }
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    background: "#0b0b10",
    color: "#e8e8ee",
    fontFamily: "system-ui, -apple-system, sans-serif",
    padding: "32px 24px",
  },
  shell: { maxWidth: 1280, margin: "0 auto" },
  header: { marginBottom: 24 },
  eyebrow: { color: "#a87bff", fontSize: 12, textTransform: "uppercase", letterSpacing: 1.5, margin: 0 },
  h1: { fontSize: 32, margin: "8px 0 4px", fontWeight: 700 },
  lede: { color: "#aaa", margin: 0, fontSize: 14 },
  card: {
    background: "#15151c",
    border: "1px solid #25252e",
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  row: { display: "flex", gap: 12, alignItems: "flex-end" },
  field: { display: "flex", flexDirection: "column", flex: 1 },
  fieldLabel: { fontSize: 12, color: "#aaa", marginBottom: 4 },
  input: {
    background: "#0b0b10",
    border: "1px solid #2a2a35",
    borderRadius: 6,
    padding: "8px 12px",
    color: "#e8e8ee",
    fontSize: 14,
  },
  button: {
    padding: "8px 16px",
    borderRadius: 6,
    border: "1px solid #2a2a35",
    background: "#1f1f28",
    color: "#e8e8ee",
    fontSize: 14,
    cursor: "pointer",
  },
  buttonPrimary: { background: "#6520BD", borderColor: "#6520BD", color: "#fff" },
  buttonGhost: { background: "transparent" },
  buttonDisabled: { opacity: 0.4, cursor: "not-allowed" },
  actions: { display: "flex", gap: 6 },
  error: { color: "#ff8585", marginTop: 12, fontSize: 13 },
  tabs: { display: "flex", gap: 4, marginBottom: 16, flexWrap: "wrap" },
  tab: {
    padding: "8px 14px",
    borderRadius: 6,
    border: "1px solid transparent",
    background: "transparent",
    color: "#aaa",
    fontSize: 13,
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
  },
  tabActive: { background: "#1f1f28", borderColor: "#2a2a35", color: "#e8e8ee" },
  tabCount: {
    background: "#2a2a35",
    color: "#e8e8ee",
    padding: "1px 7px",
    borderRadius: 10,
    fontSize: 11,
  },
  summary: { fontSize: 12, color: "#777", marginBottom: 12 },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 13 },
  th: {
    textAlign: "left",
    padding: "10px 12px",
    borderBottom: "1px solid #25252e",
    color: "#aaa",
    fontWeight: 500,
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  thRight: {
    textAlign: "right",
    padding: "10px 12px",
    borderBottom: "1px solid #25252e",
    color: "#aaa",
    fontWeight: 500,
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  tr: { borderBottom: "1px solid #1d1d25" },
  td: { padding: "12px", verticalAlign: "top" },
  tdRight: { padding: "12px", textAlign: "right", verticalAlign: "top" },
  subtle: { color: "#666", fontSize: 11, marginTop: 2 },
  badge: {
    display: "inline-block",
    padding: "3px 8px",
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
  },
  empty: { color: "#666", fontSize: 13, padding: "20px 0", textAlign: "center" },
  resultBox: {
    marginTop: 16,
    padding: 12,
    borderRadius: 6,
    fontSize: 13,
  },
  resultOk: { background: "#0e2918", border: "1px solid #1a4a2c", color: "#7be3a3" },
  resultErr: { background: "#291414", border: "1px solid #4a1a1a", color: "#ff8585" },
};
