import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
function asPct(v) {
    return `${Math.round(Math.max(0, Math.min(1, v)) * 100)}%`;
}
export function PayerScorecard({ rows }) {
    const items = rows.length
        ? rows
        : [
            { payer: "ASCAP", responsiveness: 0.72, resistance: 0.28 },
            { payer: "Distributor", responsiveness: 0.43, resistance: 0.57 },
            { payer: "Platform", responsiveness: 0.61, resistance: 0.39 },
        ];
    return (_jsxs("article", { className: "sovereignty-card payer-scorecard", children: [_jsx("h3", { children: "Payer Scorecard" }), _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Payer" }), _jsx("th", { children: "Responsiveness" }), _jsx("th", { children: "Resistance" })] }) }), _jsx("tbody", { children: items.map((row) => (_jsxs("tr", { children: [_jsx("td", { children: row.payer }), _jsx("td", { children: asPct(row.responsiveness) }), _jsx("td", { children: asPct(row.resistance) })] }, row.payer))) })] })] }));
}
