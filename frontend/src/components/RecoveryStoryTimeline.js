import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * RecoveryStoryTimeline — "My Recovery Story" personalized timeline.
 *
 * Renders a vertical timeline of the artist's recovery journey:
 * claims opened → evidence gathered → dispute filed → recovered.
 *
 * Adaptive to music vs TV/Film vertical.
 */
import { useEffect, useState } from "react";
const CATEGORY_CONFIG = {
    onboarding: { icon: "🚀", color: "#A855F7", label: "Onboarded" },
    enrichment: { icon: "✨", color: "#C084FC", label: "Profile Enriched" },
    claim: { icon: "📋", color: "#F59E0B", label: "Claim Filed" },
    evidence: { icon: "🔗", color: "#60A5FA", label: "Evidence Secured" },
    dispute: { icon: "⚖️", color: "#F97316", label: "Dispute Active" },
    payment: { icon: "💸", color: "#34D399", label: "Recovery Received" },
    milestone: { icon: "🏆", color: "#E9D5FF", label: "Milestone" },
};
function formatDate(iso) {
    try {
        return new Intl.DateTimeFormat("en-US", { year: "numeric", month: "short", day: "numeric" }).format(new Date(iso));
    }
    catch {
        return iso;
    }
}
function TimelineNode({ event, isLast }) {
    const cfg = CATEGORY_CONFIG[event.category] ?? CATEGORY_CONFIG.milestone;
    return (_jsxs("div", { className: "flex gap-3 group", children: [_jsxs("div", { className: "flex flex-col items-center", children: [_jsx("div", { className: "w-9 h-9 rounded-full flex items-center justify-center text-base flex-shrink-0 event-dot", style: { background: `${cfg.color}22`, border: `1.5px solid ${cfg.color}55` }, children: event.is_vip_milestone ? "⬡" : cfg.icon }), !isLast && _jsx("div", { className: "w-px flex-1 bg-purple-800/40 mt-1", style: { minHeight: 24 } })] }), _jsxs("div", { className: "pb-5 flex-1", children: [_jsxs("div", { className: "flex items-center gap-2 flex-wrap", children: [_jsx("span", { className: "text-xs font-semibold px-2 py-0.5 rounded-full", style: { background: `${cfg.color}18`, color: cfg.color }, children: cfg.label }), event.platform && (_jsx("span", { className: "text-xs text-purple-500", children: event.platform })), event.is_vip_milestone && (_jsx("span", { className: "text-xs text-yellow-400 font-semibold", children: "\u2605 VIP" }))] }), _jsx("h4", { className: "text-purple-100 text-sm font-medium mt-1", children: event.title }), event.description && (_jsx("p", { className: "text-purple-400 text-xs mt-0.5 leading-relaxed line-clamp-2", children: event.description })), _jsxs("div", { className: "flex items-center gap-3 mt-1.5", children: [_jsx("span", { className: "text-purple-500 text-xs", children: formatDate(event.date) }), event.amount != null && (_jsxs("span", { className: "text-emerald-400 text-xs font-semibold", children: ["+", event.currency ?? "$", event.amount.toLocaleString()] })), event.confidence != null && (_jsxs("span", { className: "text-purple-500 text-xs", children: [(event.confidence * 100).toFixed(0), "% confidence"] }))] })] })] }));
}
export function RecoveryStoryTimeline({ artistId, apiBase = "", vertical = "music", vipActive = false, }) {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    useEffect(() => {
        let mounted = true;
        const load = async () => {
            setLoading(true);
            try {
                // Fetch claims + anomalies to build timeline
                const [claimsRes, dashRes] = await Promise.all([
                    fetch(`${apiBase}/artists/${artistId}/claims?limit=50`),
                    fetch(`${apiBase}/artists/${artistId}/dashboard`),
                ]);
                const claimsData = claimsRes.ok ? await claimsRes.json() : [];
                const dashData = dashRes.ok ? await dashRes.json() : {};
                if (!mounted)
                    return;
                // Build timeline from API data
                const timeline = [];
                // Onboarding milestone
                timeline.push({
                    id: "onboard",
                    date: new Date().toISOString(),
                    category: "onboarding",
                    title: "Joined XR7 Engine",
                    description: "Your recovery journey began.",
                    is_vip_milestone: vipActive,
                });
                if (vipActive) {
                    timeline.push({
                        id: "vip-activate",
                        date: new Date().toISOString(),
                        category: "milestone",
                        title: "Founders Circle Activated",
                        description: "Concierge access, Legacy Map, and XR7 Advisor are now available.",
                        is_vip_milestone: true,
                    });
                }
                // Claims → timeline entries
                const claims = Array.isArray(claimsData) ? claimsData : (claimsData.claims ?? []);
                for (const claim of claims.slice(0, 10)) {
                    timeline.push({
                        id: `claim-${claim.id}`,
                        date: claim.created_at ?? new Date().toISOString(),
                        category: "claim",
                        title: `Claim: ${claim.description?.slice(0, 60) ?? "Recovery claim filed"}`,
                        description: claim.description,
                        platform: claim.platform,
                        confidence: claim.confidence,
                    });
                    if (claim.status === "RESOLVED" && claim.recovered_amount) {
                        timeline.push({
                            id: `payment-${claim.id}`,
                            date: claim.resolved_at ?? new Date().toISOString(),
                            category: "payment",
                            title: `Recovered: ${claim.description?.slice(0, 40) ?? "Royalty recovery"}`,
                            amount: claim.recovered_amount,
                            platform: claim.platform,
                        });
                    }
                }
                // Sort chronologically
                timeline.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
                setEvents(timeline);
            }
            catch {
                if (mounted)
                    setError("Could not load your recovery story.");
            }
            finally {
                if (mounted)
                    setLoading(false);
            }
        };
        load();
        return () => { mounted = false; };
    }, [artistId, apiBase, vipActive]);
    return (_jsxs("div", { className: "rst-container p-5", children: [_jsxs("div", { className: "flex items-center gap-2 mb-5", children: [_jsx("span", { className: "text-purple-400 text-lg", children: "\uD83D\uDCD6" }), _jsxs("div", { children: [_jsx("h3", { className: "text-purple-100 font-semibold text-base", children: "My Recovery Story" }), _jsxs("p", { className: "text-purple-500 text-xs", children: ["Your personalized ", vertical === "tv_film" ? "TV/Film residuals" : "royalty", " recovery journey"] })] })] }), loading && (_jsx("div", { className: "space-y-4", children: [1, 2, 3].map((i) => (_jsxs("div", { className: "flex gap-3 animate-pulse", children: [_jsx("div", { className: "w-9 h-9 rounded-full bg-purple-900/50" }), _jsxs("div", { className: "flex-1 space-y-2 py-1", children: [_jsx("div", { className: "h-3 bg-purple-900/50 rounded w-1/4" }), _jsx("div", { className: "h-3 bg-purple-900/40 rounded w-1/2" })] })] }, i))) })), error && _jsx("p", { className: "text-red-400 text-sm", children: error }), !loading && events.length === 0 && !error && (_jsx("p", { className: "text-purple-500 text-sm text-center py-6", children: "No recovery events yet \u2014 your story is just beginning." })), !loading && events.length > 0 && (_jsx("div", { children: events.map((ev, idx) => (_jsx(TimelineNode, { event: ev, isLast: idx === events.length - 1 }, ev.id))) })), _jsx("style", { children: `
        .rst-container {
          background: linear-gradient(160deg, rgba(15,5,35,0.96) 0%, rgba(20,6,45,0.96) 100%);
          border: 1px solid rgba(168,85,247,0.20);
          border-radius: 12px;
        }
        .event-dot {
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .group:hover .event-dot {
          transform: scale(1.12);
          box-shadow: 0 0 10px 2px rgba(168,85,247,0.25);
        }
      ` })] }));
}
