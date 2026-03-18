import { useEffect, useMemo, useState, type CSSProperties } from "react";

import styles from "./AnalysisProgressScreen.module.css";

export type AnalysisProgressThemeVariant = "xr7" | "slate" | "neutral";

export type AnalysisProgressThemeTokens = {
  textColor: string;
  backgroundPrimary: string;
  backgroundSecondary: string;
  panelBackground: string;
  borderColor: string;
  glowColorPrimary: string;
  glowColorSecondary: string;
};

export interface AnalysisProgressScreenProps {
  messages?: string[];
  logoSrc?: string;
  animationSpeed?: number;
  onComplete?: () => void;
  title?: string;
  caption?: string;
  themeVariant?: AnalysisProgressThemeVariant;
  themeOverrides?: Partial<AnalysisProgressThemeTokens>;
}

const DEFAULT_MESSAGES = [
  "Decrypting uploaded files...",
  "Fingerprinting royalty sources...",
  "Matching statements across platforms...",
  "Reconciling historical earnings...",
  "Identifying missing payments...",
  "Cross-checking metadata integrity...",
  "Analyzing distributor reports...",
  "Building your recovery dashboard...",
];

const MIN_CADENCE_MS = 1500;
const MAX_CADENCE_MS = 2500;
const DEFAULT_CADENCE_MS = 2000;
const FADE_MS = 320;

const THEME_VARIANT_CLASS: Record<AnalysisProgressThemeVariant, string | undefined> = {
  xr7: styles.themeXr7,
  slate: styles.themeSlate,
  neutral: styles.themeNeutral,
};

function clampCadence(value: number): number {
  return Math.min(MAX_CADENCE_MS, Math.max(MIN_CADENCE_MS, value));
}

function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches);
    handleChange();
    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return prefersReducedMotion;
}

export function AnalysisProgressScreen({
  messages = DEFAULT_MESSAGES,
  logoSrc = "/xr7-emblem.svg",
  animationSpeed = DEFAULT_CADENCE_MS,
  onComplete,
  title = "XR7 Forensic Analysis",
  caption = "Validating cross-platform royalty evidence with precision.",
  themeVariant = "xr7",
  themeOverrides,
}: AnalysisProgressScreenProps) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const trustedMessages = useMemo(
    () => (messages.length > 0 ? messages : DEFAULT_MESSAGES),
    [messages],
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const [messageVisible, setMessageVisible] = useState(true);

  useEffect(() => {
    setCurrentIndex(0);
    setMessageVisible(true);
  }, [trustedMessages]);

  useEffect(() => {
    if (trustedMessages.length <= 1) {
      return;
    }

    const baseCadence = clampCadence(animationSpeed);
    const jitter = Math.floor(Math.random() * 450) - 225;
    const cycleDelay = prefersReducedMotion
      ? Math.max(baseCadence, 3000)
      : clampCadence(baseCadence + jitter);

    let swapTimer: number | undefined;
    const hideTimer = window.setTimeout(() => {
      if (!prefersReducedMotion) {
        setMessageVisible(false);
      }

      const swapDelay = prefersReducedMotion ? 0 : FADE_MS;
      swapTimer = window.setTimeout(() => {
        setCurrentIndex((previous) => {
          const next = (previous + 1) % trustedMessages.length;
          if (next === 0) {
            onComplete?.();
          }
          return next;
        });
        setMessageVisible(true);
      }, swapDelay);
    }, cycleDelay);

    return () => {
      window.clearTimeout(hideTimer);
      if (swapTimer) {
        window.clearTimeout(swapTimer);
      }
    };
  }, [currentIndex, trustedMessages, animationSpeed, onComplete, prefersReducedMotion]);

  const breathingDuration = clampCadence(animationSpeed) + 500;
  const variantClass = THEME_VARIANT_CLASS[themeVariant] || "";
  const containerStyle = {
    ["--xr7-breath-duration" as string]: `${breathingDuration}ms`,
    ...(themeOverrides?.textColor ? { ["--xr7-text-color" as string]: themeOverrides.textColor } : {}),
    ...(themeOverrides?.backgroundPrimary
      ? { ["--xr7-bg-primary" as string]: themeOverrides.backgroundPrimary }
      : {}),
    ...(themeOverrides?.backgroundSecondary
      ? { ["--xr7-bg-secondary" as string]: themeOverrides.backgroundSecondary }
      : {}),
    ...(themeOverrides?.panelBackground
      ? { ["--xr7-panel-bg" as string]: themeOverrides.panelBackground }
      : {}),
    ...(themeOverrides?.borderColor ? { ["--xr7-border" as string]: themeOverrides.borderColor } : {}),
    ...(themeOverrides?.glowColorPrimary
      ? { ["--xr7-glow-primary" as string]: themeOverrides.glowColorPrimary }
      : {}),
    ...(themeOverrides?.glowColorSecondary
      ? { ["--xr7-glow-secondary" as string]: themeOverrides.glowColorSecondary }
      : {}),
  } as CSSProperties;

  return (
    <section className={`${styles.screen} ${variantClass}`} aria-label="XR7 analysis progress screen" style={containerStyle}>
      <div className={styles.vignette}>
        <div className={styles.centerStack}>
          <div className={styles.logoWrap}>
            <img
              className={styles.logo}
              src={logoSrc}
              alt="XR7 logo"
              aria-label="XR7 analysis engine active"
            />
          </div>

          <p className={styles.heading}>{title}</p>

          {/* Polite live region keeps updates readable for screen reader users. */}
          <p
            className={`${styles.message} ${messageVisible ? styles.messageVisible : styles.messageHidden}`}
            aria-live="polite"
            aria-atomic="true"
          >
            {trustedMessages[currentIndex]}
          </p>

          <p className={styles.caption}>{caption}</p>
        </div>
      </div>
    </section>
  );
}

export default AnalysisProgressScreen;