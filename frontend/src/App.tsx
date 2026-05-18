import { useEffect, useMemo, useState } from "react";

import { TVFilmDashboardVisualizations } from "./components/TVFilmDashboardVisualizations";
import { TVFilmEnterprisePanels } from "./components/TVFilmEnterprisePanels";
import { TVFilmWorkspace } from "./components/TVFilmWorkspace";
import { AnomalyDetailPage } from "./components/AnomalyDetailPage";
import { AdminWorkflowHandoffsPanel } from "./components/AdminWorkflowHandoffsPanel";
import { DashboardPage } from "./components/DashboardPage";
import { LoginPage } from "./components/LoginPage";
import { NotFoundPage } from "./components/NotFoundPage";
import { OpsDashboard } from "./components/OpsDashboard";
import { clearXR7Token, getXR7Token } from "./lib/supabase";

type ThemeMode = "dark" | "light";

const navLinks = [
  { label: "Trust", href: "#trust" },
  { label: "Capabilities", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "TV/Film", href: "#tv-film-workspace" },
  { label: "Console", href: "#recovery-console" },
];

const trustStats = [
  {
    value: "$10M+",
    title: "Missing Royalties Identified",
    body: "Platforms like Notes.fm identified over $10M in missing royalties during beta testing across 400+ artists.",
    source: "Public beta reporting",
  },
  {
    value: "$100M+",
    title: "Hidden Royalties Surfaced",
    body: "AI-driven tools have surfaced more than $100M in global hidden royalties for songwriters and artists.",
    source: "Industry recovery analyses",
  },
  {
    value: "$15K+",
    title: "Average Audit Recovery",
    body: "Average uncovered royalties per artist in real audits have exceeded $15,000 from unmatched works and streams.",
    source: "Audit benchmark references",
  },
  {
    value: "Billions",
    title: "Still Unclaimed",
    body: "Billions in unclaimed royalties remain industry-wide. XR7 helps surface and recover what is rightfully yours.",
    source: "MLC and collection society disclosures",
  },
];

const featureCards = [
  {
    title: "Connect Platforms in Minutes",
    body: "Securely link Spotify, Apple Music, TikTok, YouTube, MLC, SoundExchange, and PRO datasets without engineering overhead.",
    chips: ["Spotify", "Apple", "TikTok", "YouTube"],
  },
  {
    title: "AI-Powered Gap Detection",
    body: "Forensic models classify leakage from unmatched works, bad rates, and missing statements into ranked recovery opportunities.",
    chips: ["Detected", "Reported", "Paid", "Recovered"],
  },
  {
    title: "Real-Time Recovery Radar",
    body: "Watch risk and payout signals update across territories, counterparties, and claim phases with explainable confidence scores.",
    chips: ["Heatmaps", "SLA Risk", "Forecast"],
  },
  {
    title: "Collaborative Case Management",
    body: "Coordinate artists, managers, legal, and publishing teams inside one timeline with notes, evidence packets, and status trails.",
    chips: ["Shared Notes", "Playbooks", "Audit Trail"],
  },
];

const timelineSteps = [
  {
    title: "Connect Data",
    body: "Link DSPs, distributors, PRO statements, and catalog metadata.",
  },
  {
    title: "Analyze and Detect",
    body: "XR7 applies forensic checks and anomaly intelligence across every revenue stream.",
  },
  {
    title: "Surface Cases",
    body: "Prioritized case queue includes confidence, urgency, and estimated recovery value.",
  },
  {
    title: "Recover and Track",
    body: "Drive collections to resolution with full status visibility from claim to payout.",
  },
];

function getSystemTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "dark";
  }
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function XR7WingLogo({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 840 320" role="img" aria-label="XR7 metallic winged emblem" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="wingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6520BD" />
          <stop offset="55%" stopColor="#A855F7" />
          <stop offset="100%" stopColor="#D6B1FF" />
        </linearGradient>
        <linearGradient id="chromeLine" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#B1B7D1" stopOpacity="0.2" />
        </linearGradient>
        <filter id="softGlow" x="-40%" y="-60%" width="180%" height="220%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g filter="url(#softGlow)">
        <path d="M30 150C92 118 152 103 232 92L188 141L247 147L175 205L235 212C148 236 89 224 30 195Z" fill="url(#wingGradient)" />
        <path d="M810 150C748 118 688 103 608 92L652 141L593 147L665 205L605 212C692 236 751 224 810 195Z" fill="url(#wingGradient)" />
      </g>

      <rect x="214" y="64" width="412" height="192" rx="52" fill="url(#wingGradient)" stroke="url(#chromeLine)" strokeWidth="3" />
      <path d="M246 222L286 98H324L282 174H323L283 222Z" fill="#F8FAFC" />
      <path d="M350 98H395L425 142L456 98H500L447 160L503 222H457L425 175L394 222H348L404 160Z" fill="#F8FAFC" />
      <path d="M533 98H600L562 173H612L560 222H514L553 156H505Z" fill="#F8FAFC" />
      <path d="M220 84H620" stroke="url(#chromeLine)" strokeOpacity="0.7" strokeWidth="4" strokeLinecap="round" />
    </svg>
  );
}

export function App() {
  const [theme, setTheme] = useState<ThemeMode>("dark");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [demoOpen, setDemoOpen] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState<string>("trust");
  const [isAuthed, setIsAuthed] = useState<boolean>(() => Boolean(getXR7Token()));

  const handleSignOut = () => {
    clearXR7Token();
    setIsAuthed(false);
    // Stay on the marketing page; reload so any in-memory auth-aware components reset.
    window.location.assign("/");
  };

  useEffect(() => {
    const saved = window.localStorage.getItem("xr7-theme");
    const initial = saved === "dark" || saved === "light" ? saved : getSystemTheme();
    setTheme(initial);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem("xr7-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!demoOpen) {
      document.body.style.overflow = "";
      return;
    }

    document.body.style.overflow = "hidden";
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDemoOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [demoOpen]);

  useEffect(() => {
    const revealTargets = Array.from(document.querySelectorAll<HTMLElement>("[data-reveal='true']"));
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18 },
    );
    revealTargets.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const sectionIds = navLinks.map((link) => link.href.replace("#", ""));
    const sections = sectionIds
      .map((id) => document.getElementById(id))
      .filter((section): section is HTMLElement => section !== null);

    if (!sections.length) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

        if (!visible.length) {
          return;
        }

        const firstVisible = visible[0];
        if (!firstVisible) {
          return;
        }
        const nextId = firstVisible.target.id;
        setActiveSectionId((current) => (current === nextId ? current : nextId));
      },
      {
        root: null,
        rootMargin: "-35% 0px -45% 0px",
        threshold: [0.2, 0.45, 0.7],
      },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  const heroSubtitle = useMemo(
    () =>
      "Detect leakage across music, TV, and film revenue systems. Surface actionable recovery opportunities with AI-powered analysis, trust-layer explainability, and enterprise portfolio automation.",
    [],
  );

  const anomalyMatch = useMemo(() => window.location.pathname.match(/^\/anomalies\/([^/]+)$/), []);
  const adminHandoffsRoute = useMemo(() => window.location.pathname === "/admin/workflow/handoffs/ui", []);
  const normalizedPath = useMemo(() => window.location.pathname.replace(/\/+$/, "") || "/", []);
  const homeRoute = normalizedPath === "/";
  const loginRoute = normalizedPath === "/login";
  const dashboardRoute = normalizedPath === "/dashboard";
  const opsRoute = normalizedPath === "/ops";

  const anomalyId = anomalyMatch?.[1];
  if (anomalyId) {
    return <AnomalyDetailPage anomalyId={decodeURIComponent(anomalyId)} />;
  }

  if (adminHandoffsRoute) {
    return <AdminWorkflowHandoffsPanel />;
  }

  if (loginRoute) {
    return <LoginPage />;
  }

  if (dashboardRoute) {
    return <DashboardPage />;
  }

  if (opsRoute) {
    return <OpsDashboard />;
  }

  if (!homeRoute) {
    return <NotFoundPage />;
  }

  return (
    <div className="xr7-app">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <header className="site-nav" role="banner">
        <div className="nav-inner">
          <a className="brand" href="#top" aria-label="XR7 homepage">
            <img src="/xr7-logo-mark.png" alt="XR7 logo" />
            <span>XR7</span>
          </a>

          <nav className="desktop-nav" aria-label="Primary">
            {navLinks.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className={activeSectionId === item.href.replace("#", "") ? "active" : ""}
                aria-current={activeSectionId === item.href.replace("#", "") ? "page" : undefined}
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="nav-actions">
            <button
              type="button"
              className="theme-toggle"
              aria-label={`Current theme: ${theme === "dark" ? "Dark Mode" : "Light Mode"}. Toggle theme.`}
              onClick={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
            >
              <span aria-hidden="true">{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
            </button>
            {isAuthed ? (
              <>
                <a className="cta small" href="/dashboard" style={{ marginRight: "8px" }}>
                  Dashboard
                </a>
                <button type="button" className="cta small" onClick={handleSignOut}>
                  Sign out
                </button>
              </>
            ) : (
              <a className="cta small" href="/login">Sign in</a>
            )}
            {/* eslint-disable-next-line jsx-a11y/aria-props */}
            <button
              type="button"
              className="menu-toggle"
              aria-expanded={mobileMenuOpen ? "true" : "false"}
              aria-controls="mobile-menu"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
            >
              Menu
            </button>
          </div>
        </div>

        <div id="mobile-menu" className={`mobile-menu${mobileMenuOpen ? " open" : ""}`}>
          {navLinks.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className={activeSectionId === item.href.replace("#", "") ? "active" : ""}
              aria-current={activeSectionId === item.href.replace("#", "") ? "page" : undefined}
              onClick={() => setMobileMenuOpen(false)}
            >
              {item.label}
            </a>
          ))}
          {isAuthed ? (
            <>
              <a
                className="cta"
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </a>
              <button
                type="button"
                className="cta"
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleSignOut();
                }}
              >
                Sign out
              </button>
            </>
          ) : (
            <a
              className="cta"
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
            >
              Sign in
            </a>
          )}
        </div>
      </header>

      <main id="main-content">
        <section className="hero" data-reveal="true">
          <div className="hero-bg" aria-hidden="true" />
          <XR7WingLogo className="hero-logo" />
          <p className="eyebrow">Forensic Royalty Recovery - Powered by K6 Labs</p>
          <h1>Uncover Every Dollar You Are Owed</h1>
          <p className="hero-copy">{heroSubtitle}</p>
          <div className="hero-actions">
            {isAuthed ? (
              <a className="cta large pulse" href="/dashboard">
                Go to dashboard
              </a>
            ) : (
              <a className="cta large pulse" href="/login">
                Get Started Free
              </a>
            )}
            <button type="button" className="ghost large" onClick={() => setDemoOpen(true)}>
              Watch Demo
            </button>
          </div>
        </section>

        <section id="trust" className="trust" data-reveal="true">
          <div className="section-head">
            <h2>Trusted by Reality, Not Hype</h2>
            <p>Grounded in publicly discussed royalty recovery outcomes and unmatched-funds reporting across the industry.</p>
          </div>
          <div className="trust-grid">
            {trustStats.map((item) => (
              <article className="stat-card" key={item.title}>
                <p className="stat-value">{item.value}</p>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
                <small>Source: {item.source}</small>
              </article>
            ))}
          </div>
        </section>

        <section id="features" className="features" data-reveal="true">
          <div className="section-head">
            <h2>Core XR7 Capabilities</h2>
            <p>Built for artists, managers, songwriters, agencies, production teams, and rights operators that need forensic-grade revenue visibility.</p>
          </div>
          <div className="feature-grid">
            {featureCards.map((card) => (
              <article className="feature-card" key={card.title}>
                <h3>{card.title}</h3>
                <p>{card.body}</p>
                <div className="chip-row" aria-label="Feature highlights">
                  {card.chips.map((chip) => (
                    <span key={chip}>{chip}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="how-it-works" data-reveal="true">
          <div className="section-head">
            <h2>How It Works</h2>
          </div>
          <ol className="timeline">
            {timelineSteps.map((step, index) => (
              <li key={step.title}>
                <span className="node">{index + 1}</span>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <TVFilmWorkspace />

        <TVFilmEnterprisePanels />

        <TVFilmDashboardVisualizations />

        <section id="recovery-console" className="dashboard-preview" data-reveal="true">
          <div className="section-head">
            <h2>Inside the XR7 Recovery Console</h2>
            <p>A premium, data-dense workspace designed for real legal and royalty operations.</p>
          </div>

          <div className="app-mock" aria-label="XR7 dashboard preview with metrics, chart, and case table">
            <aside className="mock-sidebar">
              <img src="/xr7-logo-mark.png" alt="" aria-hidden="true" />
              <a href="#">Overview</a>
              <a href="#">Recovery Cases</a>
              <a href="#">Platform Coverage</a>
              <a href="#">Legal Packets</a>
              <a href="#">Team Activity</a>
            </aside>

            <div className="mock-main">
              <div className="mock-topbar">
                <input type="text" readOnly value="Search claims, ISRC, payers" aria-label="Search" />
                <div className="mock-actions">
                  <span className="badge">4 alerts</span>
                  <button
                    type="button"
                    className="theme-toggle compact"
                    aria-label={`Current theme: ${theme === "dark" ? "Dark Mode" : "Light Mode"}. Preview toggle.`}
                  >
                    {theme === "dark" ? "Dark Mode" : "Light Mode"}
                  </button>
                </div>
              </div>

              <div className="metric-grid">
                <article>
                  <p>Recovery Potential</p>
                  <strong>$2.84M</strong>
                </article>
                <article>
                  <p>Open Cases</p>
                  <strong>128</strong>
                </article>
                <article>
                  <p>Coverage Health</p>
                  <strong>92.4%</strong>
                </article>
                <article>
                  <p>Recovered 30d</p>
                  <strong className="gold">$318K</strong>
                </article>
              </div>

              <div className="chart-panel">
                <div className="chart-bars" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
                <div className="chart-caption">
                  Leakage Heatmap: Risk concentration is highest in US recording + neighboring rights lanes this week.
                </div>
              </div>

              <table>
                <caption>Recent Recovery Cases</caption>
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>Platform</th>
                    <th>Status</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>XR7-4412</td>
                    <td>Spotify</td>
                    <td><span className="chip teal">In Review</span></td>
                    <td>$81,400</td>
                  </tr>
                  <tr>
                    <td>XR7-4386</td>
                    <td>MLC</td>
                    <td><span className="chip">Detected</span></td>
                    <td>$45,220</td>
                  </tr>
                  <tr>
                    <td>XR7-4360</td>
                    <td>YouTube</td>
                    <td><span className="chip success">Recovered</span></td>
                    <td>$129,900</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <p>XR7 Forensic Royalty Recovery</p>
        <div>
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="#">Security</a>
          <a href="#">Contact</a>
        </div>
      </footer>

      {demoOpen ? (
        <div
          className="modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="demo-title"
          onClick={() => setDemoOpen(false)}
        >
          <div className="modal-card" onClick={(event) => event.stopPropagation()}>
            <h2 id="demo-title">XR7 Product Demo</h2>
            <p>
              Demo modal placeholder. Embed your hosted product walkthrough here (Wistia, Vimeo, or in-app interactive demo).
            </p>
            <button type="button" className="cta" onClick={() => setDemoOpen(false)}>
              Close Demo
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
