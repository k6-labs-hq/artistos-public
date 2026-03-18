import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function RecoverableWaterfallChart({ steps }) {
    const items = steps.length
        ? steps
        : [
            { label: "Detected", amount: 120000 },
            { label: "Disputed", amount: -28000 },
            { label: "Accepted", amount: 76000 },
            { label: "Paid", amount: -19000 },
        ];
    const max = Math.max(...items.map((s) => Math.abs(s.amount)), 1);
    return (_jsxs("article", { className: "sovereignty-card waterfall", children: [_jsx("h3", { children: "Recoverable Waterfall" }), _jsx("ul", { children: items.map((step) => {
                    const width = Math.max(8, Math.round((Math.abs(step.amount) / max) * 100));
                    const positive = step.amount >= 0;
                    return (_jsxs("li", { children: [_jsx("span", { children: step.label }), _jsx("div", { className: "bar-wrap", children: _jsx("div", { className: `bar ${positive ? "positive" : "negative"}`, style: { width: `${width}%` } }) }), _jsxs("strong", { children: [positive ? "+" : "-", "$", Math.abs(step.amount).toLocaleString()] })] }, step.label));
                }) })] }));
}
