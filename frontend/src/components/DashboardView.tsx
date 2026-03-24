import { useEffect, useState } from "react";

import { api } from "@/api";
import { SovereigntyInsightsPanel } from "./SovereigntyInsightsPanel";
import { RecoverabilityExplainer } from "./RecoverabilityExplainer";
import { EarningsTimeMachineCard } from "./EarningsTimeMachineCard";
import { GhostCatalogDetectorCard } from "./GhostCatalogDetectorCard";
import { BlackBoxCountdownCard } from "./BlackBoxCountdownCard";
import { RoyaltyDNAProfileCard } from "./RoyaltyDNAProfileCard";
import { PayerHealthScoreCard } from "./PayerHealthScoreCard";
import { ContractDriftMonitorCard } from "./ContractDriftMonitorCard";
import { CatalogValueAppraiserCard } from "./CatalogValueAppraiserCard";
import { RecoveryCreditScoreCard } from "./RecoveryCreditScoreCard";

const ALL_MODULES = [
  { id: "earnings_time_machine", label: "Earnings Time Machine" },
  { id: "ghost_catalog_detector", label: "Ghost Catalog Detector" },
  { id: "black_box_countdown", label: "Black Box Countdown" },
  { id: "royalty_dna_profile", label: "Royalty DNA Profile" },
  { id: "payer_health_score", label: "Payer Health Score" },
  { id: "contract_drift_monitor", label: "Contract Drift Monitor" },
  { id: "catalog_value_appraiser", label: "Catalog Value Appraiser" },
  { id: "recovery_credit_score", label: "Recovery Credit Score", alwaysOn: true },
] as const;

type ModuleId = typeof ALL_MODULES[number]["id"];

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

  const defaultEnabled = new Set<ModuleId>(["recovery_credit_score"]);
  const [enabledModules, setEnabledModules] = useState<Set<ModuleId>>(defaultEnabled);
  const [selectorOpen, setSelectorOpen] = useState(false);

  function toggleModule(id: ModuleId, alwaysOn?: boolean) {
    if (alwaysOn) return;
    setEnabledModules((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

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
  const recoverability = (dashboard.recoverability_breakdown || {}) as Record<string, unknown>;
  const probabilityNarrative = String((recoverability.probability_narrative as string | undefined) || "");
  const contractClauseCitation = String((recoverability.contract_clause_citation as string | undefined) || "");

  const confidence = Number(
    agentStatus.agent_orchestra_status?.confidence ??
      ((dashboard as Record<string, unknown>).forecast_confidence as number | undefined) ??
      0,
  );
  const solCells = [
    { label: "Urgent", value: Number(deadlines.urgent_count || 0) },
    { label: "Soon", value: Number(deadlines.upcoming_count || 0) },
    { label: "Missed", value: Number(deadlines.overdue_count || 0) },
    { label: "Safe", value: Math.max(0, 10 - Number(deadlines.urgent_count || 0) - Number(deadlines.overdue_count || 0)) },
  ];
  const waterfall = [
    { label: "Leakage", amount: Number(leakage.total_estimated_recoverable || 0) },
    { label: "In Pursuit", amount: -Number(pursuit.total_amount_in_pursuit || 0) },
    { label: "Recovered", amount: Number(recovered.total_deposited || 0) },
  ];
  const payerRows = [
    { payer: "Primary", responsiveness: Math.max(0, Math.min(1, confidence)), resistance: Math.max(0, Math.min(1, 1 - confidence)) },
    { payer: "Secondary", responsiveness: Math.max(0, Math.min(1, confidence * 0.8)), resistance: Math.max(0, Math.min(1, 1 - confidence * 0.8)) },
  ];

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

      <RecoverabilityExplainer
        title="Post Black-Box Recoverability"
        recoverableAmount={Number((recoverability.recoverable_total as number | undefined) || 0)}
        expiredAmount={Number((recoverability.expired_total as number | undefined) || 0)}
        byClass={(recoverability.by_class as Record<string, { count?: number; amount?: number; estimated_recoverable?: number }> | undefined) || {}}
        claimWindowLabel="Recoverable, contract-based, and copyright-damages classes are draftable"
        probabilityNarrative={probabilityNarrative || undefined}
        contractClauseCitation={contractClauseCitation || undefined}
      />

      <SovereigntyInsightsPanel
        confidence={confidence}
        solCells={solCells}
        waterfall={waterfall}
        payerRows={payerRows}
      />

      {/* ── Module Selector ── */}
      <div style={{ marginTop: 32, borderTop: "1px solid #2D2D4E", paddingTop: 20 }}>
        <div
          style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", marginBottom: 12 }}
          onClick={() => setSelectorOpen((o) => !o)}
        >
          <span style={{ fontWeight: 700, fontSize: 15, color: "#F1F1F3" }}>Intelligence Modules</span>
          <span style={{ fontSize: 12, color: "#9CA3AF" }}>({enabledModules.size} active)</span>
          <span style={{ marginLeft: "auto", color: "#9CA3AF" }}>{selectorOpen ? "▲" : "▼"}</span>
        </div>

        {selectorOpen && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 20 }}>
            {ALL_MODULES.map((m) => {
              const on = enabledModules.has(m.id);
              return (
                <button
                  key={m.id}
                  onClick={() => toggleModule(m.id, "alwaysOn" in m && m.alwaysOn)}
                  style={{
                    background: on ? "#C89B3C22" : "#1F2937",
                    border: `1px solid ${on ? "#C89B3C" : "#374151"}`,
                    color: on ? "#C89B3C" : "#9CA3AF",
                    borderRadius: 20, padding: "5px 14px", fontSize: 12, cursor: "alwaysOn" in m && m.alwaysOn ? "default" : "pointer",
                    fontWeight: on ? 600 : 400,
                  }}
                >
                  {m.label}{"alwaysOn" in m && m.alwaysOn ? " (always on)" : ""}
                </button>
              );
            })}
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 20 }}>
          {enabledModules.has("recovery_credit_score") && (
            <RecoveryCreditScoreCard artistId={artistId} />
          )}
          {enabledModules.has("earnings_time_machine") && (
            <EarningsTimeMachineCard artistId={artistId} />
          )}
          {enabledModules.has("ghost_catalog_detector") && (
            <GhostCatalogDetectorCard artistId={artistId} />
          )}
          {enabledModules.has("black_box_countdown") && (
            <BlackBoxCountdownCard artistId={artistId} />
          )}
          {enabledModules.has("royalty_dna_profile") && (
            <RoyaltyDNAProfileCard artistId={artistId} />
          )}
          {enabledModules.has("payer_health_score") && (
            <PayerHealthScoreCard artistId={artistId} />
          )}
          {enabledModules.has("contract_drift_monitor") && (
            <ContractDriftMonitorCard artistId={artistId} />
          )}
          {enabledModules.has("catalog_value_appraiser") && (
            <CatalogValueAppraiserCard artistId={artistId} />
          )}
        </div>
      </div>
    </section>
  );
}
