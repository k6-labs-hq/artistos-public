/**
 * XR7LogoGlow — Animated XR7 logo with cinematic purple glow/pulse.
 *
 * Used on load screens, VIP onboarding, and interaction micro-states.
 * Supports "idle", "loading", and "active" pulse intensities.
 */

export type GlowState = "idle" | "loading" | "active";

export interface XR7LogoGlowProps {
  state?: GlowState;
  size?: number;
  className?: string;
}

export function XR7LogoGlow({ state = "idle", size = 48, className = "" }: XR7LogoGlowProps) {
  const animClass =
    state === "loading"
      ? "xr7-glow-loading"
      : state === "active"
      ? "xr7-glow-active"
      : "xr7-glow-idle";

  return (
    <div
      className={["relative inline-flex items-center justify-center", animClass, className]
        .filter(Boolean)
        .join(" ")}
      style={{ width: size, height: size }}
      aria-label="XR7 Engine"
    >
      {/* Outer glow ring */}
      <div
        className="absolute inset-0 rounded-full xr7-ring"
        style={{
          background:
            "radial-gradient(circle, rgba(168,85,247,0.35) 0%, rgba(124,58,237,0.10) 60%, transparent 80%)",
        }}
      />
      {/* Logo mark */}
      <svg
        width={size * 0.65}
        height={size * 0.65}
        viewBox="0 0 32 32"
        fill="none"
        aria-hidden="true"
      >
        {/* X */}
        <line x1="4" y1="4" x2="14" y2="16" stroke="#A855F7" strokeWidth="2.5" strokeLinecap="round" />
        <line x1="14" y1="4" x2="4" y2="16" stroke="#A855F7" strokeWidth="2.5" strokeLinecap="round" />
        {/* R */}
        <path
          d="M18 4 L18 16 M18 4 L24 4 Q28 4 28 8 Q28 12 24 12 L18 12 M24 12 L28 16"
          stroke="#C084FC"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        {/* 7 */}
        <path
          d="M4 20 L12 20 L7 32"
          stroke="#E9D5FF"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      </svg>

      <style>{`
        .xr7-ring {
          transition: opacity 0.4s ease;
        }
        .xr7-glow-idle .xr7-ring {
          animation: xr7IdlePulse 4s ease-in-out infinite;
        }
        .xr7-glow-loading .xr7-ring {
          animation: xr7LoadingPulse 1.2s ease-in-out infinite;
        }
        .xr7-glow-active .xr7-ring {
          animation: xr7ActiveBurst 0.6s ease-out forwards;
        }
        @keyframes xr7IdlePulse {
          0%, 100% { opacity: 0.6; transform: scale(1);    }
          50%       { opacity: 1.0; transform: scale(1.08); }
        }
        @keyframes xr7LoadingPulse {
          0%, 100% { opacity: 0.5; transform: scale(0.95); }
          50%       { opacity: 1.0; transform: scale(1.15); }
        }
        @keyframes xr7ActiveBurst {
          0%   { opacity: 0.4; transform: scale(1);    }
          40%  { opacity: 1.0; transform: scale(1.35); }
          100% { opacity: 0.7; transform: scale(1.1);  }
        }
      `}</style>
    </div>
  );
}
