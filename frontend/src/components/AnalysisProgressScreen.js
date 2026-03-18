import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import styles from "./AnalysisProgressScreen.module.css";
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
const THEME_VARIANT_CLASS = {
    xr7: styles.themeXr7,
    slate: styles.themeSlate,
    neutral: styles.themeNeutral,
};
function clampCadence(value) {
    return Math.min(MAX_CADENCE_MS, Math.max(MIN_CADENCE_MS, value));
}
function usePrefersReducedMotion() {
    const [prefersReducedMotion, setPrefersReducedMotion] = useState(() => {
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
export function AnalysisProgressScreen({ messages = DEFAULT_MESSAGES, logoSrc = "/xr7-emblem.svg", animationSpeed = DEFAULT_CADENCE_MS, onComplete, title = "XR7 Forensic Analysis", caption = "Validating cross-platform royalty evidence with precision.", themeVariant = "xr7", themeOverrides, }) {
    const prefersReducedMotion = usePrefersReducedMotion();
    const trustedMessages = useMemo(() => (messages.length > 0 ? messages : DEFAULT_MESSAGES), [messages]);
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
        let swapTimer;
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
        ["--xr7-breath-duration"]: `${breathingDuration}ms`,
        ...(themeOverrides?.textColor ? { ["--xr7-text-color"]: themeOverrides.textColor } : {}),
        ...(themeOverrides?.backgroundPrimary
            ? { ["--xr7-bg-primary"]: themeOverrides.backgroundPrimary }
            : {}),
        ...(themeOverrides?.backgroundSecondary
            ? { ["--xr7-bg-secondary"]: themeOverrides.backgroundSecondary }
            : {}),
        ...(themeOverrides?.panelBackground
            ? { ["--xr7-panel-bg"]: themeOverrides.panelBackground }
            : {}),
        ...(themeOverrides?.borderColor ? { ["--xr7-border"]: themeOverrides.borderColor } : {}),
        ...(themeOverrides?.glowColorPrimary
            ? { ["--xr7-glow-primary"]: themeOverrides.glowColorPrimary }
            : {}),
        ...(themeOverrides?.glowColorSecondary
            ? { ["--xr7-glow-secondary"]: themeOverrides.glowColorSecondary }
            : {}),
    };
    return (_jsx("section", { className: `${styles.screen} ${variantClass}`, "aria-label": "XR7 analysis progress screen", style: containerStyle, children: _jsx("div", { className: styles.vignette, children: _jsxs("div", { className: styles.centerStack, children: [_jsx("div", { className: styles.logoWrap, children: _jsx("img", { className: styles.logo, src: logoSrc, alt: "XR7 logo", "aria-label": "XR7 analysis engine active" }) }), _jsx("p", { className: styles.heading, children: title }), _jsx("p", { className: `${styles.message} ${messageVisible ? styles.messageVisible : styles.messageHidden}`, "aria-live": "polite", "aria-atomic": "true", children: trustedMessages[currentIndex] }), _jsx("p", { className: styles.caption, children: caption })] }) }) }));
}
export default AnalysisProgressScreen;
