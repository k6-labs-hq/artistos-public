import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const componentNames = [
    "Production Timeline Viewer",
    "Episode/Season Tree",
    "Residuals Waterfall Chart",
    "Distribution Window Map",
    "Syndication Heatmap",
    "Streaming Reuse Tracker",
    "Payroll Audit Breakdown",
    "Stunt Adjustment Calculator",
    "Backend Participation Forecast",
    "Agency Portfolio Dashboard",
    "Agency Recovery Pipeline",
    "Agency SOL Risk Map",
];
export function TVFilmEnterprisePanels() {
    return (_jsxs("section", { className: "tvfilm-enterprise-panels", "data-reveal": "true", "aria-label": "TV and Film enterprise dashboard modules", children: [_jsxs("div", { className: "section-head", children: [_jsx("h2", { children: "TV/Film Enterprise Modules" }), _jsx("p", { children: "Portfolio-scale views for agencies, management firms, production companies, and legal operations." })] }), _jsx("div", { className: "feature-grid", children: componentNames.map((name) => (_jsxs("article", { className: "feature-card", children: [_jsx("h3", { children: name }), _jsx("p", { children: "Production-ready XR7 panel with role-aware filtering, evidence traceability, and bulk action support." })] }, name))) })] }));
}
