/**
 * Per-artist file browser + reprocess view for the operator console.
 *
 * Hits two admin endpoints:
 *   GET  /admin/artists/statements          — cross-artist listing
 *   POST /admin/statements/{id}/reprocess   — re-parse stored bytes
 *
 * Sibling to OpsDashboard's Filing Queue — see that component for the
 * auth handshake. We accept the resolved `headers` and `basePath` as
 * props rather than re-deriving them so the two views stay in sync.
 */
import { Fragment, useCallback, useEffect, useMemo, useState } from "react";

type StatementRow = {
  id: string;
  filename: string | null;
  format_detected: string | null;
  row_count: number;
  events_created: number;
  payments_created: number;
  skipped_rows: number;
  status: string | null;
  error_summary: string | null;
  s3_uri_present: boolean;
  uploaded_at: string | null;
};

type ArtistBlock = {
  artist_id: string;
  artist_name: string | null;
  artist_email: string | null;
  statements_count: number;
  events_count: number;
  payments_count: number;
  anomalies_count: number;
  latest_upload_at: string | null;
  statements: StatementRow[];
};

type FilesResponse = {
  total: number;
  items: ArtistBlock[];
};

type ReprocessResult = {
  statement_id: string;
  format_detected: string | null;
  events_added: number;
  payments_added: number;
  row_count: number;
  skipped_rows: number;
  errors: string[];
  status: string | null;
};

export function OpsFiles({
  isAuthed,
  basePath,
  headers,
}: {
  isAuthed: boolean;
  basePath: string;
  headers: Record<string, string>;
}) {
  const [data, setData] = useState<ArtistBlock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [reprocessingId, setReprocessingId] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<{
    statement_id: string;
    label: string;
    result: ReprocessResult;
  } | null>(null);

  const loadFiles = useCallback(async () => {
    if (!isAuthed) {
      setError("Admin auth required — sign in or paste an admin key.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${basePath}/admin/artists/statements`, { headers });
      const payload = (await res.json()) as FilesResponse | { detail?: string };
      if (!res.ok) {
        setData([]);
        setError((payload as { detail?: string }).detail || `Request failed (${res.status}).`);
        return;
      }
      setData((payload as FilesResponse).items || []);
    } catch (e) {
      setData([]);
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [isAuthed, basePath, headers]);

  useEffect(() => {
    if (isAuthed) loadFiles();
    // We deliberately re-run only when auth flips; the explicit Reload
    // button covers operator-driven refresh.
  }, [isAuthed, loadFiles]);

  const downloadStatement = async (id: string, filename: string | null) => {
    setDownloadingId(id);
    setError("");
    try {
      const res = await fetch(`${basePath}/admin/statements/${id}/download`, { headers });
      if (!res.ok) {
        const text = await res.text();
        setError(`Download failed (${res.status}): ${text.slice(0, 200)}`);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || `${id}.bin`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (e) {
      setError(String(e));
    } finally {
      setDownloadingId(null);
    }
  };

  const reprocessStatement = async (id: string, filename: string | null) => {
    if (
      !window.confirm(
        `Reprocess ${filename || id}?\n\n` +
          `This pulls the stored bytes through the current parser. Existing ` +
          `events/payments dedup; only newly-parseable rows are added.`,
      )
    ) {
      return;
    }
    setReprocessingId(id);
    setError("");
    setLastResult(null);
    try {
      const res = await fetch(`${basePath}/admin/statements/${id}/reprocess`, {
        method: "POST",
        headers,
      });
      const payload = await res.json();
      if (!res.ok) {
        setError(
          (payload as { detail?: string }).detail || `Reprocess failed (${res.status}).`,
        );
        return;
      }
      setLastResult({
        statement_id: id,
        label: filename || id,
        result: payload as ReprocessResult,
      });
      // Refresh counts after reprocess so the UI reflects new rows.
      await loadFiles();
    } catch (e) {
      setError(String(e));
    } finally {
      setReprocessingId(null);
    }
  };

  const totals = useMemo(() => {
    return data.reduce(
      (acc, a) => ({
        artists: acc.artists + 1,
        statements: acc.statements + a.statements_count,
        events: acc.events + a.events_count,
        payments: acc.payments + a.payments_count,
      }),
      { artists: 0, statements: 0, events: 0, payments: 0 },
    );
  }, [data]);

  const toggleArtist = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <section
      style={{
        padding: "16px",
        background: "rgba(15, 23, 42, 0.6)",
        border: "1px solid rgba(168, 85, 247, 0.2)",
        borderRadius: "12px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px" }}>
        <div>
          <div style={{ fontSize: "12px", color: "#94a3b8" }}>
            {totals.artists} artist{totals.artists === 1 ? "" : "s"} · {totals.statements}{" "}
            statement{totals.statements === 1 ? "" : "s"} ·{" "}
            {totals.events.toLocaleString()} events ·{" "}
            {totals.payments.toLocaleString()} payments
          </div>
        </div>
        <button
          type="button"
          onClick={loadFiles}
          disabled={loading || !isAuthed}
          style={{
            background: loading ? "rgba(168,85,247,0.25)" : "rgba(168,85,247,0.7)",
            border: "1px solid rgba(168,85,247,0.5)",
            borderRadius: "8px",
            color: "#fff",
            padding: "6px 12px",
            cursor: loading || !isAuthed ? "default" : "pointer",
            fontSize: "13px",
          }}
        >
          {loading ? "Loading…" : "Reload"}
        </button>
      </div>

      {error ? (
        <p style={{ color: "#f87171", fontSize: "13px", margin: "0 0 12px" }}>{error}</p>
      ) : null}

      {lastResult ? (
        <div
          style={{
            marginBottom: "12px",
            padding: "10px 12px",
            background: "rgba(34, 197, 94, 0.08)",
            border: "1px solid rgba(34, 197, 94, 0.3)",
            borderRadius: "8px",
            fontSize: "12px",
            color: "#cbd5e1",
          }}
        >
          <strong>Reprocessed {lastResult.label}</strong> — format{" "}
          <code>{lastResult.result.format_detected || "?"}</code>,{" "}
          +{lastResult.result.events_added} events, +{lastResult.result.payments_added} payments,
          status <code>{lastResult.result.status}</code>
          {lastResult.result.errors.length > 0
            ? ` · errors: ${lastResult.result.errors.join("; ")}`
            : ""}
        </div>
      ) : null}

      {!loading && data.length === 0 ? (
        <p style={{ color: "#94a3b8", fontSize: "13px", margin: 0 }}>
          No statements have been uploaded yet.
        </p>
      ) : null}

      {data.map((artist) => {
        const open = expanded.has(artist.artist_id);
        return (
          <div
            key={artist.artist_id}
            style={{
              marginBottom: "10px",
              border: "1px solid rgba(168, 85, 247, 0.15)",
              borderRadius: "8px",
              overflow: "hidden",
            }}
          >
            <button
              type="button"
              onClick={() => toggleArtist(artist.artist_id)}
              style={{
                width: "100%",
                textAlign: "left",
                background: "rgba(15, 23, 42, 0.5)",
                border: "none",
                padding: "10px 14px",
                color: "#e2e8f0",
                cursor: "pointer",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "12px",
                fontSize: "13px",
              }}
            >
              <div>
                <strong style={{ fontSize: "14px" }}>{open ? "▾" : "▸"}{" "}
                  {artist.artist_name || artist.artist_id}</strong>
                <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>
                  {artist.artist_email || "(no email)"} · {artist.statements_count} statements ·{" "}
                  {artist.events_count.toLocaleString()} events ·{" "}
                  {artist.payments_count.toLocaleString()} payments ·{" "}
                  {artist.anomalies_count} anomalies
                </div>
              </div>
              <span style={{ fontSize: "11px", color: "#94a3b8" }}>
                latest {artist.latest_upload_at?.slice(0, 10) || "—"}
              </span>
            </button>

            {open ? (
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                <thead>
                  <tr style={{ background: "rgba(15, 23, 42, 0.7)", color: "#94a3b8" }}>
                    <th style={cellHead}>Filename</th>
                    <th style={cellHead}>Format</th>
                    <th style={cellHeadRight}>Rows</th>
                    <th style={cellHeadRight}>Events</th>
                    <th style={cellHeadRight}>Payments</th>
                    <th style={cellHead}>Status</th>
                    <th style={cellHead}>Uploaded</th>
                    <th style={cellHead}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {artist.statements.map((s) => (
                    <Fragment key={s.id}>
                      <tr style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
                        <td style={cell}>{s.filename || "(no name)"}</td>
                        <td style={cell}><code style={{ fontSize: "11px" }}>{s.format_detected || "—"}</code></td>
                        <td style={cellRight}>{s.row_count}</td>
                        <td style={cellRight}>{s.events_created}</td>
                        <td style={cellRight}>{s.payments_created}</td>
                        <td style={cell}>
                          <span
                            style={{
                              fontSize: "11px",
                              color: s.status === "FAILED" ? "#f87171" : "#86efac",
                            }}
                          >
                            {s.status || "—"}
                          </span>
                        </td>
                        <td style={cell}>{s.uploaded_at?.slice(0, 10) || "—"}</td>
                        <td style={cell}>
                          <div style={{ display: "flex", gap: "6px" }}>
                            <button
                              type="button"
                              onClick={() => downloadStatement(s.id, s.filename)}
                              disabled={!s.s3_uri_present || downloadingId === s.id}
                              title={
                                s.s3_uri_present
                                  ? "Download the original uploaded bytes"
                                  : "Source bytes not retained for this statement"
                              }
                              style={btnGhost(!s.s3_uri_present)}
                            >
                              {downloadingId === s.id ? "…" : "Download"}
                            </button>
                            <button
                              type="button"
                              onClick={() => reprocessStatement(s.id, s.filename)}
                              disabled={!s.s3_uri_present || reprocessingId === s.id}
                              title={
                                s.s3_uri_present
                                  ? "Re-parse stored bytes through the current parser + re-run detection"
                                  : "Source bytes not retained — cannot reprocess"
                              }
                              style={btnGhost(!s.s3_uri_present)}
                            >
                              {reprocessingId === s.id ? "Reprocessing…" : "Reprocess"}
                            </button>
                          </div>
                        </td>
                      </tr>
                      {s.error_summary ? (
                        <tr>
                          <td colSpan={8} style={{ ...cell, color: "#fca5a5", fontSize: "11px" }}>
                            {s.error_summary}
                          </td>
                        </tr>
                      ) : null}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            ) : null}
          </div>
        );
      })}
    </section>
  );
}

// ---- styling helpers ----

const cellHead: React.CSSProperties = {
  textAlign: "left",
  padding: "8px 12px",
  fontWeight: 500,
  fontSize: "11px",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

const cellHeadRight: React.CSSProperties = { ...cellHead, textAlign: "right" };

const cell: React.CSSProperties = {
  padding: "6px 12px",
  verticalAlign: "top",
  color: "#cbd5e1",
};

const cellRight: React.CSSProperties = { ...cell, textAlign: "right" };

const btnGhost = (disabled: boolean): React.CSSProperties => ({
  background: "transparent",
  border: "1px solid rgba(168,85,247,0.35)",
  borderRadius: "6px",
  color: disabled ? "#64748b" : "#cbd5e1",
  padding: "3px 8px",
  fontSize: "11px",
  cursor: disabled ? "not-allowed" : "pointer",
});
