import { useEffect, useState } from "react";

import AnalysisProgressScreen from "./AnalysisProgressScreen";

export function AnalysisProgressScreenExample() {
  const [analysisRunning, setAnalysisRunning] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setAnalysisRunning(false);
    }, 14000);

    return () => window.clearTimeout(timer);
  }, []);

  if (analysisRunning) {
    return (
      <AnalysisProgressScreen
        animationSpeed={2100}
        themeVariant="slate"
        title="NovaSound Revenue Intelligence"
        caption="Reconciling global royalty evidence with audit-grade controls."
        themeOverrides={{
          glowColorPrimary: "rgba(124, 198, 211, 0.42)",
          glowColorSecondary: "rgba(103, 168, 208, 0.36)",
          borderColor: "rgba(166, 198, 214, 0.3)",
        }}
        onComplete={() => {
          // Hook for analytics or heartbeat updates after one full message pass.
          console.info("Analysis progress messages completed one full cycle.");
        }}
      />
    );
  }

  return (
    <main style={{ padding: "2rem", fontFamily: "Manrope, sans-serif" }}>
      <h1>Analysis Complete</h1>
      <p>Your XR7 recovery dashboard is ready.</p>
    </main>
  );
}

export default AnalysisProgressScreenExample;