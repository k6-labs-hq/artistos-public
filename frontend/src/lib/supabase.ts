/**
 * Supabase client for ArtistOS frontend.
 *
 * Usage:
 *   import { supabase } from "@/lib/supabase";
 *   await supabase.auth.signInWithPassword({ email, password });
 *
 * Stubbed for MVP: real Supabase project values come from VITE_SUPABASE_URL
 * and VITE_SUPABASE_ANON_KEY env vars (see frontend/.env.example).
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

let _client: SupabaseClient | null = null;

export function getSupabaseClient(): SupabaseClient {
  if (!_client) {
    if (!url || !anonKey) {
      throw new Error(
        "Supabase not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in frontend/.env.",
      );
    }
    _client = createClient(url, anonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
  }
  return _client;
}

/**
 * Exchange a Supabase access token for an XR7 JWT.
 * Stores the XR7 token in localStorage; every API call should pick it up.
 */
export async function exchangeForXR7Token(supabaseAccessToken: string): Promise<string> {
  const apiBase = (import.meta.env.VITE_API_BASE_URL as string) ?? "";
  const resp = await fetch(`${apiBase}/auth/supabase/exchange`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${supabaseAccessToken}`,
    },
  });
  if (!resp.ok) {
    throw new Error(`XR7 token exchange failed: ${resp.status}`);
  }
  const data = (await resp.json()) as { access_token: string };
  localStorage.setItem("xr7_access_token", data.access_token);
  return data.access_token;
}

export function getXR7Token(): string | null {
  return localStorage.getItem("xr7_access_token");
}

export function clearXR7Token(): void {
  localStorage.removeItem("xr7_access_token");
}
