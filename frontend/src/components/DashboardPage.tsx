/**
 * Beta dashboard.
 *
 * Minimum surface for a signed-in beta user: identifies them, accepts terms
 * if not yet accepted, lets them upload a statement, lists detected
 * anomalies. Heavily restrained — anything richer (charts, claim filing,
 * payouts) is post-beta.
 */
import { useCallback, useEffect, useState } from "react";

import { clearXR7Token, getXR7Token } from "../lib/supabase";
import { type Anomaly, type Me, UnauthorizedError, xr7 } from "../lib/xr7Client";

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

type LoadState = "loading" | "ready" | "needs_terms" | "error";

export function DashboardPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);

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
        await refreshAnomalies(meResp.artist_id);
        setState("ready");
      } catch (err) {
        if (err instanceof UnauthorizedError) return;
        setError(err instanceof Error ? err.message : String(err));
        setState("error");
      }
    })();
  }, [refreshAnomalies]);

  const handleAcceptTerms = async () => {
    if (!me?.artist_id) return;
    setError(null);
    try {
      const terms = await xr7.getTermsStatus(me.artist_id);
      if (terms.pending_version) {
        await xr7.acceptTerms(me.artist_id, terms.pending_version);
      }
      await refreshAnomalies(me.artist_id);
      setState("ready");
    } catch (err) {
      if (err instanceof UnauthorizedError) return;
      setError(err instanceof Error ? err.message : String(err));
      setState("error");
    }
  };

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!me?.artist_id || !uploadFile) return;
    setUploading(true);
    setUploadResult(null);
    setError(null);
    try {
      const result = await xr7.uploadStatement(me.artist_id, uploadFile);
      setUploadResult(
        `Uploaded ${uploadFile.name} — format ${result.format_detected}, ` +
          `${result.events_created} events, ${result.payments_created} payments.`,
      );
      setUploadFile(null);
      await refreshAnomalies(me.artist_id);
    } catch (err) {
      if (err instanceof UnauthorizedError) return;
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
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
            <h2>One quick step before you upload</h2>
            <p>
              You need to accept the Artist Recovery Services Agreement before XR7 can ingest a
              statement on your behalf.
            </p>
            <button type="button" className="cta" onClick={handleAcceptTerms}>
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
                Accepted formats: CSV, TSV, XLSX. BMI, MLC, ASCAP, DistroKid, TuneCore, and others
                are auto-detected.
              </p>
              <form onSubmit={handleUpload}>
                <input
                  type="file"
                  accept=".csv,.tsv,.xlsx"
                  onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                  aria-label="Royalty statement file"
                />
                <button
                  type="submit"
                  className="cta"
                  disabled={!uploadFile || uploading}
                  style={{ marginLeft: "12px" }}
                >
                  {uploading ? "Uploading…" : "Upload"}
                </button>
              </form>
              {uploadResult ? (
                <p style={{ marginTop: "16px", color: "#86efac" }}>{uploadResult}</p>
              ) : null}
              {error ? (
                <p role="alert" style={{ marginTop: "16px", color: "#fca5a5" }}>
                  {error}
                </p>
              ) : null}
            </section>

            <section style={{ marginTop: "32px" }}>
              <h2>Detected anomalies</h2>
              {anomalies.length === 0 ? (
                <EmptyAnomaliesGuidance />
              ) : (
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ textAlign: "left", borderBottom: "1px solid rgba(255,255,255,0.15)" }}>
                      <th style={{ padding: "8px 4px" }}>Type</th>
                      <th style={{ padding: "8px 4px" }}>Severity</th>
                      <th style={{ padding: "8px 4px", textAlign: "right" }}>Recoverable</th>
                      <th style={{ padding: "8px 4px", textAlign: "right" }}>Confidence</th>
                      <th style={{ padding: "8px 4px" }}>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((a) => (
                      <tr key={a.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                        <td style={{ padding: "8px 4px", fontFamily: "monospace" }}>{a.subtype ?? "—"}</td>
                        <td style={{ padding: "8px 4px" }}>{a.severity ?? "—"}</td>
                        <td style={{ padding: "8px 4px", textAlign: "right" }}>
                          ${(a.estimated_recoverable ?? 0).toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </td>
                        <td style={{ padding: "8px 4px", textAlign: "right" }}>
                          {a.confidence_score != null ? (a.confidence_score * 100).toFixed(0) + "%" : "—"}
                        </td>
                        <td style={{ padding: "8px 4px", opacity: 0.85 }}>{a.description ?? ""}</td>
                      </tr>
                    ))}
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
