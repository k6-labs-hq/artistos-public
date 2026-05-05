import { Fragment, useEffect, useMemo, useState } from "react";

import { getXR7Token } from "../lib/supabase";
import { ErrorBoundary } from "./ErrorBoundary";

type Me = {
  role?: string | null;
  admin_email?: string | null;
  artist_email?: string | null;
};

type Communication = {
  direction?: string;
  message_id?: string | null;
  channel?: string | null;
  payer_id?: string | null;
  submission_address?: string | null;
  stubbed?: boolean;
  timestamp?: string | null;
  artist_id?: string | null;
  in_reply_to?: string | null;
  from_address?: string | null;
  subject?: string | null;
  body_excerpt?: string | null;
  received_at?: string | null;
};

type ClaimRow = {
  claim_id: string;
  reference_number: string | null;
  artist_id: string;
  artist_name: string | null;
  payer_name: string | null;
  status: string;
  anomaly_subtype: string | null;
  estimated_recoverable: number | null;
  sol_days_remaining: number | null;
  communications_count: number;
  last_communication_at: string | null;
  communications: Communication[];
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
  const [me, setMe] = useState<Me | null>(null);
  const [authChecking, setAuthChecking] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [rows, setRows] = useState<ClaimRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filingClaimId, setFilingClaimId] = useState<string | null>(null);
  const [previewingClaimId, setPreviewingClaimId] = useState<string | null>(null);
  const [expandedClaimId, setExpandedClaimId] = useState<string | null>(null);
  const [remittanceClaimId, setRemittanceClaimId] = useState<string | null>(null);
  const [remittanceForm, setRemittanceForm] = useState({
    gross_amount: "",
    remittance_method: "ach",
    reference_number: "",
  });
  const [submittingRemittance, setSubmittingRemittance] = useState(false);
  const [lastResult, setLastResult] = useState<{
    claim_id: string;
    reference: string;
    result: FilingResult;
  } | null>(null);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_ADMIN_KEY);
    if (saved) setAdminKey(saved);
  }, []);

  useEffect(() => {
    if (adminKey) window.localStorage.setItem(STORAGE_ADMIN_KEY, adminKey);
  }, [adminKey]);

  // On mount, check whether we have a Supabase-issued admin JWT. If yes,
  // we use Bearer auth and hide the admin-key field. If no JWT or the
  // JWT is for an artist, we fall back to the X-Admin-Key flow.
  useEffect(() => {
    const token = getXR7Token();
    if (!token) {
      setAuthChecking(false);
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${basePath}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const body = (await res.json()) as Me;
          setMe(body);
        }
      } catch {
        // Ignore — fall back to admin-key flow.
      } finally {
        setAuthChecking(false);
      }
    })();
  }, []);

  const isJwtAdmin = me?.role === "admin";

  const headers = useMemo<Record<string, string>>(() => {
    const token = getXR7Token();
    const h: Record<string, string> = {};
    if (isJwtAdmin && token) {
      h.Authorization = `Bearer ${token}`;
    } else {
      h["X-Admin-Key"] = adminKey;
    }
    return h;
  }, [adminKey, isJwtAdmin]);

  const isAuthed = isJwtAdmin || adminKey.trim().length > 0;

  const loadQueue = async () => {
    if (!isAuthed) {
      setError("Admin auth required — sign in or paste an admin key.");
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
    if (!isAuthed) {
      setError("Admin auth required — sign in or paste an admin key.");
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

  const submitRemittance = async (claimId: string) => {
    if (!isAuthed) {
      setError("Admin auth required — sign in or paste an admin key.");
      return;
    }
    const amount = parseFloat(remittanceForm.gross_amount);
    if (!amount || amount <= 0) {
      setError("Gross amount must be a positive number.");
      return;
    }
    if (!remittanceForm.reference_number.trim()) {
      setError("Reference number is required.");
      return;
    }
    setSubmittingRemittance(true);
    setError("");
    try {
      const res = await fetch(`${basePath}/admin/claims/${claimId}/record-remittance`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          gross_amount: amount,
          remittance_method: remittanceForm.remittance_method,
          reference_number: remittanceForm.reference_number.trim(),
        }),
      });
      const payload = await res.json();
      if (!res.ok) {
        setError(payload.detail || `Failed (${res.status}).`);
        return;
      }
      setRemittanceClaimId(null);
      setRemittanceForm({ gross_amount: "", remittance_method: "ach", reference_number: "" });
      await loadQueue();
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmittingRemittance(false);
    }
  };

  const fileClaim = async (claimId: string, reference: string) => {
    if (!isAuthed) {
      setError("Admin auth required — sign in or paste an admin key.");
      return;
    }
    if (!window.confirm(`File ${reference} via email? This sends a real dispute to the payer.`)) {
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
      setLastResult({ claim_id: claimId, reference, result });
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
            {authChecking ? (
              <p style={styles.subtle}>Checking session…</p>
            ) : isJwtAdmin ? (
              <div style={styles.row}>
                <div style={styles.field}>
                  <span style={styles.fieldLabel}>Signed in</span>
                  <div>
                    <strong>{me?.admin_email || "(admin)"}</strong>{" "}
                    <span style={styles.subtle}>· role: admin</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={loadQueue}
                  disabled={loading}
                  style={{ ...styles.button, ...styles.buttonPrimary }}
                >
                  {loading ? "Loading…" : "Load queue"}
                </button>
              </div>
            ) : (
              <div style={styles.row}>
                <label style={styles.field}>
                  <span style={styles.fieldLabel}>Admin key (fallback)</span>
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
            )}
            {!authChecking && !isJwtAdmin ? (
              <p style={styles.subtle}>
                Sign in via <a href="/login" style={{ color: "#a87bff" }}>/login</a> with an admin
                email (in <code>XR7_ADMIN_USER_EMAILS</code>) to authenticate via Supabase instead
                of pasting a key.
              </p>
            ) : null}
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
                      <th style={styles.th}></th>
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
                      const isExpanded = expandedClaimId === r.claim_id;
                      const hasComms = (r.communications?.length || 0) > 0;
                      return (
                        <Fragment key={r.claim_id}>
                        <tr style={styles.tr}>
                          <td style={styles.tdToggle}>
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedClaimId(isExpanded ? null : r.claim_id)
                              }
                              disabled={!hasComms}
                              style={{
                                ...styles.expandBtn,
                                ...(hasComms ? {} : styles.buttonDisabled),
                              }}
                              title={
                                hasComms
                                  ? `Show ${r.communications_count} message(s)`
                                  : "No communications yet"
                              }
                            >
                              {isExpanded ? "▾" : "▸"}
                            </button>
                          </td>
                          <td style={styles.td}>
                            <strong>{r.artist_name || r.artist_id}</strong>
                            <div style={styles.subtle}>{r.reference_number || r.claim_id}</div>
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
                                onClick={() => fileClaim(r.claim_id, r.reference_number || r.claim_id)}
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
                              {["FILED", "IN_REVIEW", "ACCEPTED"].includes(r.status) ? (
                                <button
                                  type="button"
                                  onClick={() =>
                                    setRemittanceClaimId(
                                      remittanceClaimId === r.claim_id ? null : r.claim_id,
                                    )
                                  }
                                  style={{ ...styles.button, ...styles.buttonGhost }}
                                  title="Record remittance from payer"
                                >
                                  Record remittance
                                </button>
                              ) : null}
                            </div>
                          </td>
                        </tr>
                        {remittanceClaimId === r.claim_id ? (
                          <tr style={styles.tr}>
                            <td></td>
                            <td colSpan={7} style={styles.tdExpanded}>
                              <RemittanceForm
                                form={remittanceForm}
                                setForm={setRemittanceForm}
                                onSubmit={() => submitRemittance(r.claim_id)}
                                onCancel={() => setRemittanceClaimId(null)}
                                submitting={submittingRemittance}
                              />
                            </td>
                          </tr>
                        ) : null}
                        {isExpanded && hasComms ? (
                          <tr style={styles.tr}>
                            <td></td>
                            <td colSpan={7} style={styles.tdExpanded}>
                              <CommsTimeline comms={r.communications} />
                            </td>
                          </tr>
                        ) : null}
                        </Fragment>
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
                  {lastResult.result.success ? "Filed" : "Failed"}: {lastResult.reference}
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

function RemittanceForm({
  form,
  setForm,
  onSubmit,
  onCancel,
  submitting,
}: {
  form: { gross_amount: string; remittance_method: string; reference_number: string };
  setForm: (f: { gross_amount: string; remittance_method: string; reference_number: string }) => void;
  onSubmit: () => void;
  onCancel: () => void;
  submitting: boolean;
}) {
  return (
    <div style={styles.remittanceBox}>
      <div style={styles.remittanceTitle}>Record remittance from payer</div>
      <div style={styles.remittanceGrid}>
        <label style={styles.field}>
          <span style={styles.fieldLabel}>Gross amount (USD)</span>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={form.gross_amount}
            onChange={(e) => setForm({ ...form, gross_amount: e.target.value })}
            style={styles.input}
            placeholder="6120.00"
          />
        </label>
        <label style={styles.field}>
          <span style={styles.fieldLabel}>Method</span>
          <select
            value={form.remittance_method}
            onChange={(e) => setForm({ ...form, remittance_method: e.target.value })}
            style={styles.input}
          >
            <option value="ach">ACH</option>
            <option value="wire">Wire</option>
            <option value="check">Check</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label style={styles.field}>
          <span style={styles.fieldLabel}>Reference number</span>
          <input
            type="text"
            value={form.reference_number}
            onChange={(e) => setForm({ ...form, reference_number: e.target.value })}
            style={styles.input}
            placeholder="BMI-2026-04-DR-12345"
          />
        </label>
      </div>
      <div style={styles.remittanceActions}>
        <button
          type="button"
          onClick={onSubmit}
          disabled={submitting}
          style={{ ...styles.button, ...styles.buttonPrimary }}
        >
          {submitting ? "Saving…" : "Save remittance"}
        </button>
        <button type="button" onClick={onCancel} style={{ ...styles.button, ...styles.buttonGhost }}>
          Cancel
        </button>
      </div>
      <p style={styles.remittanceMeta}>
        Advances claim to FUNDS_RECEIVED, computes platform fee + artist net, and writes the
        immutable ledger entry. Trolley payout to the artist remains a separate manual step.
      </p>
    </div>
  );
}

function CommsTimeline({ comms }: { comms: Communication[] }) {
  return (
    <ol style={styles.timeline}>
      {comms.map((c, i) => {
        const inbound = c.direction === "inbound";
        const ts = c.received_at || c.timestamp || "";
        return (
          <li key={`${c.message_id || i}-${i}`} style={styles.timelineItem}>
            <div style={styles.timelineHead}>
              <span
                style={{
                  ...styles.badge,
                  ...(inbound
                    ? { background: "#2a143a", color: "#c885ff" }
                    : { background: "#142a3a", color: "#7bb3e3" }),
                }}
              >
                {inbound ? "← Inbound" : "Outbound →"}
              </span>
              <span style={styles.timelineTime}>{ts ? new Date(ts).toLocaleString() : "—"}</span>
              {c.stubbed ? <span style={styles.timelineMeta}>(stub)</span> : null}
            </div>
            {inbound ? (
              <>
                <div style={styles.timelineMeta}>From: {c.from_address || "—"}</div>
                {c.subject ? (
                  <div style={styles.timelineSubject}>{c.subject}</div>
                ) : null}
                {c.body_excerpt ? (
                  <pre style={styles.timelineBody}>{c.body_excerpt}</pre>
                ) : null}
                {c.in_reply_to ? (
                  <div style={styles.timelineMeta}>In-Reply-To: {c.in_reply_to}</div>
                ) : null}
              </>
            ) : (
              <>
                <div style={styles.timelineMeta}>
                  To: {c.submission_address || c.payer_id || "—"} · channel: {c.channel || "email"}
                </div>
                {c.message_id ? (
                  <div style={styles.timelineMeta}>MessageID: {c.message_id}</div>
                ) : null}
              </>
            )}
          </li>
        );
      })}
    </ol>
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
  tdToggle: { padding: "12px 4px 12px 12px", verticalAlign: "top", width: 32 },
  tdExpanded: { padding: "0 12px 16px", background: "#101019" },
  expandBtn: {
    width: 22,
    height: 22,
    padding: 0,
    borderRadius: 4,
    border: "1px solid #2a2a35",
    background: "#1f1f28",
    color: "#aaa",
    fontSize: 11,
    cursor: "pointer",
    lineHeight: "20px",
    textAlign: "center",
  },
  timeline: { listStyle: "none", padding: 0, margin: 0, fontSize: 12 },
  timelineItem: {
    padding: "10px 12px",
    borderLeft: "2px solid #2a2a35",
    marginLeft: 8,
    marginBottom: 8,
    background: "#15151c",
    borderRadius: "0 6px 6px 0",
  },
  timelineHead: { display: "flex", alignItems: "center", gap: 8, marginBottom: 4 },
  timelineTime: { color: "#aaa", fontSize: 11 },
  timelineMeta: { color: "#888", fontSize: 11, margin: "2px 0" },
  timelineSubject: { color: "#e8e8ee", fontWeight: 600, margin: "4px 0" },
  remittanceBox: { padding: "12px 0" },
  remittanceTitle: { fontWeight: 600, marginBottom: 8 },
  remittanceGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 12,
    marginBottom: 12,
  },
  remittanceActions: { display: "flex", gap: 8 },
  remittanceMeta: { color: "#888", fontSize: 11, marginTop: 8 },
  timelineBody: {
    background: "#0b0b10",
    border: "1px solid #25252e",
    borderRadius: 4,
    padding: 8,
    fontSize: 11,
    color: "#ddd",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    margin: "6px 0 0",
    maxHeight: 240,
    overflow: "auto",
  },
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
