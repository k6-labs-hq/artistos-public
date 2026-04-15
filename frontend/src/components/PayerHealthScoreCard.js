import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Your Payer Health Score turns every source of revenue into a rated counterparty. We look at how accurately they pay, how often they redistribute on time, whether rates are drifting lower than contracted, how they resolve disputes, and the quality of their data. The combined score tells you exactly who you can trust and who needs to be watched — before the money stops coming.";
const tierColor = (tier) => {
    if (tier === "TRUSTED")
        return "#10B981";
    if (tier === "RELIABLE")
        return "#6EE7B7";
    if (tier === "WATCH")
        return "#FCD34D";
    if (tier === "ELEVATED_RISK")
        return "#F97316";
    return "#F87171";
};
const subLabel = {
    payment_accuracy: "Payment Accuracy",
    redistribution_timing: "Redistribution Timing",
    rate_drift: "Rate Drift",
    dispute_resolution: "Dispute Resolution",
    data_quality: "Data Quality",
};
const subMax = {
    payment_accuracy: 25,
    redistribution_timing: 20,
    rate_drift: 20,
    dispute_resolution: 20,
    data_quality: 15,
};
export function PayerHealthScoreCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [payers, setPayers] = useState([]);
    const [expanded, setExpanded] = useState(null);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    async function fetchScores() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/payers/health`);
            if (!res.ok)
                throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setPayers(data.payers ?? []);
            setState("done");
        }
        catch (e) {
            setError(String(e));
            setState("error");
        }
    }
    function MiniSparkline({ data }) {
        if (!data || data.length < 2)
            return _jsx("span", { style: { color: textSecondary, fontSize: 11 }, children: "\u2014" });
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;
        const w = 48, h = 20;
        const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(" ");
        const trend = data[data.length - 1] - data[0];
        return (_jsx("svg", { width: w, height: h, style: { display: "inline-block" }, children: _jsx("polyline", { points: pts, fill: "none", stroke: trend >= 0 ? "#10B981" : "#F87171", strokeWidth: 1.5 }) }));
    }
    function GaugeMini({ value }) {
        const pct = value / 100;
        const r = 16;
        const circ = 2 * Math.PI * r;
        const stroke = circ * pct;
        const color = value >= 80 ? "#10B981" : value >= 60 ? "#FCD34D" : value >= 40 ? "#F97316" : "#F87171";
        return (_jsxs("svg", { width: 40, height: 40, viewBox: "0 0 40 40", children: [_jsx("circle", { cx: 20, cy: 20, r: r, fill: "none", stroke: "#1F2937", strokeWidth: 4 }), _jsx("circle", { cx: 20, cy: 20, r: r, fill: "none", stroke: color, strokeWidth: 4, strokeDasharray: `${stroke} ${circ - stroke}`, strokeLinecap: "round", transform: "rotate(-90 20 20)" }), _jsx("text", { x: 20, y: 24, textAnchor: "middle", fill: color, fontSize: 10, fontWeight: "bold", children: Math.round(value) })] }));
    }
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Payer Health Score" }), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "Rate every payer 0\u2013100 on reliability, timing, accuracy, and data quality." }), _jsx("button", { onClick: fetchScores, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Score My Payers" })] })), state === "loading" && (_jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\uD83D\uDCCA Scoring your payers\u2026" })), state === "error" && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), state === "done" && (_jsx("div", { children: payers.length === 0 ? (_jsx("div", { style: { color: textSecondary, textAlign: "center" }, children: "No payer data found." })) : (payers.sort((a, b) => a.total_score - b.total_score).map((p) => (_jsxs("div", { style: { marginBottom: 8, border: "1px solid #2D2D4E", borderRadius: 8, overflow: "hidden" }, children: [_jsxs("div", { style: {
                                display: "flex", alignItems: "center", gap: 10, padding: "10px 12px",
                                cursor: "pointer", background: "#111827",
                            }, onClick: () => setExpanded(expanded === p.payer_id ? null : p.payer_id), children: [_jsx(GaugeMini, { value: p.total_score }), _jsxs("div", { style: { flex: 1 }, children: [_jsx("div", { style: { fontWeight: 600, fontSize: 13 }, children: p.payer_name }), _jsx("span", { style: {
                                                background: tierColor(p.risk_tier) + "22",
                                                color: tierColor(p.risk_tier), fontSize: 11, borderRadius: 4, padding: "1px 7px",
                                            }, children: p.risk_tier.replace(/_/g, " ") })] }), _jsx(MiniSparkline, { data: p.trend }), _jsx("span", { style: { color: textSecondary, fontSize: 12 }, children: expanded === p.payer_id ? "▲" : "▼" })] }), expanded === p.payer_id && (_jsxs("div", { style: { background: "#0F172A", padding: "10px 14px" }, children: [Object.keys(subLabel).map((k) => {
                                    const val = p.sub_scores[k];
                                    const max = subMax[k];
                                    const pct = (val / max) * 100;
                                    return (_jsxs("div", { style: { marginBottom: 6 }, children: [_jsxs("div", { style: { display: "flex", justifyContent: "space-between", fontSize: 11 }, children: [_jsx("span", { children: subLabel[k] }), _jsxs("span", { style: { color: amber }, children: [val, "/", max] })] }), _jsx("div", { style: { background: "#1F2937", borderRadius: 4, height: 5, overflow: "hidden" }, children: _jsx("div", { style: {
                                                        width: `${pct}%`, height: "100%",
                                                        background: pct >= 80 ? "#10B981" : pct >= 60 ? "#FCD34D" : "#F87171",
                                                    } }) })] }, k));
                                }), p.flags.length > 0 && (_jsx("div", { style: { marginTop: 8, fontSize: 11, color: "#F87171" }, children: p.flags.map((f, i) => _jsxs("div", { children: ["\u26A0 ", f] }, i)) }))] }))] }, p.payer_id)))) }))] }));
}
