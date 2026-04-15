import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "This analysis reconstructs what you would have earned if your catalog had always been clean — every royalty correctly paid, every identifier properly registered, every split correct from day one. The gap between that number and what you actually received is your estimated lifetime leakage. This is not a guarantee of recovery — it is a map of what the system cost you.";
export function EarningsTimeMachineCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    async function runAnalysis() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/earnings/time-machine`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ granularity: "year" }),
            });
            if (!res.ok)
                throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setResult(data);
            setState("done");
        }
        catch (e) {
            setError(String(e));
            setState("error");
        }
    }
    const amber = "#C89B3C";
    const amberFaded = "#C89B3C33";
    const textSecondary = "#9CA3AF";
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Earnings Time Machine" }), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, userSelect: "none" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "Reconstruct your lifetime earnings as if the system had always worked correctly." }), _jsx("button", { onClick: runAnalysis, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Run Analysis" })] })), state === "loading" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: [_jsx("div", { style: { marginBottom: 8 }, children: "\u23F3 Analysing your earnings history\u2026" }), _jsx("div", { style: { fontSize: 13 }, children: "Estimated time: 10\u201330 seconds" })] })), state === "error" && (_jsxs("div", { style: { color: "#F87171", padding: "16px 0" }, children: ["Error: ", error] })), state === "done" && result && (_jsxs("div", { children: [_jsx("p", { style: { fontSize: 13, color: "#D1D5DB", marginBottom: 16, lineHeight: 1.5 }, children: result.summary }), _jsxs("div", { style: { background: "#111827", borderRadius: 8, padding: 16, marginBottom: 16, textAlign: "center" }, children: [_jsxs("div", { style: { fontSize: 28, fontWeight: 800, color: amber }, children: ["$", result.total_lifetime_leakage.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })] }), _jsx("div", { style: { fontSize: 13, color: textSecondary }, children: "Estimated Lifetime Leakage" }), _jsxs("div", { style: { fontSize: 12, color: textSecondary, marginTop: 4 }, children: ["Low: $", result.confidence_band.low.toLocaleString(), " \u00B7 Expected: $", result.confidence_band.expected.toLocaleString(), " \u00B7 High: $", result.confidence_band.high.toLocaleString()] })] }), result.time_series.length > 0 && (_jsx(DivergingTimeline, { timeSeries: result.time_series })), _jsxs("table", { style: { width: "100%", fontSize: 12, borderCollapse: "collapse", marginTop: 16 }, children: [_jsx("thead", { children: _jsxs("tr", { style: { color: textSecondary }, children: [_jsx("th", { style: { textAlign: "left", paddingBottom: 4 }, children: "Period" }), _jsx("th", { style: { textAlign: "right" }, children: "Actual" }), _jsx("th", { style: { textAlign: "right" }, children: "Clean World" }), _jsx("th", { style: { textAlign: "right", color: amber }, children: "Leakage" })] }) }), _jsx("tbody", { children: result.time_series.map((row) => (_jsxs("tr", { style: { borderTop: "1px solid #1F2937" }, children: [_jsx("td", { style: { padding: "6px 0" }, children: row.period }), _jsxs("td", { style: { textAlign: "right" }, children: ["$", row.actual_earned.toLocaleString()] }), _jsxs("td", { style: { textAlign: "right" }, children: ["$", row.estimated_clean_world_earned.toLocaleString()] }), _jsxs("td", { style: { textAlign: "right", color: amber }, children: ["$", row.delta.toLocaleString()] })] }, row.period))) })] }), _jsxs("div", { style: { fontSize: 11, color: "#6B7280", marginTop: 12 }, children: ["Trust hash: ", result.chain_of_custody_hash?.slice(0, 16), "\u2026"] })] }))] }));
}
function DivergingTimeline({ timeSeries }) {
    const width = 480;
    const height = 160;
    const pad = { top: 10, right: 10, bottom: 20, left: 40 };
    const W = width - pad.left - pad.right;
    const H = height - pad.top - pad.bottom;
    const maxVal = Math.max(...timeSeries.map((d) => d.estimated_clean_world_earned), 1);
    const xStep = W / Math.max(timeSeries.length - 1, 1);
    const px = (i) => pad.left + i * xStep;
    const py = (v) => pad.top + H - (v / maxVal) * H;
    const actualPath = timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.actual_earned)}`).join(" ");
    const cleanPath = timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.estimated_clean_world_earned)}`).join(" ");
    // Shaded area between actual and clean
    const areaPath = [
        ...timeSeries.map((d, i) => `${i === 0 ? "M" : "L"} ${px(i)} ${py(d.estimated_clean_world_earned)}`),
        ...[...timeSeries].reverse().map((d, i) => `L ${px(timeSeries.length - 1 - i)} ${py(d.actual_earned)}`),
        "Z",
    ].join(" ");
    return (_jsxs("svg", { viewBox: `0 0 ${width} ${height}`, style: { width: "100%", maxWidth: width }, children: [_jsx("defs", { children: _jsxs("linearGradient", { id: "leak-gradient", x1: "0", y1: "0", x2: "0", y2: "1", children: [_jsx("stop", { offset: "0%", stopColor: "#C89B3C", stopOpacity: "0.4" }), _jsx("stop", { offset: "100%", stopColor: "#C89B3C", stopOpacity: "0.05" })] }) }), _jsx("path", { d: areaPath, fill: "url(#leak-gradient)" }), _jsx("path", { d: cleanPath, stroke: "#C89B3C", strokeWidth: "2", fill: "none" }), _jsx("path", { d: actualPath, stroke: "#60A5FA", strokeWidth: "2", fill: "none" }), timeSeries.map((d, i) => (_jsx("text", { x: px(i), y: height - 4, textAnchor: "middle", fontSize: "10", fill: "#6B7280", children: d.period }, d.period))), _jsx("text", { x: 2, y: pad.top + 6, fontSize: "9", fill: "#C89B3C", children: "Clean World" }), _jsx("text", { x: 2, y: pad.top + 16, fontSize: "9", fill: "#60A5FA", children: "Actual" })] }));
}
