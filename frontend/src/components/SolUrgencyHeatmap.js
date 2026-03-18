import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
function tone(value) {
    if (value >= 8)
        return "#ef4444";
    if (value >= 4)
        return "#f97316";
    if (value >= 2)
        return "#f59e0b";
    return "#22c55e";
}
export function SolUrgencyHeatmap({ cells }) {
    const items = cells.length ? cells : [
        { label: "US", value: 1 },
        { label: "UK", value: 0 },
        { label: "DE", value: 2 },
        { label: "FR", value: 1 },
    ];
    return (_jsxs("article", { className: "sovereignty-card sol-heatmap", children: [_jsx("h3", { children: "SOL Urgency Heatmap" }), _jsx("div", { className: "sol-grid", children: items.map((cell) => (_jsxs("div", { className: "sol-cell", style: { background: tone(cell.value) }, children: [_jsx("strong", { children: cell.label }), _jsx("span", { children: cell.value })] }, cell.label))) }), _jsx("p", { children: "Higher intensity indicates more claims nearing statute-of-limitations deadlines." })] }));
}
