import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * PersonaCard — VIP artist persona profile card.
 *
 * Displays enriched public-source data (roles, notable works, bio,
 * social handles, detected vertical) in a premium metallic card UI.
 *
 * Shows a skeleton while enrichment is in progress.
 */
import { useEffect, useState } from "react";
const VERTICAL_LABELS = {
    music: "Music",
    tv_film: "TV / Film",
    both: "Music + TV / Film",
};
function Chip({ label, color = "purple" }) {
    return (_jsx("span", { className: "inline-flex items-center text-xs bg-purple-900/60 text-purple-200 border border-purple-600/40 rounded-full px-2 py-0.5", children: label }));
}
function SkeletonLine({ width = "full" }) {
    return (_jsx("div", { className: `h-3 rounded bg-purple-900/50 animate-pulse w-${width}` }));
}
export function PersonaCard({ artistId, apiBase = "", initialData = null, onEnrich, }) {
    const [persona, setPersona] = useState(initialData);
    const [loading, setLoading] = useState(!initialData);
    const [enriching, setEnriching] = useState(false);
    const [error, setError] = useState("");
    useEffect(() => {
        if (initialData)
            return;
        let mounted = true;
        const load = async () => {
            setLoading(true);
            try {
                const res = await fetch(`${apiBase}/artists/${artistId}/persona`);
                if (!mounted)
                    return;
                if (res.ok) {
                    const data = await res.json();
                    setPersona(data);
                }
                else if (res.status !== 404) {
                    setError("Could not load persona.");
                }
            }
            catch {
                if (mounted)
                    setError("Network error.");
            }
            finally {
                if (mounted)
                    setLoading(false);
            }
        };
        load();
        return () => { mounted = false; };
    }, [artistId, apiBase, initialData]);
    const handleEnrich = async () => {
        setEnriching(true);
        try {
            const res = await fetch(`${apiBase}/artists/${artistId}/persona/enrich`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ force: false }),
            });
            if (res.ok) {
                onEnrich?.();
                // Poll for completion
                setTimeout(async () => {
                    const r2 = await fetch(`${apiBase}/artists/${artistId}/persona`);
                    if (r2.ok) {
                        setPersona(await r2.json());
                    }
                    setEnriching(false);
                }, 4000);
            }
        }
        catch {
            setEnriching(false);
        }
    };
    if (loading) {
        return (_jsxs("div", { className: "vip-card space-y-3 p-5", children: [_jsx(SkeletonLine, { width: "1/2" }), _jsx(SkeletonLine, { width: "3/4" }), _jsx(SkeletonLine, { width: "2/3" }), _jsx(SkeletonLine, { width: "full" })] }));
    }
    if (error) {
        return (_jsx("div", { className: "vip-card p-5 text-red-400 text-sm", children: error }));
    }
    const isPending = !persona ||
        persona.enrichment_status === "pending" ||
        persona.enrichment_status === "in_progress";
    return (_jsxs("div", { className: "vip-card p-5 space-y-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-purple-100 font-semibold text-base tracking-wide", children: "Your Public Persona" }), _jsx("p", { className: "text-purple-400 text-xs mt-0.5", children: "Enriched from public sources \u00B7 IMDb \u00B7 Discogs \u00B7 MusicBrainz" })] }), !enriching && (_jsx("button", { onClick: handleEnrich, className: "vip-btn-sm", title: "Re-run persona enrichment", children: "Refresh" })), enriching && (_jsx("span", { className: "text-purple-400 text-xs animate-pulse", children: "Enriching\u2026" }))] }), persona?.primary_vertical && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("span", { className: "text-purple-300 text-xs", children: "Vertical:" }), _jsx(Chip, { label: VERTICAL_LABELS[persona.primary_vertical] ?? persona.primary_vertical })] })), (persona?.detected_roles ?? []).length > 0 && (_jsxs("div", { children: [_jsx("p", { className: "text-purple-400 text-xs mb-1.5", children: "Detected Roles" }), _jsx("div", { className: "flex flex-wrap gap-1.5", children: (persona.detected_roles ?? []).map((role) => (_jsx(Chip, { label: role }, role))) })] })), (persona?.genre_tags ?? []).length > 0 && (_jsxs("div", { children: [_jsx("p", { className: "text-purple-400 text-xs mb-1.5", children: "Genres" }), _jsx("div", { className: "flex flex-wrap gap-1.5", children: (persona.genre_tags ?? []).slice(0, 8).map((g) => (_jsx(Chip, { label: g }, g))) })] })), persona?.bio_snippet && (_jsxs("div", { children: [_jsx("p", { className: "text-purple-400 text-xs mb-1", children: "Bio" }), _jsx("p", { className: "text-purple-200 text-sm leading-relaxed line-clamp-3", children: persona.bio_snippet })] })), (persona?.notable_works ?? []).length > 0 && (_jsxs("div", { children: [_jsx("p", { className: "text-purple-400 text-xs mb-1.5", children: "Notable Works" }), _jsx("ul", { className: "space-y-0.5", children: (persona.notable_works ?? []).slice(0, 5).map((w) => (_jsxs("li", { className: "text-purple-200 text-sm flex items-center gap-1.5", children: [_jsx("span", { className: "text-purple-500", children: "\u203A" }), " ", w] }, w))) })] })), _jsxs("div", { className: "flex flex-wrap gap-3 pt-1 border-t border-purple-800/50", children: [persona?.musicbrainz_id && (_jsx(ExternalIdBadge, { label: "MusicBrainz", id: persona.musicbrainz_id })), persona?.spotify_artist_id && (_jsx(ExternalIdBadge, { label: "Spotify", id: persona.spotify_artist_id })), persona?.imdb_id && (_jsx(ExternalIdBadge, { label: "IMDb", id: persona.imdb_id }))] }), isPending && (_jsx("div", { className: "rounded-lg bg-purple-950/60 border border-purple-700/30 p-3 text-purple-300 text-xs", children: persona?.enrichment_status === "in_progress"
                    ? "⟳ Enriching your persona from public sources…"
                    : "Your persona profile will be enriched automatically — or click Refresh now." })), _jsx("style", { children: `
        .vip-card {
          background: linear-gradient(135deg, rgba(30,10,60,0.95) 0%, rgba(50,15,90,0.90) 100%);
          border: 1px solid rgba(168,85,247,0.25);
          border-radius: 12px;
          box-shadow: 0 4px 24px rgba(168,85,247,0.12), inset 0 1px 0 rgba(168,85,247,0.10);
        }
        .vip-btn-sm {
          font-size: 0.7rem;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          background: rgba(168,85,247,0.15);
          border: 1px solid rgba(168,85,247,0.40);
          color: #d8b4fe;
          cursor: pointer;
          transition: background 0.2s;
        }
        .vip-btn-sm:hover { background: rgba(168,85,247,0.30); }
      ` })] }));
}
function ExternalIdBadge({ label, id }) {
    return (_jsxs("div", { className: "flex items-center gap-1 text-xs text-purple-400", children: [_jsx("span", { className: "font-medium text-purple-300", children: label }), _jsx("span", { className: "font-mono text-purple-500 truncate max-w-[80px]", title: id, children: id.length > 10 ? id.slice(0, 8) + "…" : id })] }));
}
