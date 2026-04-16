import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "This scan looks for works in your catalog that exist everywhere they should — registered with your PRO, live on streaming platforms — but have gone completely silent with zero dollars returned during periods when they should have been generating income. These aren't underpayments. They are works the system has completely forgotten about. Finding them is the first step to getting them paid.";
const CAUSE_LABELS = {
    metadata_mismatch: "Metadata Mismatch",
    registration_gap: "Registration Gap",
    routing_failure: "Routing Failure",
    dsp_attribution_error: "DSP Attribution Error",
    unknown: "Unknown",
};
export function GhostCatalogDetectorCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    async function runScan() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/catalog/ghost-scan`, { method: "POST" });
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
    function scoreColor(score) {
        if (score >= 0.85)
            return "#F87171";
        if (score >= 0.60)
            return "#FB923C";
        return amber;
    }
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Ghost Catalog Detector" }), result && (_jsxs("span", { style: { background: "#F87171", color: "#fff", borderRadius: 999, padding: "2px 10px", fontSize: 12, fontWeight: 700 }, children: [result.ghost_count, " ghost", result.ghost_count !== 1 ? "s" : ""] })), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "Scan for works present everywhere but paying nothing." }), _jsx("button", { onClick: runScan, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Run Scan" })] })), state === "loading" && (_jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\uD83D\uDC7B Scanning your catalog for ghost works\u2026" })), state === "error" && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), state === "done" && result && (_jsxs("div", { children: [_jsxs("div", { style: { background: "#111827", borderRadius: 8, padding: 12, marginBottom: 16, display: "flex", justifyContent: "space-between" }, children: [_jsx("span", { style: { color: textSecondary, fontSize: 13 }, children: "Total missing value" }), _jsxs("span", { style: { color: amber, fontWeight: 700, fontSize: 18 }, children: ["$", result.total_estimated_missing_value.toLocaleString("en-US", { minimumFractionDigits: 2 })] })] }), result.ghost_works.length === 0 ? (_jsx("p", { style: { color: textSecondary, textAlign: "center" }, children: "No ghost works detected. \uD83D\uDC7B" })) : (_jsx("div", { style: { display: "flex", flexDirection: "column", gap: 10 }, children: result.ghost_works.map((work) => (_jsxs("div", { style: {
                                background: "#111827",
                                border: `1px solid ${work.auto_escalate ? "#F87171" : "#374151"}`,
                                borderRadius: 8,
                                padding: 12,
                                opacity: 0.9,
                                position: "relative",
                            }, children: [_jsx("div", { style: { position: "absolute", top: 8, right: 10, opacity: 0.3, fontSize: 20 }, children: "\uD83D\uDC7B" }), _jsx("div", { style: { fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#D1D5DB" }, children: work.title }), work.isrc && _jsxs("div", { style: { fontSize: 11, color: textSecondary }, children: ["ISRC: ", work.isrc] }), _jsxs("div", { style: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }, children: [_jsxs("span", { style: {
                                                background: scoreColor(work.ghost_score) + "22",
                                                color: scoreColor(work.ghost_score),
                                                borderRadius: 4, padding: "2px 8px", fontSize: 11,
                                            }, children: ["Score: ", Math.round(work.ghost_score * 100), "%"] }), _jsx("span", { style: { background: "#1F2937", color: textSecondary, borderRadius: 4, padding: "2px 8px", fontSize: 11 }, children: CAUSE_LABELS[work.suspected_cause] || work.suspected_cause }), _jsxs("span", { style: { background: "#1F2937", color: amber, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700 }, children: ["$", work.estimated_missing_value.toLocaleString()] })] }), _jsxs("div", { style: { fontSize: 12, color: "#6B7280", marginTop: 6 }, children: ["Silent since: ", work.ghost_start_date.slice(0, 10)] }), _jsx("button", { style: {
                                        marginTop: 10, background: "transparent", border: `1px solid ${amber}`,
                                        color: amber, borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer",
                                    }, onClick: () => alert(`Draft claim for: ${work.title} — hands off to Claims Orchestration`), children: "Draft Claim \u2192" })] }, work.work_id))) })), _jsxs("div", { style: { fontSize: 11, color: "#6B7280", marginTop: 12 }, children: ["Trust hash: ", result.chain_of_custody_hash?.slice(0, 16), "\u2026"] })] }))] }));
}
