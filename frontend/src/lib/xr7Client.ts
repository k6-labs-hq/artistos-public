/**
 * Thin fetch wrapper for the XR7 API.
 *
 * Reads the XR7 access token from localStorage on every call (so a sign-in
 * elsewhere in the tab is picked up immediately) and applies a global 401
 * interceptor: an expired or rejected token clears the stored token and
 * bounces the user to /login. Without this, the nav still says "Sign out"
 * but every API call silently 401s.
 */
import { clearXR7Token, getXR7Token } from "./supabase";

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

export class UnauthorizedError extends Error {
  constructor() {
    super("XR7 token rejected (401). Redirecting to /login.");
    this.name = "UnauthorizedError";
  }
}

function authHeader(): Record<string, string> {
  const tok = getXR7Token();
  return tok ? { Authorization: `Bearer ${tok}` } : {};
}

async function handle<T>(resp: Response): Promise<T> {
  if (resp.status === 401) {
    clearXR7Token();
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      window.location.assign("/login");
    }
    throw new UnauthorizedError();
  }
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`HTTP ${resp.status}${text ? `: ${text}` : ""}`);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export async function xr7Get<T>(path: string): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, { headers: { ...authHeader() } });
  return handle<T>(resp);
}

export async function xr7PostJson<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { ...authHeader(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handle<T>(resp);
}

export async function xr7PostMultipart<T>(path: string, form: FormData): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { ...authHeader() },
    body: form,
  });
  return handle<T>(resp);
}

export type Me = {
  subject: string | null;
  role: string | null;
  artist_id: string | null;
  artist_name: string | null;
  artist_email: string | null;
  tenant_id: string | null;
  issued_at: number | null;
  expires_at: number | null;
};

export type Anomaly = {
  id: string;
  subtype: string | null;
  category: string | null;
  severity: string | null;
  estimated_recoverable: number | null;
  confidence_score: number | null;
  description: string | null;
  status: string | null;
  created_at: string | null;
};

export const xr7 = {
  me: () => xr7Get<Me>("/auth/me"),
  listAnomalies: (artistId: string) =>
    xr7Get<Anomaly[]>(`/artists/${encodeURIComponent(artistId)}/anomalies`),
  uploadStatement: (artistId: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return xr7PostMultipart<{ id: string; format_detected: string; events_created: number; payments_created: number; status: string }>(
      `/artists/${encodeURIComponent(artistId)}/statements/upload`,
      fd,
    );
  },
  getTermsStatus: (artistId: string) =>
    xr7Get<{ accepted: boolean; pending_version: string | null }>(
      `/artists/${encodeURIComponent(artistId)}/terms/status`,
    ),
  acceptTerms: (artistId: string, version: string) =>
    xr7PostJson(`/artists/${encodeURIComponent(artistId)}/terms/accept`, {
      terms_version: version,
      agreed: true,
    }),
};
