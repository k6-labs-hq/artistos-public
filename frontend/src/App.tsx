import { useState } from "react";

import { DashboardView } from "@/components/DashboardView";
import { OnboardingFlow } from "@/components/OnboardingFlow";

export function App() {
  const [artistId, setArtistId] = useState("");

  return (
    <main className="app-shell">
      {!artistId ? (
        <OnboardingFlow onReady={(id) => setArtistId(id)} />
      ) : (
        <DashboardView artistId={artistId} />
      )}
    </main>
  );
}
