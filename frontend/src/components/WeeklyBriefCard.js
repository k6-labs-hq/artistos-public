import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * WeeklyBriefCard — Displays and triggers the AI-generated weekly strategic brief.
 */
import { useEffect, useRef, useState } from "react";
const PRIORITY_COLOR = {
    high: "#f87171",
    medium: "#fbbf24",
    low: "#86efac",
};
const SENTIMENT_COLOR = {
    positive: "#86efac",
    neutral: "#c4b5fd",
    negative: "#f87171",
};
export function WeeklyBriefCard({ artistId, apiBase = "" }) {
    const [brief, setBrief] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState(null);
    const [audioPlaying, setAudioPlaying] = useState(false);
    const audioRef = useRef(null);
    const pollRef = useRef(null);
    async function fetchBrief() {
        try {
            const r = await fetch(`${apiBase}/artists/${artistId}/weekly-brief`);
            if (!r.ok)
                throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            setBrief(data);
            return data.status;
        }
        catch (e) {
            setError(e.message ?? "Failed to load brief");
            return "FAILED";
        }
        finally {
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
                    if (pollRef.current)
                        clearInterval(pollRef.current);
                }
            }, 4000);
        }
        return () => {
            if (pollRef.current)
                clearInterval(pollRef.current);
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
            if (!r.ok)
                throw new Error(`HTTP ${r.status}`);
            const data = await r.json();
            setBrief(data);
        }
        catch (e) {
            setError(e.message ?? "Generation failed");
        }
        finally {
            setGenerating(false);
        }
    }
    function toggleAudio() {
        if (!audioRef.current)
            return;
        if (audioPlaying) {
            audioRef.current.pause();
            setAudioPlaying(false);
        }
        else {
            audioRef.current.play().catch(() => { });
            setAudioPlaying(true);
        }
    }
    if (loading) {
        return (_jsxs("div", { className: "wbc-skeleton", children: [_jsx("div", { className: "wbc-skeleton-line w-2/3" }), _jsx("div", { className: "wbc-skeleton-line w-full mt-2" }), _jsx("div", { className: "wbc-skeleton-line w-4/5 mt-1" }), _jsx("style", { children: skeletonCSS })] }));
    }
    const isReady = brief?.status === "READY";
    const isGenerating = brief?.status === "GENERATING" || generating;
    return (_jsxs("div", { className: "wbc-card", children: [_jsxs("div", { className: "wbc-header", children: [_jsxs("div", { children: [_jsx("span", { className: "wbc-eyebrow", children: "Weekly Brief" }), brief?.brief_week && (_jsxs("span", { className: "wbc-week", children: ["Week of ", brief.brief_week] }))] }), _jsx("button", { onClick: triggerGeneration, disabled: isGenerating, className: "wbc-generate-btn", title: "Generate a fresh brief with latest data", children: isGenerating ? (_jsx("span", { className: "wbc-spinner" })) : ("↺ Regenerate") })] }), isGenerating && !isReady && (_jsxs("div", { className: "wbc-generating-pill", children: [_jsx("span", { className: "wbc-spinner sm" }), _jsx("span", { children: "XR7 Advisor is crafting your brief\u2026" })] })), brief?.text_summary && (_jsx("div", { className: "wbc-summary", children: _jsx("p", { children: brief.text_summary }) })), brief?.audio_url && (_jsxs("div", { className: "wbc-audio-row", children: [_jsx("audio", { ref: audioRef, src: brief.audio_url, onEnded: () => setAudioPlaying(false) }), _jsx("button", { className: "wbc-audio-btn", onClick: toggleAudio, children: audioPlaying ? "⏸ Pause Audio Brief" : "▶ Play Audio Brief" })] })), (brief?.key_insights?.length ?? 0) > 0 && (_jsxs("div", { className: "wbc-section", children: [_jsx("h4", { className: "wbc-section-title", children: "Key Insights" }), _jsx("ul", { className: "wbc-insights-list", children: brief.key_insights.map((ins, i) => (_jsxs("li", { className: "wbc-insight-item", children: [_jsx("span", { className: "wbc-insight-dot", style: {
                                        background: ins.sentiment
                                            ? SENTIMENT_COLOR[ins.sentiment]
                                            : "#c4b5fd",
                                    } }), _jsxs("div", { children: [_jsxs("span", { className: "font-semibold text-purple-200", children: [ins.label, ":"] }), " ", _jsx("span", { className: "text-purple-300 text-sm", children: ins.value })] })] }, i))) })] })), (brief?.action_items?.length ?? 0) > 0 && (_jsxs("div", { className: "wbc-section", children: [_jsx("h4", { className: "wbc-section-title", children: "Action Items" }), _jsx("ul", { className: "wbc-actions-list", children: brief.action_items.map((item, i) => (_jsxs("li", { className: "wbc-action-item", children: [_jsx("span", { className: "wbc-priority-dot", style: { background: PRIORITY_COLOR[item.priority] }, title: item.priority }), _jsx("span", { className: [
                                        "text-sm",
                                        item.completed
                                            ? "line-through text-purple-600"
                                            : "text-purple-200",
                                    ].join(" "), children: item.text })] }, i))) })] })), error && _jsxs("p", { className: "wbc-error", children: ["\u26A0 ", error] }), !brief?.text_summary && !isGenerating && !error && (_jsxs("p", { className: "wbc-empty", children: ["No brief yet. Hit ", _jsx("strong", { children: "Regenerate" }), " to create your first personalized weekly brief."] })), _jsx("style", { children: css })] }));
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
