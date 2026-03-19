import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const TIER_LABELS = {
    FOUNDERS_CIRCLE: "Founders Circle",
    VIP: "VIP Member",
};
const SIZE_CLASSES = {
    sm: "text-xs px-2 py-0.5 gap-1",
    md: "text-sm px-3 py-1 gap-1.5",
    lg: "text-base px-4 py-1.5 gap-2",
};
const ICON_SIZE = {
    sm: 12,
    md: 16,
    lg: 20,
};
export function VIPBadge({ tierLevel = "FOUNDERS_CIRCLE", size = "md", animated = true, className = "", }) {
    const label = TIER_LABELS[tierLevel] ?? "VIP";
    return (_jsxs("span", { className: [
            "inline-flex items-center font-semibold rounded-full select-none",
            "border border-purple-400/50",
            "bg-gradient-to-r from-purple-900/80 via-purple-700/70 to-purple-900/80",
            "text-purple-100",
            animated ? "vip-badge-glow" : "",
            SIZE_CLASSES[size],
            className,
        ]
            .filter(Boolean)
            .join(" "), title: `${label} — Invite-Only Premier Experience`, children: [_jsxs("svg", { width: ICON_SIZE[size], height: ICON_SIZE[size], viewBox: "0 0 16 16", fill: "none", "aria-hidden": "true", className: animated ? "vip-icon-pulse" : "", children: [_jsx("polygon", { points: "8,1 15,6 8,15 1,6", fill: "url(#vip-diamond-grad)", stroke: "#A855F7", strokeWidth: "0.8" }), _jsx("defs", { children: _jsxs("linearGradient", { id: "vip-diamond-grad", x1: "0", y1: "0", x2: "1", y2: "1", children: [_jsx("stop", { offset: "0%", stopColor: "#E9D5FF" }), _jsx("stop", { offset: "50%", stopColor: "#A855F7" }), _jsx("stop", { offset: "100%", stopColor: "#7C3AED" })] }) })] }), _jsx("span", { children: label }), _jsx("style", { children: `
        .vip-badge-glow {
          box-shadow: 0 0 8px 2px rgba(168, 85, 247, 0.45),
                      0 0 20px 4px rgba(168, 85, 247, 0.15);
          animation: vipBadgePulse 3s ease-in-out infinite;
        }
        @keyframes vipBadgePulse {
          0%, 100% { box-shadow: 0 0 8px 2px rgba(168, 85, 247, 0.45), 0 0 20px 4px rgba(168, 85, 247, 0.15); }
          50%       { box-shadow: 0 0 14px 5px rgba(168, 85, 247, 0.70), 0 0 30px 8px rgba(168, 85, 247, 0.25); }
        }
        .vip-icon-pulse {
          animation: vipIconSpin 8s linear infinite;
        }
        @keyframes vipIconSpin {
          0%   { transform: rotate(0deg)   scale(1);    }
          25%  { transform: rotate(5deg)   scale(1.08); }
          50%  { transform: rotate(0deg)   scale(1);    }
          75%  { transform: rotate(-5deg)  scale(1.08); }
          100% { transform: rotate(0deg)   scale(1);    }
        }
      ` })] }));
}
