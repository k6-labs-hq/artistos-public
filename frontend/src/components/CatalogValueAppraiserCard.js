import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DISCLAIMER = "This valuation is provided for informational purposes only and does not constitute a formal appraisal, legal advice, or a guarantee of sale or advance eligibility. Valuations are based on available data and proprietary models, which may not capture all factors affecting actual catalog market value. Consult qualified professionals before making financial decisions.";
const TOOLTIP = "Catalog Value Appraiser uses your net publishing share (NPS), performance and mechanical royalties, and a proprietary multiple that adjusts for catalog health, diversity, momentum, and recoverable upside. It gives you a real-world defensible estimate of what your catalog is worth today — and how much that number goes up once outstanding claims are collected.";
function WaterfallChart({ data }) {
    if (!data || data.length === 0)
        return null;
    const max = Math.max(...data.map((d) => Math.abs(d.cumulative)));
    const W = 280, barH = 22, gap = 6;
    const svgH = (barH + gap) * data.length + 10;
    return (_jsx("svg", { width: W, height: svgH, children: data.map((d, i) => {
            const isPositive = d.impact >= 0;
            const barLen = Math.abs(d.impact) / max * (W / 2 - 60);
            const baseX = W / 2;
            const barX = isPositive ? baseX : baseX - barLen;
            const y = i * (barH + gap);
            return (_jsxs("g", { children: [_jsx("text", { x: baseX - 4, y: y + barH * 0.7, textAnchor: "end", fill: "#9CA3AF", fontSize: 10, children: d.label.length > 16 ? d.label.slice(0, 14) + "…" : d.label }), _jsx("rect", { x: barX, y: y + 2, width: Math.max(barLen, 2), height: barH - 4, fill: isPositive ? "#10B981" : "#F87171", rx: 3 }), _jsxs("text", { x: baseX + barLen + 4, y: y + barH * 0.7, fill: isPositive ? "#10B981" : "#F87171", fontSize: 10, children: [isPositive ? "+" : "−", "$", Math.abs(d.impact).toLocaleString(undefined, { maximumFractionDigits: 0 })] })] }, d.label));
        }) }));
}
export function CatalogValueAppraiserCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [result, setResult] = useState(null);
    const [showDisclaimer, setShowDisclaimer] = useState(false);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    async function appraise() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/catalog/value-appraisal`, { method: "POST" });
            if (!res.ok)
                throw new Error(`HTTP ${res.status}`);
            setResult(await res.json());
            setState("done");
        }
        catch (e) {
            setError(String(e));
            setState("error");
        }
    }
    const fmt = (v) => v === undefined || v === null
        ? "—"
        : "$" + v.toLocaleString(undefined, { maximumFractionDigits: 0 });
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Catalog Value Appraiser" }), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "Get a defensible market-value estimate for your catalog with recovery upside included." }), _jsx("button", { onClick: appraise, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Appraise My Catalog" })] })), state === "loading" && (_jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\uD83D\uDCD0 Calculating catalog value\u2026" })), state === "error" && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), state === "done" && result && (_jsxs("div", { children: [_jsxs("div", { style: { background: "#111827", borderRadius: 10, padding: 16, marginBottom: 14, textAlign: "center" }, children: [_jsx("div", { style: { fontSize: 11, color: textSecondary, marginBottom: 4 }, children: "Estimated Catalog Value" }), _jsxs("div", { style: { fontWeight: 800, fontSize: 26, color: amber, letterSpacing: -0.5 }, children: [fmt(result.valuation_low), "\u2013", fmt(result.valuation_high)] }), _jsxs("div", { style: { fontSize: 13, color: textSecondary, marginTop: 4 }, children: ["Expected: ", _jsx("span", { style: { color: "#F1F1F3", fontWeight: 600 }, children: fmt(result.valuation_expected) }), " ", "\u00B7 Multiple: ", result.multiple_applied_low, "\u00D7\u2013", result.multiple_applied_high, "\u00D7"] })] }), result.recovery_upside_value > 0 && (_jsx("div", { style: { background: "#064E3B", border: "1px solid #047857", borderRadius: 8, padding: 10, marginBottom: 14 }, children: _jsxs("div", { style: { fontSize: 12, color: "#6EE7B7" }, children: [_jsxs("b", { children: ["+", fmt(result.recovery_upside_value)] }), " recovery upside included \u2014 ", " ", "once outstanding claims are collected, your catalog is worth that much more."] }) })), _jsxs("div", { style: { marginBottom: 14 }, children: [_jsx("div", { style: { fontSize: 12, color: textSecondary, marginBottom: 6 }, children: "Value Bridge" }), _jsx(WaterfallChart, { data: result.waterfall })] }), _jsxs("div", { style: { display: "flex", gap: 8, marginBottom: 14 }, children: [_jsxs("div", { style: { flex: 1 }, children: [_jsx("div", { style: { fontSize: 11, color: "#6EE7B7", marginBottom: 4 }, children: "Value Drivers" }), result.key_value_drivers.map((d, i) => (_jsxs("div", { style: { fontSize: 11, color: "#D1D5DB", marginBottom: 3 }, children: ["\u2191 ", d] }, i)))] }), _jsxs("div", { style: { flex: 1 }, children: [_jsx("div", { style: { fontSize: 11, color: "#F87171", marginBottom: 4 }, children: "Value Risks" }), result.key_value_risks.map((r, i) => (_jsxs("div", { style: { fontSize: 11, color: "#D1D5DB", marginBottom: 3 }, children: ["\u2193 ", r] }, i)))] })] }), _jsx("div", { style: { fontSize: 12, color: textSecondary, lineHeight: 1.6, marginBottom: 10 }, children: result.narrative }), _jsxs("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #2D2D4E", paddingTop: 8 }, children: [_jsx("button", { onClick: () => setShowDisclaimer(!showDisclaimer), style: { background: "none", border: "none", color: "#6B7280", fontSize: 11, cursor: "pointer" }, children: showDisclaimer ? "Hide disclaimer" : "Disclaimer ⓘ" }), _jsx("div", { style: { display: "flex", gap: 8 }, children: _jsx("button", { onClick: () => alert("PNG export —  generates a branded shareable summary"), style: { background: "transparent", border: `1px solid ${amber}`, color: amber, borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer" }, children: "Share / Export" }) })] }), showDisclaimer && (_jsx("div", { style: { marginTop: 8, fontSize: 11, color: "#6B7280", lineHeight: 1.5 }, children: DISCLAIMER })), _jsxs("div", { style: { fontSize: 11, color: "#374151", marginTop: 4 }, children: ["Trust hash: ", result.chain_of_custody_hash?.slice(0, 16), "\u2026"] })] }))] }));
}
