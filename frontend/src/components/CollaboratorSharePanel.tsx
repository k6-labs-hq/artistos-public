/**
 * CollaboratorSharePanel
 *
 * Shown after an artist's analysis completes. The creator enters their
 * co-writers, producers, and publishers. Clicking "Generate Message" calls
 * the backend which:
 *   - Creates individual invite records for each collaborator
 *   - Logs each person in the CRM as a pipeline lead
 *   - Returns a ready-to-copy message the creator can forward
 *
 * This closes the viral loop: every collaborator the creator reaches out to
 * can run their own analysis and discover their own unpaid royalties.
 */
import { useState } from "react";

import { ErrorBoundary } from "./ErrorBoundary";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type CollaboratorRole = "co_writer" | "producer" | "publisher" | "manager" | "label" | "other";

interface CollaboratorRow {
  id: string; // client-side only for key prop
  name: string;
  email: string;
  role: CollaboratorRole;
}

interface CollaboratorShareResult {
  collaborator_name: string;
  role: string;
  invite_link: string;
  invite_token: string;
  lead_id: string;
  hubspot_logged: boolean;
}

interface CollaboratorShareResponse {
  share_message: string;
  collaborators: CollaboratorShareResult[];
  total_logged: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ROLE_OPTIONS: { value: CollaboratorRole; label: string }[] = [
  { value: "co_writer", label: "Co-Writer" },
  { value: "producer", label: "Producer" },
  { value: "publisher", label: "Publisher" },
  { value: "manager", label: "Manager" },
  { value: "label", label: "Label" },
  { value: "other", label: "Other" },
];

const ROLE_COLORS: Record<CollaboratorRole, string> = {
  co_writer: "#a78bfa",
  producer: "#34d399",
  publisher: "#60a5fa",
  manager: "#fbbf24",
  label: "#f87171",
  other: "#94a3b8",
};

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function emptyRow(): CollaboratorRow {
  return { id: uid(), name: "", email: "", role: "co_writer" };
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface CollaboratorSharePanelProps {
  artistId: string;
  apiBase?: string;
  /** Pre-populated list from analysis metadata (e.g. split-sheet data) */
  detectedCollaborators?: Array<{ name: string; role?: CollaboratorRole }>;
  onDismiss?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CollaboratorSharePanel({
  artistId,
  apiBase = "",
  detectedCollaborators,
  onDismiss,
}: CollaboratorSharePanelProps) {
  const initialRows =
    detectedCollaborators && detectedCollaborators.length > 0
      ? detectedCollaborators.map((c) => ({
          id: uid(),
          name: c.name,
          email: "",
          role: c.role ?? ("co_writer" as CollaboratorRole),
        }))
      : [emptyRow()];

  const [rows, setRows] = useState<CollaboratorRow[]>(initialRows);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CollaboratorShareResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --------------------------------------------------------------------------
  // Row management
  // --------------------------------------------------------------------------

  function updateRow(id: string, field: keyof CollaboratorRow, value: string) {
    setRows((prev) =>
      prev.map((r) => (r.id === id ? { ...r, [field]: value } : r))
    );
  }

  function addRow() {
    setRows((prev) => [...prev, emptyRow()]);
  }

  function removeRow(id: string) {
    setRows((prev) => prev.filter((r) => r.id !== id));
  }

  // --------------------------------------------------------------------------
  // Submit
  // --------------------------------------------------------------------------

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const validRows = rows.filter((r) => r.name.trim().length > 0);
    if (validRows.length === 0) {
      setError("Add at least one collaborator name.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(
        `${apiBase}/artists/${artistId}/collaborator-share`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            collaborators: validRows.map((r) => ({
              name: r.name.trim(),
              email: r.email.trim() || null,
              role: r.role,
            })),
          }),
        }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `HTTP ${res.status}`);
      }
      const data: CollaboratorShareResponse = await res.json();
      setResult(data);
    } catch (err: unknown) {
      setError((err as Error).message ?? "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function copyMessage() {
    if (!result?.share_message) return;
    await navigator.clipboard.writeText(result.share_message).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  function reset() {
    setResult(null);
    setCopied(false);
    setRows([emptyRow()]);
  }

  // --------------------------------------------------------------------------
  // Render — message view
  // --------------------------------------------------------------------------

  if (result) {
    return (
      <ErrorBoundary name="Collaborator Share Panel">
      <div style={styles.panel}>
        <div style={styles.header}>
          <div>
            <h3 style={styles.title}>Share With Your Team</h3>
            <p style={styles.subtitle}>
              {result.total_logged} collaborator
              {result.total_logged !== 1 ? "s" : ""} added to the pipeline
            </p>
          </div>
          {onDismiss && (
            <button style={styles.dismissBtn} onClick={onDismiss} aria-label="Dismiss">
              ✕
            </button>
          )}
        </div>

        {/* Copyable message */}
        <div style={styles.messageBox}>
          <div style={styles.messageHeader}>
            <span style={styles.messageLabel}>Your Share Message</span>
            <button
              style={{ ...styles.copyBtn, ...(copied ? styles.copyBtnCopied : {}) }}
              onClick={copyMessage}
            >
              {copied ? "✓ Copied!" : "Copy Message"}
            </button>
          </div>
          <pre style={styles.messageText}>{result.share_message}</pre>
        </div>

        {/* Collaborator results list */}
        <div style={styles.resultList}>
          {result.collaborators.map((c) => (
            <div key={c.lead_id} style={styles.resultRow}>
              <div style={styles.resultLeft}>
                <span
                  style={{
                    ...styles.rolePill,
                    background: `${ROLE_COLORS[c.role as CollaboratorRole] ?? "#94a3b8"}22`,
                    color: ROLE_COLORS[c.role as CollaboratorRole] ?? "#94a3b8",
                  }}
                >
                  {ROLE_OPTIONS.find((o) => o.value === c.role)?.label ?? c.role}
                </span>
                <span style={styles.resultName}>{c.collaborator_name}</span>
              </div>
              <div style={styles.resultRight}>
                {c.hubspot_logged && (
                  <span style={styles.crmBadge}>CRM ✓</span>
                )}
                <InviteLinkCopy link={c.invite_link} />
              </div>
            </div>
          ))}
        </div>

        <button style={styles.secondaryBtn} onClick={reset}>
          Add More Collaborators
        </button>
      </div>
      </ErrorBoundary>
    );
  }

  // --------------------------------------------------------------------------
  // Render — form view
  // --------------------------------------------------------------------------

  return (
    <ErrorBoundary name="Collaborator Share Panel">
    <div style={styles.panel}>
      <div style={styles.header}>
        <div>
          <h3 style={styles.title}>Invite Your Collaborators</h3>
          <p style={styles.subtitle}>
            Co-writers, producers, and publishers on your catalog likely have
            unclaimed royalties too. Send them a personalised invite.
          </p>
        </div>
        {onDismiss && (
          <button style={styles.dismissBtn} onClick={onDismiss} aria-label="Dismiss">
            ✕
          </button>
        )}
      </div>

      <form onSubmit={handleGenerate} noValidate>
        <div style={styles.rowList}>
          {rows.map((row, idx) => (
            <div key={row.id} style={styles.row}>
              <div style={styles.rowNumber}>{idx + 1}</div>

              <input
                type="text"
                placeholder="Name *"
                value={row.name}
                onChange={(e) => updateRow(row.id, "name", e.target.value)}
                style={styles.nameInput}
                required
                aria-label={`Collaborator ${idx + 1} name`}
              />

              <input
                type="email"
                placeholder="Email (optional)"
                value={row.email}
                onChange={(e) => updateRow(row.id, "email", e.target.value)}
                style={styles.emailInput}
                aria-label={`Collaborator ${idx + 1} email`}
              />

              <select
                value={row.role}
                onChange={(e) =>
                  updateRow(row.id, "role", e.target.value)
                }
                style={styles.roleSelect}
                aria-label={`Collaborator ${idx + 1} role`}
              >
                {ROLE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>

              {rows.length > 1 && (
                <button
                  type="button"
                  style={styles.removeBtn}
                  onClick={() => removeRow(row.id)}
                  aria-label="Remove row"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>

        <button type="button" style={styles.addRowBtn} onClick={addRow}>
          + Add Another
        </button>

        {error && <p style={styles.errorText}>⚠ {error}</p>}

        <div style={styles.formFooter}>
          <p style={styles.footerNote}>
            Each person will get their own invite link. Their names will be
            logged in our system so we can follow up.
          </p>
          <button
            type="submit"
            style={{ ...styles.generateBtn, ...(loading ? styles.generateBtnLoading : {}) }}
            disabled={loading}
          >
            {loading ? (
              <span style={styles.spinner} />
            ) : (
              "Generate Share Message"
            )}
          </button>
        </div>
      </form>
    </div>
    </ErrorBoundary>
  );
}

// ---------------------------------------------------------------------------
// Sub-component: per-collaborator invite link copy button
// ---------------------------------------------------------------------------

function InviteLinkCopy({ link }: { link: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    const full = `${window.location.origin}${link}`;
    await navigator.clipboard.writeText(full).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button style={styles.linkCopyBtn} onClick={copy}>
      {copied ? "✓" : "Link"}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Inline styles (no external CSS dependency)
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  panel: {
    background: "rgba(15,15,25,0.95)",
    border: "1px solid rgba(167,139,250,0.25)",
    borderRadius: 12,
    padding: "24px 28px",
    color: "#e2e8f0",
    fontFamily: "inherit",
    maxWidth: 760,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 20,
    gap: 12,
  },
  title: {
    margin: "0 0 4px",
    fontSize: 18,
    fontWeight: 700,
    color: "#f1f5f9",
  },
  subtitle: {
    margin: 0,
    fontSize: 13,
    color: "#94a3b8",
    lineHeight: 1.5,
    maxWidth: 520,
  },
  dismissBtn: {
    background: "none",
    border: "none",
    color: "#64748b",
    fontSize: 16,
    cursor: "pointer",
    padding: "2px 6px",
    flexShrink: 0,
  },
  rowList: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    marginBottom: 10,
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  rowNumber: {
    width: 22,
    fontSize: 12,
    color: "#475569",
    textAlign: "right",
    flexShrink: 0,
  },
  nameInput: {
    flex: "1 1 160px",
    minWidth: 100,
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 6,
    color: "#e2e8f0",
    padding: "7px 10px",
    fontSize: 13,
    outline: "none",
  },
  emailInput: {
    flex: "1 1 180px",
    minWidth: 100,
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 6,
    color: "#e2e8f0",
    padding: "7px 10px",
    fontSize: 13,
    outline: "none",
  },
  roleSelect: {
    flex: "0 0 120px",
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 6,
    color: "#e2e8f0",
    padding: "7px 8px",
    fontSize: 12,
    outline: "none",
    cursor: "pointer",
  },
  removeBtn: {
    background: "none",
    border: "none",
    color: "#64748b",
    cursor: "pointer",
    fontSize: 13,
    padding: "4px 6px",
    flexShrink: 0,
  },
  addRowBtn: {
    background: "none",
    border: "1px dashed rgba(167,139,250,0.35)",
    borderRadius: 6,
    color: "#a78bfa",
    padding: "6px 14px",
    fontSize: 12,
    cursor: "pointer",
    marginBottom: 16,
  },
  errorText: {
    color: "#f87171",
    fontSize: 13,
    margin: "8px 0",
  },
  formFooter: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 16,
    marginTop: 8,
    flexWrap: "wrap",
  },
  footerNote: {
    color: "#475569",
    fontSize: 12,
    margin: 0,
    flex: "1 1 200px",
  },
  generateBtn: {
    background: "linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)",
    border: "none",
    borderRadius: 8,
    color: "#fff",
    padding: "10px 22px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 8,
    minWidth: 180,
    justifyContent: "center",
  },
  generateBtnLoading: {
    opacity: 0.7,
    cursor: "not-allowed",
  },
  spinner: {
    width: 16,
    height: 16,
    border: "2px solid rgba(255,255,255,0.3)",
    borderTopColor: "#fff",
    borderRadius: "50%",
    animation: "spin 0.7s linear infinite",
    display: "inline-block",
  },
  // ---- Result view ----
  messageBox: {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(167,139,250,0.2)",
    borderRadius: 8,
    padding: "14px 16px",
    marginBottom: 20,
  },
  messageHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  messageLabel: {
    fontSize: 12,
    fontWeight: 600,
    color: "#a78bfa",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  copyBtn: {
    background: "rgba(167,139,250,0.15)",
    border: "1px solid rgba(167,139,250,0.4)",
    borderRadius: 6,
    color: "#a78bfa",
    padding: "5px 14px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
  },
  copyBtnCopied: {
    background: "rgba(52,211,153,0.15)",
    borderColor: "rgba(52,211,153,0.4)",
    color: "#34d399",
  },
  messageText: {
    margin: 0,
    fontSize: 13,
    lineHeight: 1.7,
    whiteSpace: "pre-wrap",
    color: "#cbd5e1",
    fontFamily: "inherit",
  },
  resultList: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
    marginBottom: 20,
  },
  resultRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "rgba(255,255,255,0.03)",
    borderRadius: 6,
    padding: "8px 12px",
    gap: 10,
  },
  resultLeft: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  resultRight: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  rolePill: {
    fontSize: 11,
    fontWeight: 600,
    borderRadius: 4,
    padding: "2px 8px",
    textTransform: "capitalize",
  },
  resultName: {
    fontSize: 13,
    color: "#e2e8f0",
  },
  crmBadge: {
    fontSize: 10,
    fontWeight: 700,
    color: "#34d399",
    background: "rgba(52,211,153,0.1)",
    borderRadius: 4,
    padding: "2px 6px",
  },
  linkCopyBtn: {
    background: "rgba(255,255,255,0.06)",
    border: "1px solid rgba(255,255,255,0.12)",
    borderRadius: 4,
    color: "#94a3b8",
    fontSize: 11,
    padding: "3px 10px",
    cursor: "pointer",
  },
  secondaryBtn: {
    background: "none",
    border: "1px solid rgba(167,139,250,0.35)",
    borderRadius: 6,
    color: "#a78bfa",
    padding: "8px 18px",
    fontSize: 13,
    cursor: "pointer",
  },
};
