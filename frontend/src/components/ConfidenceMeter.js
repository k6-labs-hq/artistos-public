import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function ConfidenceMeter({ value, label = "Confidence" }) {
    const normalized = Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0));
    const pct = Math.round(normalized * 100);
    const angle = -90 + 180 * normalized;
    const color = pct >= 75 ? "#10b981" : pct >= 50 ? "#f59e0b" : "#ef4444";
    return (_jsxs("article", { className: "sovereignty-card confidence-meter", "aria-label": `${label} ${pct} percent`, children: [_jsx("h3", { children: label }), _jsxs("svg", { viewBox: "0 0 220 140", role: "img", "aria-hidden": "true", children: [_jsx("path", { d: "M20 110 A90 90 0 0 1 200 110", fill: "none", stroke: "#334155", strokeWidth: "16", strokeLinecap: "round" }), _jsx("path", { d: "M20 110 A90 90 0 0 1 200 110", fill: "none", stroke: color, strokeWidth: "16", strokeLinecap: "round", strokeDasharray: `${Math.PI * 90 * normalized} ${Math.PI * 90}` }), _jsx("line", { x1: "110", y1: "110", x2: 110 + 72 * Math.cos((Math.PI * angle) / 180), y2: 110 + 72 * Math.sin((Math.PI * angle) / 180), stroke: color, strokeWidth: "6", strokeLinecap: "round" }), _jsx("circle", { cx: "110", cy: "110", r: "8", fill: color }), _jsxs("text", { x: "110", y: "96", textAnchor: "middle", fill: "#e2e8f0", fontSize: "30", fontWeight: "800", children: [pct, "%"] })] }), _jsx("p", { children: "Model confidence for current recovery prioritization and payout likelihood." })] }));
}
