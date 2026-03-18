import { useEffect, useState } from "react";

import { api } from "@/api";

type DashboardViewProps = {
  artistId: string;
};

type DashboardPayload = Record<string, unknown>;

type AgentStatusPayload = {
  agent_orchestra_status?: { current_step?: string | null; confidence?: number | null; trace_url?: string | null };
  comfort_messages?: string[];
  portal_guidance?: string[];
  follow_up_actions?: Array<Record<string, unknown>>;
};

export function DashboardView({ artistId }: DashboardViewProps) {
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatusPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const [d, a] = await Promise.all([
          api.dashboard.getArtistDashboardArtistsArtistIdDashboardGet({ artistId }),
          fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/artists/${artistId}/agents/status`).then((r) => r.json()),
        ]);
        if (!mounted) return;
        setDashboard((d as DashboardPayload) || {});
        setAgentStatus((a as AgentStatusPayload) || {});
      } catch (e) {
        if (!mounted) return;
        setError(String(e));
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [artistId]);

  if (error) {
    return <section className="panel">Unable to load dashboard: {error}</section>;
  }

  if (!dashboard || !agentStatus) {
    return <section className="panel">Loading dashboard...</section>;
  }

  const leakage = (dashboard.leakage_discovered || {}) as Record<string, unknown>;
  const pursuit = (dashboard.in_pursuit || {}) as Record<string, unknown>;
  const recovered = (dashboard.recovered_and_deposited || {}) as Record<string, unknown>;
  const deadlines = (dashboard.deadlines || {}) as Record<string, unknown>;
  const catalogHealth = (dashboard.catalog_health || {}) as Record<string, unknown>;
  const trend = (dashboard.earnings_trend || {}) as Record<string, unknown>;

  return (
    <section className="panel dashboard-panel">
      <header className="dashboard-header">
        <h2>Artist Recovery Dashboard</h2>
        <p>Live recovery intelligence sourced from ingestion, anomaly, claims, and forecasting pipelines.</p>
      </header>

      <div className="kpi-grid">
        <article className="kpi-card">
          <span>Leakage discovered</span>
          <strong>${Number(leakage.total_estimated_recoverable || 0).toFixed(2)}</strong>
        </article>
        <article className="kpi-card">
          <span>In pursuit</span>
          <strong>${Number(pursuit.total_amount_in_pursuit || 0).toFixed(2)}</strong>
        </article>
        <article className="kpi-card">
          <span>Recovered and deposited</span>
          <strong>${Number(recovered.total_deposited || 0).toFixed(2)}</strong>
        </article>
        <article className="kpi-card">
          <span>Urgent deadlines</span>
          <strong>{Number(deadlines.urgent_count || 0)}</strong>
        </article>
      </div>

      <div className="split-grid">
        <article className="panel nested">
          <h3>Priority actions</h3>
          <ul>
            {((dashboard.priority_actions as Record<string, unknown>)?.top_10_actions as Array<Record<string, unknown>> | undefined)?.slice(0, 5).map((item, index) => (
              <li key={`${index}-${String(item.id || index)}`}>
                <strong>{String(item.kind || "action")}</strong> · {String(item.title || item.subtype || "Review item")}
              </li>
            )) || <li>No actions yet. Upload more statements for stronger recovery signals.</li>}
          </ul>
        </article>

        <article className="panel nested">
          <h3>Agent status</h3>
          <p>Step: {agentStatus.agent_orchestra_status?.current_step || "idle"}</p>
          <p>Confidence: {agentStatus.agent_orchestra_status?.confidence ?? "n/a"}</p>
          <p>Trace: {agentStatus.agent_orchestra_status?.trace_url || "n/a"}</p>
          <h4>Comfort messages</h4>
          <ul>
            {(agentStatus.comfort_messages || []).slice(0, 3).map((msg, i) => (
              <li key={`comfort-${i}`}>{msg}</li>
            ))}
          </ul>
        </article>

        <article className="panel nested">
          <h3>Catalog and trend</h3>
          <p>Catalog health score: {Number(catalogHealth.health_score || 0).toFixed(1)}</p>
          <p>Earnings trend: {String(trend.trend || "INSUFFICIENT_DATA")}</p>
          <p>Expected 90-day total: ${Number(trend.predicted_total || 0).toFixed(2)}</p>
        </article>
      </div>
    </section>
  );
}
