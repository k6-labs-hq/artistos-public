import { jsx as _jsx } from "react/jsx-runtime";
import { useState } from "react";
import { DashboardView } from "@/components/DashboardView";
import { OnboardingFlow } from "@/components/OnboardingFlow";
export function App() {
    const [artistId, setArtistId] = useState("");
    return (_jsx("main", { className: "app-shell", children: !artistId ? (_jsx(OnboardingFlow, { onReady: (id) => setArtistId(id) })) : (_jsx(DashboardView, { artistId: artistId })) }));
}
