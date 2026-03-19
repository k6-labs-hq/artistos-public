import { useEffect, useMemo, useState } from "react";

import "./AdminWorkflowHandoffsPanel.css";

type HandoffRow = {
  id: string;
  run_id: string;
  artist_id: string;
  artist_name?: string | null;
  handoff_id: string;
  from_agent: string;
  to_agent: string;
  status: string;
  readiness_score: number;
  readiness_threshold: number;
  created_at?: string | null;
};

type HandoffListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: HandoffRow[];
};

const storageKeys = {
  adminKey: "xr7-admin-handoffs-key",
  adminActor: "xr7-admin-handoffs-actor",
};

const basePath = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function AdminWorkflowHandoffsPanel() {
  const [adminKey, setAdminKey] = useState("");
  const [adminActor, setAdminActor] = useState("ops@xr7.test");
  const [artistId, setArtistId] = useState("");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [fromAgent, setFromAgent] = useState("");
  const [toAgent, setToAgent] = useState("");
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const [limit, setLimit] = useState("50");
  const [rows, setRows] = useState<HandoffRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastQuery, setLastQuery] = useState("");

  useEffect(() => {
    const savedKey = window.localStorage.getItem(storageKeys.adminKey);
    const savedActor = window.localStorage.getItem(storageKeys.adminActor);
    if (savedKey) setAdminKey(savedKey);
    if (savedActor) setAdminActor(savedActor);
  }, []);

  useEffect(() => {
    if (adminKey) {
      window.localStorage.setItem(storageKeys.adminKey, adminKey);
    }
  }, [adminKey]);

  useEffect(() => {
    if (adminActor) {
      window.localStorage.setItem(storageKeys.adminActor, adminActor);
    }
  }, [adminActor]);

  const requestHeaders = useMemo(
    () => ({
      "X-Admin-Key": adminKey,
      "X-Admin-Actor": adminActor,
    }),
    [adminActor, adminKey],
  );

  const buildQueryString = (format: "json" | "csv") => {
    const params = new URLSearchParams();
    if (artistId.trim()) params.set("artist_id", artistId.trim());
    if (query.trim()) params.set("q", query.trim());
    if (status.trim()) params.set("status", status.trim());
    if (fromAgent.trim()) params.set("from_agent", fromAgent.trim());
    if (toAgent.trim()) params.set("to_agent", toAgent.trim());
    if (since) params.set("since", new Date(`${since}T00:00:00`).toISOString());
    if (until) params.set("until", new Date(`${until}T23:59:59`).toISOString());
    params.set("limit", String(Math.max(1, Number(limit) || 50)));
    params.set("offset", "0");
    params.set("format", format);
    return params.toString();
  };

  const handlePreview = async () => {
    if (!adminKey.trim()) {
      setError("Admin key is required.");
      return;
    }

    const queryString = buildQueryString("json");
    setLoading(true);
    setError("");
    setLastQuery(queryString);

    try {
      const response = await fetch(`${basePath}/admin/workflow/handoffs?${queryString}`, {
        headers: requestHeaders,
      });
      const payload = (await response.json()) as HandoffListResponse | { detail?: string };
      if (!response.ok) {
        setRows([]);
        setTotal(0);
        setError((payload as { detail?: string }).detail || `Request failed (${response.status}).`);
        return;
      }
      const result = payload as HandoffListResponse;
      setRows(result.items || []);
      setTotal(Number(result.total || 0));
    } catch (requestError) {
      setRows([]);
      setTotal(0);
      setError(String(requestError));
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = async () => {
    if (!adminKey.trim()) {
      setError("Admin key is required.");
      return;
    }

    const queryString = buildQueryString("csv");
    setLoading(true);
    setError("");
    setLastQuery(queryString);

    try {
      const response = await fetch(`${basePath}/admin/workflow/handoffs?${queryString}`, {
        headers: requestHeaders,
      });
      if (!response.ok) {
        let message = `Export failed (${response.status}).`;
        try {
          const payload = (await response.json()) as { detail?: string };
          message = payload.detail || message;
        } catch {
          // Ignore parse failures for non-JSON error bodies.
        }
        setError(message);
        return;
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "workflow_handoffs.csv";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(String(requestError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="handoff-admin-page">
      <section className="handoff-admin-shell">
        <header className="handoff-admin-header">
          <p className="handoff-admin-eyebrow">XR7 Operator Tools</p>
          <h1>Workflow Handoff Search</h1>
          <p>
            Preview or export two-agent handoffs across artists without hand-building query strings.
          </p>
        </header>

        <section className="handoff-admin-card">
          <div className="handoff-admin-grid handoff-admin-grid--credentials">
            <label>
              <span>Admin key</span>
              <input
                type="password"
                value={adminKey}
                onChange={(event) => setAdminKey(event.target.value)}
                placeholder="Enter X-Admin-Key"
              />
            </label>
            <label>
              <span>Admin actor</span>
              <input
                type="text"
                value={adminActor}
                onChange={(event) => setAdminActor(event.target.value)}
                placeholder="ops@xr7.test"
              />
            </label>
          </div>

          <div className="handoff-admin-grid">
            <label>
              <span>Artist ID</span>
              <input type="text" value={artistId} onChange={(event) => setArtistId(event.target.value)} placeholder="Optional exact artist id" />
            </label>
            <label>
              <span>Artist name search</span>
              <input type="text" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by artist name" />
            </label>
            <label>
              <span>Status</span>
              <input type="text" value={status} onChange={(event) => setStatus(event.target.value)} placeholder="active" />
            </label>
            <label>
              <span>From agent</span>
              <input type="text" value={fromAgent} onChange={(event) => setFromAgent(event.target.value)} placeholder="onboarding_preparation" />
            </label>
            <label>
              <span>To agent</span>
              <input type="text" value={toAgent} onChange={(event) => setToAgent(event.target.value)} placeholder="recovery_execution" />
            </label>
            <label>
              <span>Limit</span>
              <input type="number" min="1" max="200" value={limit} onChange={(event) => setLimit(event.target.value)} />
            </label>
            <label>
              <span>Since</span>
              <input type="date" value={since} onChange={(event) => setSince(event.target.value)} />
            </label>
            <label>
              <span>Until</span>
              <input type="date" value={until} onChange={(event) => setUntil(event.target.value)} />
            </label>
          </div>

          <div className="handoff-admin-actions">
            <button type="button" className="handoff-admin-button handoff-admin-button--primary" onClick={handlePreview} disabled={loading}>
              {loading ? "Loading..." : "Preview Results"}
            </button>
            <button type="button" className="handoff-admin-button" onClick={handleExportCsv} disabled={loading}>
              Export CSV
            </button>
          </div>

          {error ? <p className="handoff-admin-error">{error}</p> : null}
          {lastQuery ? <p className="handoff-admin-meta">Last query: /admin/workflow/handoffs?{lastQuery}</p> : null}
        </section>

        <section className="handoff-admin-card">
          <div className="handoff-admin-results-head">
            <h2>Preview</h2>
            <span>{total} matching handoffs</span>
          </div>

          {rows.length ? (
            <div className="handoff-admin-table-wrap">
              <table className="handoff-admin-table">
                <thead>
                  <tr>
                    <th>Artist</th>
                    <th>Transition</th>
                    <th>Status</th>
                    <th>Readiness</th>
                    <th>Recorded</th>
                    <th>Handoff ID</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.id}>
                      <td>
                        <strong>{row.artist_name || row.artist_id}</strong>
                        <div>{row.artist_id}</div>
                      </td>
                      <td>{row.from_agent} -&gt; {row.to_agent}</td>
                      <td>{row.status}</td>
                      <td>{row.readiness_score.toFixed(1)} / {row.readiness_threshold.toFixed(1)}</td>
                      <td>{row.created_at ? new Date(row.created_at).toLocaleString() : "n/a"}</td>
                      <td className="handoff-admin-mono">{row.handoff_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="handoff-admin-empty">No handoffs loaded yet. Enter filters and choose Preview Results.</p>
          )}
        </section>
      </section>
    </main>
  );
}

export default AdminWorkflowHandoffsPanel;