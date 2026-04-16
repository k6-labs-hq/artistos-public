import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOOLTIP = "Every unmatched royalty has a deadline. After that deadline, the society redistributes the money to other rights holders — and it's gone forever. This clock shows exactly how much time remains for each of your open anomalies before that window closes. Green means you have time. Amber means act soon. Red means act now. Critical means today.";
const TIER_COLORS = {
    CRITICAL: "#EF4444",
    RED: "#EF4444",
    AMBER: "#C89B3C",
    GREEN: "#10B981",
    EXPIRED: "#6B7280",
};
const TIER_BORDER = {
    CRITICAL: "2px solid #EF4444",
    RED: "2px solid #EF4444",
    AMBER: "2px solid #C89B3C",
    GREEN: "none",
    EXPIRED: "none",
};
function formatCountdown(hours) {
    const d = Math.floor(hours / 24);
    const h = hours % 24;
    return `${d}d ${h}h`;
}
export function BlackBoxCountdownCard({ artistId }) {
    const [state, setState] = useState("idle");
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [tooltip, setTooltip] = useState(false);
    const intervalRef = useRef(null);
    const amber = "#C89B3C";
    const textSecondary = "#9CA3AF";
    async function load() {
        setState("loading");
        try {
            const res = await fetch(`${BASE}/artists/${artistId}/anomalies/countdown`);
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
    // Live timer refresh every minute
    useEffect(() => {
        if (state === "done") {
            intervalRef.current = setInterval(() => {
                setResult((prev) => {
                    if (!prev)
                        return prev;
                    return {
                        ...prev,
                        countdowns: prev.countdowns.map((c) => ({
                            ...c,
                            hours_remaining: Math.max(0, c.hours_remaining - 1),
                            days_remaining: Math.max(0, Math.floor((c.hours_remaining - 1) / 24)),
                        })),
                    };
                });
            }, 60_000);
        }
        return () => {
            if (intervalRef.current)
                clearInterval(intervalRef.current);
        };
    }, [state]);
    return (_jsxs("div", { style: { background: "#1A1A2E", border: "1px solid #2D2D4E", borderRadius: 12, padding: 24, color: "#F1F1F3", minWidth: 320 }, children: [_jsxs("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }, children: [_jsx("span", { style: { fontWeight: 700, fontSize: 16 }, children: "Black Box Countdown" }), _jsxs("span", { style: { cursor: "pointer", color: textSecondary, marginLeft: "auto" }, onMouseEnter: () => setTooltip(true), onMouseLeave: () => setTooltip(false), children: ["\u24D8", tooltip && (_jsx("span", { style: {
                                    position: "absolute", background: "#111827", border: "1px solid #374151",
                                    borderRadius: 8, padding: 12, maxWidth: 340, fontSize: 13, color: "#D1D5DB",
                                    zIndex: 100, lineHeight: 1.5,
                                }, children: TOOLTIP }))] })] }), state === "idle" && (_jsxs("div", { style: { textAlign: "center", padding: "24px 0" }, children: [_jsx("p", { style: { color: textSecondary, marginBottom: 16, fontSize: 14 }, children: "See exactly how much time remains before each royalty is redistributed and gone forever." }), _jsx("button", { onClick: load, style: { background: amber, color: "#000", border: "none", borderRadius: 8, padding: "10px 20px", fontWeight: 700, cursor: "pointer" }, children: "Show Countdown" })] })), state === "loading" && (_jsx("div", { style: { textAlign: "center", padding: "24px 0", color: textSecondary }, children: "\u23F0 Loading deadlines\u2026" })), state === "error" && _jsxs("div", { style: { color: "#F87171" }, children: ["Error: ", error] }), state === "done" && result && (_jsxs("div", { children: [_jsxs("div", { style: {
                            background: result.critical_count > 0 ? "#450A0A" : "#111827",
                            border: result.critical_count > 0 ? "1px solid #EF4444" : "1px solid #1F2937",
                            borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13,
                        }, children: [_jsxs("span", { style: { color: result.critical_count > 0 ? "#F87171" : textSecondary }, children: [_jsx("strong", { children: result.critical_count }), " anomal", result.critical_count !== 1 ? "ies" : "y", " at critical risk \u00B7\u00A0"] }), _jsxs("span", { style: { color: amber }, children: [_jsxs("strong", { children: ["$", result.at_risk_value_next_30_days.toLocaleString()] }), " at risk in the next 30 days"] })] }), _jsx("div", { style: { display: "flex", flexDirection: "column", gap: 8 }, children: result.countdowns.map((c) => (_jsxs("div", { style: {
                                background: "#111827",
                                borderLeft: TIER_BORDER[c.urgency_tier] || "none",
                                borderRadius: 8,
                                padding: 12,
                                animation: c.urgency_tier === "CRITICAL" ? "pulse-red 1.5s infinite" : undefined,
                            }, children: [_jsxs("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center" }, children: [_jsx("span", { style: {
                                                background: TIER_COLORS[c.urgency_tier] + "22",
                                                color: TIER_COLORS[c.urgency_tier],
                                                borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700,
                                            }, children: c.urgency_tier }), _jsx("span", { style: { color: TIER_COLORS[c.urgency_tier], fontWeight: 700, fontSize: 15 }, children: c.is_expired ? "EXPIRED" : formatCountdown(c.hours_remaining) })] }), _jsx("div", { style: { marginTop: 6, fontSize: 13, color: "#D1D5DB" }, children: c.society }), c.description && (_jsxs("div", { style: { fontSize: 12, color: textSecondary, marginTop: 2 }, children: [c.description.slice(0, 80), "\u2026"] })), _jsxs("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }, children: [_jsxs("span", { style: { color: amber, fontWeight: 600, fontSize: 13 }, children: ["$", c.estimated_at_risk_value.toLocaleString(), " at risk"] }), _jsx("button", { style: {
                                                background: "transparent", border: `1px solid ${TIER_COLORS[c.urgency_tier]}`,
                                                color: TIER_COLORS[c.urgency_tier], borderRadius: 6, padding: "3px 10px",
                                                fontSize: 12, cursor: "pointer",
                                            }, onClick: () => alert(`Drafting claim for anomaly ${c.anomaly_id}`), children: "Draft Claim Now" })] })] }, c.anomaly_id))) }), _jsxs("div", { style: { fontSize: 11, color: "#6B7280", marginTop: 12 }, children: ["Trust hash: ", result.chain_of_custody_hash?.slice(0, 16), "\u2026 \u00B7 Updates automatically every minute"] })] })), _jsx("style", { children: `
        @keyframes pulse-red {
          0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
          50% { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
        }
      ` })] }));
}
