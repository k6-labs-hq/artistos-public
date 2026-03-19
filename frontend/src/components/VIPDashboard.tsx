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

/* ─── Data types ─────────────────────────────────────────────────────────── */

interface VipStatus {
  is_vip: boolean;
  tier_level: "FOUNDERS_CIRCLE" | "VIP" | null;
  perks_unlocked: string[];
  referral_slots_remaining: number;
  concierge_analyst_name: string | null;
  concierge_analyst_email: string | null;
  calendly_link: string | null;
  logo_url: string | null;
  watermark_text: string | null;
  joined_at: string | null;
}

interface PersonaSnippet {
  primary_vertical: "music" | "tv_film" | "other" | null;
  bio_snippet: string | null;
  genre_tags: string[];
}

export interface VIPDashboardProps {
  artistId: string;
  apiBase?: string;
  /** Pre-injected state from LangGraph onboarding agent */
  agentState?: {
    vip_active?: boolean;
    vip_tier?: string;
    vip_perks?: string[];
    persona_greeting?: string;
    adaptive_ui_mode?: string;
    concierge_analyst_name?: string;
    concierge_calendly_link?: string;
  };
}

type Tab = "overview" | "concierge" | "copilot" | "legacy" | "referrals";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "overview", label: "Overview", icon: "◈" },
  { id: "concierge", label: "Concierge", icon: "✉" },
  { id: "copilot", label: "XR7 Advisor", icon: "⬡" },
  { id: "legacy", label: "Legacy Map", icon: "✦" },
  { id: "referrals", label: "Referrals", icon: "⊕" },
];

/* ─── Component ─────────────────────────────────────────────────────────── */

export function VIPDashboard({
  artistId,
  apiBase = "",
  agentState,
}: VIPDashboardProps) {
  const [status, setStatus] = useState<VipStatus | null>(null);
  const [persona, setPersona] = useState<PersonaSnippet | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [loading, setLoading] = useState(true);
  const [notVip, setNotVip] = useState(false);
  const [logoGlowState, setLogoGlowState] = useState<"idle" | "loading" | "active">(
    "loading"
  );

  useEffect(() => {
    Promise.all([
      fetch(`${apiBase}/artists/${artistId}/vip/status`).then((r) =>
        r.ok ? r.json() : null
      ),
      fetch(`${apiBase}/artists/${artistId}/persona`).then((r) =>
        r.ok ? r.json() : null
      ),
    ])
      .then(([vipData, personaData]) => {
        if (!vipData?.is_vip) {
          setNotVip(true);
        } else {
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

  if (loading) return <DashboardSkeleton />;
  if (notVip) return <NotVipGate apiBase={apiBase} />;

  const tier = (status?.tier_level ?? agentState?.vip_tier ?? "VIP") as
    | "FOUNDERS_CIRCLE"
    | "VIP";
  const greeting =
    agentState?.persona_greeting ??
    (status?.concierge_analyst_name
      ? `Welcome back. ${status.concierge_analyst_name} is here when you need them.`
      : "Welcome to your Founders Circle experience.");

  const vertical = persona?.primary_vertical ?? "music";

  return (
    <div className="vd-root">
      {/* === Header strip === */}
      <header className="vd-header">
        <div className="vd-header-inner">
          <XR7LogoGlow state={logoGlowState} size={38} />
          <div className="flex-1 min-w-0">
            <VIPBadge tierLevel={tier} size="sm" animated />
            <p className="vd-greeting">{greeting}</p>
          </div>
          {status?.logo_url && (
            <img
              src={status.logo_url}
              alt="Custom logo"
              className="vd-custom-logo"
            />
          )}
        </div>
      </header>

      {/* === Founders Circle Banner (full-width) === */}
      <div className="vd-banner-wrap">
        <FoundersCircleBanner
          artistId={artistId}
          apiBase={apiBase}
          greeting={greeting}
          tierLevel={tier}
          analystName={status?.concierge_analyst_name ?? "XR7 Strategy Team"}
          referralSlotsRemaining={status?.referral_slots_remaining ?? 0}
          onReferralClick={() => setActiveTab("referrals")}
        />
      </div>

      {/* === Tab bar === */}
      <nav className="vd-tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={activeTab === t.id}
            className={["vd-tab", activeTab === t.id ? "active" : ""].join(" ")}
            onClick={() => setActiveTab(t.id)}
          >
            <span className="vd-tab-icon">{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </nav>

      {/* === Tab panels === */}
      <main className="vd-panel">
        {activeTab === "overview" && (
          <OverviewPane
            artistId={artistId}
            apiBase={apiBase}
            persona={persona}
            status={status}
            vertical={vertical}
          />
        )}
        {activeTab === "concierge" && (
          <ConciergeInbox
            artistId={artistId}
            apiBase={apiBase}
            analystName={status?.concierge_analyst_name ?? undefined}
            calendlyLink={status?.calendly_link ?? undefined}
          />
        )}
        {activeTab === "copilot" && (
          <CopilotChat
            artistId={artistId}
            apiBase={apiBase}
            personaGreeting={greeting}
          />
        )}
        {activeTab === "legacy" && (
          <LegacyMap artistId={artistId} apiBase={apiBase} />
        )}
        {activeTab === "referrals" && (
          <VipReferralPanel
            artistId={artistId}
            apiBase={apiBase}
            slotsRemaining={status?.referral_slots_remaining ?? 0}
          />
        )}
      </main>

      <style>{css}</style>
    </div>
  );
}

/* ─── Overview pane ─────────────────────────────────────────────────────── */

interface OverviewPaneProps {
  artistId: string;
  apiBase: string;
  persona: PersonaSnippet | null;
  status: VipStatus | null;
  vertical: string;
}

function OverviewPane({
  artistId,
  apiBase,
  persona,
  status,
  vertical,
}: OverviewPaneProps) {
  return (
    <div className="vd-overview">
      {/* Column A: Persona + Recovery Timeline */}
      <div className="vd-col-a">
        <PersonaCard artistId={artistId} apiBase={apiBase} />
        <RecoveryStoryTimeline artistId={artistId} apiBase={apiBase} />
      </div>

      {/* Column B: Weekly Brief + perks strip */}
      <div className="vd-col-b">
        <WeeklyBriefCard artistId={artistId} apiBase={apiBase} />

        {vertical !== "music" && (
          <div className="vd-vertical-note">
            <span className="vd-vertical-icon">
              {vertical === "tv_film" ? "🎬" : "◈"}
            </span>
            <span>
              Your profile is tailored for the{" "}
              <strong>{vertical === "tv_film" ? "TV & Film" : vertical}</strong>{" "}
              vertical.
            </span>
          </div>
        )}

        {/* Perks strip */}
        {(status?.perks_unlocked?.length ?? 0) > 0 && (
          <div className="vd-perks">
            <h4 className="vd-perks-title">Your Perks</h4>
            <div className="vd-perks-list">
              {status!.perks_unlocked.map((p) => (
                <span key={p} className="vd-perk-chip">
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Watermark branding */}
        {status?.watermark_text && (
          <div className="vd-watermark">{status.watermark_text}</div>
        )}
      </div>
    </div>
  );
}

/* ─── Not-VIP gate ──────────────────────────────────────────────────────── */

function NotVipGate({ apiBase }: { apiBase: string }) {
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function claim(e: React.FormEvent) {
    e.preventDefault();
    if (!code.trim() || submitting) return;
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
    } catch (err: unknown) {
      setError((err as Error).message ?? "Invalid code");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="vd-gate">
      <XR7LogoGlow state="idle" size={52} />
      <h2 className="vd-gate-title">Founders Circle</h2>
      <p className="vd-gate-sub">
        This experience is invite-only. Enter your exclusive access code below.
      </p>
      {success ? (
        <div className="vd-gate-success">
          ✓ You're in. Reload to access your VIP dashboard.
        </div>
      ) : (
        <form onSubmit={claim} className="vd-gate-form" noValidate>
          <input
            type="text"
            placeholder="Enter invite code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="vd-gate-input"
            maxLength={64}
          />
          <button className="vd-gate-btn" type="submit" disabled={submitting}>
            {submitting ? <span className="vd-gate-spinner" /> : "Claim Access"}
          </button>
          {error && <p className="vd-gate-error">⚠ {error}</p>}
        </form>
      )}
      <style>{css}</style>
    </div>
  );
}

/* ─── Loading skeleton ───────────────────────────────────────────────────── */

function DashboardSkeleton() {
  return (
    <div className="vd-root">
      <div style={{ padding: "1.25rem" }}>
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            style={{
              height: i === 1 ? 28 : i === 2 ? 80 : 140,
              borderRadius: 10,
              marginBottom: "0.75rem",
              background:
                "linear-gradient(90deg,rgba(88,28,135,0.3) 25%,rgba(168,85,247,0.18) 50%,rgba(88,28,135,0.3) 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.4s infinite",
            }}
          />
        ))}
      </div>
      <style>{`@keyframes shimmer{to{background-position:-200% 0}}`}</style>
    </div>
  );
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
