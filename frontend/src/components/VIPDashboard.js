import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * VIPDashboard — Founders Circle premier experience root view.
 *
 * Assembles all VIP feature components based on membership state
 * and adapts layout to primary_vertical (music vs tv_film vs other).
 *
 * Usage:
 *   <VIPDashboard artistId="42" apiBase="/api/v1" />
 */
import { useEffect, useState } from "react";
import { VIPBadge } from "./VIPBadge";
import { XR7LogoGlow } from "./XR7LogoGlow";
import { PersonaCard } from "./PersonaCard";
import { ConciergeInbox } from "./ConciergeInbox";
import { RecoveryStoryTimeline } from "./RecoveryStoryTimeline";
import { LegacyMap } from "./LegacyMap";
import { FoundersCircleBanner } from "./FoundersCircleBanner";
import { WeeklyBriefCard } from "./WeeklyBriefCard";
import { CopilotChat } from "./CopilotChat";
import { VipReferralPanel } from "./VipReferralPanel";
const TABS = [
    { id: "overview", label: "Overview", icon: "◈" },
    { id: "concierge", label: "Concierge", icon: "✉" },
    { id: "copilot", label: "XR7 Advisor", icon: "⬡" },
    { id: "legacy", label: "Legacy Map", icon: "✦" },
    { id: "referrals", label: "Referrals", icon: "⊕" },
];
/* ─── Component ─────────────────────────────────────────────────────────── */
export function VIPDashboard({ artistId, apiBase = "", agentState, }) {
    const [status, setStatus] = useState(null);
    const [persona, setPersona] = useState(null);
    const [activeTab, setActiveTab] = useState("overview");
    const [loading, setLoading] = useState(true);
    const [notVip, setNotVip] = useState(false);
    const [logoGlowState, setLogoGlowState] = useState("loading");
    useEffect(() => {
        Promise.all([
            fetch(`${apiBase}/artists/${artistId}/vip/status`).then((r) => r.ok ? r.json() : null),
            fetch(`${apiBase}/artists/${artistId}/persona`).then((r) => r.ok ? r.json() : null),
        ])
            .then(([vipData, personaData]) => {
            if (!vipData?.is_vip) {
                setNotVip(true);
            }
            else {
                setStatus(vipData);
                setPersona(personaData);
            }
        })
            .catch(() => setNotVip(true))
            .finally(() => {
            setLoading(false);
            setLogoGlowState("active");
            setTimeout(() => setLogoGlowState("idle"), 1400);
        });
    }, [artistId, apiBase]);
    if (loading)
        return _jsx(DashboardSkeleton, {});
    if (notVip)
        return _jsx(NotVipGate, { apiBase: apiBase });
    const tier = (status?.tier_level ?? agentState?.vip_tier ?? "VIP");
    const greeting = agentState?.persona_greeting ??
        (status?.concierge_analyst_name
            ? `Welcome back. ${status.concierge_analyst_name} is here when you need them.`
            : "Welcome to your Founders Circle experience.");
    const vertical = persona?.primary_vertical ?? "music";
    return (_jsxs("div", { className: "vd-root", children: [_jsx("header", { className: "vd-header", children: _jsxs("div", { className: "vd-header-inner", children: [_jsx(XR7LogoGlow, { state: logoGlowState, size: 38 }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx(VIPBadge, { tierLevel: tier, size: "sm", animated: true }), _jsx("p", { className: "vd-greeting", children: greeting })] }), status?.logo_url && (_jsx("img", { src: status.logo_url, alt: "Custom logo", className: "vd-custom-logo" }))] }) }), _jsx("div", { className: "vd-banner-wrap", children: _jsx(FoundersCircleBanner, { artistId: artistId, apiBase: apiBase, greeting: greeting, tierLevel: tier, analystName: status?.concierge_analyst_name ?? "XR7 Strategy Team", referralSlotsRemaining: status?.referral_slots_remaining ?? 0, onReferralClick: () => setActiveTab("referrals") }) }), _jsx("nav", { className: "vd-tabs", role: "tablist", children: TABS.map((t) => (_jsxs("button", { role: "tab", "aria-selected": activeTab === t.id, className: ["vd-tab", activeTab === t.id ? "active" : ""].join(" "), onClick: () => setActiveTab(t.id), children: [_jsx("span", { className: "vd-tab-icon", children: t.icon }), _jsx("span", { children: t.label })] }, t.id))) }), _jsxs("main", { className: "vd-panel", children: [activeTab === "overview" && (_jsx(OverviewPane, { artistId: artistId, apiBase: apiBase, persona: persona, status: status, vertical: vertical })), activeTab === "concierge" && (_jsx(ConciergeInbox, { artistId: artistId, apiBase: apiBase, analystName: status?.concierge_analyst_name ?? undefined, calendlyLink: status?.calendly_link ?? undefined })), activeTab === "copilot" && (_jsx(CopilotChat, { artistId: artistId, apiBase: apiBase, personaGreeting: greeting })), activeTab === "legacy" && (_jsx(LegacyMap, { artistId: artistId, apiBase: apiBase })), activeTab === "referrals" && (_jsx(VipReferralPanel, { artistId: artistId, apiBase: apiBase, slotsRemaining: status?.referral_slots_remaining ?? 0 }))] }), _jsx("style", { children: css })] }));
}
function OverviewPane({ artistId, apiBase, persona, status, vertical, }) {
    return (_jsxs("div", { className: "vd-overview", children: [_jsxs("div", { className: "vd-col-a", children: [_jsx(PersonaCard, { artistId: artistId, apiBase: apiBase }), _jsx(RecoveryStoryTimeline, { artistId: artistId, apiBase: apiBase })] }), _jsxs("div", { className: "vd-col-b", children: [_jsx(WeeklyBriefCard, { artistId: artistId, apiBase: apiBase }), vertical !== "music" && (_jsxs("div", { className: "vd-vertical-note", children: [_jsx("span", { className: "vd-vertical-icon", children: vertical === "tv_film" ? "🎬" : "◈" }), _jsxs("span", { children: ["Your profile is tailored for the", " ", _jsx("strong", { children: vertical === "tv_film" ? "TV & Film" : vertical }), " ", "vertical."] })] })), (status?.perks_unlocked?.length ?? 0) > 0 && (_jsxs("div", { className: "vd-perks", children: [_jsx("h4", { className: "vd-perks-title", children: "Your Perks" }), _jsx("div", { className: "vd-perks-list", children: status.perks_unlocked.map((p) => (_jsx("span", { className: "vd-perk-chip", children: p }, p))) })] })), status?.watermark_text && (_jsx("div", { className: "vd-watermark", children: status.watermark_text }))] })] }));
}
/* ─── Not-VIP gate ──────────────────────────────────────────────────────── */
function NotVipGate({ apiBase }) {
    const [code, setCode] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    async function claim(e) {
        e.preventDefault();
        if (!code.trim() || submitting)
            return;
        setSubmitting(true);
        setError(null);
        try {
            const r = await fetch(`${apiBase}/invite/vip/claim`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ invite_code: code.trim() }),
            });
            if (!r.ok) {
                const b = await r.json().catch(() => ({}));
                throw new Error(b.detail ?? `HTTP ${r.status}`);
            }
            setSuccess(true);
        }
        catch (err) {
            setError(err.message ?? "Invalid code");
        }
        finally {
            setSubmitting(false);
        }
    }
    return (_jsxs("div", { className: "vd-gate", children: [_jsx(XR7LogoGlow, { state: "idle", size: 52 }), _jsx("h2", { className: "vd-gate-title", children: "Founders Circle" }), _jsx("p", { className: "vd-gate-sub", children: "This experience is invite-only. Enter your exclusive access code below." }), success ? (_jsx("div", { className: "vd-gate-success", children: "\u2713 You're in. Reload to access your VIP dashboard." })) : (_jsxs("form", { onSubmit: claim, className: "vd-gate-form", noValidate: true, children: [_jsx("input", { type: "text", placeholder: "Enter invite code", value: code, onChange: (e) => setCode(e.target.value), className: "vd-gate-input", maxLength: 64 }), _jsx("button", { className: "vd-gate-btn", type: "submit", disabled: submitting, children: submitting ? _jsx("span", { className: "vd-gate-spinner" }) : "Claim Access" }), error && _jsxs("p", { className: "vd-gate-error", children: ["\u26A0 ", error] })] })), _jsx("style", { children: css })] }));
}
/* ─── Loading skeleton ───────────────────────────────────────────────────── */
function DashboardSkeleton() {
    return (_jsxs("div", { className: "vd-root", children: [_jsx("div", { style: { padding: "1.25rem" }, children: [1, 2, 3].map((i) => (_jsx("div", { style: {
                        height: i === 1 ? 28 : i === 2 ? 80 : 140,
                        borderRadius: 10,
                        marginBottom: "0.75rem",
                        background: "linear-gradient(90deg,rgba(88,28,135,0.3) 25%,rgba(168,85,247,0.18) 50%,rgba(88,28,135,0.3) 75%)",
                        backgroundSize: "200% 100%",
                        animation: "shimmer 1.4s infinite",
                    } }, i))) }), _jsx("style", { children: `@keyframes shimmer{to{background-position:-200% 0}}` })] }));
}
/* ─── CSS ────────────────────────────────────────────────────────────────── */
const css = `
  .vd-root {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(160deg,#0d0221 0%,#150535 50%,#0d0221 100%);
    min-height:100vh; color:#e9d5ff;
  }
  .vd-header {
    border-bottom:1px solid rgba(168,85,247,0.18);
    background:rgba(20,5,50,0.9);
    position:sticky; top:0; z-index:40;
    backdrop-filter:blur(10px);
  }
  .vd-header-inner {
    max-width:1200px; margin:0 auto; padding:0.65rem 1.25rem;
    display:flex; align-items:center; gap:0.85rem;
  }
  .vd-greeting { font-size:0.78rem; color:#c4b5fd; margin:0.2rem 0 0; line-height:1.3; }
  .vd-custom-logo { height:32px; width:auto; border-radius:6px; object-fit:contain; }
  .vd-banner-wrap { max-width:1200px; margin:1rem auto 0; padding:0 1.25rem; }
  .vd-tabs {
    display:flex; gap:0; overflow-x:auto;
    max-width:1200px; margin:0.75rem auto 0; padding:0 1.25rem;
    border-bottom:1px solid rgba(168,85,247,0.15);
    scrollbar-width:none;
  }
  .vd-tabs::-webkit-scrollbar { display:none; }
  .vd-tab {
    display:flex; align-items:center; gap:0.4rem;
    padding:0.6rem 1.1rem; font-size:0.8rem; font-weight:600;
    color:#9f7ced; background:none; border:none; border-bottom:2px solid transparent;
    cursor:pointer; white-space:nowrap; transition:color 0.18s, border-color 0.18s;
  }
  .vd-tab.active { color:#d8b4fe; border-bottom-color:#a855f7; }
  .vd-tab:hover:not(.active) { color:#c4b5fd; }
  .vd-tab-icon { font-size:0.7rem; }
  .vd-panel { max-width:1200px; margin:0 auto; padding:1.25rem; }
  /* Overview two-column layout */
  .vd-overview { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }
  @media(max-width:700px) { .vd-overview { grid-template-columns:1fr; } }
  .vd-col-a, .vd-col-b { display:flex; flex-direction:column; gap:1.25rem; }
  .vd-vertical-note {
    display:flex; align-items:center; gap:0.5rem;
    padding:0.6rem 1rem; border-radius:10px; font-size:0.8rem; color:#c4b5fd;
    background:rgba(88,28,135,0.18); border:1px solid rgba(168,85,247,0.2);
  }
  .vd-perks {
    padding:0.9rem 1.1rem; border-radius:12px;
    background:rgba(30,8,65,0.8); border:1px solid rgba(168,85,247,0.2);
  }
  .vd-perks-title {
    font-size:0.65rem; font-weight:800; text-transform:uppercase;
    letter-spacing:0.12em; color:#a855f7; margin:0 0 0.5rem;
  }
  .vd-perks-list { display:flex; flex-wrap:wrap; gap:0.4rem; }
  .vd-perk-chip {
    font-size:0.72rem; padding:0.28rem 0.7rem; border-radius:9999px;
    background:rgba(168,85,247,0.12); border:1px solid rgba(168,85,247,0.32);
    color:#d8b4fe; font-weight:600;
  }
  .vd-watermark {
    text-align:center; font-size:0.65rem; letter-spacing:0.25em; font-weight:800;
    text-transform:uppercase; color:rgba(168,85,247,0.25); padding:0.5rem;
    user-select:none;
  }
  /* Gate */
  .vd-gate {
    min-height:100vh; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:1rem;
    padding:2rem 1.5rem; text-align:center;
  }
  .vd-gate-title { font-size:1.6rem; font-weight:900; color:#e9d5ff; letter-spacing:0.06em; }
  .vd-gate-sub { font-size:0.85rem; color:#9f7ced; max-width:340px; line-height:1.6; }
  .vd-gate-form { display:flex; flex-direction:column; gap:0.6rem; width:100%; max-width:360px; }
  .vd-gate-input {
    font-size:0.88rem; color:#e9d5ff; text-align:center;
    background:rgba(60,20,120,0.4); border:1px solid rgba(168,85,247,0.4);
    border-radius:12px; padding:0.75rem 1rem; outline:none;
    transition:border-color 0.2s; letter-spacing:0.05em;
  }
  .vd-gate-input:focus { border-color:rgba(168,85,247,0.75); }
  .vd-gate-input::placeholder { color:#6d4fa3; letter-spacing:0; }
  .vd-gate-btn {
    padding:0.75rem 1.5rem; border-radius:12px; cursor:pointer; font-weight:800;
    font-size:0.9rem; border:none;
    background:linear-gradient(135deg,#7c3aed,#a855f7); color:#fff;
    transition:opacity 0.18s; display:flex; align-items:center; justify-content:center;
  }
  .vd-gate-btn:disabled { opacity:0.45; cursor:not-allowed; }
  .vd-gate-btn:hover:not(:disabled) { opacity:0.87; }
  .vd-gate-spinner {
    width:18px; height:18px;
    border:2px solid rgba(255,255,255,0.35);
    border-top-color:#fff; border-radius:50%;
    animation:spin 0.7s linear infinite; display:inline-block;
  }
  @keyframes spin{to{transform:rotate(360deg)}}
  .vd-gate-error { font-size:0.78rem; color:#f87171; }
  .vd-gate-success {
    font-size:0.88rem; color:#86efac; font-weight:700;
    padding:0.75rem 1.5rem; border-radius:12px;
    background:rgba(134,239,172,0.1); border:1px solid rgba(134,239,172,0.3);
  }
`;
