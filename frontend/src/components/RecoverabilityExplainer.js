import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from "react";
function money(value) {
    return `$${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}
function itemAmount(row) {
    if (!row)
        return 0;
    if (typeof row.amount === "number")
        return row.amount;
    if (typeof row.estimated_recoverable === "number")
        return row.estimated_recoverable;
    return 0;
}
export function RecoverabilityExplainer({ title = "Recoverability Explainer", recoverableAmount, expiredAmount, byClass, eventDate, expirationDate, discoveryDate, claimWindowLabel = "Varies by payer/society", probabilityNarrative, contractClauseCitation, compact = false, }) {
    const [showDetails, setShowDetails] = useState(false);
    const timelineItems = useMemo(() => [
        { key: "event", label: "Event date", value: eventDate || "Unknown", state: "neutral" },
        { key: "expiration", label: "Expiration date", value: expirationDate || "Contract-governed or unknown", state: expiredAmount > 0 ? "expired" : "active" },
        { key: "discovery", label: "Discovery date", value: discoveryDate || new Date().toISOString().slice(0, 10), state: "active" },
        { key: "claim", label: "Claim window", value: claimWindowLabel, state: recoverableAmount > 0 ? "active" : "neutral" },
    ], [eventDate, expirationDate, discoveryDate, claimWindowLabel, expiredAmount, recoverableAmount]);
    const topRule = useMemo(() => {
        if (!byClass)
            return "ASCAP redistributes unmatched royalties after 2-3 years.";
        if (byClass["Expired (Black-Box Redistributed)"]) {
            return "Foreign societies often redistribute unmatched royalties after 6-18 months.";
        }
        return "MLC redistributes unmatched digital mechanicals after 3 years.";
    }, [byClass]);
    const classEntries = Object.entries(byClass || {});
    return (_jsxs("section", { className: `recoverability-explainer ${compact ? "compact" : ""}`, "data-reveal": "true", children: [_jsxs("header", { className: "recoverability-head", children: [_jsx("h3", { children: title }), _jsx("button", { type: "button", className: "learn-more-btn", onClick: () => setShowDetails(true), children: "Learn more" })] }), _jsxs("div", { className: "recoverability-grid", children: [_jsxs("article", { className: "recoverability-card can-recover", title: "Recoverable, contract-based, and copyright-damages classes are actionable.", children: [_jsx("p", { className: "label", children: "Here is what you can still recover" }), _jsx("strong", { children: money(recoverableAmount) }), _jsx("p", { children: "XR7 can still pursue this through claim windows, contract enforcement, or damages pathways." })] }), _jsxs("article", { className: "recoverability-card expired", title: "Expired amounts are generally redistributed by payer/society black-box rules.", children: [_jsx("p", { className: "label", children: "Here is what expired" }), _jsx("strong", { children: money(expiredAmount) }), _jsx("p", { children: "These funds likely crossed redistribution windows and are now prevention signals." })] }), _jsxs("article", { className: "recoverability-card why", title: "Rule logic depends on payer/society and royalty type.", children: [_jsx("p", { className: "label", children: "Here is why" }), _jsx("p", { children: topRule }), _jsx("p", { children: "Rule windows are applied to event date, then compared to discovery date." }), probabilityNarrative && _jsx("p", { children: probabilityNarrative }), contractClauseCitation && _jsxs("p", { children: ["Contract clause: ", contractClauseCitation] })] }), _jsxs("article", { className: "recoverability-card prevention", title: "Expired and low-confidence anomalies still improve future recovery outcomes.", children: [_jsx("p", { className: "label", children: "Here is what XR7 prevents going forward" }), _jsxs("ul", { children: [_jsx("li", { children: "Metadata repair" }), _jsx("li", { children: "Identifier normalization" }), _jsx("li", { children: "Cross-system linking" }), _jsx("li", { children: "Future leakage prevention" }), _jsx("li", { children: "UGC fingerprinting" }), _jsx("li", { children: "Foreign society crosswalks" })] })] })] }), _jsx("div", { className: "recoverability-timeline", "aria-label": "Recoverability timeline", children: timelineItems.map((item) => (_jsxs("div", { className: `timeline-item ${item.state}`, children: [_jsx("span", { className: "dot" }), _jsxs("div", { children: [_jsx("p", { children: item.label }), _jsx("strong", { children: item.value })] })] }, item.key))) }), classEntries.length > 0 && (_jsx("div", { className: "recoverability-class-grid", children: classEntries.map(([key, value]) => (_jsxs("article", { className: "class-row", children: [_jsx("span", { children: key }), _jsx("strong", { children: money(itemAmount(value)) }), _jsxs("small", { children: [Number(value.count || 0), " items"] })] }, key))) })), showDetails && (_jsx("div", { className: "recoverability-modal-backdrop", role: "dialog", "aria-modal": "true", "aria-label": "Recoverability details", children: _jsxs("div", { className: "recoverability-modal", children: [_jsx("h4", { children: "Recoverability details" }), _jsx("p", { children: "XR7 classifies anomalies into recoverable, contract-based, expired black-box, copyright damages, and future-prevention classes. Claim drafting is enabled only for the legally actionable classes." }), _jsxs("ul", { children: [_jsx("li", { children: "ASCAP redistributes unmatched royalties after 2-3 years." }), _jsx("li", { children: "MLC redistributes unmatched digital mechanicals after 3 years." }), _jsx("li", { children: "Foreign societies often redistribute after 6-18 months." }), _jsx("li", { children: "Studio backend and streaming reuse are contract-governed." })] }), _jsx("button", { type: "button", className: "learn-more-btn", onClick: () => setShowDetails(false), children: "Close" })] }) }))] }));
}
