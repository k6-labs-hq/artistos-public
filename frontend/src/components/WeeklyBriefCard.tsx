/**
 * WeeklyBriefCard — Displays and triggers the AI-generated weekly strategic brief.
 */
import { useEffect, useRef, useState } from "react";

interface KeyInsight {
  label: string;
  value: string;
  sentiment?: "positive" | "neutral" | "negative";
}

interface ActionItem {
  text: string;
  priority: "high" | "medium" | "low";
  completed: boolean;
}

interface WeeklyBrief {
  id: string;
  brief_week: string;
  status: "PENDING" | "GENERATING" | "READY" | "FAILED";
  text_summary: string | null;
  audio_url: string | null;
  video_url: string | null;
  key_insights: KeyInsight[];
  action_items: ActionItem[];
  generated_at: string | null;
}

export interface WeeklyBriefCardProps {
  artistId: string;
  apiBase?: string;
}

const PRIORITY_COLOR: Record<ActionItem["priority"], string> = {
  high: "#f87171",
  medium: "#fbbf24",
  low: "#86efac",
};

const SENTIMENT_COLOR: Record<NonNullable<KeyInsight["sentiment"]>, string> = {
  positive: "#86efac",
  neutral: "#c4b5fd",
  negative: "#f87171",
};

export function WeeklyBriefCard({ artistId, apiBase = "" }: WeeklyBriefCardProps) {
  const [brief, setBrief] = useState<WeeklyBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function fetchBrief() {
    try {
      const r = await fetch(`${apiBase}/artists/${artistId}/weekly-brief`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data: WeeklyBrief = await r.json();
      setBrief(data);
      return data.status;
    } catch (e: unknown) {
      setError((e as Error).message ?? "Failed to load brief");
      return "FAILED";
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchBrief();
  }, [artistId]);

  // Poll while generating
  useEffect(() => {
    if (brief?.status === "GENERATING") {
      pollRef.current = setInterval(async () => {
        const status = await fetchBrief();
        if (status === "READY" || status === "FAILED") {
          if (pollRef.current) clearInterval(pollRef.current);
        }
      }, 4000);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [brief?.status]);

  async function triggerGeneration() {
    setGenerating(true);
    setError(null);
    try {
      const r = await fetch(`${apiBase}/artists/${artistId}/weekly-brief/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data: WeeklyBrief = await r.json();
      setBrief(data);
    } catch (e: unknown) {
      setError((e as Error).message ?? "Generation failed");
    } finally {
      setGenerating(false);
    }
  }

  function toggleAudio() {
    if (!audioRef.current) return;
    if (audioPlaying) {
      audioRef.current.pause();
      setAudioPlaying(false);
    } else {
      audioRef.current.play().catch(() => {});
      setAudioPlaying(true);
    }
  }

  if (loading) {
    return (
      <div className="wbc-skeleton">
        <div className="wbc-skeleton-line w-2/3" />
        <div className="wbc-skeleton-line w-full mt-2" />
        <div className="wbc-skeleton-line w-4/5 mt-1" />
        <style>{skeletonCSS}</style>
      </div>
    );
  }

  const isReady = brief?.status === "READY";
  const isGenerating = brief?.status === "GENERATING" || generating;

  return (
    <div className="wbc-card">
      {/* Header */}
      <div className="wbc-header">
        <div>
          <span className="wbc-eyebrow">Weekly Brief</span>
          {brief?.brief_week && (
            <span className="wbc-week">Week of {brief.brief_week}</span>
          )}
        </div>
        <button
          onClick={triggerGeneration}
          disabled={isGenerating}
          className="wbc-generate-btn"
          title="Generate a fresh brief with latest data"
        >
          {isGenerating ? (
            <span className="wbc-spinner" />
          ) : (
            "↺ Regenerate"
          )}
        </button>
      </div>

      {/* Generating state */}
      {isGenerating && !isReady && (
        <div className="wbc-generating-pill">
          <span className="wbc-spinner sm" />
          <span>XR7 Advisor is crafting your brief…</span>
        </div>
      )}

      {/* Summary */}
      {brief?.text_summary && (
        <div className="wbc-summary">
          <p>{brief.text_summary}</p>
        </div>
      )}

      {/* Audio player */}
      {brief?.audio_url && (
        <div className="wbc-audio-row">
          <audio
            ref={audioRef}
            src={brief.audio_url}
            onEnded={() => setAudioPlaying(false)}
          />
          <button className="wbc-audio-btn" onClick={toggleAudio}>
            {audioPlaying ? "⏸ Pause Audio Brief" : "▶ Play Audio Brief"}
          </button>
        </div>
      )}

      {/* Key insights */}
      {(brief?.key_insights?.length ?? 0) > 0 && (
        <div className="wbc-section">
          <h4 className="wbc-section-title">Key Insights</h4>
          <ul className="wbc-insights-list">
            {brief!.key_insights.map((ins, i) => (
              <li key={i} className="wbc-insight-item">
                <span
                  className="wbc-insight-dot"
                  style={{
                    background: ins.sentiment
                      ? SENTIMENT_COLOR[ins.sentiment]
                      : "#c4b5fd",
                  }}
                />
                <div>
                  <span className="font-semibold text-purple-200">{ins.label}:</span>{" "}
                  <span className="text-purple-300 text-sm">{ins.value}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action items */}
      {(brief?.action_items?.length ?? 0) > 0 && (
        <div className="wbc-section">
          <h4 className="wbc-section-title">Action Items</h4>
          <ul className="wbc-actions-list">
            {brief!.action_items.map((item, i) => (
              <li key={i} className="wbc-action-item">
                <span
                  className="wbc-priority-dot"
                  style={{ background: PRIORITY_COLOR[item.priority] }}
                  title={item.priority}
                />
                <span
                  className={[
                    "text-sm",
                    item.completed
                      ? "line-through text-purple-600"
                      : "text-purple-200",
                  ].join(" ")}
                >
                  {item.text}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Error */}
      {error && <p className="wbc-error">⚠ {error}</p>}

      {/* Empty state */}
      {!brief?.text_summary && !isGenerating && !error && (
        <p className="wbc-empty">
          No brief yet. Hit <strong>Regenerate</strong> to create your first
          personalized weekly brief.
        </p>
      )}

      <style>{css}</style>
    </div>
  );
}

const skeletonCSS = `
  .wbc-skeleton { padding:1.25rem; }
  .wbc-skeleton-line {
    height:12px; border-radius:6px;
    background: linear-gradient(90deg,rgba(88,28,135,0.3) 25%,rgba(168,85,247,0.18) 50%,rgba(88,28,135,0.3) 75%);
    background-size:200% 100%;
    animation: shimmer 1.4s infinite;
  }
  @keyframes shimmer{to{background-position:-200% 0}}
`;

const css = `
  .wbc-card {
    background: linear-gradient(145deg,rgba(30,8,65,0.97) 0%,rgba(45,12,90,0.95) 100%);
    border:1px solid rgba(168,85,247,0.28);
    border-radius:14px;
    overflow:hidden;
  }
  .wbc-header {
    display:flex; align-items:flex-start; justify-content:space-between;
    padding:1rem 1.25rem 0.75rem;
    border-bottom:1px solid rgba(168,85,247,0.18);
  }
  .wbc-eyebrow {
    display:block; font-size:0.65rem; font-weight:800; letter-spacing:0.14em;
    text-transform:uppercase; color:#a855f7;
  }
  .wbc-week { display:block; font-size:0.78rem; color:#c4b5fd; margin-top:2px; }
  .wbc-generate-btn {
    font-size:0.73rem; padding:0.38rem 0.9rem;
    border-radius:9999px; cursor:pointer; font-weight:700;
    border:1px solid rgba(168,85,247,0.38);
    background:rgba(168,85,247,0.12); color:#d8b4fe;
    display:flex; align-items:center; gap:0.4rem;
    transition:background 0.2s, transform 0.15s;
  }
  .wbc-generate-btn:hover:not(:disabled) {
    background:rgba(168,85,247,0.26); transform:scale(1.03);
  }
  .wbc-generate-btn:disabled { opacity:0.45; cursor:not-allowed; }
  .wbc-spinner {
    width:14px; height:14px;
    border:2px solid rgba(168,85,247,0.3);
    border-top-color:#a855f7;
    border-radius:50%;
    animation:spin 0.7s linear infinite;
    display:inline-block;
  }
  .wbc-spinner.sm { width:11px; height:11px; }
  @keyframes spin{to{transform:rotate(360deg)}}
  .wbc-generating-pill {
    display:flex; align-items:center; gap:0.6rem;
    margin:0.75rem 1.25rem; padding:0.6rem 1rem;
    border-radius:9999px; font-size:0.78rem; color:#c4b5fd;
    background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.22);
  }
  .wbc-summary {
    padding:1rem 1.25rem; font-size:0.85rem; color:#e9d5ff; line-height:1.6;
  }
  .wbc-audio-row { padding:0 1.25rem 0.75rem; }
  .wbc-audio-btn {
    font-size:0.78rem; padding:0.4rem 1.1rem;
    border-radius:9999px; cursor:pointer; font-weight:600;
    border:1px solid rgba(168,85,247,0.45);
    background:rgba(168,85,247,0.14); color:#d8b4fe;
    transition:background 0.2s;
  }
  .wbc-audio-btn:hover { background:rgba(168,85,247,0.28); }
  .wbc-section { padding:0 1.25rem 0.9rem; }
  .wbc-section-title {
    font-size:0.68rem; font-weight:800; text-transform:uppercase;
    letter-spacing:0.12em; color:#a855f7; margin-bottom:0.5rem;
  }
  .wbc-insights-list, .wbc-actions-list {
    list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:0.45rem;
  }
  .wbc-insight-item, .wbc-action-item {
    display:flex; align-items:flex-start; gap:0.55rem;
  }
  .wbc-insight-dot, .wbc-priority-dot {
    width:8px; height:8px; border-radius:50%; flex-shrink:0; margin-top:4px;
  }
  .wbc-error { padding:0.75rem 1.25rem; color:#f87171; font-size:0.8rem; }
  .wbc-empty { padding:0.75rem 1.25rem 1.25rem; color:#7e6bad; font-size:0.83rem; }
`;
