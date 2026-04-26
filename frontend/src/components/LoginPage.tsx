import { useState } from "react";

import { exchangeForXR7Token, getSupabaseClient } from "../lib/supabase";

type LoginState = "idle" | "submitting" | "error";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState<LoginState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const supabaseConfigured = Boolean(
    (import.meta.env.VITE_SUPABASE_URL as string | undefined) &&
      (import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined),
  );

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setState("submitting");
    setErrorMessage(null);

    try {
      const supabase = getSupabaseClient();
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        throw error;
      }
      const supabaseToken = data.session?.access_token;
      if (!supabaseToken) {
        throw new Error("Supabase returned no access token");
      }
      await exchangeForXR7Token(supabaseToken);
      // MVP: bounce to the dashboard (recovery console). Replace with a real
      // router once react-router lands.
      window.location.assign("/");
    } catch (err) {
      setState("error");
      setErrorMessage(err instanceof Error ? err.message : "Sign-in failed");
    }
  };

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
            Sign in to XR7
          </h1>
          {!supabaseConfigured ? (
            <p role="alert" style={{ color: "#fca5a5" }}>
              Supabase is not configured. Set <code>VITE_SUPABASE_URL</code> and{" "}
              <code>VITE_SUPABASE_ANON_KEY</code> in <code>frontend/.env</code> — credentials are in
              the team password manager.
            </p>
          ) : null}

          <form onSubmit={handleSubmit} noValidate>
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
              autoComplete="current-password"
              required
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

            <button
              type="submit"
              className="cta large"
              disabled={state === "submitting" || !supabaseConfigured}
              style={{ width: "100%" }}
            >
              {state === "submitting" ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p style={{ marginTop: "24px", fontSize: "0.9em", opacity: 0.7 }}>
            Auth is handled by Supabase. Your XR7 session token is stored locally and expires on
            sign-out.
          </p>
        </section>
      </main>
    </div>
  );
}
