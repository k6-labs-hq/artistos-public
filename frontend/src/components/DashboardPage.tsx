/**
 * Beta dashboard.
 *
 * Minimum surface for a signed-in beta user: identifies them, accepts terms
 * if not yet accepted, lets them upload a statement, lists detected
 * anomalies. Heavily restrained — anything richer (charts, claim filing,
 * payouts) is post-beta.
 */
import { Fragment, useCallback, useEffect, useState } from "react";

import { clearXR7Token, getXR7Token } from "../lib/supabase";
import {
  type Anomaly,
  type AnomalyEvidence,
  type Me,
  UnauthorizedError,
  xr7,
} from "../lib/xr7Client";

/**
 * Rendered when an artist has uploaded data but the engine has no findings to
 * surface. Empty state must NOT read as "engine broken" or "we couldn't find
 * any money" — both lie about the methodology. Instead, explain what we look
 * for, why silence is sometimes the honest answer, and what additional data
 * unlocks which rules. See the conversation around #209 for why this matters
 * to credibility.
 */
function EmptyAnomaliesGuidance() {
  const surfaces = [
    {
      title: "Cross-platform rate audits",
      detail:
        "Compare per-stream rates across DSPs and against industry baselines to surface tracks paid below market.",
      unlocks: "Multiple distributor months",
    },
    {
      title: "PRO retroactive analysis",
      detail:
        "Identify when a PRO (BMI/ASCAP/MLC) is delivering a high share of payments as retroactive corrections — a leading indicator of unrecovered current-period royalties.",
      unlocks: "A BMI / ASCAP / MLC quarterly statement",
    },
    {
      title: "Track-level rate outliers",
      detail:
        "Flag tracks earning materially below your catalog's median rate at the same platform.",
      unlocks: "4+ tracks with meaningful stream volume",
    },
    {
      title: "Missing-period detection",
      detail:
        "Detect months that have streaming activity but no corresponding royalty payment, after accounting for the typical 60–90 day distributor lag.",
      unlocks: "3+ months of statement history",
    },
    {
      title: "Below-threshold accruals",
      detail:
        "Surface royalties accrued but unpaid because they sit under a payer's distribution threshold (BMI's $2 minimum is the common one).",
      unlocks: "Your BMI Accrual Report PDF (coming soon)",
    },
  ];

  return (
    <div
      style={{
        padding: "24px",
        borderRadius: "16px",
        border: "1px solid rgba(168, 85, 247, 0.3)",
        background: "rgba(16, 16, 28, 0.6)",
      }}
    >
      <p style={{ marginTop: 0, opacity: 0.85 }}>
        No anomalies detected for the data you've uploaded so far. <strong>That's not the
        engine giving up — it's the honest answer for the data we have.</strong> Royalty
        recovery is fundamentally a cross-source, cross-period exercise. Below is what XR7
        looks for and what additional data unlocks each surface.
      </p>
      <ul style={{ listStyle: "none", padding: 0, margin: "16px 0 0 0" }}>
        {surfaces.map((s) => (
          <li
            key={s.title}
            style={{
              padding: "12px 0",
              borderTop: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: "16px" }}>
              <strong style={{ flex: 1 }}>{s.title}</strong>
              <span style={{ opacity: 0.6, fontSize: "0.85em", whiteSpace: "nowrap" }}>
                Unlocks with: {s.unlocks}
              </span>
            </div>
            <p style={{ margin: "4px 0 0 0", opacity: 0.8, fontSize: "0.95em" }}>{s.detail}</p>
          </li>
        ))}
      </ul>
      <p style={{ marginTop: "20px", marginBottom: 0, opacity: 0.7, fontSize: "0.9em" }}>
        Add another statement above to expand the audit surface.
      </p>
    </div>
  );
}

/**
 * Drill-down panel for a single anomaly. Rendered when the user expands a
 * row in the anomalies table. Three sections so the artist can self-verify
 * the figure before treating it as a real claim:
 *
 *   1. The rule that fired + the raw evidence dict the engine emitted.
 *   2. Aggregate counts of the source events + payments inside the anomaly's
 *      time window — i.e. the dataset the rule actually consumed.
 *   3. Sample rows from each side so the artist can spot-check that the
 *      activity looks real and the payments cover the right period.
 *
 * Designed to be readable, not pretty — this is a forensic surface, not a
 * marketing one.
 */
function fmtMoney(n: number | null | undefined): string {
  return `$${(n ?? 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/**
 * If the evidence dict carries an `unpaid_estimate`, return a one-liner
 * confirming it equals the recoverable. (We removed the prior 30%
 * recovery-likelihood discount — recoverable now equals unpaid until we
 * have settlement data to fit a real distribution.) Returns null when
 * the rule's evidence shape doesn't fit a derivation we know how to
 * explain — better to stay silent than invent a story.
 */
function evidenceHeadline(
  ev: Record<string, unknown>,
  recoverable: number | null,
): string | null {
  const unpaid = typeof ev.unpaid_estimate === "number" ? ev.unpaid_estimate : null;
  if (unpaid != null) {
    return `${fmtMoney(unpaid)} unpaid stream activity → ${fmtMoney(recoverable)} recoverable`;
  }
  return null;
}

function EvidencePanel({ evidence }: { evidence: AnomalyEvidence }) {
  const a = evidence.anomaly;
  const r = evidence.rule;
  const s = evidence.source_data;
  const cellStyle: React.CSSProperties = { padding: "6px 8px", verticalAlign: "top" };
  const headerStyle: React.CSSProperties = {
    ...cellStyle,
    fontSize: "11px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    color: "#94a3b8",
    fontWeight: 500,
  };
  const hasWindow = a.time_window_start != null || a.time_window_end != null;
  const hasExpectedActual =
    (a.expected_amount != null && a.expected_amount !== 0) ||
    (a.actual_amount != null && a.actual_amount !== 0);
  const headline = evidenceHeadline(r.evidence, a.estimated_recoverable);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div>
        <h4 style={{ margin: "0 0 8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px", color: "#a78bfa" }}>
          Rule + evidence
        </h4>
        {a.description ? (
          <p style={{ margin: "0 0 10px", fontSize: "13px" }}>{a.description}</p>
        ) : null}
        {headline ? (
          <p style={{ margin: "0 0 10px", fontSize: "13px", color: "#cbd5e1" }}>
            <strong>How we got to {fmtMoney(a.estimated_recoverable)}: </strong>
            {headline}
          </p>
        ) : null}
        <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "4px 16px", fontSize: "13px" }}>
          <div style={{ opacity: 0.7 }}>Rule</div>
          <div style={{ fontFamily: "monospace" }}>
            {r.rule_id ?? "—"}{r.rule_name ? ` — ${r.rule_name}` : ""}
          </div>
          {hasWindow ? (
            <>
              <div style={{ opacity: 0.7 }}>Time window</div>
              <div>
                {a.time_window_start ?? "—"} → {a.time_window_end ?? "—"}
                {a.territory ? ` (${a.territory})` : ""}
              </div>
            </>
          ) : a.territory ? (
            <>
              <div style={{ opacity: 0.7 }}>Territory</div>
              <div>{a.territory}</div>
            </>
          ) : null}
          {hasExpectedActual ? (
            <>
              <div style={{ opacity: 0.7 }}>Expected vs actual</div>
              <div>
                {fmtMoney(a.expected_amount)} expected, {fmtMoney(a.actual_amount)} observed
              </div>
            </>
          ) : null}
        </div>
        {Object.keys(r.evidence).length > 0 ? (
          <details style={{ marginTop: "10px" }}>
            <summary style={{ cursor: "pointer", fontSize: "12px", opacity: 0.7 }}>
              Raw evidence (rule output)
            </summary>
            <pre
              style={{
                marginTop: "8px",
                padding: "10px",
                background: "rgba(0,0,0,0.4)",
                borderRadius: "6px",
                fontSize: "12px",
                overflowX: "auto",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {JSON.stringify(r.evidence, null, 2)}
            </pre>
          </details>
        ) : null}
      </div>

      <div>
        <h4 style={{ margin: "0 0 8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px", color: "#a78bfa" }}>
          Source data in window
        </h4>
        <div style={{ fontSize: "13px", opacity: 0.85 }}>
          {s.events_count.toLocaleString()} events ({s.events_total_quantity.toLocaleString()} total units)
          {" · "}
          {s.payments_count.toLocaleString()} payments totaling $
          {s.payments_total_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>

      {s.sample_events.length > 0 ? (
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px", color: "#a78bfa" }}>
            Sample events (most recent 10)
          </h4>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", textAlign: "left" }}>
                <th style={headerStyle}>Date</th>
                <th style={headerStyle}>Platform</th>
                <th style={headerStyle}>Territory</th>
                <th style={headerStyle}>Work</th>
                <th style={{ ...headerStyle, textAlign: "right" }}>Qty</th>
                <th style={{ ...headerStyle, textAlign: "right" }}>Unit</th>
              </tr>
            </thead>
            <tbody>
              {s.sample_events.map((e) => (
                <tr key={e.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={cellStyle}>{e.timestamp?.slice(0, 10) ?? "—"}</td>
                  <td style={cellStyle}>{e.platform ?? "—"}</td>
                  <td style={cellStyle}>{e.territory ?? "—"}</td>
                  <td style={cellStyle}>{e.work_title ?? "—"}</td>
                  <td style={{ ...cellStyle, textAlign: "right" }}>{e.quantity.toLocaleString()}</td>
                  <td style={{ ...cellStyle, textAlign: "right", fontFamily: "monospace" }}>
                    {e.unit_value.toFixed(6)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {s.sample_payments.length > 0 ? (
        <div>
          <h4 style={{ margin: "0 0 8px", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px", color: "#a78bfa" }}>
            Sample payments (most recent 10)
          </h4>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", textAlign: "left" }}>
                <th style={headerStyle}>Received</th>
                <th style={headerStyle}>Source</th>
                <th style={headerStyle}>Period</th>
                <th style={headerStyle}>Reference</th>
                <th style={{ ...headerStyle, textAlign: "right" }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {s.sample_payments.map((p) => (
                <tr key={p.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <td style={cellStyle}>{p.received_at?.slice(0, 10) ?? "—"}</td>
                  <td style={cellStyle}>{p.source ?? "—"}</td>
                  <td style={cellStyle}>
                    {p.period_start?.slice(0, 10) ?? "—"} → {p.period_end?.slice(0, 10) ?? "—"}
                  </td>
                  <td style={{ ...cellStyle, fontFamily: "monospace", fontSize: "11px" }}>
                    {p.reference_id ?? "—"}
                  </td>
                  <td style={{ ...cellStyle, textAlign: "right" }}>
                    ${(p.amount ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}

type LoadState = "loading" | "ready" | "needs_terms" | "error";

// Accepted statement file extensions. Single source of truth shared by the
// native file input's `accept` attr, the picker onChange filter, and the
// drag-and-drop handler.
const ACCEPTED_UPLOAD_EXTENSIONS = [".csv", ".tsv", ".xlsx", ".numbers", ".pdf"] as const;

export function DashboardPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<{
    completed: number;
    total: number;
    processed: number;
    failed: number;
    duplicates: number;
  } | null>(null);
  const [statementHistory, setStatementHistory] = useState<
    Array<{
      id: string;
      filename: string;
      format_detected: string;
      events_created: number;
      payments_created: number;
      skipped_rows: number;
      status: string;
      error_summary: string | null;
      uploaded_at: string;
    }>
  >([]);
  const [termsText, setTermsText] = useState<string | null>(null);
  const [termsVersion, setTermsVersion] = useState<string | null>(null);
  const [termsLoading, setTermsLoading] = useState(false);
  const [termsAcknowledged, setTermsAcknowledged] = useState(false);
  const [expandedAnomalyId, setExpandedAnomalyId] = useState<string | null>(null);
  const [evidenceById, setEvidenceById] = useState<
    Record<string, { loading: boolean; error: string | null; data: AnomalyEvidence | null }>
  >({});

  const toggleEvidence = useCallback(
    async (anomalyId: string) => {
      if (expandedAnomalyId === anomalyId) {
        setExpandedAnomalyId(null);
        return;
      }
      setExpandedAnomalyId(anomalyId);
      if (evidenceById[anomalyId]?.data) return;
      if (!me?.artist_id) return;
      setEvidenceById((prev) => ({
        ...prev,
        [anomalyId]: { loading: true, error: null, data: null },
      }));
      try {
        const data = await xr7.getAnomalyEvidence(me.artist_id, anomalyId);
        setEvidenceById((prev) => ({
          ...prev,
          [anomalyId]: { loading: false, error: null, data },
        }));
      } catch (err) {
        if (err instanceof UnauthorizedError) return;
        setEvidenceById((prev) => ({
          ...prev,
          [anomalyId]: {
            loading: false,
            error: err instanceof Error ? err.message : String(err),
            data: null,
          },
        }));
      }
    },
    [expandedAnomalyId, evidenceById, me],
  );

  const refreshHistory = useCallback(async (artistId: string) => {
    try {
      const rows = await xr7.listStatements(artistId);
      setStatementHistory(rows);
    } catch {
      // Non-critical — history is informational; don't blow up the
      // whole dashboard if this fails.
    }
  }, []);

  const refreshAnomalies = useCallback(async (artistId: string) => {
    const rows = await xr7.listAnomalies(artistId);
    setAnomalies(rows);
  }, []);

  useEffect(() => {
    const token = getXR7Token();
    if (!token) {
      window.location.assign("/login");
      return;
    }
    (async () => {
      try {
        const meResp = await xr7.me();
        setMe(meResp);
        if (!meResp.artist_id) {
          throw new Error("Token has no artist_id; please sign in again.");
        }
        const terms = await xr7.getTermsStatus(meResp.artist_id);
        if (!terms.accepted) {
          setState("needs_terms");
          return;
        }
        await refreshAnomalies(meResp.artist_id); await refreshHistory(meResp.artist_id);
        setState("ready");
      } catch (err) {
        if (err instanceof UnauthorizedError) return;
        setError(err instanceof Error ? err.message : String(err));
        setState("error");
      }
    })();
  }, [refreshAnomalies, refreshHistory]);

  // Fetch the full Terms text once, when we transition into needs_terms.
  // Without this the screen had only a button — nothing to actually read.
  useEffect(() => {
    if (state !== "needs_terms" || termsText !== null) return;
    setTermsLoading(true);
    xr7
      .getTerms()
      .then((resp) => {
        setTermsText(resp.text);
        setTermsVersion(resp.version);
      })
      .catch((err) => {
        if (err instanceof UnauthorizedError) return;
        setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => setTermsLoading(false));
  }, [state, termsText]);

  const handleAcceptTerms = async () => {
    if (!me?.artist_id) return;
    setError(null);
    try {
      const terms = await xr7.getTermsStatus(me.artist_id);
      if (terms.pending_version) {
        await xr7.acceptTerms(me.artist_id, terms.pending_version);
      }
      await refreshAnomalies(me.artist_id); await refreshHistory(me.artist_id);
      setState("ready");
    } catch (err) {
      if (err instanceof UnauthorizedError) return;
      setError(err instanceof Error ? err.message : String(err));
      setState("error");
    }
  };

  // Shared between the file picker's onChange and the drag-and-drop
  // handler. Filters to accepted extensions and appends with name+size
  // dedup so re-adding the same file (picker then drop, or two drops)
  // doesn't double-stage it.
  const addFiles = useCallback((incoming: File[]) => {
    const accepted = incoming.filter((f) =>
      ACCEPTED_UPLOAD_EXTENSIONS.some((ext) => f.name.toLowerCase().endsWith(ext)),
    );
    setUploadFiles((prev) => {
      const seen = new Set(prev.map((f) => f.name + ":" + f.size));
      return [...prev, ...accepted.filter((f) => !seen.has(f.name + ":" + f.size))];
    });
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = Array.from(e.dataTransfer.files ?? []);
      addFiles(dropped);
      const rejected = dropped.filter(
        (f) => !ACCEPTED_UPLOAD_EXTENSIONS.some((ext) => f.name.toLowerCase().endsWith(ext)),
      );
      if (rejected.length > 0) {
        setError(
          `Skipped ${rejected.length} file(s) with unsupported type. ` +
            `Accepted: ${ACCEPTED_UPLOAD_EXTENSIONS.join(", ")}.`,
        );
      }
    },
    [addFiles],
  );

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!me?.artist_id || uploadFiles.length === 0) return;
    // Snapshot the staged list at submit time. Files added later (while this
    // upload is in flight) stay queued so the user can keep building the
    // next batch instead of being locked out until completion.
    const filesToUpload = uploadFiles;
    setUploading(true);
    setUploadResult(null);
    setUploadProgress(null);
    setError(null);
    try {
      if (filesToUpload.length === 1) {
        const onlyFile = filesToUpload[0];
        if (!onlyFile) return;
        const result = await xr7.uploadStatement(me.artist_id, onlyFile);
        setUploadResult(
          `Uploaded ${onlyFile.name} — format ${result.format_detected}, ` +
            `${result.events_created} events, ${result.payments_created} payments.`,
        );
      } else {
        // Smaller chunks (10/req) so the progress counter actually moves
        // for the user instead of staring at "Uploading…" for a minute on
        // a 79-file batch. Backend caps each batch at 100; 10 keeps each
        // round-trip fast and gives us 8 progress updates per 80 files.
        const CHUNK = 10;
        let processed = 0;
        let failed = 0;
        let duplicates = 0;
        const failedNames: string[] = [];
        setUploadProgress({
          completed: 0,
          total: filesToUpload.length,
          processed: 0,
          failed: 0,
          duplicates: 0,
        });
        for (let i = 0; i < filesToUpload.length; i += CHUNK) {
          const slice = filesToUpload.slice(i, i + CHUNK);
          const result = await xr7.uploadStatementBatch(me.artist_id, slice);
          processed += result.processed?.length || 0;
          failed += result.failed?.length || 0;
          duplicates += result.duplicates || 0;
          for (const f of (result.failed || []).slice(0, 5)) {
            if (failedNames.length < 5) {
              failedNames.push(`${f.filename}: ${f.error}`);
            }
          }
          setUploadProgress({
            completed: Math.min(i + CHUNK, filesToUpload.length),
            total: filesToUpload.length,
            processed,
            failed,
            duplicates,
          });
        }
        setUploadResult(
          `Uploaded ${filesToUpload.length} files: ${processed} processed, ` +
            `${duplicates} duplicates, ${failed} failed.` +
            (failedNames.length
              ? `\nFirst failures: ${failedNames.join("; ")}`
              : ""),
        );
      }
      // Only remove the snapshot's files. Anything the user staged while
      // the upload was running stays queued — drop by identity (name+size),
      // not by clearing wholesale.
      const uploadedKeys = new Set(filesToUpload.map((f) => f.name + ":" + f.size));
      setUploadFiles((prev) => prev.filter((f) => !uploadedKeys.has(f.name + ":" + f.size)));
      await refreshAnomalies(me.artist_id); await refreshHistory(me.artist_id);
    } catch (err) {
      if (err instanceof UnauthorizedError) return;
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  const handleSignOut = () => {
    clearXR7Token();
    window.location.assign("/");
  };

  if (state === "loading") {
    return (
      <div className="xr7-app">
        <main id="main-content" style={{ padding: "64px 24px", textAlign: "center" }}>
          <p>Loading your dashboard…</p>
        </main>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="xr7-app">
        <main id="main-content" style={{ padding: "64px 24px" }}>
          <h1>Something went wrong</h1>
          <p style={{ color: "#fca5a5" }}>{error}</p>
          <button type="button" className="cta" onClick={handleSignOut}>
            Sign out
          </button>
        </main>
      </div>
    );
  }

  return (
    <div className="xr7-app">
      <header className="site-nav" role="banner">
        <div className="nav-inner">
          <a className="brand" href="/dashboard" aria-label="XR7 dashboard">
            {/* Use the SVG (transparent) instead of the PNG (RGB w/ baked white background)
                so the dashboard's dark theme doesn't show a white card behind the logo. */}
            <img src="/xr7-logo-mark.svg" alt="XR7 logo" />
            <span>XR7</span>
          </a>
          <div className="nav-actions">
            <span style={{ marginRight: "12px", opacity: 0.85 }}>
              {me?.artist_name ?? me?.artist_email ?? "Signed in"}
            </span>
            <button type="button" className="cta small" onClick={handleSignOut}>
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main id="main-content" style={{ maxWidth: 920, margin: "0 auto", padding: "48px 24px" }}>
        <h1 style={{ marginBottom: "8px" }}>
          Welcome{me?.artist_name ? `, ${me.artist_name}` : ""}
        </h1>
        <p style={{ opacity: 0.8, marginTop: 0 }}>
          Upload a royalty statement and XR7 will detect underpayment anomalies in seconds.
        </p>

        {state === "needs_terms" ? (
          <section
            style={{
              marginTop: "32px",
              padding: "24px",
              borderRadius: "16px",
              border: "1px solid rgba(168, 85, 247, 0.3)",
              background: "rgba(16, 16, 28, 0.6)",
            }}
          >
            <h2 style={{ marginTop: 0 }}>Artist Recovery Services Agreement</h2>
            <p style={{ color: "#cbd5e1" }}>
              Please review the agreement below before continuing. By accepting, you grant XR7
              limited authority to file royalty audit findings on your behalf and acknowledge the
              12% contingency-fee compensation model.
              {termsVersion ? (
                <span style={{ display: "block", marginTop: "4px", fontSize: "12px", opacity: 0.7 }}>
                  Version {termsVersion}
                </span>
              ) : null}
            </p>
            <div
              style={{
                maxHeight: "420px",
                overflow: "auto",
                padding: "16px 20px",
                marginTop: "12px",
                background: "#0b0b14",
                border: "1px solid rgba(168, 85, 247, 0.2)",
                borderRadius: "8px",
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontSize: "13px",
                lineHeight: 1.55,
                color: "#e2e8f0",
                whiteSpace: "pre-wrap",
              }}
              tabIndex={0}
              aria-label="Artist Recovery Services Agreement text"
            >
              {termsLoading ? "Loading…" : termsText || "(Terms unavailable — please refresh.)"}
            </div>

            <label
              style={{
                display: "flex",
                gap: "8px",
                alignItems: "flex-start",
                marginTop: "16px",
                color: "#cbd5e1",
                fontSize: "14px",
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                checked={termsAcknowledged}
                onChange={(e) => setTermsAcknowledged(e.target.checked)}
                style={{ marginTop: "4px" }}
              />
              <span>
                I have read and understood the Artist Recovery Services Agreement above and agree
                to be bound by its terms, including the 12% contingency fee on Recovered Funds and
                the limited power of attorney described in Section 3.
              </span>
            </label>

            <button
              type="button"
              className="cta"
              onClick={handleAcceptTerms}
              disabled={!termsAcknowledged || termsLoading}
              style={{ marginTop: "16px" }}
            >
              I accept the agreement
            </button>
          </section>
        ) : null}

        {state === "ready" ? (
          <>
            <section
              style={{
                marginTop: "32px",
                padding: "24px",
                borderRadius: "16px",
                border: "1px solid rgba(168, 85, 247, 0.3)",
                background: "rgba(16, 16, 28, 0.6)",
              }}
            >
              <h2 style={{ marginTop: 0 }}>Upload a statement</h2>
              <p style={{ opacity: 0.8 }}>
                Accepted formats: CSV, TSV, XLSX, Numbers, PDF. BMI, MLC, ASCAP, DistroKid,
                TuneCore, and others are auto-detected — including MLC's native Apple Numbers
                exports and BMI Royalty Statement PDFs.
              </p>
              <form onSubmit={handleUpload}>
                {/*
                  Native file input is visually hidden — its default
                  "No file chosen" text is redundant given the staged-files
                  list below. The drop zone wraps the trigger <label> so a
                  click anywhere in the zone opens the picker, and the same
                  zone accepts drag-and-drop.
                */}
                <input
                  id="upload-files-input"
                  type="file"
                  multiple
                  accept={ACCEPTED_UPLOAD_EXTENSIONS.join(",")}
                  onChange={(e) => {
                    addFiles(Array.from(e.target.files ?? []));
                    // Clear the input so onChange fires again if the user
                    // re-picks the same file (otherwise the browser
                    // suppresses the change event for repeat selections).
                    e.target.value = "";
                  }}
                  aria-label="Royalty statement files"
                  style={{
                    position: "absolute",
                    width: "1px",
                    height: "1px",
                    padding: 0,
                    margin: "-1px",
                    overflow: "hidden",
                    clip: "rect(0, 0, 0, 0)",
                    border: 0,
                  }}
                />
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    if (!isDragging) setIsDragging(true);
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault();
                    setIsDragging(false);
                  }}
                  onDrop={handleDrop}
                  style={{
                    border: isDragging
                      ? "2px dashed rgba(168, 85, 247, 0.9)"
                      : "2px dashed rgba(168, 85, 247, 0.35)",
                    borderRadius: "10px",
                    padding: "24px 16px",
                    textAlign: "center",
                    background: isDragging
                      ? "rgba(168, 85, 247, 0.12)"
                      : "rgba(15, 23, 42, 0.4)",
                    transition: "background 120ms, border-color 120ms",
                  }}
                >
                  <label
                    htmlFor="upload-files-input"
                    className="cta"
                    style={{
                      display: "inline-block",
                      cursor: "pointer",
                      background: "transparent",
                      border: "1px solid rgba(168, 85, 247, 0.5)",
                    }}
                  >
                    Choose files…
                  </label>
                  <div style={{ marginTop: "8px", fontSize: "12px", color: "#94a3b8" }}>
                    or drag &amp; drop your statements here
                  </div>
                </div>
                <button
                  type="submit"
                  className="cta"
                  disabled={uploadFiles.length === 0 || uploading}
                  style={{ marginTop: "12px" }}
                >
                  {uploading
                    ? "Uploading…"
                    : uploadFiles.length > 1
                      ? `Upload ${uploadFiles.length} files`
                      : "Upload"}
                </button>
                {uploadFiles.length > 0 ? (
                  <div
                    style={{
                      marginTop: "12px",
                      padding: "10px 12px",
                      background: "rgba(15, 23, 42, 0.6)",
                      border: "1px solid rgba(168, 85, 247, 0.2)",
                      borderRadius: "6px",
                      maxHeight: "180px",
                      overflowY: "auto",
                      fontSize: "12px",
                      color: "#cbd5e1",
                    }}
                  >
                    <div style={{ marginBottom: "6px", fontSize: "11px", color: "#94a3b8" }}>
                      Staged for upload ({uploadFiles.length}):
                    </div>
                    {uploadFiles.map((f) => (
                      <div
                        key={`${f.name}:${f.size}`}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: "8px",
                          padding: "2px 0",
                        }}
                      >
                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {f.name}
                        </span>
                        <button
                          type="button"
                          onClick={() =>
                            setUploadFiles((prev) =>
                              prev.filter((p) => !(p.name === f.name && p.size === f.size)),
                            )
                          }
                          style={{
                            background: "transparent",
                            border: "none",
                            color: "#fca5a5",
                            cursor: "pointer",
                            fontSize: "12px",
                            padding: "0 4px",
                          }}
                          aria-label={`Remove ${f.name}`}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => setUploadFiles([])}
                      style={{
                        marginTop: "6px",
                        background: "transparent",
                        border: "none",
                        color: "#94a3b8",
                        cursor: "pointer",
                        fontSize: "11px",
                        padding: 0,
                      }}
                    >
                      Clear all
                    </button>
                  </div>
                ) : null}
              </form>
              {uploadProgress ? (
                <div style={{ marginTop: "16px" }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "6px",
                      fontSize: "13px",
                      color: "#cbd5e1",
                    }}
                  >
                    <span>
                      Uploaded {uploadProgress.completed} of {uploadProgress.total}
                    </span>
                    <span style={{ color: "#94a3b8" }}>
                      {uploadProgress.processed} processed
                      {uploadProgress.duplicates > 0
                        ? ` · ${uploadProgress.duplicates} duplicates`
                        : ""}
                      {uploadProgress.failed > 0
                        ? ` · ${uploadProgress.failed} failed`
                        : ""}
                    </span>
                  </div>
                  <div
                    style={{
                      height: "8px",
                      borderRadius: "4px",
                      background: "rgba(168, 85, 247, 0.15)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${(uploadProgress.completed / uploadProgress.total) * 100}%`,
                        background: "linear-gradient(90deg, #a855f7, #6520BD)",
                        transition: "width 0.3s ease",
                      }}
                    />
                  </div>
                </div>
              ) : null}
              {uploadResult ? (
                <p
                  style={{
                    marginTop: "16px",
                    color: "#86efac",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {uploadResult}
                </p>
              ) : null}
              {error ? (
                <p role="alert" style={{ marginTop: "16px", color: "#fca5a5" }}>
                  {error}
                </p>
              ) : null}
            </section>

            {statementHistory.length > 0 ? (
              <section style={{ marginTop: "32px" }}>
                <h2 style={{ marginBottom: "12px" }}>Upload history</h2>
                <p style={{ marginTop: 0, opacity: 0.7, fontSize: "14px" }}>
                  Last {statementHistory.length} statement{statementHistory.length === 1 ? "" : "s"}{" "}
                  ingested for your account, newest first.
                </p>
                <div
                  style={{
                    maxHeight: "320px",
                    overflowY: "auto",
                    border: "1px solid rgba(168, 85, 247, 0.2)",
                    borderRadius: "8px",
                  }}
                >
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                    <thead>
                      <tr
                        style={{
                          textAlign: "left",
                          background: "rgba(15, 23, 42, 0.7)",
                          position: "sticky",
                          top: 0,
                        }}
                      >
                        <th style={{ padding: "8px 12px" }}>File</th>
                        <th style={{ padding: "8px 12px" }}>Format</th>
                        <th style={{ padding: "8px 12px", textAlign: "right" }}>Events</th>
                        <th style={{ padding: "8px 12px", textAlign: "right" }}>Payments</th>
                        <th style={{ padding: "8px 12px" }}>Status</th>
                        <th style={{ padding: "8px 12px" }}>Uploaded</th>
                      </tr>
                    </thead>
                    <tbody>
                      {statementHistory.slice(0, 200).map((s) => (
                        <tr
                          key={s.id}
                          style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}
                        >
                          <td
                            style={{
                              padding: "6px 12px",
                              maxWidth: "300px",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                            title={s.filename}
                          >
                            {s.filename}
                          </td>
                          <td style={{ padding: "6px 12px", color: "#94a3b8" }}>
                            {s.format_detected}
                          </td>
                          <td style={{ padding: "6px 12px", textAlign: "right" }}>
                            {s.events_created.toLocaleString()}
                          </td>
                          <td style={{ padding: "6px 12px", textAlign: "right" }}>
                            {s.payments_created.toLocaleString()}
                          </td>
                          <td
                            style={{
                              padding: "6px 12px",
                              color:
                                s.status === "PROCESSED"
                                  ? "#86efac"
                                  : s.status === "FAILED"
                                    ? "#fca5a5"
                                    : "#fde68a",
                            }}
                          >
                            {s.status}
                          </td>
                          <td style={{ padding: "6px 12px", color: "#94a3b8" }}>
                            {new Date(s.uploaded_at).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            ) : null}

            <section style={{ marginTop: "32px" }}>
              <h2>Detected anomalies</h2>
              {anomalies.length === 0 ? (
                <EmptyAnomaliesGuidance />
              ) : (
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ textAlign: "left", borderBottom: "1px solid rgba(255,255,255,0.15)" }}>
                      <th style={{ padding: "8px 4px", width: "20px" }} aria-label="Expand" />
                      <th style={{ padding: "8px 4px" }}>Type</th>
                      <th style={{ padding: "8px 4px" }}>Severity</th>
                      <th style={{ padding: "8px 4px", textAlign: "right" }}>Recoverable</th>
                      <th style={{ padding: "8px 4px", textAlign: "right" }}>Confidence</th>
                      <th style={{ padding: "8px 4px" }}>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((a) => {
                      const expanded = expandedAnomalyId === a.id;
                      const ev = evidenceById[a.id];
                      return (
                        <Fragment key={a.id}>
                          <tr
                            onClick={() => toggleEvidence(a.id)}
                            style={{
                              borderBottom: "1px solid rgba(255,255,255,0.07)",
                              cursor: "pointer",
                            }}
                          >
                            <td style={{ padding: "8px 4px", textAlign: "center", opacity: 0.6 }}>
                              {expanded ? "▾" : "▸"}
                            </td>
                            <td style={{ padding: "8px 4px", fontFamily: "monospace" }}>
                              {a.subtype ?? "—"}
                            </td>
                            <td style={{ padding: "8px 4px" }}>{a.severity ?? "—"}</td>
                            <td style={{ padding: "8px 4px", textAlign: "right" }}>
                              ${(a.estimated_recoverable ?? 0).toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </td>
                            <td style={{ padding: "8px 4px", textAlign: "right" }}>
                              {a.confidence_score != null
                                ? (a.confidence_score * 100).toFixed(0) + "%"
                                : "—"}
                            </td>
                            <td style={{ padding: "8px 4px", opacity: 0.85 }}>
                              {a.description ?? ""}
                            </td>
                          </tr>
                          {expanded ? (
                            <tr style={{ background: "rgba(255,255,255,0.03)" }}>
                              <td colSpan={6} style={{ padding: "16px" }}>
                                {ev?.loading ? (
                                  <p style={{ margin: 0, opacity: 0.7 }}>Loading evidence…</p>
                                ) : ev?.error ? (
                                  <p style={{ margin: 0, color: "#f87171" }}>
                                    Could not load evidence: {ev.error}
                                  </p>
                                ) : ev?.data ? (
                                  <EvidencePanel evidence={ev.data} />
                                ) : null}
                              </td>
                            </tr>
                          ) : null}
                        </Fragment>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}
