import React, { useEffect, useState } from "react";

import { ErrorBoundary } from "./ErrorBoundary";
import "./InviteDashboard.css";

interface Invite {
  id: string;
  recipient_name: string;
  recipient_email: string | null;
  status: string;
  created_at: string;
  is_vip: boolean;
}

interface QuickGenerateResult {
  success: boolean;
  invite_id: string;
  invite_link: string;
  recipient_name: string;
  expires_at: string;
  error?: string;
}

export const InviteDashboard: React.FC = () => {
  const [recipientName, setRecipientName] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [role, setRole] = useState("artist");
  const [campaign, setCampaign] = useState("");
  const [isVip, setIsVip] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QuickGenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [invites, setInvites] = useState<Invite[]>([]);
  const [invitesLoading, setInvitesLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"generate" | "list" | "analytics">(
    "generate"
  );
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    loadInvites();
    loadAnalytics();
  }, []);

  const loadInvites = async () => {
    setInvitesLoading(true);
    try {
      const response = await fetch("/api/invites/?limit=50&offset=0");
      const data = await response.json();
      setInvites(data.invites);
    } catch (err) {
      console.error("Failed to load invites:", err);
    } finally {
      setInvitesLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch("/api/invites/analytics/summary?days=30");
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    }
  };

  const handleQuickGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/invites/dashboard/quick-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recipient_name: recipientName,
          recipient_email: recipientEmail || null,
          role,
          campaign: campaign || "manual_generation",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Failed to generate invite");
      } else {
        setResult(data);
        // Reset form
        setRecipientName("");
        setRecipientEmail("");
        setRole("artist");
        setCampaign("");
        setIsVip(false);
        // Reload invites
        loadInvites();
      }
    } catch (err) {
      setError("Network error generating invite");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Link copied to clipboard!");
    });
  };

  return (
    <ErrorBoundary name="Invite Dashboard">
    <div className="invite-dashboard">
      <h1>Invite Management Dashboard</h1>
      <p className="subtitle">
        Generate and manage private XR7 invites for selected creators.
      </p>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === "generate" ? "active" : ""}`}
          onClick={() => setActiveTab("generate")}
        >
          Generate Invite
        </button>
        <button
          className={`tab ${activeTab === "list" ? "active" : ""}`}
          onClick={() => setActiveTab("list")}
        >
          All Invites ({invites.length})
        </button>
        <button
          className={`tab ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          Analytics
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === "generate" && (
        <div className="tab-content">
          <form onSubmit={handleQuickGenerate} className="generate-form">
            <div className="form-group">
              <label>Recipient Name</label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="e.g., Jane Smith"
                required
              />
            </div>

            <div className="form-group">
              <label>Email Address (optional)</label>
              <input
                type="email"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                placeholder="jane@example.com"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="artist">Artist</option>
                  <option value="writer">Writer</option>
                  <option value="director">Director</option>
                  <option value="actor">Actor</option>
                  <option value="studio">Studio</option>
                  <option value="manager">Manager</option>
                  <option value="agent">Agent</option>
                </select>
              </div>

              <div className="form-group">
                <label>Campaign</label>
                <input
                  type="text"
                  value={campaign}
                  onChange={(e) => setCampaign(e.target.value)}
                  placeholder="e.g., vip_kickoff"
                />
              </div>
            </div>

            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={isVip}
                  onChange={(e) => setIsVip(e.target.checked)}
                />
                Grant VIP Status
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? "Generating..." : "Generate Invite Link"}
            </button>
          </form>

          {/* Result */}
          {result && (
            <div className="result-card success">
              <div className="result-header">
                <h3>✓ Invite Generated Successfully</h3>
                <p className="result-id">ID: {result.invite_id}</p>
              </div>

              <div className="result-details">
                <p>
                  <strong>Recipient:</strong> {result.recipient_name}
                </p>
                <p>
                  <strong>Expires:</strong>{" "}
                  {new Date(result.expires_at).toLocaleString()}
                </p>
              </div>

              <div className="result-link-section">
                <label>Invite Link:</label>
                <div className="link-box">
                  <code>{result.invite_link}</code>
                  <button
                    className="copy-button"
                    onClick={() => copyToClipboard(result.invite_link)}
                  >
                    Copy
                  </button>
                </div>
              </div>

              <p className="result-hint">
                Share this link with the creator. It's exclusive to them and
                expires in 72 hours.
              </p>
            </div>
          )}
        </div>
      )}

      {/* List Tab */}
      {activeTab === "list" && (
        <div className="tab-content">
          {invitesLoading ? (
            <p className="loading-text">Loading invites...</p>
          ) : invites.length > 0 ? (
            <div className="invites-table">
              <table>
                <thead>
                  <tr>
                    <th>Recipient Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>VIP</th>
                  </tr>
                </thead>
                <tbody>
                  {invites.map((invite) => (
                    <tr key={invite.id}>
                      <td>{invite.recipient_name}</td>
                      <td>{invite.recipient_email || "—"}</td>
                      <td>
                        <span className={`status-badge ${invite.status}`}>
                          {invite.status}
                        </span>
                      </td>
                      <td>{new Date(invite.created_at).toLocaleDateString()}</td>
                      <td>{invite.is_vip ? "✓" : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="loading-text">No invites yet. Generate one above.</p>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === "analytics" && (
        <div className="tab-content">
          {analytics ? (
            <div className="analytics-grid">
              <div className="stat-card">
                <h4>Invites Created</h4>
                <p className="stat-value">{analytics.invites_created}</p>
              </div>
              <div className="stat-card">
                <h4>Invites Sent</h4>
                <p className="stat-value">{analytics.invites_sent}</p>
              </div>
              <div className="stat-card">
                <h4>Invites Opened</h4>
                <p className="stat-value">{analytics.invites_opened}</p>
              </div>
              <div className="stat-card">
                <h4>Invites Redeemed</h4>
                <p className="stat-value">{analytics.invites_redeemed}</p>
              </div>
              <div className="stat-card">
                <h4>Open Rate</h4>
                <p className="stat-value">{analytics.open_rate_percent}%</p>
              </div>
              <div className="stat-card">
                <h4>Redemption Rate</h4>
                <p className="stat-value">
                  {analytics.redemption_rate_percent}%
                </p>
              </div>
            </div>
          ) : (
            <p className="loading-text">Loading analytics...</p>
          )}
        </div>
      )}
    </div>
    </ErrorBoundary>
  );
};

export default InviteDashboard;
