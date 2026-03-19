/**
 * PersonaCard — VIP artist persona profile card.
 *
 * Displays enriched public-source data (roles, notable works, bio,
 * social handles, detected vertical) in a premium metallic card UI.
 *
 * Shows a skeleton while enrichment is in progress.
 */
import { useEffect, useState } from "react";

export interface PersonaData {
  artist_id: string;
  enrichment_status: "pending" | "in_progress" | "complete" | "failed";
  enriched_at?: string | null;
  imdb_id?: string | null;
  discogs_artist_id?: string | null;
  spotify_artist_id?: string | null;
  musicbrainz_id?: string | null;
  pro_credits?: unknown[] | null;
  social_handles?: Record<string, string> | null;
  detected_roles?: string[] | null;
  primary_vertical?: string | null;
  bio_snippet?: string | null;
  genre_tags?: string[] | null;
  notable_works?: string[] | null;
  collaborators?: string[] | null;
}

export interface PersonaCardProps {
  artistId: string;
  apiBase?: string;
  initialData?: PersonaData | null;
  onEnrich?: () => void;
}

const VERTICAL_LABELS: Record<string, string> = {
  music: "Music",
  tv_film: "TV / Film",
  both: "Music + TV / Film",
};

function Chip({ label, color = "purple" }: { label: string; color?: string }) {
  return (
    <span className="inline-flex items-center text-xs bg-purple-900/60 text-purple-200 border border-purple-600/40 rounded-full px-2 py-0.5">
      {label}
    </span>
  );
}

function SkeletonLine({ width = "full" }: { width?: string }) {
  return (
    <div
      className={`h-3 rounded bg-purple-900/50 animate-pulse w-${width}`}
    />
  );
}

export function PersonaCard({
  artistId,
  apiBase = "",
  initialData = null,
  onEnrich,
}: PersonaCardProps) {
  const [persona, setPersona] = useState<PersonaData | null>(initialData);
  const [loading, setLoading] = useState(!initialData);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (initialData) return;
    let mounted = true;
    const load = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${apiBase}/artists/${artistId}/persona`);
        if (!mounted) return;
        if (res.ok) {
          const data = await res.json();
          setPersona(data);
        } else if (res.status !== 404) {
          setError("Could not load persona.");
        }
      } catch {
        if (mounted) setError("Network error.");
      } finally {
        if (mounted) setLoading(false);
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
    } catch {
      setEnriching(false);
    }
  };

  if (loading) {
    return (
      <div className="vip-card space-y-3 p-5">
        <SkeletonLine width="1/2" />
        <SkeletonLine width="3/4" />
        <SkeletonLine width="2/3" />
        <SkeletonLine width="full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="vip-card p-5 text-red-400 text-sm">{error}</div>
    );
  }

  const isPending =
    !persona ||
    persona.enrichment_status === "pending" ||
    persona.enrichment_status === "in_progress";

  return (
    <div className="vip-card p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-purple-100 font-semibold text-base tracking-wide">
            Your Public Persona
          </h3>
          <p className="text-purple-400 text-xs mt-0.5">
            Enriched from public sources · IMDb · Discogs · MusicBrainz
          </p>
        </div>
        {!enriching && (
          <button
            onClick={handleEnrich}
            className="vip-btn-sm"
            title="Re-run persona enrichment"
          >
            Refresh
          </button>
        )}
        {enriching && (
          <span className="text-purple-400 text-xs animate-pulse">
            Enriching…
          </span>
        )}
      </div>

      {/* Vertical badge */}
      {persona?.primary_vertical && (
        <div className="flex items-center gap-2">
          <span className="text-purple-300 text-xs">Vertical:</span>
          <Chip label={VERTICAL_LABELS[persona.primary_vertical] ?? persona.primary_vertical} />
        </div>
      )}

      {/* Detected roles */}
      {(persona?.detected_roles ?? []).length > 0 && (
        <div>
          <p className="text-purple-400 text-xs mb-1.5">Detected Roles</p>
          <div className="flex flex-wrap gap-1.5">
            {(persona!.detected_roles ?? []).map((role) => (
              <Chip key={role} label={role} />
            ))}
          </div>
        </div>
      )}

      {/* Genre tags */}
      {(persona?.genre_tags ?? []).length > 0 && (
        <div>
          <p className="text-purple-400 text-xs mb-1.5">Genres</p>
          <div className="flex flex-wrap gap-1.5">
            {(persona!.genre_tags ?? []).slice(0, 8).map((g) => (
              <Chip key={g} label={g} />
            ))}
          </div>
        </div>
      )}

      {/* Bio */}
      {persona?.bio_snippet && (
        <div>
          <p className="text-purple-400 text-xs mb-1">Bio</p>
          <p className="text-purple-200 text-sm leading-relaxed line-clamp-3">
            {persona.bio_snippet}
          </p>
        </div>
      )}

      {/* Notable works */}
      {(persona?.notable_works ?? []).length > 0 && (
        <div>
          <p className="text-purple-400 text-xs mb-1.5">Notable Works</p>
          <ul className="space-y-0.5">
            {(persona!.notable_works ?? []).slice(0, 5).map((w) => (
              <li key={w} className="text-purple-200 text-sm flex items-center gap-1.5">
                <span className="text-purple-500">›</span> {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Source IDs */}
      <div className="flex flex-wrap gap-3 pt-1 border-t border-purple-800/50">
        {persona?.musicbrainz_id && (
          <ExternalIdBadge label="MusicBrainz" id={persona.musicbrainz_id} />
        )}
        {persona?.spotify_artist_id && (
          <ExternalIdBadge label="Spotify" id={persona.spotify_artist_id} />
        )}
        {persona?.imdb_id && (
          <ExternalIdBadge label="IMDb" id={persona.imdb_id} />
        )}
      </div>

      {/* Pending state */}
      {isPending && (
        <div className="rounded-lg bg-purple-950/60 border border-purple-700/30 p-3 text-purple-300 text-xs">
          {persona?.enrichment_status === "in_progress"
            ? "⟳ Enriching your persona from public sources…"
            : "Your persona profile will be enriched automatically — or click Refresh now."}
        </div>
      )}

      <style>{`
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
      `}</style>
    </div>
  );
}

function ExternalIdBadge({ label, id }: { label: string; id: string }) {
  return (
    <div className="flex items-center gap-1 text-xs text-purple-400">
      <span className="font-medium text-purple-300">{label}</span>
      <span className="font-mono text-purple-500 truncate max-w-[80px]" title={id}>
        {id.length > 10 ? id.slice(0, 8) + "…" : id}
      </span>
    </div>
  );
}
