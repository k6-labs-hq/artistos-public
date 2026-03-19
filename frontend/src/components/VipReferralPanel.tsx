/**
 * VipReferralPanel — Referral programme UI for Founders Circle members.
 *
 * Shows referral slots remaining, invite-by-email form,
 * generated invite link, and existing referral status list.
 */
import { useEffect, useState } from "react";

interface VipReferral {
  id: string;
  referred_email: string;
  status: "PENDING" | "CLAIMED" | "EXPIRED" | "CANCELLED";
  perk_granted_code: string | null;
  created_at: string;
  claimed_at: string | null;
}

interface CreateReferralResponse {
  id: string;
  invite_code: string;
  invite_link: string;
  referred_email: string;
}

export interface VipReferralPanelProps {
  artistId: string;
  apiBase?: string;
  slotsRemaining?: number;
  inviteBaseUrl?: string;
}

const STATUS_CONFIG: Record<
  VipReferral["status"],
  { label: string; color: string; bg: string }
> = {
  PENDING: { label: "Pending", color: "#fbbf24", bg: "rgba(251,191,36,0.12)" },
  CLAIMED: { label: "Joined ✓", color: "#86efac", bg: "rgba(134,239,172,0.12)" },
  EXPIRED: { label: "Expired", color: "#f87171", bg: "rgba(248,113,113,0.12)" },
  CANCELLED: { label: "Cancelled", color: "#9f7ced", bg: "rgba(159,124,237,0.1)" },
};

export function VipReferralPanel({
  artistId,
  apiBase = "",
  slotsRemaining: initialSlots = 5,
}: VipReferralPanelProps) {
  const [referrals, setReferrals] = useState<VipReferral[]>([]);
  const [slots, setSlots] = useState(initialSlots);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [createdLink, setCreatedLink] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReferrals();
  }, [artistId]);

  async function fetchReferrals() {
    try {
      const r = await fetch(`${apiBase}/artists/${artistId}/vip/referrals`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setReferrals(data.referrals ?? data ?? []);
      if (data.slots_remaining !== undefined) setSlots(data.slots_remaining);
    } catch {
      // silent — slots from prop
    } finally {
      setLoading(false);
    }
  }

  async function sendInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || submitting || slots <= 0) return;
    setSubmitting(true);
    setError(null);
    setCreatedLink(null);
    try {
      const r = await fetch(`${apiBase}/artists/${artistId}/vip/referral`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ referred_email: email.trim() }),
      });
      if (!r.ok) {
        const body = await r.json().catch(() => ({}));
        throw new Error(body.detail ?? `HTTP ${r.status}`);
      }
      const data: CreateReferralResponse = await r.json();
      setCreatedLink(data.invite_link);
      setSlots((s) => Math.max(0, s - 1));
      setEmail("");
      await fetchReferrals();
    } catch (err: unknown) {
      setError((err as Error).message ?? "Failed to create invite");
    } finally {
      setSubmitting(false);
    }
  }

  async function copyLink() {
    if (!createdLink) return;
    await navigator.clipboard.writeText(createdLink).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="vrp-panel">
      {/* Header */}
      <div className="vrp-header">
        <div>
          <h3 className="vrp-title">Invite a Creator</h3>
          <p className="vrp-subtitle">
            Share your VIP access with another elite artist
          </p>
        </div>
        <div className="vrp-slots-badge" title="Invites you can still send">
          <span className="vrp-slots-num">{slots}</span>
          <span className="vrp-slots-label">slots left</span>
        </div>
      </div>

      {/* Invite form */}
      <form onSubmit={sendInvite} className="vrp-form" noValidate>
        <div className="vrp-input-row">
          <input
            type="email"
            placeholder="creator@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="vrp-email-input"
            disabled={submitting || slots <= 0}
            required
          />
          <button
            type="submit"
            className="vrp-send-btn"
            disabled={submitting || slots <= 0 || !email.trim()}
          >
            {submitting ? <span className="vrp-spinner" /> : "Send Invite"}
          </button>
        </div>
        {slots === 0 && (
          <p className="vrp-no-slots">No referral slots remaining.</p>
        )}
        {error && <p className="vrp-error">⚠ {error}</p>}
      </form>

      {/* Generated invite link */}
      {createdLink && (
        <div className="vrp-link-box">
          <span className="vrp-link-label">Invite link</span>
          <div className="vrp-link-row">
            <span className="vrp-link-text">{createdLink}</span>
            <button className="vrp-copy-btn" onClick={copyLink}>
              {copied ? "✓ Copied" : "Copy"}
            </button>
          </div>
        </div>
      )}

      {/* Referral list */}
      <div className="vrp-list-section">
        <h4 className="vrp-list-title">
          Your Referrals {referrals.length > 0 && `(${referrals.length})`}
        </h4>
        {loading ? (
          <div className="vrp-skel-list">
            <div className="vrp-skel-row" />
            <div className="vrp-skel-row" />
          </div>
        ) : referrals.length === 0 ? (
          <p className="vrp-empty">No referrals sent yet.</p>
        ) : (
          <ul className="vrp-referral-list">
            {referrals.map((ref) => {
              const cfg = STATUS_CONFIG[ref.status];
              return (
                <li key={ref.id} className="vrp-referral-item">
                  <div className="vrp-referral-email">{ref.referred_email}</div>
                  <div className="flex items-center gap-2">
                    <span
                      className="vrp-status-chip"
                      style={{ color: cfg.color, background: cfg.bg }}
                    >
                      {cfg.label}
                    </span>
                    {ref.claimed_at && (
                      <span className="vrp-date">
                        {new Date(ref.claimed_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <style>{css}</style>
    </div>
  );
}

const css = `
  .vrp-panel {
    background:linear-gradient(145deg,rgba(30,8,65,0.97) 0%,rgba(45,12,90,0.95) 100%);
    border:1px solid rgba(168,85,247,0.28); border-radius:14px; overflow:hidden;
  }
  .vrp-header {
    display:flex; align-items:center; justify-content:space-between;
    padding:1rem 1.25rem 0.75rem;
    border-bottom:1px solid rgba(168,85,247,0.18);
  }
  .vrp-title { font-size:0.9rem; font-weight:700; color:#e9d5ff; margin:0; }
  .vrp-subtitle { font-size:0.72rem; color:#9f7ced; margin:0.1rem 0 0; }
  .vrp-slots-badge {
    display:flex; flex-direction:column; align-items:center;
    padding:0.4rem 0.85rem;
    border:1px solid rgba(168,85,247,0.38); border-radius:12px;
    background:rgba(168,85,247,0.1); text-align:center;
  }
  .vrp-slots-num { font-size:1.4rem; font-weight:900; color:#d8b4fe; line-height:1; }
  .vrp-slots-label { font-size:0.6rem; color:#9f7ced; text-transform:uppercase; letter-spacing:0.1em; }
  .vrp-form { padding:0.9rem 1.25rem; border-bottom:1px solid rgba(168,85,247,0.15); }
  .vrp-input-row { display:flex; gap:0.5rem; }
  .vrp-email-input {
    flex:1; font-size:0.83rem; color:#e9d5ff; line-height:1.4;
    background:rgba(60,20,120,0.35); border:1px solid rgba(168,85,247,0.3);
    border-radius:10px; padding:0.5rem 0.85rem; outline:none;
    transition:border-color 0.2s;
  }
  .vrp-email-input:focus { border-color:rgba(168,85,247,0.65); }
  .vrp-email-input::placeholder { color:#6d4fa3; }
  .vrp-send-btn {
    padding:0.5rem 1.15rem; border-radius:10px; cursor:pointer; font-weight:700;
    font-size:0.8rem; border:none;
    background:linear-gradient(135deg,#7c3aed,#a855f7); color:#fff;
    display:flex; align-items:center; justify-content:center; gap:0.3rem;
    transition:opacity 0.18s; white-space:nowrap; min-width:100px;
  }
  .vrp-send-btn:disabled { opacity:0.4; cursor:not-allowed; }
  .vrp-send-btn:hover:not(:disabled) { opacity:0.85; }
  .vrp-spinner {
    width:14px; height:14px;
    border:2px solid rgba(255,255,255,0.3);
    border-top-color:#fff; border-radius:50%;
    animation:spin 0.7s linear infinite; display:inline-block;
  }
  @keyframes spin{to{transform:rotate(360deg)}}
  .vrp-no-slots { font-size:0.75rem; color:#9f7ced; margin:0.45rem 0 0; }
  .vrp-error { font-size:0.75rem; color:#f87171; margin:0.45rem 0 0; }
  .vrp-link-box {
    margin:0.75rem 1.25rem; padding:0.7rem;
    border:1px dashed rgba(168,85,247,0.4); border-radius:10px;
    background:rgba(168,85,247,0.07);
  }
  .vrp-link-label { font-size:0.65rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.1em; color:#a855f7; display:block; margin-bottom:0.35rem; }
  .vrp-link-row { display:flex; align-items:center; gap:0.5rem; }
  .vrp-link-text {
    flex:1; font-size:0.74rem; color:#c4b5fd; word-break:break-all;
    font-family:monospace;
  }
  .vrp-copy-btn {
    font-size:0.72rem; padding:0.3rem 0.7rem; border-radius:8px; cursor:pointer;
    border:1px solid rgba(168,85,247,0.38); background:rgba(168,85,247,0.14);
    color:#d8b4fe; font-weight:600; white-space:nowrap; transition:background 0.18s;
    flex-shrink:0;
  }
  .vrp-copy-btn:hover { background:rgba(168,85,247,0.28); }
  .vrp-list-section { padding:0.85rem 1.25rem 1rem; }
  .vrp-list-title {
    font-size:0.68rem; font-weight:800; text-transform:uppercase;
    letter-spacing:0.12em; color:#a855f7; margin:0 0 0.6rem;
  }
  .vrp-referral-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:0.45rem; }
  .vrp-referral-item {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.5rem 0.75rem; border-radius:8px;
    background:rgba(88,28,135,0.12); border:1px solid rgba(88,28,135,0.25);
    gap:0.5rem;
  }
  .vrp-referral-email { font-size:0.8rem; color:#e9d5ff; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }
  .vrp-status-chip { font-size:0.65rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:9999px; white-space:nowrap; }
  .vrp-date { font-size:0.65rem; color:#7e6bad; }
  .vrp-empty { font-size:0.8rem; color:#7e6bad; }
  .vrp-skel-list { display:flex; flex-direction:column; gap:0.4rem; }
  .vrp-skel-row {
    height:42px; border-radius:8px;
    background:linear-gradient(90deg,rgba(88,28,135,0.3) 25%,rgba(168,85,247,0.18) 50%,rgba(88,28,135,0.3) 75%);
    background-size:200% 100%; animation:shimmer 1.4s infinite;
  }
  @keyframes shimmer{to{background-position:-200% 0}}
`;
