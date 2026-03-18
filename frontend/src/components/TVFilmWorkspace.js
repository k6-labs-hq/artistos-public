import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from "react";
const roleOptions = [
    "Writer (TV/Film)",
    "Screenwriter",
    "Showrunner",
    "Director",
    "Producer",
    "Actor",
    "Voice Actor",
    "Stunt Performer",
    "Editor",
    "Cinematographer",
    "Composer",
    "VFX Artist",
    "Animator",
    "Crew (Grip, Gaffer, PA, etc.)",
    "Reality TV Participant",
    "Documentary Creator",
    "Talent Agency",
    "Management Company",
    "Law Firm",
    "Production Company",
];
const trustEvents = [
    "Matching episode-season hierarchies against statement rows",
    "Applying union and studio compensation rules",
    "Scoring SOL risk across productions and territories",
    "Preparing evidence-backed claim packets and forecasts",
];
const dashboardRows = [
    ["Residuals Discovered", "$486,000", "21 productions", "SAG-AFTRA / WGA"],
    ["Production Payments", "$72,400", "Overtime + penalties", "IATSE / Crew"],
    ["Distribution & Licensing", "$214,300", "Syndication + FAST", "Studios / Streamers"],
    ["Streaming Reuse", "$180,200", "14 window mismatches", "Netflix / Hulu / Max"],
    ["UGC & Clips", "$39,800", "92 clip detections", "YouTube / TikTok / IG"],
    ["Backend Participation", "$96,000", "5 participation gaps", "Studio backend"],
];
export function TVFilmWorkspace() {
    const [selectedRole, setSelectedRole] = useState(roleOptions[5] ?? "Actor");
    const [agencyMode, setAgencyMode] = useState(false);
    const [rosterCount, setRosterCount] = useState(480);
    const roleExplanation = useMemo(() => {
        if (selectedRole === "Talent Agency") {
            return "Run portfolio-wide historical analyses across multiple unions, roles, productions, and studios with bulk claim drafting and SOL risk mapping.";
        }
        if (selectedRole === "Stunt Performer") {
            return "XR7 prioritizes stunt adjustments, turnaround penalties, hazard premiums, and reuse category mismatches for stunt-heavy productions.";
        }
        if (selectedRole === "Writer (TV/Film)" || selectedRole === "Screenwriter" || selectedRole === "Showrunner") {
            return "XR7 focuses on residual windows, credited episode counts, backend participation, and foreign residual lag factors.";
        }
        return "XR7 maps every compensation line to role, market, production, and reuse window so missing payments can be explained in plain language before claim filing.";
    }, [selectedRole]);
    return (_jsxs("section", { className: "tvfilm-workspace", "data-reveal": "true", children: [_jsxs("div", { className: "section-head", children: [_jsx("h2", { children: "TV/Film Onboarding and Enterprise Workspace" }), _jsx("p", { children: "Role-specific onboarding, live trust messaging, and agency-scale portfolio operations in one surface." })] }), _jsxs("div", { className: "tvfilm-grid", children: [_jsxs("article", { className: "tvfilm-card onboarding-card", children: [_jsx("p", { className: "eyebrow small", children: "Which role best describes you?" }), _jsxs("label", { className: "stacked-field", children: [_jsx("span", { children: "Role" }), _jsx("select", { value: selectedRole, onChange: (event) => setSelectedRole(event.target.value), children: roleOptions.map((role) => (_jsx("option", { value: role, children: role }, role))) })] }), _jsxs("label", { className: "toggle-row", children: [_jsx("input", { type: "checkbox", checked: agencyMode, onChange: (event) => setAgencyMode(event.target.checked) }), _jsx("span", { children: "Enable enterprise agency mode" })] }), _jsx("p", { className: "support-copy", children: roleExplanation }), _jsxs("div", { className: "chip-row", children: [_jsx("span", { children: agencyMode ? "Portfolio Mode" : "Individual Mode" }), _jsx("span", { children: selectedRole })] })] }), _jsxs("article", { className: "tvfilm-card roster-card", children: [_jsxs("div", { className: "card-head", children: [_jsx("h3", { children: "Agency Roster Intake" }), _jsx("span", { className: "chip teal", children: "CSV / XLSX / API" })] }), _jsx("p", { children: "Upload 100s to 10,000+ clients across unions, productions, and platforms." }), _jsxs("label", { className: "stacked-field", children: [_jsx("span", { children: "Roster Size" }), _jsx("input", { type: "range", min: "100", max: "10000", step: "100", value: rosterCount, onChange: (event) => setRosterCount(Number(event.target.value)) })] }), _jsxs("div", { className: "roster-meter", children: [_jsxs("strong", { children: [rosterCount.toLocaleString(), " clients"] }), _jsx("p", { children: "Bulk metadata repair, bulk forecasting, and bulk evidence generation are ready for this roster." })] }), _jsxs("div", { className: "mini-metrics", children: [_jsxs("div", { children: [_jsx("span", { children: "Total Missing" }), _jsxs("strong", { children: ["$", (rosterCount * 1280).toLocaleString()] })] }), _jsxs("div", { children: [_jsx("span", { children: "High SOL Risk" }), _jsx("strong", { children: Math.max(12, Math.round(rosterCount * 0.09)) })] }), _jsxs("div", { children: [_jsx("span", { children: "Union Coverage" }), _jsx("strong", { children: "5 unions" })] })] })] }), _jsxs("article", { className: "tvfilm-card trust-card", children: [_jsxs("div", { className: "card-head", children: [_jsx("h3", { children: "What XR7 Is Doing Now" }), _jsx("span", { className: `signal-dot ${agencyMode ? "live" : "idle"}` })] }), _jsx("ul", { className: "trust-feed", children: trustEvents.map((event, index) => (_jsx("li", { style: { animationDelay: `${index * 0.08}s` }, children: event }, event))) }), _jsx("p", { className: "support-copy", children: agencyMode
                                    ? "Agency mode is aggregating roster-wide role, union, and platform deltas into a single recovery pipeline."
                                    : `XR7 is preparing a ${selectedRole} explanation layer before any legal step is taken.` })] })] }), _jsxs("div", { className: "tvfilm-dashboard-table", children: [_jsxs("div", { className: "card-head", children: [_jsx("h3", { children: "TV/Film Dashboard Sections" }), _jsx("span", { className: "chip success", children: "Market-ready surface" })] }), _jsxs("table", { children: [_jsx("caption", { children: "Role-aware recovery dashboard" }), _jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Section" }), _jsx("th", { children: "Value" }), _jsx("th", { children: "Signal" }), _jsx("th", { children: "Primary Lens" })] }) }), _jsx("tbody", { children: dashboardRows.map((row) => (_jsxs("tr", { children: [_jsx("td", { children: row[0] }), _jsx("td", { children: row[1] }), _jsx("td", { children: row[2] }), _jsx("td", { children: row[3] })] }, row[0]))) })] })] })] }));
}
