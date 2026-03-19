import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * FoundersCircleBanner — Early access banner for VIP members.
 *
 * Displays the Founders Circle badge, VIP drops carousel,
 * referral CTA, and adaptive greeting.
 */
import { useEffect, useState } from "react";
import { VIPBadge } from "./VIPBadge";
import { XR7LogoGlow } from "./XR7LogoGlow";
export function FoundersCircleBanner({ artistId, apiBase = "", greeting, tierLevel = "FOUNDERS_CIRCLE", analystName = "XR7 Strategy Team", referralSlotsRemaining = 5, onReferralClick, }) {
    const [drops, setDrops] = useState([]);
    const [dropIdx, setDropIdx] = useState(0);
    const [glowState, setGlowState] = useState("idle");
    useEffect(() => {
        fetch(`${apiBase}/artists/${artistId}/vip/drops`)
            .then((r) => (r.ok ? r.json() : []))
            .then(setDrops)
            .catch(() => { });
    }, [artistId, apiBase]);
    // Glow burst on mount
    useEffect(() => {
        setGlowState("active");
        const t = setTimeout(() => setGlowState("idle"), 1200);
        return () => clearTimeout(t);
    }, []);
    // Auto-rotate drops
    useEffect(() => {
        if (drops.length <= 1)
            return;
        const t = setInterval(() => setDropIdx((i) => (i + 1) % drops.length), 5000);
        return () => clearInterval(t);
    }, [drops.length]);
    const currentDrop = drops[dropIdx];
    return (_jsxs("div", { className: "fc-banner", children: [_jsxs("div", { className: "flex items-center gap-4 px-5 pt-4 pb-3 border-b border-purple-800/30", children: [_jsx(XR7LogoGlow, { state: glowState, size: 44 }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsxs("div", { className: "flex items-center gap-2 flex-wrap", children: [_jsx(VIPBadge, { tierLevel: tierLevel, size: "sm", animated: true }), _jsx("span", { className: "text-purple-500 text-xs", children: "\u00B7" }), _jsx("span", { className: "text-purple-400 text-xs", children: analystName })] }), greeting && (_jsx("p", { className: "text-purple-100 text-sm font-medium mt-0.5 leading-snug", children: greeting }))] }), _jsxs("div", { className: "text-right flex-shrink-0", children: [_jsx("p", { className: "text-purple-400 text-xs", children: "Referral slots" }), _jsx("p", { className: "text-purple-200 text-lg font-bold leading-none", children: referralSlotsRemaining })] })] }), currentDrop && (_jsxs("div", { className: "px-5 py-3 border-b border-purple-800/20", children: [_jsxs("div", { className: "flex items-center gap-2 mb-1.5", children: [_jsx("span", { className: "text-xs font-bold text-purple-400 uppercase tracking-widest", children: "VIP Drop" }), currentDrop.is_new && (_jsx("span", { className: "bg-purple-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full", children: "NEW" })), drops.length > 1 && (_jsx("div", { className: "ml-auto flex gap-1", children: drops.map((_, i) => (_jsx("button", { onClick: () => setDropIdx(i), className: [
                                        "w-1.5 h-1.5 rounded-full transition-all",
                                        i === dropIdx ? "bg-purple-400 scale-125" : "bg-purple-700",
                                    ].join(" "), "aria-label": `Switch to drop ${i + 1}` }, i))) }))] }), _jsx("h4", { className: "text-purple-100 text-sm font-semibold", children: currentDrop.title }), _jsx("p", { className: "text-purple-400 text-xs mt-0.5 leading-relaxed line-clamp-2", children: currentDrop.description })] })), _jsx("div", { className: "flex items-center gap-2 px-5 py-3 flex-wrap", children: _jsxs("button", { onClick: onReferralClick, className: "fc-cta-btn flex items-center gap-1.5", disabled: referralSlotsRemaining === 0, title: "Invite another elite creator", children: [_jsx("span", { children: "\u2709" }), _jsx("span", { children: "Invite a Creator" }), _jsxs("span", { className: "text-purple-400 text-[10px]", children: ["(", referralSlotsRemaining, " left)"] })] }) }), _jsx("style", { children: `
        .fc-banner {
          background: linear-gradient(135deg, rgba(30,8,65,0.97) 0%, rgba(45,12,90,0.95) 50%, rgba(30,8,65,0.97) 100%);
          border: 1px solid rgba(168,85,247,0.28);
          border-radius: 14px;
          box-shadow: 0 4px 30px rgba(168,85,247,0.12), 0 0 0 0.5px rgba(168,85,247,0.10);
          overflow: hidden;
        }
        .fc-cta-btn {
          font-size: 0.78rem;
          padding: 0.4rem 1rem;
          border-radius: 9999px;
          background: linear-gradient(135deg, rgba(168,85,247,0.18), rgba(124,58,237,0.14));
          border: 1px solid rgba(168,85,247,0.38);
          color: #d8b4fe;
          cursor: pointer;
          font-weight: 600;
          transition: background 0.2s, transform 0.15s;
        }
        .fc-cta-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, rgba(168,85,247,0.32), rgba(124,58,237,0.26));
          transform: scale(1.03);
        }
        .fc-cta-btn:disabled { opacity: 0.45; cursor: not-allowed; }
      ` })] }));
}
