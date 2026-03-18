import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
const navLinks = ["Platform", "How It Works", "Use Cases", "Security", "Docs"];
const trustStats = [
    {
        value: "$10M+",
        title: "Missing Royalties Identified",
        body: "Platforms like Notes.fm identified over $10M in missing royalties during beta testing across 400+ artists.",
        source: "Public beta reporting",
    },
    {
        value: "$100M+",
        title: "Hidden Royalties Surfaced",
        body: "AI-driven tools have surfaced more than $100M in global hidden royalties for songwriters and artists.",
        source: "Industry recovery analyses",
    },
    {
        value: "$15K+",
        title: "Average Audit Recovery",
        body: "Average uncovered royalties per artist in real audits have exceeded $15,000 from unmatched works and streams.",
        source: "Audit benchmark references",
    },
    {
        value: "Billions",
        title: "Still Unclaimed",
        body: "Billions in unclaimed royalties remain industry-wide. XR7 helps surface and recover what is rightfully yours.",
        source: "MLC and collection society disclosures",
    },
];
const featureCards = [
    {
        title: "Connect Platforms in Minutes",
        body: "Securely link Spotify, Apple Music, TikTok, YouTube, MLC, SoundExchange, and PRO datasets without engineering overhead.",
        chips: ["Spotify", "Apple", "TikTok", "YouTube"],
    },
    {
        title: "AI-Powered Gap Detection",
        body: "Forensic models classify leakage from unmatched works, bad rates, and missing statements into ranked recovery opportunities.",
        chips: ["Detected", "Reported", "Paid", "Recovered"],
    },
    {
        title: "Real-Time Recovery Radar",
        body: "Watch risk and payout signals update across territories, counterparties, and claim phases with explainable confidence scores.",
        chips: ["Heatmaps", "SLA Risk", "Forecast"],
    },
    {
        title: "Collaborative Case Management",
        body: "Coordinate artists, managers, legal, and publishing teams inside one timeline with notes, evidence packets, and status trails.",
        chips: ["Shared Notes", "Playbooks", "Audit Trail"],
    },
];
const timelineSteps = [
    {
        title: "Connect Data",
        body: "Link DSPs, distributors, PRO statements, and catalog metadata.",
    },
    {
        title: "Analyze and Detect",
        body: "XR7 applies forensic checks and anomaly intelligence across every revenue stream.",
    },
    {
        title: "Surface Cases",
        body: "Prioritized case queue includes confidence, urgency, and estimated recovery value.",
    },
    {
        title: "Recover and Track",
        body: "Drive collections to resolution with full status visibility from claim to payout.",
    },
];
function getSystemTheme() {
    if (typeof window === "undefined") {
        return "dark";
    }
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}
function XR7WingLogo({ className = "" }) {
    return (_jsxs("svg", { className: className, viewBox: "0 0 840 320", role: "img", "aria-label": "XR7 metallic winged emblem", xmlns: "http://www.w3.org/2000/svg", children: [_jsxs("defs", { children: [_jsxs("linearGradient", { id: "wingGradient", x1: "0%", y1: "0%", x2: "100%", y2: "100%", children: [_jsx("stop", { offset: "0%", stopColor: "#6520BD" }), _jsx("stop", { offset: "55%", stopColor: "#A855F7" }), _jsx("stop", { offset: "100%", stopColor: "#D6B1FF" })] }), _jsxs("linearGradient", { id: "chromeLine", x1: "0%", y1: "0%", x2: "0%", y2: "100%", children: [_jsx("stop", { offset: "0%", stopColor: "#FFFFFF", stopOpacity: "0.9" }), _jsx("stop", { offset: "100%", stopColor: "#B1B7D1", stopOpacity: "0.2" })] }), _jsxs("filter", { id: "softGlow", x: "-40%", y: "-60%", width: "180%", height: "220%", children: [_jsx("feGaussianBlur", { stdDeviation: "8", result: "blur" }), _jsxs("feMerge", { children: [_jsx("feMergeNode", { in: "blur" }), _jsx("feMergeNode", { in: "SourceGraphic" })] })] })] }), _jsxs("g", { filter: "url(#softGlow)", children: [_jsx("path", { d: "M30 150C92 118 152 103 232 92L188 141L247 147L175 205L235 212C148 236 89 224 30 195Z", fill: "url(#wingGradient)" }), _jsx("path", { d: "M810 150C748 118 688 103 608 92L652 141L593 147L665 205L605 212C692 236 751 224 810 195Z", fill: "url(#wingGradient)" })] }), _jsx("rect", { x: "214", y: "64", width: "412", height: "192", rx: "52", fill: "url(#wingGradient)", stroke: "url(#chromeLine)", strokeWidth: "3" }), _jsx("path", { d: "M246 222L286 98H324L282 174H323L283 222Z", fill: "#F8FAFC" }), _jsx("path", { d: "M350 98H395L425 142L456 98H500L447 160L503 222H457L425 175L394 222H348L404 160Z", fill: "#F8FAFC" }), _jsx("path", { d: "M533 98H600L562 173H612L560 222H514L553 156H505Z", fill: "#F8FAFC" }), _jsx("path", { d: "M220 84H620", stroke: "url(#chromeLine)", strokeOpacity: "0.7", strokeWidth: "4", strokeLinecap: "round" })] }));
}
export function App() {
    const [theme, setTheme] = useState("dark");
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [demoOpen, setDemoOpen] = useState(false);
    useEffect(() => {
        const saved = window.localStorage.getItem("xr7-theme");
        const initial = saved === "dark" || saved === "light" ? saved : getSystemTheme();
        setTheme(initial);
    }, []);
    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme);
        document.documentElement.style.colorScheme = theme;
        window.localStorage.setItem("xr7-theme", theme);
    }, [theme]);
    useEffect(() => {
        if (!demoOpen) {
            document.body.style.overflow = "";
            return;
        }
        document.body.style.overflow = "hidden";
        const onKeyDown = (event) => {
            if (event.key === "Escape") {
                setDemoOpen(false);
            }
        };
        window.addEventListener("keydown", onKeyDown);
        return () => {
            document.body.style.overflow = "";
            window.removeEventListener("keydown", onKeyDown);
        };
    }, [demoOpen]);
    useEffect(() => {
        const revealTargets = Array.from(document.querySelectorAll("[data-reveal='true']"));
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.18 });
        revealTargets.forEach((el) => observer.observe(el));
        return () => observer.disconnect();
    }, []);
    const heroSubtitle = useMemo(() => "Detect leakage across Spotify, TikTok, YouTube, PROs, MLC and more. Surface actionable recovery opportunities with AI-powered analysis.", []);
    return (_jsxs("div", { className: "xr7-app", children: [_jsx("a", { className: "skip-link", href: "#main-content", children: "Skip to content" }), _jsxs("header", { className: "site-nav", role: "banner", children: [_jsxs("div", { className: "nav-inner", children: [_jsxs("a", { className: "brand", href: "#top", "aria-label": "XR7 homepage", children: [_jsx("img", { src: "/xr7-emblem.svg", alt: "XR7 emblem" }), _jsx("span", { children: "XR7" })] }), _jsx("nav", { className: "desktop-nav", "aria-label": "Primary", children: navLinks.map((item) => (_jsx("a", { href: "#features", children: item }, item))) }), _jsxs("div", { className: "nav-actions", children: [_jsx("button", { type: "button", className: "theme-toggle", "aria-label": "Toggle light and dark theme", onClick: () => setTheme((prev) => (prev === "dark" ? "light" : "dark")), children: _jsx("span", { "aria-hidden": "true", children: theme === "dark" ? "Sun" : "Moon" }) }), _jsx("button", { type: "button", className: "cta small", children: "Get Started" }), _jsx("button", { type: "button", className: "menu-toggle", "aria-expanded": mobileMenuOpen, "aria-controls": "mobile-menu", onClick: () => setMobileMenuOpen((prev) => !prev), children: "Menu" })] })] }), _jsxs("div", { id: "mobile-menu", className: `mobile-menu${mobileMenuOpen ? " open" : ""}`, children: [navLinks.map((item) => (_jsx("a", { href: "#features", onClick: () => setMobileMenuOpen(false), children: item }, item))), _jsx("button", { type: "button", className: "cta", onClick: () => setMobileMenuOpen(false), children: "Start Free" })] })] }), _jsxs("main", { id: "main-content", children: [_jsxs("section", { className: "hero", "data-reveal": "true", children: [_jsx("div", { className: "hero-bg", "aria-hidden": "true" }), _jsx(XR7WingLogo, { className: "hero-logo" }), _jsx("p", { className: "eyebrow", children: "Forensic Royalty Recovery - Powered by K6 Labs" }), _jsx("h1", { children: "Uncover Every Dollar You Are Owed" }), _jsx("p", { className: "hero-copy", children: heroSubtitle }), _jsxs("div", { className: "hero-actions", children: [_jsx("button", { type: "button", className: "cta large pulse", children: "Get Started Free" }), _jsx("button", { type: "button", className: "ghost large", onClick: () => setDemoOpen(true), children: "Watch Demo" })] })] }), _jsxs("section", { className: "trust", "data-reveal": "true", children: [_jsxs("div", { className: "section-head", children: [_jsx("h2", { children: "Trusted by Reality, Not Hype" }), _jsx("p", { children: "Grounded in publicly discussed royalty recovery outcomes and unmatched-funds reporting across the industry." })] }), _jsx("div", { className: "trust-grid", children: trustStats.map((item) => (_jsxs("article", { className: "stat-card", children: [_jsx("p", { className: "stat-value", children: item.value }), _jsx("h3", { children: item.title }), _jsx("p", { children: item.body }), _jsxs("small", { children: ["Source: ", item.source] })] }, item.title))) })] }), _jsxs("section", { id: "features", className: "features", "data-reveal": "true", children: [_jsxs("div", { className: "section-head", children: [_jsx("h2", { children: "Core XR7 Capabilities" }), _jsx("p", { children: "Built for artists, managers, songwriters, and publishers that need forensic-grade royalty visibility." })] }), _jsx("div", { className: "feature-grid", children: featureCards.map((card) => (_jsxs("article", { className: "feature-card", children: [_jsx("h3", { children: card.title }), _jsx("p", { children: card.body }), _jsx("div", { className: "chip-row", "aria-label": "Feature highlights", children: card.chips.map((chip) => (_jsx("span", { children: chip }, chip))) })] }, card.title))) })] }), _jsxs("section", { className: "how-it-works", "data-reveal": "true", children: [_jsx("div", { className: "section-head", children: _jsx("h2", { children: "How It Works" }) }), _jsx("ol", { className: "timeline", children: timelineSteps.map((step, index) => (_jsxs("li", { children: [_jsx("span", { className: "node", children: index + 1 }), _jsxs("div", { children: [_jsx("h3", { children: step.title }), _jsx("p", { children: step.body })] })] }, step.title))) })] }), _jsxs("section", { className: "dashboard-preview", "data-reveal": "true", children: [_jsxs("div", { className: "section-head", children: [_jsx("h2", { children: "Inside the XR7 Recovery Console" }), _jsx("p", { children: "A premium, data-dense workspace designed for real legal and royalty operations." })] }), _jsxs("div", { className: "app-mock", role: "img", "aria-label": "XR7 dashboard preview with metrics, chart, and case table", children: [_jsxs("aside", { className: "mock-sidebar", children: [_jsx("img", { src: "/xr7-emblem.svg", alt: "", "aria-hidden": "true" }), _jsx("a", { href: "#", children: "Overview" }), _jsx("a", { href: "#", children: "Recovery Cases" }), _jsx("a", { href: "#", children: "Platform Coverage" }), _jsx("a", { href: "#", children: "Legal Packets" }), _jsx("a", { href: "#", children: "Team Activity" })] }), _jsxs("div", { className: "mock-main", children: [_jsxs("div", { className: "mock-topbar", children: [_jsx("input", { type: "text", readOnly: true, value: "Search claims, ISRC, payers", "aria-label": "Search" }), _jsxs("div", { className: "mock-actions", children: [_jsx("span", { className: "badge", children: "4 alerts" }), _jsx("button", { type: "button", className: "theme-toggle compact", "aria-label": "Theme toggle preview", children: theme === "dark" ? "Sun" : "Moon" })] })] }), _jsxs("div", { className: "metric-grid", children: [_jsxs("article", { children: [_jsx("p", { children: "Recovery Potential" }), _jsx("strong", { children: "$2.84M" })] }), _jsxs("article", { children: [_jsx("p", { children: "Open Cases" }), _jsx("strong", { children: "128" })] }), _jsxs("article", { children: [_jsx("p", { children: "Coverage Health" }), _jsx("strong", { children: "92.4%" })] }), _jsxs("article", { children: [_jsx("p", { children: "Recovered 30d" }), _jsx("strong", { className: "gold", children: "$318K" })] })] }), _jsxs("div", { className: "chart-panel", children: [_jsxs("div", { className: "chart-bars", "aria-hidden": "true", children: [_jsx("span", { style: { height: "42%" } }), _jsx("span", { style: { height: "65%" } }), _jsx("span", { style: { height: "76%" } }), _jsx("span", { style: { height: "58%" } }), _jsx("span", { style: { height: "83%" } }), _jsx("span", { style: { height: "91%" } }), _jsx("span", { style: { height: "72%" } })] }), _jsx("div", { className: "chart-caption", children: "Leakage Heatmap: Risk concentration is highest in US recording + neighboring rights lanes this week." })] }), _jsxs("table", { children: [_jsx("caption", { children: "Recent Recovery Cases" }), _jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Case" }), _jsx("th", { children: "Platform" }), _jsx("th", { children: "Status" }), _jsx("th", { children: "Value" })] }) }), _jsxs("tbody", { children: [_jsxs("tr", { children: [_jsx("td", { children: "XR7-4412" }), _jsx("td", { children: "Spotify" }), _jsx("td", { children: _jsx("span", { className: "chip teal", children: "In Review" }) }), _jsx("td", { children: "$81,400" })] }), _jsxs("tr", { children: [_jsx("td", { children: "XR7-4386" }), _jsx("td", { children: "MLC" }), _jsx("td", { children: _jsx("span", { className: "chip", children: "Detected" }) }), _jsx("td", { children: "$45,220" })] }), _jsxs("tr", { children: [_jsx("td", { children: "XR7-4360" }), _jsx("td", { children: "YouTube" }), _jsx("td", { children: _jsx("span", { className: "chip success", children: "Recovered" }) }), _jsx("td", { children: "$129,900" })] })] })] })] })] })] })] }), _jsxs("footer", { className: "site-footer", children: [_jsx("p", { children: "XR7 Forensic Royalty Recovery" }), _jsxs("div", { children: [_jsx("a", { href: "#", children: "Privacy" }), _jsx("a", { href: "#", children: "Terms" }), _jsx("a", { href: "#", children: "Security" }), _jsx("a", { href: "#", children: "Contact" })] })] }), demoOpen ? (_jsx("div", { className: "modal-backdrop", role: "dialog", "aria-modal": "true", "aria-labelledby": "demo-title", onClick: () => setDemoOpen(false), children: _jsxs("div", { className: "modal-card", onClick: (event) => event.stopPropagation(), children: [_jsx("h2", { id: "demo-title", children: "XR7 Product Demo" }), _jsx("p", { children: "Demo modal placeholder. Embed your hosted product walkthrough here (Wistia, Vimeo, or in-app interactive demo)." }), _jsx("button", { type: "button", className: "cta", onClick: () => setDemoOpen(false), children: "Close Demo" })] }) })) : null] }));
}
