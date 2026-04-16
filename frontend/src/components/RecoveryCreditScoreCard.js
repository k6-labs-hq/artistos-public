import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Your Recovery Credit Score is a 0–850 proprietary rating across 7 dimensions: catalog health, anomaly recoverability, statute-of-limitations safety margin, contract clarity, payer reliability, territory coverage, and platform diversification. It determines advance eligibility and the maximum advance you qualify for. The higher your score, the larger the advance — and the more confidently we can recover what's yours.";
const compMeta = {
    catalog_health: "Catalog Health",
    anomaly_recoverability: "Anomaly Recoverability",
    sol_safety: "SoL Safety",
    contract_clarity: "Contract Clarity",
    payer_reliability: "Payer Reliability",
    territory_coverage: "Territory Coverage",
    platform_diversification: "Platform Diversification",
};
const tierColor = (tier) => {
    if (tier === "EXCEPTIONAL")
        return "#10B981";
    if (tier === "STRONG")
        return "#34D399";
    if (tier === "GOOD")
        return "#FCD34D";
    if (tier === "FAIR")
        return "#F97316";
    if (tier === "DEVELOPING")
        return "#F87171";
    return "#9CA3AF";
};
const SCORE_STOPS = [
    { label: "LIMITED", min: 0, max: 299 },
    { label: "DEVELOPING", min: 300, max: 449 },
    { label: "FAIR", min: 450, max: 549 },
    { label: "GOOD", min: 550, max: 649 },
    { label: "STRONG", min: 650, max: 749 },
    { label: "EXCEPTIONAL", min: 750, max: 850 },
];
function ScoreGauge({ score, tier }) {
    const pct = score / 850;
    const R = 52;
    const circ = Math.PI * R; // half-circle
    const stroke = circ * pct;
    const color = tierColor(tier);
    return (_jsxs("svg", { width: 130, height: 70, viewBox: "0 0 130 80", style: { overflow: "visible" }, children: [_jsx("path", { d: `M 15 70 A ${R} ${R} 0 0 1 115 70`, fill: "none", stroke: "#1F2937", strokeWidth: 10 }), _jsx("path", { d: `M 15 70 A ${R} ${R} 0 0 1 115 70`, fill: "none", stroke: color, strokeWidth: 10, strokeDasharray: `${stroke} ${circ - stroke}`, strokeLinecap: "round" }), _jsx("text", { x: 65, y: 66, textAnchor: "middle", fill: color, fontSize: 22, fontWeight: "bold", children: score }), _jsx("text", { x: 65, y: 80, textAnchor: "middle", fill: color, fontSize: 10, children: tier })] }));
}
export function RecoveryCreditScoreCard({ artistId }) {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const [expandedComp, setExpandedComp] = useState(null);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    useEffect(() => {
        fetch(`${BASE}/artists/${artistId}/recovery-score`)
            .then((r) => {
            if (!r.ok)
                throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
            .then((d) => { setResult(d); setLoading(false); })
            .catch((e) => { setError(String(e)); setLoading(false); });
    }, [artistId]);
    function ComponentBar({ name, comp }) {
        const pct = (comp.score / comp.max) * 100;
        const label = compMeta[name] ?? name;
        const isHelping = comp.score / comp.max >= 0.6;
        return (_jsxs("div", { style: { marginBottom: 8, cursor: "pointer" }, onClick: () => setExpandedComp(expandedComp === name ? null : name), children: [_jsxs("div", { style: { display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }, children: [_jsx("span", { style: { color: isHelping ? "#D1D5DB" : "#F87171" }, children: label }), _jsxs("span", { style: { color: amber }, children: [comp.score, "/", comp.max] })] }), _jsx("div", { style: { background: "#1F2937", borderRadius: 4, height: 6, overflow: "hidden" }, children: _jsx("div", { style: {
                            width: `${pct}%`, height: "100%",
                            background: pct >= 80 ? "#10B981" : pct >= 60 ? "#FCD34D" : "#F87171",
                        } }) }), expandedComp === name && (_jsx("div", { style: { fontSize: 11, color: textSecondary, marginTop: 4, lineHeight: 1.5 }, children: comp.explanation }))] }));
    }
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Recovery Credit Score" }), result && (_jsx("span", { style: {
                            marginLeft: 4, background: tierColor(result.tier) + "22",
                            color: tierColor(result.tier), borderRadius: 20, padding: "2px 10px", fontSize: 12, fontWeight: 700,
                        }, children: result.score })), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), loading && _jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\u26A1 Calculating score\u2026" }), error && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), result && (_jsxs("div", { children: [_jsx("div", { style: { display: "flex", justifyContent: "center", marginBottom: 12 }, children: _jsx(ScoreGauge, { score: result.score, tier: result.tier }) }), _jsxs("div", { style: { textAlign: "center", marginBottom: 14 }, children: [result.score_delta !== 0 && (_jsxs("span", { style: {
                                    fontSize: 12, fontWeight: 700,
                                    color: result.score_delta > 0 ? "#10B981" : "#F87171",
                                }, children: [result.score_delta > 0 ? `↑ +${result.score_delta}` : `↓ ${result.score_delta}`, " pts since last calc"] })), _jsxs("span", { style: { fontSize: 12, color: textSecondary, marginLeft: 8 }, children: ["Trend: ", result.trend] })] }), result.max_advance_amount !== undefined && result.max_advance_amount > 0 && (_jsxs("div", { style: {
                            background: "#1C3055", border: "1px solid #1E40AF",
                            borderRadius: 8, padding: 10, marginBottom: 14, textAlign: "center",
                        }, children: [_jsx("div", { style: { fontSize: 11, color: "#93C5FD" }, children: "Advance Eligibility" }), _jsxs("div", { style: { fontSize: 20, fontWeight: 700, color: "#60A5FA" }, children: ["Up to $", result.max_advance_amount.toLocaleString()] })] })), _jsxs("div", { style: { marginBottom: 14 }, children: [_jsx("div", { style: { fontSize: 12, color: textSecondary, marginBottom: 8 }, children: "Score Breakdown" }), Object.keys(compMeta).map((k) => (_jsx(ComponentBar, { name: k, comp: result.components[k] }, k)))] }), result.actions.length > 0 && (_jsxs("div", { style: { marginBottom: 14 }, children: [_jsx("div", { style: { fontSize: 12, color: textSecondary, marginBottom: 6 }, children: "Top Actions to Improve Score" }), result.actions.map((a, i) => (_jsxs("div", { style: {
                                    background: "#111827", borderRadius: 7, padding: "8px 10px",
                                    marginBottom: 6, display: "flex", gap: 10, alignItems: "flex-start",
                                }, children: [_jsx("span", { style: { background: amber, color: "#000", borderRadius: "50%", width: 18, height: 18, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, flexShrink: 0 }, children: a.priority }), _jsxs("div", { style: { flex: 1 }, children: [_jsx("div", { style: { fontSize: 12 }, children: a.action }), _jsxs("div", { style: { fontSize: 11, color: "#6EE7B7" }, children: ["+", a.impact, " pts \u00B7 via ", a.module] })] })] }, i)))] })), _jsx("div", { style: { fontSize: 12, color: textSecondary, lineHeight: 1.6, marginBottom: 10 }, children: result.narrative }), _jsxs("div", { style: { fontSize: 11, color: "#374151" }, children: ["Trust hash: ", result.chain_of_custody_hash?.slice(0, 16), "\u2026"] })] }))] }));
}
