/**
 * FeatureFlagAdmin — Admin UI for managing feature flags.
 *
 * Lists all feature flags, allows toggling enabled/disabled state and editing
 * rollout percentage inline.  Calls the admin API:
 *   GET  /admin/feature-flags
 *   PUT  /admin/feature-flags/:key
 *
 * Requires the X-Admin-Key header, which it reads from the
 * VITE_ADMIN_KEY environment variable (or prompt if absent).
 */
import React, { useCallback, useEffect, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FeatureFlag {
  key: string;
  description: string | null;
  enabled: boolean;
  rollout_percentage: number;
  target_user_ids: string[] | null;
  conditions: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_URL ?? "";
const ADMIN_KEY = import.meta.env.VITE_ADMIN_KEY ?? "";

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": ADMIN_KEY,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface FlagRowProps {
  flag: FeatureFlag;
  onUpdate: (key: string, patch: Partial<FeatureFlag>) => Promise<void>;
}

function FlagRow({ flag, onUpdate }: FlagRowProps) {
  const [rollout, setRollout] = useState<number>(flag.rollout_percentage ?? 100);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = useCallback(async () => {
    setSaving(true);
    setError(null);
    try {
      await onUpdate(flag.key, { enabled: !flag.enabled });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setSaving(false);
    }
  }, [flag.key, flag.enabled, onUpdate]);

  const handleRolloutSave = useCallback(async () => {
    setSaving(true);
    setError(null);
    try {
      await onUpdate(flag.key, { rollout_percentage: rollout });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setSaving(false);
    }
  }, [flag.key, rollout, onUpdate]);

  return (
    <tr
      role="row"
      aria-label={`Feature flag ${flag.key}, ${flag.enabled ? "enabled" : "disabled"}`}
      style={{ borderBottom: "1px solid #e5e7eb" }}
    >
      <td style={{ padding: "10px 12px", fontFamily: "monospace", fontWeight: 600 }}>
        {flag.key}
      </td>
      <td style={{ padding: "10px 12px", color: "#6b7280", maxWidth: 280 }}>
        {flag.description ?? <em>No description</em>}
      </td>
      <td style={{ padding: "10px 12px", textAlign: "center" }}>
        <button
          type="button"
          role="switch"
          aria-checked={flag.enabled}
          aria-label={`Toggle ${flag.key} ${flag.enabled ? "off" : "on"}`}
          disabled={saving}
          onClick={handleToggle}
          style={{
            padding: "4px 14px",
            borderRadius: 4,
            border: "none",
            cursor: saving ? "not-allowed" : "pointer",
            background: flag.enabled ? "#16a34a" : "#d1d5db",
            color: flag.enabled ? "#fff" : "#374151",
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          {flag.enabled ? "ON" : "OFF"}
        </button>
      </td>
      <td style={{ padding: "10px 12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            id={`rollout-${flag.key}`}
            type="range"
            min={0}
            max={100}
            step={1}
            value={rollout}
            aria-label={`Rollout percentage for ${flag.key}`}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={rollout}
            onChange={(e) => setRollout(Number(e.target.value))}
            style={{ width: 100 }}
          />
          <span aria-live="polite" aria-atomic="true" style={{ minWidth: 36, fontSize: 13 }}>
            {rollout}%
          </span>
          <button
            type="button"
            aria-label={`Save rollout for ${flag.key}`}
            disabled={saving || rollout === flag.rollout_percentage}
            onClick={handleRolloutSave}
            style={{
              padding: "2px 10px",
              fontSize: 12,
              borderRadius: 4,
              border: "1px solid #d1d5db",
              cursor: saving ? "not-allowed" : "pointer",
              background: "#f3f4f6",
            }}
          >
            Save
          </button>
        </div>
      </td>
      <td style={{ padding: "10px 12px", fontSize: 12, color: "#9ca3af" }}>
        {new Date(flag.updated_at).toLocaleString()}
      </td>
      <td style={{ padding: "10px 12px" }}>
        {error && (
          <span role="alert" style={{ color: "#dc2626", fontSize: 12 }}>
            {error}
          </span>
        )}
      </td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function FeatureFlagAdmin() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const loadFlags = useCallback(async () => {
    setLoading(true);
    setGlobalError(null);
    try {
      const data = await apiFetch<FeatureFlag[]>("/admin/feature-flags");
      setFlags(data);
    } catch (e: unknown) {
      setGlobalError(e instanceof Error ? e.message : "Failed to load flags");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadFlags();
  }, [loadFlags]);

  const handleUpdate = useCallback(
    async (key: string, patch: Partial<FeatureFlag>) => {
      const existing = flags.find((f) => f.key === key);
      if (!existing) return;
      const updated = await apiFetch<FeatureFlag>(`/admin/feature-flags/${key}`, {
        method: "PUT",
        body: JSON.stringify({
          description: existing.description,
          enabled: existing.enabled,
          rollout_percentage: existing.rollout_percentage,
          target_user_ids: existing.target_user_ids,
          conditions: existing.conditions,
          ...patch,
        }),
      });
      setFlags((prev) => prev.map((f) => (f.key === key ? updated : f)));
    },
    [flags]
  );

  const filtered = flags.filter(
    (f) =>
      f.key.toLowerCase().includes(search.toLowerCase()) ||
      (f.description ?? "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <main
      role="main"
      aria-label="Feature Flag Administration"
      style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 1100, margin: "0 auto" }}
    >
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16 }}>Feature Flag Admin</h1>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 16,
        }}
      >
        <label htmlFor="flag-search" style={{ fontWeight: 600, fontSize: 14 }}>
          Search
        </label>
        <input
          id="flag-search"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by key or description…"
          aria-label="Filter feature flags"
          style={{
            padding: "6px 12px",
            border: "1px solid #d1d5db",
            borderRadius: 4,
            fontSize: 14,
            width: 280,
          }}
        />
        <button
          type="button"
          onClick={loadFlags}
          aria-label="Refresh feature flags list"
          style={{
            padding: "6px 14px",
            borderRadius: 4,
            border: "1px solid #6366f1",
            background: "#6366f1",
            color: "#fff",
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          Refresh
        </button>
        <span aria-live="polite" style={{ fontSize: 13, color: "#6b7280" }}>
          {loading ? "Loading…" : `${filtered.length} flag${filtered.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {globalError && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            background: "#fef2f2",
            color: "#dc2626",
            border: "1px solid #fca5a5",
            borderRadius: 4,
            padding: "10px 14px",
            marginBottom: 16,
            fontSize: 14,
          }}
        >
          {globalError}
        </div>
      )}

      {!loading && flags.length === 0 && !globalError && (
        <p style={{ color: "#6b7280" }}>No feature flags configured.</p>
      )}

      {flags.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table
            role="grid"
            aria-label="Feature flags"
            style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}
          >
            <thead>
              <tr style={{ background: "#f9fafb", textAlign: "left" }}>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600 }}>
                  Key
                </th>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600 }}>
                  Description
                </th>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600, textAlign: "center" }}>
                  Status
                </th>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600 }}>
                  Rollout
                </th>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600 }}>
                  Updated
                </th>
                <th scope="col" style={{ padding: "10px 12px", fontWeight: 600 }}>
                  &nbsp;
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((flag) => (
                <FlagRow key={flag.key} flag={flag} onUpdate={handleUpdate} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
