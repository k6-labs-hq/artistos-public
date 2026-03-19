/**
 * FoundersCircleBanner — Early access banner for VIP members.
 *
 * Displays the Founders Circle badge, VIP drops carousel,
 * referral CTA, and adaptive greeting.
 */
import { useEffect, useState } from "react";
import { VIPBadge } from "./VIPBadge";
import { XR7LogoGlow } from "./XR7LogoGlow";

interface VipDrop {
  title: string;
  description: string;
  available_since: string;
  is_new: boolean;
  feature_flag?: string;
}

export interface FoundersCircleBannerProps {
  artistId: string;
  apiBase?: string;
  greeting?: string;
  tierLevel?: "FOUNDERS_CIRCLE" | "VIP";
  analystName?: string;
  referralSlotsRemaining?: number;
  onReferralClick?: () => void;
}

export function FoundersCircleBanner({
  artistId,
  apiBase = "",
  greeting,
  tierLevel = "FOUNDERS_CIRCLE",
  analystName = "XR7 Strategy Team",
  referralSlotsRemaining = 5,
  onReferralClick,
}: FoundersCircleBannerProps) {
  const [drops, setDrops] = useState<VipDrop[]>([]);
  const [dropIdx, setDropIdx] = useState(0);
  const [glowState, setGlowState] = useState<"idle" | "active">("idle");

  useEffect(() => {
    fetch(`${apiBase}/artists/${artistId}/vip/drops`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setDrops)
      .catch(() => {});
  }, [artistId, apiBase]);

  // Glow burst on mount
  useEffect(() => {
    setGlowState("active");
    const t = setTimeout(() => setGlowState("idle"), 1200);
    return () => clearTimeout(t);
  }, []);

  // Auto-rotate drops
  useEffect(() => {
    if (drops.length <= 1) return;
    const t = setInterval(() => setDropIdx((i) => (i + 1) % drops.length), 5000);
    return () => clearInterval(t);
  }, [drops.length]);

  const currentDrop = drops[dropIdx];

  return (
    <div className="fc-banner">
      {/* Top row: logo + badge + greeting */}
      <div className="flex items-center gap-4 px-5 pt-4 pb-3 border-b border-purple-800/30">
        <XR7LogoGlow state={glowState} size={44} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <VIPBadge tierLevel={tierLevel} size="sm" animated />
            <span className="text-purple-500 text-xs">·</span>
            <span className="text-purple-400 text-xs">{analystName}</span>
          </div>
          {greeting && (
            <p className="text-purple-100 text-sm font-medium mt-0.5 leading-snug">
              {greeting}
            </p>
          )}
        </div>
        <div className="text-right flex-shrink-0">
          <p className="text-purple-400 text-xs">Referral slots</p>
          <p className="text-purple-200 text-lg font-bold leading-none">
            {referralSlotsRemaining}
          </p>
        </div>
      </div>

      {/* VIP Drop carousel */}
      {currentDrop && (
        <div className="px-5 py-3 border-b border-purple-800/20">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-widest">
              VIP Drop
            </span>
            {currentDrop.is_new && (
              <span className="bg-purple-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                NEW
              </span>
            )}
            {drops.length > 1 && (
              <div className="ml-auto flex gap-1">
                {drops.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setDropIdx(i)}
                    className={[
                      "w-1.5 h-1.5 rounded-full transition-all",
                      i === dropIdx ? "bg-purple-400 scale-125" : "bg-purple-700",
                    ].join(" ")}
                    aria-label={`Switch to drop ${i + 1}`}
                  />
                ))}
              </div>
            )}
          </div>
          <h4 className="text-purple-100 text-sm font-semibold">{currentDrop.title}</h4>
          <p className="text-purple-400 text-xs mt-0.5 leading-relaxed line-clamp-2">
            {currentDrop.description}
          </p>
        </div>
      )}

      {/* Bottom row: quick actions */}
      <div className="flex items-center gap-2 px-5 py-3 flex-wrap">
        <button
          onClick={onReferralClick}
          className="fc-cta-btn flex items-center gap-1.5"
          disabled={referralSlotsRemaining === 0}
          title="Invite another elite creator"
        >
          <span>✉</span>
          <span>Invite a Creator</span>
          <span className="text-purple-400 text-[10px]">({referralSlotsRemaining} left)</span>
        </button>
      </div>

      <style>{`
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
      `}</style>
    </div>
  );
}
