import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { api } from "@/api";
export function DashboardView({ artistId }) {
    const [dashboard, setDashboard] = useState(null);
    const [agentStatus, setAgentStatus] = useState(null);
    const [error, setError] = useState("");
    useEffect(() => {
        let mounted = true;
        const load = async () => {
            try {
                const [d, a] = await Promise.all([
                    api.dashboard.getArtistDashboardArtistsArtistIdDashboardGet({ artistId }),
                    fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/artists/${artistId}/agents/status`).then((r) => r.json()),
                ]);
                if (!mounted)
                    return;
                setDashboard(d || {});
                setAgentStatus(a || {});
            }
            catch (e) {
                if (!mounted)
                    return;
                setError(String(e));
            }
        };
        load();
        return () => {
            mounted = false;
        };
    }, [artistId]);
    if (error) {
        return _jsxs("section", { className: "panel", children: ["Unable to load dashboard: ", error] });
    }
    if (!dashboard || !agentStatus) {
        return _jsx("section", { className: "panel", children: "Loading dashboard..." });
    }
    const leakage = (dashboard.leakage_discovered || {});
    const pursuit = (dashboard.in_pursuit || {});
    const recovered = (dashboard.recovered_and_deposited || {});
    const deadlines = (dashboard.deadlines || {});
    const catalogHealth = (dashboard.catalog_health || {});
    const trend = (dashboard.earnings_trend || {});
    return (_jsxs("section", { className: "panel dashboard-panel", children: [_jsxs("header", { className: "dashboard-header", children: [_jsx("h2", { children: "Artist Recovery Dashboard" }), _jsx("p", { children: "Live recovery intelligence sourced from ingestion, anomaly, claims, and forecasting pipelines." })] }), _jsxs("div", { className: "kpi-grid", children: [_jsxs("article", { className: "kpi-card", children: [_jsx("span", { children: "Leakage discovered" }), _jsxs("strong", { children: ["$", Number(leakage.total_estimated_recoverable || 0).toFixed(2)] })] }), _jsxs("article", { className: "kpi-card", children: [_jsx("span", { children: "In pursuit" }), _jsxs("strong", { children: ["$", Number(pursuit.total_amount_in_pursuit || 0).toFixed(2)] })] }), _jsxs("article", { className: "kpi-card", children: [_jsx("span", { children: "Recovered and deposited" }), _jsxs("strong", { children: ["$", Number(recovered.total_deposited || 0).toFixed(2)] })] }), _jsxs("article", { className: "kpi-card", children: [_jsx("span", { children: "Urgent deadlines" }), _jsx("strong", { children: Number(deadlines.urgent_count || 0) })] })] }), _jsxs("div", { className: "split-grid", children: [_jsxs("article", { className: "panel nested", children: [_jsx("h3", { children: "Priority actions" }), _jsx("ul", { children: dashboard.priority_actions?.top_10_actions?.slice(0, 5).map((item, index) => (_jsxs("li", { children: [_jsx("strong", { children: String(item.kind || "action") }), " \u00B7 ", String(item.title || item.subtype || "Review item")] }, `${index}-${String(item.id || index)}`))) || _jsx("li", { children: "No actions yet. Upload more statements for stronger recovery signals." }) })] }), _jsxs("article", { className: "panel nested", children: [_jsx("h3", { children: "Agent status" }), _jsxs("p", { children: ["Step: ", agentStatus.agent_orchestra_status?.current_step || "idle"] }), _jsxs("p", { children: ["Confidence: ", agentStatus.agent_orchestra_status?.confidence ?? "n/a"] }), _jsxs("p", { children: ["Trace: ", agentStatus.agent_orchestra_status?.trace_url || "n/a"] }), _jsx("h4", { children: "Comfort messages" }), _jsx("ul", { children: (agentStatus.comfort_messages || []).slice(0, 3).map((msg, i) => (_jsx("li", { children: msg }, `comfort-${i}`))) })] }), _jsxs("article", { className: "panel nested", children: [_jsx("h3", { children: "Catalog and trend" }), _jsxs("p", { children: ["Catalog health score: ", Number(catalogHealth.health_score || 0).toFixed(1)] }), _jsxs("p", { children: ["Earnings trend: ", String(trend.trend || "INSUFFICIENT_DATA")] }), _jsxs("p", { children: ["Expected 90-day total: $", Number(trend.predicted_total || 0).toFixed(2)] })] })] })] }));
}
