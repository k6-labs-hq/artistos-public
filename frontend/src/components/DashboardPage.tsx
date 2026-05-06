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

type LoadState = "loading" | "ready" | "needs_terms" | "needs_payer_setup" | "error";

const SUPPORTED_PROS = ["BMI", "ASCAP", "MLC", "SoundExchange"] as const;
const BMI_OFFICES = [
  "Nashville",
  "New York",
  "Los Angeles",
  "Atlanta",
  "Austin",
  "London",
];

export function DashboardPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [termsText, setTermsText] = useState<string | null>(null);
  const [termsVersion, setTermsVersion] = useState<string | null>(null);
  const [termsLoading, setTermsLoading] = useState(false);
  const [termsAcknowledged, setTermsAcknowledged] = useState(false);
  const [selectedPros, setSelectedPros] = useState<string[]>([]);
  const [selectedBmiOffice, setSelectedBmiOffice] = useState<string>("Nashville");
  const [savingRouting, setSavingRouting] = useState(false);

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
        // After terms, gate on payer routing — we need to know which PROs
        // the artist receives statements from before any anomaly we
        // surface can be filed correctly.
        if (!meResp.pro_affiliations || meResp.pro_affiliations.length === 0) {
          setState("needs_payer_setup");
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

  const handleSavePayerRouting = async () => {
    if (!me?.artist_id) return;
    if (selectedPros.length === 0) {
      setError("Pick at least one PRO/collective.");
      return;
    }
    setSavingRouting(true);
    setError(null);
    try {
      const includesBmi = selectedPros.includes("BMI");
      await xr7.updatePayerRouting(me.artist_id, {
        pro_affiliations: selectedPros,
        bmi_office_name: includesBmi ? selectedBmiOffice : null,
      });
      // Refresh /me so the cached state matches.
      const refreshed = await xr7.me();
      setMe(refreshed);
      await refreshAnomalies(me.artist_id);
      setState("ready");
    } catch (err) {
      if (err instanceof UnauthorizedError) return;
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSavingRouting(false);
    }
  };

  const togglePro = (pro: string) => {
    setSelectedPros((prev) =>
      prev.includes(pro) ? prev.filter((p) => p !== pro) : [...prev, pro],
    );
  };

  const handleAcceptTerms = async () => {
    if (!me?.artist_id) return;
    setError(null);
    try {
      const terms = await xr7.getTermsStatus(me.artist_id);
      if (terms.pending_version) {
        await xr7.acceptTerms(me.artist_id, terms.pending_version);
      }
      // Same gate as the mount handler: after terms, if payer setup hasn't
      // been completed, bounce into needs_payer_setup before showing the
      // upload UI. Without this, accepting terms skipped straight to
      // "ready" and the artist never saw the PRO/region question.
      const refreshed = await xr7.me();
      setMe(refreshed);
      if (!refreshed.pro_affiliations || refreshed.pro_affiliations.length === 0) {
        setState("needs_payer_setup");
        return;
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
    if (!me?.artist_id || uploadFiles.length === 0) return;
    setUploading(true);
    setUploadResult(null);
    setError(null);
    try {
      // Single-file path keeps the format-detected + counts feedback;
      // multi-file path uses the batch endpoint and reports aggregate
      // results. Backend caps at 100 files per batch.
      if (uploadFiles.length === 1) {
        const onlyFile = uploadFiles[0];
        if (!onlyFile) return;
        const result = await xr7.uploadStatement(me.artist_id, onlyFile);
        setUploadResult(
          `Uploaded ${onlyFile.name} — format ${result.format_detected}, ` +
            `${result.events_created} events, ${result.payments_created} payments.`,
        );
      } else {
        const CHUNK = 80; // stay under the server's 100 cap
        let processed = 0;
        let failed = 0;
        let duplicates = 0;
        const failedNames: string[] = [];
        for (let i = 0; i < uploadFiles.length; i += CHUNK) {
          const slice = uploadFiles.slice(i, i + CHUNK);
          const result = await xr7.uploadStatementBatch(me.artist_id, slice);
          processed += result.processed?.length || 0;
          failed += result.failed?.length || 0;
          duplicates += result.duplicates || 0;
          for (const f of (result.failed || []).slice(0, 5)) {
            failedNames.push(`${f.filename}: ${f.error}`);
          }
        }
        setUploadResult(
          `Uploaded ${uploadFiles.length} files: ${processed} processed, ` +
            `${duplicates} duplicates, ${failed} failed.` +
            (failedNames.length
              ? `\nFirst failures: ${failedNames.join("; ")}`
              : ""),
        );
      }
      setUploadFiles([]);
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

        {state === "needs_payer_setup" ? (
          <section
            style={{
              marginTop: "32px",
              padding: "24px",
              borderRadius: "16px",
              border: "1px solid rgba(168, 85, 247, 0.3)",
              background: "rgba(16, 16, 28, 0.6)",
            }}
          >
            <h2>Where do your statements come from?</h2>
            <p style={{ marginTop: "0", color: "#cbd5e1" }}>
              Pick the PROs/collectives you receive royalty statements from. We use this to
              route any disputes to the right submission address.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "16px" }}>
              {SUPPORTED_PROS.map((pro) => (
                <label key={pro} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input
                    type="checkbox"
                    checked={selectedPros.includes(pro)}
                    onChange={() => togglePro(pro)}
                  />
                  <span>{pro}</span>
                </label>
              ))}
            </div>

            {selectedPros.includes("BMI") ? (
              <div style={{ marginTop: "20px" }}>
                <label style={{ display: "block" }}>
                  <span style={{ display: "block", marginBottom: "6px", color: "#cbd5e1" }}>
                    BMI regional office
                  </span>
                  <select
                    value={selectedBmiOffice}
                    onChange={(e) => setSelectedBmiOffice(e.target.value)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: "8px",
                      background: "#0b0b14",
                      color: "#e8e8ee",
                      border: "1px solid rgba(168, 85, 247, 0.3)",
                      minWidth: "240px",
                    }}
                  >
                    {BMI_OFFICES.map((office) => (
                      <option key={office} value={office}>
                        {office}
                      </option>
                    ))}
                  </select>
                </label>
                <p style={{ fontSize: "12px", color: "#777", marginTop: "6px" }}>
                  Pick the office nearest your home base — this is where BMI's Writer/Publisher
                  Relations team routes member inquiries. Default is Nashville.
                </p>
              </div>
            ) : null}

            <button
              type="button"
              className="cta"
              onClick={handleSavePayerRouting}
              disabled={savingRouting || selectedPros.length === 0}
              style={{ marginTop: "20px" }}
            >
              {savingRouting ? "Saving…" : "Save and continue"}
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
                Accepted formats: CSV, TSV, XLSX, Numbers. BMI, MLC, ASCAP, DistroKid, TuneCore,
                and others are auto-detected — including MLC's native Apple Numbers exports.
              </p>
              <form onSubmit={handleUpload}>
                <input
                  type="file"
                  multiple
                  accept=".csv,.tsv,.xlsx,.numbers"
                  onChange={(e) => setUploadFiles(Array.from(e.target.files ?? []))}
                  aria-label="Royalty statement files"
                />
                <button
                  type="submit"
                  className="cta"
                  disabled={uploadFiles.length === 0 || uploading}
                  style={{ marginLeft: "12px" }}
                >
                  {uploading
                    ? "Uploading…"
                    : uploadFiles.length > 1
                      ? `Upload ${uploadFiles.length} files`
                      : "Upload"}
                </button>
                {uploadFiles.length > 1 ? (
                  <p style={{ marginTop: "8px", color: "#94a3b8", fontSize: "13px" }}>
                    {uploadFiles.length} files selected. Up to 100 per batch.
                  </p>
                ) : null}
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
