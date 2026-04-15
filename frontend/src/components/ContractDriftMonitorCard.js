import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Contract Drift Monitor watches every contract you've ever signed and measures whether what actually came in matches what was agreed on paper. Every quarter it computes the gap — the contracted rate versus the actual effective rate — flags the ones that are silently decaying, and tells you when you're close to having a legitimate breach claim. Most artists never know their rates are drifting because no-one adds it up.";
const classColor = (c) => {
    if (c === "WITHIN_VARIANCE")
        return "#10B981";
    if (c === "SOFT_DRIFT")
        return "#FCD34D";
    if (c === "HARD_DRIFT")
        return "#F97316";
    return "#F87171";
};
const trendIcon = (t) => t === "WIDENING" ? "↗" : t === "NARROWING" ? "↘" : "→";
function DriftSparkline({ data }) {
    if (!data || data.length < 2)
        return null;
    const w = 120, h = 40;
    const maxR = Math.max(...data.map((d) => d.contracted_rate), 1);
    const pts = (arr) => arr.map((v, i) => `${(i / (arr.length - 1)) * w},${h - (v / maxR) * h}`).join(" ");
    const contracted = data.map((d) => d.contracted_rate);
    const actual = data.map((d) => d.actual_rate);
    const areaTop = actual.map((v, i) => `${(i / (actual.length - 1)) * w},${h - (v / maxR) * h}`).join(" ");
    const areaBottom = [...actual].reverse().map((v, i) => {
        const idx = actual.length - 1 - i;
        return `${(idx / (actual.length - 1)) * w},${h - (contracted[idx] / maxR) * h}`;
    }).join(" ");
    return (_jsxs("svg", { width: w, height: h, style: { display: "block" }, children: [_jsx("polygon", { points: `${areaTop} ${areaBottom}`, fill: "#F97316", opacity: "0.15" }), _jsx("polyline", { points: pts(contracted), fill: "none", stroke: "#C89B3C", strokeWidth: 1.5, strokeDasharray: "4 2" }), _jsx("polyline", { points: pts(actual), fill: "none", stroke: "#60A5FA", strokeWidth: 1.5 })] }));
}
export function ContractDriftMonitorCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [contracts, setContracts] = useState([]);
    const [expanded, setExpanded] = useState(null);
    const [disputing, setDisputing] = useState(null);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    async function load() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/contracts/drift`);
            if (!res.ok)
                throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setContracts(data.contracts ?? []);
            setState("done");
        }
        catch (e) {
            setError(String(e));
            setState("error");
        }
    }
    async function initiateDispute(contractId) {
        setDisputing(contractId);
        try {
            await fetch(`${BASE}/artists/${artistId}/contracts/${contractId}/drift/dispute`, { method: "POST" });
        }
        finally {
            setDisputing(null);
        }
    }
    const totalUnderpaid = contracts.reduce((s, c) => s + c.cumulative_underpayment, 0);
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Contract Drift Monitor" }), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "Monitor whether your contracted rates and actual payouts are in sync \u2014 every quarter." }), _jsx("button", { onClick: load, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Monitor My Contracts" })] })), state === "loading" && (_jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\uD83D\uDCCB Analysing contracts\u2026" })), state === "error" && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), state === "done" && (_jsx("div", { children: contracts.length === 0 ? (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("div", { style: { color: textSecondary, marginBottom: 8 }, children: "No contracts found." }), _jsx("div", { style: { fontSize: 12, color: "#6B7280" }, children: "Upload a contract under Settings to begin monitoring." })] })) : (_jsxs(_Fragment, { children: [totalUnderpaid > 0 && (_jsxs("div", { style: { background: "#491A03", border: "1px solid #92400E", borderRadius: 8, padding: 12, marginBottom: 16, textAlign: "center" }, children: [_jsxs("div", { style: { fontSize: 22, fontWeight: 700, color: "#F87171" }, children: ["$", totalUnderpaid.toLocaleString(undefined, { maximumFractionDigits: 2 })] }), _jsx("div", { style: { fontSize: 12, color: "#FDE68A" }, children: "Total cumulative underpayment across all contracts" })] })), contracts.map((c) => (_jsxs("div", { style: { marginBottom: 8, border: "1px solid #2D2D4E", borderRadius: 8, overflow: "hidden" }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", cursor: "pointer", background: "#111827" }, onClick: () => setExpanded(expanded === c.contract_id ? null : c.contract_id), children: [_jsx("div", { style: {
                                                width: 10, height: 10, borderRadius: "50%",
                                                background: classColor(c.classification), flexShrink: 0,
                                            } }), _jsxs("div", { style: { flex: 1 }, children: [_jsx("div", { style: { fontWeight: 600, fontSize: 13 }, children: c.payer_name }), _jsx("span", { style: {
                                                        color: classColor(c.classification), fontSize: 11,
                                                    }, children: c.classification.replace(/_/g, " ") })] }), _jsxs("div", { style: { textAlign: "right", flexShrink: 0 }, children: [_jsxs("div", { style: { fontSize: 13, fontWeight: 600, color: c.current_drift_pct > 5 ? "#F87171" : "#FCD34D" }, children: ["\u2212", c.current_drift_pct.toFixed(1), "%"] }), _jsxs("div", { style: { fontSize: 11, color: textSecondary }, children: [trendIcon(c.drift_trend), " ", c.drift_trend] })] }), _jsx("span", { style: { color: textSecondary, fontSize: 12 }, children: expanded === c.contract_id ? "▲" : "▼" })] }), expanded === c.contract_id && (_jsxs("div", { style: { background: "#0F172A", padding: "10px 14px" }, children: [_jsx(DriftSparkline, { data: c.quarterly_timeline }), _jsxs("div", { style: { display: "flex", gap: 16, fontSize: 11, marginTop: 6 }, children: [_jsx("span", { style: { color: amber }, children: "\u2500\u2500 Contracted" }), _jsx("span", { style: { color: "#60A5FA" }, children: "\u2500\u2500 Actual" })] }), _jsxs("div", { style: { marginTop: 8, fontSize: 12, color: textSecondary }, children: ["Cumulative underpayment:", " ", _jsxs("span", { style: { color: "#F87171", fontWeight: 700 }, children: ["$", c.cumulative_underpayment.toLocaleString(undefined, { maximumFractionDigits: 2 })] })] }), (c.classification === "BREACH_RISK" || c.classification === "HARD_DRIFT") && (_jsx("button", { onClick: () => initiateDispute(c.contract_id), disabled: disputing === c.contract_id, style: {
                                                marginTop: 10, background: "#7F1D1D", color: "#FCA5A5",
                                                border: "1px solid #991B1B", borderRadius: 6, padding: "6px 14px",
                                                fontSize: 12, cursor: "pointer",
                                            }, children: disputing === c.contract_id ? "Filing…" : "Initiate Dispute" }))] }))] }, c.contract_id)))] })) }))] }));
}
