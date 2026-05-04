import { useState } from "react";

import { exchangeForXR7Token, getSupabaseClient } from "../lib/supabase";

const apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

/**
 * Decide the post-login destination based on the JWT we just received.
 * Admin role → operator console (/ops). Everyone else → artist dashboard.
 *
 * We fetch /auth/me rather than decoding the JWT client-side because (a)
 * the role is the source of truth on the server, (b) we want to surface
 * any auth-state issues here before the user lands on a screen they can't
 * use, and (c) it's one fetch — cheap.
 */
async function postLoginDestination(xr7Token: string): Promise<string> {
  try {
    const res = await fetch(`${apiBase}/auth/me`, {
      headers: { Authorization: `Bearer ${xr7Token}` },
    });
    if (res.ok) {
      const body = (await res.json()) as { role?: string | null };
      if (body.role === "admin") return "/ops";
    }
  } catch {
    // Fall through to default.
  }
  return "/dashboard";
}

type FormState = "idle" | "submitting" | "error" | "needs_confirmation";
type Mode = "signin" | "signup";

export function LoginPage() {
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [artistName, setArtistName] = useState("");
  const [state, setState] = useState<FormState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const supabaseConfigured = Boolean(
    (import.meta.env.VITE_SUPABASE_URL as string | undefined) &&
      (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined),
  );

  const handleSignIn = async () => {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    const supabaseToken = data.session?.access_token;
    if (!supabaseToken) {
      throw new Error("Supabase returned no access token");
    }
    const xr7Token = await exchangeForXR7Token(supabaseToken);
    window.location.assign(await postLoginDestination(xr7Token));
  };

  const handleSignUp = async () => {
    const supabase = getSupabaseClient();
    const trimmedName = artistName.trim();
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: trimmedName ? { artist_name: trimmedName } : undefined,
      },
    });
    if (error) throw error;

    // Two outcomes from Supabase:
    //   - Project has email confirmation OFF → session is returned, sign-in is immediate.
    //   - Project has email confirmation ON  → user is created but session is null;
    //     we can't currently deliver the confirmation email (no SMTP wired, see
    //     issue #180). Surface a clear message instead of a dead "Sign in" loop.
    if (data.session) {
      const xr7Token = await exchangeForXR7Token(data.session.access_token);
      window.location.assign(await postLoginDestination(xr7Token));
      return;
    }
    setState("needs_confirmation");
    setInfo(
      "Account created. Email confirmation is required by the project, but no email " +
        "provider is wired yet — ask an operator to confirm your account, then sign in.",
    );
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setState("submitting");
    setErrorMessage(null);
    setInfo(null);
    try {
      if (mode === "signup") {
        await handleSignUp();
      } else {
        await handleSignIn();
      }
    } catch (err) {
      setState("error");
      setErrorMessage(err instanceof Error ? err.message : `${mode} failed`);
    }
  };

  const switchMode = (next: Mode) => {
    setMode(next);
    setErrorMessage(null);
    setInfo(null);
    setState("idle");
  };

  const heading = mode === "signup" ? "Create your XR7 account" : "Sign in to XR7";
  const submitLabel =
    state === "submitting"
      ? mode === "signup"
        ? "Creating account…"
        : "Signing in…"
      : mode === "signup"
        ? "Create account"
        : "Sign in";

  return (
    <div className="xr7-app">
      <main id="main-content" style={{ display: "flex", justifyContent: "center", padding: "64px 24px" }}>
        <section
          aria-labelledby="login-heading"
          style={{
            width: "100%",
            maxWidth: "420px",
            padding: "32px",
            borderRadius: "16px",
            background: "rgba(16, 16, 28, 0.6)",
            border: "1px solid rgba(168, 85, 247, 0.3)",
          }}
        >
          <h1 id="login-heading" style={{ marginTop: 0 }}>
            {heading}
          </h1>
          {!supabaseConfigured ? (
            <p role="alert" style={{ color: "#fca5a5" }}>
              Supabase is not configured. Set <code>VITE_SUPABASE_URL</code> and{" "}
              <code>VITE_SUPABASE_ANON_KEY</code> in <code>frontend/.env</code> — credentials are in
              the team password manager.
            </p>
          ) : null}

          <form onSubmit={handleSubmit} noValidate>
            {mode === "signup" ? (
              <>
                <label htmlFor="signup-name" style={{ display: "block", marginBottom: "6px" }}>
                  Artist or songwriter name
                </label>
                <input
                  id="signup-name"
                  type="text"
                  autoComplete="name"
                  value={artistName}
                  onChange={(e) => setArtistName(e.target.value)}
                  disabled={state === "submitting" || !supabaseConfigured}
                  placeholder="How you want to be addressed"
                  style={{ width: "100%", marginBottom: "16px", padding: "10px" }}
                />
              </>
            ) : null}

            <label htmlFor="login-email" style={{ display: "block", marginBottom: "6px" }}>
              Email
            </label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={state === "submitting" || !supabaseConfigured}
              style={{ width: "100%", marginBottom: "16px", padding: "10px" }}
            />

            <label htmlFor="login-password" style={{ display: "block", marginBottom: "6px" }}>
              Password
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={state === "submitting" || !supabaseConfigured}
              style={{ width: "100%", marginBottom: "16px", padding: "10px" }}
            />

            {errorMessage ? (
              <p role="alert" style={{ color: "#fca5a5", marginTop: 0 }}>
                {errorMessage}
              </p>
            ) : null}
            {info ? (
              <p role="status" style={{ color: "#86efac", marginTop: 0 }}>
                {info}
              </p>
            ) : null}

            <button
              type="submit"
              className="cta large"
              disabled={state === "submitting" || !supabaseConfigured}
              style={{ width: "100%" }}
            >
              {submitLabel}
            </button>
          </form>

          <p style={{ marginTop: "24px", fontSize: "0.9em", opacity: 0.85 }}>
            {mode === "signup" ? (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("signin")}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#a855f7",
                    cursor: "pointer",
                    padding: 0,
                    textDecoration: "underline",
                  }}
                >
                  Sign in
                </button>
              </>
            ) : (
              <>
                New to XR7?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("signup")}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#a855f7",
                    cursor: "pointer",
                    padding: 0,
                    textDecoration: "underline",
                  }}
                >
                  Create an account
                </button>
              </>
            )}
          </p>

          <p style={{ marginTop: "16px", fontSize: "0.85em", opacity: 0.6 }}>
            Auth is handled by Supabase. Your XR7 session token is stored locally and expires on
            sign-out.
          </p>
        </section>
      </main>
    </div>
  );
}
