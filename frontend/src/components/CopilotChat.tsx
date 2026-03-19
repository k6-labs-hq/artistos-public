/**
 * CopilotChat — XR7 Advisor conversational interface for VIP artists.
 *
 * Features:
 * - Full chat history loaded from /copilot/history
 * - Real-time query submission to /copilot/query
 * - Confidence meter per AI response
 * - Action suggestions rendered as clickable chips
 * - Thumbs up/down feedback
 * - Sources cited accordion
 */
import { useEffect, useRef, useState } from "react";

interface CopilotHistoryItem {
  id: string;
  query_text: string;
  response_text: string;
  confidence: number;
  sources_cited: string[];
  action_suggestions: string[];
  thumbs_up: boolean | null;
  created_at: string;
}

interface CopilotQueryResponse {
  id: string;
  response_text: string;
  confidence: number;
  sources_cited: string[];
  action_suggestions: string[];
}

export interface CopilotChatProps {
  artistId: string;
  apiBase?: string;
  personaGreeting?: string;
}

type UIMessage =
  | { type: "user"; text: string; id?: string }
  | {
      type: "assistant";
      text: string;
      id: string;
      confidence: number;
      sources: string[];
      actionSuggestions: string[];
      thumbsUp: boolean | null;
    };

export function CopilotChat({
  artistId,
  apiBase = "",
  personaGreeting,
}: CopilotChatProps) {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialising, setInitialising] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fetch(`${apiBase}/artists/${artistId}/copilot/history`)
      .then((r) => (r.ok ? r.json() : []))
      .then((items: CopilotHistoryItem[]) => {
        const msgs: UIMessage[] = [];
        // Add greeting as first assistant message if no history
        if (items.length === 0 && personaGreeting) {
          msgs.push({
            type: "assistant",
            text: personaGreeting,
            id: "__greeting__",
            confidence: 1,
            sources: [],
            actionSuggestions: [],
            thumbsUp: null,
          });
        }
        for (const item of items) {
          msgs.push({ type: "user", text: item.query_text });
          msgs.push({
            type: "assistant",
            text: item.response_text,
            id: item.id,
            confidence: item.confidence,
            sources: item.sources_cited ?? [],
            actionSuggestions: item.action_suggestions ?? [],
            thumbsUp: item.thumbs_up,
          });
        }
        setMessages(msgs);
      })
      .catch(() => {})
      .finally(() => setInitialising(false));
  }, [artistId, apiBase, personaGreeting]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { type: "user", text }]);
    setLoading(true);
    try {
      const r = await fetch(`${apiBase}/artists/${artistId}/copilot/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_text: text }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data: CopilotQueryResponse = await r.json();
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: data.response_text,
          id: data.id,
          confidence: data.confidence,
          sources: data.sources_cited ?? [],
          actionSuggestions: data.action_suggestions ?? [],
          thumbsUp: null,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: "⚠ XR7 Advisor is temporarily unavailable. Please try again shortly.",
          id: `err_${Date.now()}`,
          confidence: 0,
          sources: [],
          actionSuggestions: [],
          thumbsUp: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function sendFeedback(queryId: string, value: boolean) {
    setMessages((prev) =>
      prev.map((m) =>
        m.type === "assistant" && m.id === queryId
          ? { ...m, thumbsUp: value }
          : m
      )
    );
    await fetch(`${apiBase}/artists/${artistId}/copilot/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query_id: queryId, thumbs_up: value }),
    }).catch(() => {});
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function useSuggestion(text: string) {
    setInput(text);
    inputRef.current?.focus();
  }

  return (
    <div className="cc-chat">
      {/* Header */}
      <div className="cc-header">
        <div className="cc-avatar">XR7</div>
        <div>
          <h3 className="cc-title">XR7 Advisor</h3>
          <p className="cc-subtitle">Personalized AI strategy concierge</p>
        </div>
        <div className="cc-live-dot" title="AI online" />
      </div>

      {/* Messages */}
      <div className="cc-messages">
        {initialising ? (
          <div className="cc-init-skeleton">
            <div className="cc-skel-line w-1/2" />
            <div className="cc-skel-line w-3/4 mt-2" />
          </div>
        ) : (
          messages.map((msg, i) =>
            msg.type === "user" ? (
              <UserBubble key={i} text={msg.text} />
            ) : (
              <AssistantBubble
                key={i}
                msg={msg}
                onFeedback={sendFeedback}
                onSuggestionClick={useSuggestion}
              />
            )
          )
        )}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="cc-input-row">
        <textarea
          ref={inputRef}
          className="cc-input"
          rows={2}
          placeholder="Ask about your royalties, claims, strategy…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="cc-send-btn"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          {loading ? <span className="cc-spinner" /> : "↑"}
        </button>
      </div>

      <style>{css}</style>
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function UserBubble({ text }: { text: string }) {
  return (
    <div className="cc-user-bubble-row">
      <div className="cc-user-bubble">{text}</div>
    </div>
  );
}

interface AssistantBubbleProps {
  msg: Extract<UIMessage, { type: "assistant" }>;
  onFeedback: (id: string, value: boolean) => void;
  onSuggestionClick: (text: string) => void;
}

function AssistantBubble({ msg, onFeedback, onSuggestionClick }: AssistantBubbleProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const pct = Math.round(msg.confidence * 100);
  // Color gradient: red→yellow→green mapped to 0–100
  const confColor = pct >= 75 ? "#86efac" : pct >= 50 ? "#fbbf24" : "#f87171";

  return (
    <div className="cc-assistant-msg">
      <p className="cc-assistant-text">{msg.text}</p>

      {/* Confidence meter */}
      {msg.id !== "__greeting__" && (
        <div className="cc-conf-row">
          <span className="cc-conf-label">Confidence</span>
          <div className="cc-conf-bar-track">
            <div
              className="cc-conf-bar-fill"
              style={{ width: `${pct}%`, background: confColor }}
            />
          </div>
          <span className="cc-conf-pct" style={{ color: confColor }}>
            {pct}%
          </span>
        </div>
      )}

      {/* Action suggestions */}
      {msg.actionSuggestions.length > 0 && (
        <div className="cc-suggestions">
          {msg.actionSuggestions.map((s, i) => (
            <button key={i} className="cc-suggestion-chip" onClick={() => onSuggestionClick(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Sources */}
      {msg.sources.length > 0 && (
        <div className="cc-sources">
          <button
            className="cc-sources-toggle"
            onClick={() => setSourcesOpen((o) => !o)}
          >
            {sourcesOpen ? "▾ " : "▸ "} {msg.sources.length} source
            {msg.sources.length !== 1 ? "s" : ""}
          </button>
          {sourcesOpen && (
            <ul className="cc-sources-list">
              {msg.sources.map((s, i) => (
                <li key={i} className="cc-source-item">
                  {s}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Feedback */}
      {msg.id !== "__greeting__" && (
        <div className="cc-feedback-row">
          <button
            className={[
              "cc-feedback-btn",
              msg.thumbsUp === true ? "active-pos" : "",
            ].join(" ")}
            onClick={() => onFeedback(msg.id, true)}
            title="Helpful"
          >
            👍
          </button>
          <button
            className={[
              "cc-feedback-btn",
              msg.thumbsUp === false ? "active-neg" : "",
            ].join(" ")}
            onClick={() => onFeedback(msg.id, false)}
            title="Not helpful"
          >
            👎
          </button>
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="cc-assistant-msg cc-typing">
      <span className="cc-dot" />
      <span className="cc-dot" style={{ animationDelay: "0.15s" }} />
      <span className="cc-dot" style={{ animationDelay: "0.3s" }} />
    </div>
  );
}

const css = `
  .cc-chat {
    display:flex; flex-direction:column; height:100%;
    min-height:480px; max-height:680px;
    background:linear-gradient(175deg,rgba(20,5,50,0.98) 0%,rgba(30,8,65,0.97) 100%);
    border:1px solid rgba(168,85,247,0.28); border-radius:14px; overflow:hidden;
  }
  .cc-header {
    display:flex; align-items:center; gap:0.75rem;
    padding:0.85rem 1.1rem;
    border-bottom:1px solid rgba(168,85,247,0.18);
    background:rgba(88,28,135,0.25);
  }
  .cc-avatar {
    width:36px; height:36px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#a855f7);
    display:flex; align-items:center; justify-content:center;
    font-size:0.7rem; font-weight:900; color:#fff; letter-spacing:0.05em;
    flex-shrink:0;
  }
  .cc-title { font-size:0.9rem; font-weight:700; color:#e9d5ff; margin:0; }
  .cc-subtitle { font-size:0.7rem; color:#9f7ced; margin:0; }
  .cc-live-dot {
    width:8px; height:8px; border-radius:50%;
    background:#86efac; margin-left:auto; flex-shrink:0;
    box-shadow:0 0 6px #86efac;
    animation:pulse-green 2s ease-in-out infinite;
  }
  @keyframes pulse-green{0%,100%{opacity:1}50%{opacity:0.45}}
  .cc-messages {
    flex:1; overflow-y:auto; padding:1rem;
    display:flex; flex-direction:column; gap:0.75rem;
    scrollbar-width:thin; scrollbar-color:rgba(168,85,247,0.3) transparent;
  }
  .cc-user-bubble-row { display:flex; justify-content:flex-end; }
  .cc-user-bubble {
    max-width:80%; font-size:0.84rem; color:#ede9fe; line-height:1.55;
    background:rgba(124,58,237,0.3); border:1px solid rgba(168,85,247,0.3);
    border-radius:14px 14px 4px 14px; padding:0.6rem 0.9rem;
  }
  .cc-assistant-msg {
    max-width:88%; background:rgba(30,8,65,0.7);
    border:1px solid rgba(168,85,247,0.18);
    border-radius:4px 14px 14px 14px; padding:0.7rem 1rem;
  }
  .cc-assistant-text { font-size:0.84rem; color:#e9d5ff; line-height:1.6; margin:0 0 0.4rem; }
  .cc-conf-row {
    display:flex; align-items:center; gap:0.5rem; margin-top:0.4rem;
  }
  .cc-conf-label { font-size:0.65rem; color:#9f7ced; white-space:nowrap; }
  .cc-conf-bar-track {
    flex:1; height:4px; border-radius:999px;
    background:rgba(88,28,135,0.5); overflow:hidden;
  }
  .cc-conf-bar-fill { height:100%; border-radius:999px; transition:width 0.4s; }
  .cc-conf-pct { font-size:0.65rem; font-weight:700; min-width:28px; }
  .cc-suggestions {
    display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.55rem;
  }
  .cc-suggestion-chip {
    font-size:0.72rem; padding:0.3rem 0.8rem;
    border-radius:9999px; cursor:pointer;
    border:1px solid rgba(168,85,247,0.35);
    background:rgba(168,85,247,0.1); color:#d8b4fe;
    transition:background 0.18s;
  }
  .cc-suggestion-chip:hover { background:rgba(168,85,247,0.24); }
  .cc-sources { margin-top:0.5rem; }
  .cc-sources-toggle {
    font-size:0.68rem; color:#9f7ced; background:none; border:none;
    cursor:pointer; padding:0;
  }
  .cc-sources-list {
    list-style:none; padding:0.4rem 0 0 0.5rem; margin:0;
    display:flex; flex-direction:column; gap:0.25rem;
  }
  .cc-source-item { font-size:0.68rem; color:#7c3aed; }
  .cc-feedback-row {
    display:flex; gap:0.4rem; margin-top:0.5rem;
    border-top:1px solid rgba(88,28,135,0.35); padding-top:0.4rem;
  }
  .cc-feedback-btn {
    background:none; border:none; cursor:pointer; font-size:0.9rem;
    opacity:0.5; transition:opacity 0.18s, transform 0.15s;
    padding:0.1rem;
  }
  .cc-feedback-btn:hover { opacity:1; transform:scale(1.2); }
  .cc-feedback-btn.active-pos { opacity:1; filter:drop-shadow(0 0 4px #86efac); }
  .cc-feedback-btn.active-neg { opacity:1; filter:drop-shadow(0 0 4px #f87171); }
  .cc-typing {
    display:flex; align-items:center; gap:0.3rem; padding:0.6rem 0.9rem;
    min-height:2.2rem;
  }
  .cc-dot {
    width:7px; height:7px; border-radius:50%;
    background:#a855f7; display:inline-block;
    animation:bounce-dot 0.9s ease-in-out infinite;
  }
  @keyframes bounce-dot{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
  .cc-input-row {
    display:flex; gap:0.5rem; padding:0.75rem;
    border-top:1px solid rgba(168,85,247,0.18);
    background:rgba(20,5,50,0.6);
  }
  .cc-input {
    flex:1; font-size:0.83rem; color:#e9d5ff; line-height:1.5;
    background:rgba(60,20,120,0.35); border:1px solid rgba(168,85,247,0.3);
    border-radius:10px; padding:0.55rem 0.85rem; resize:none; outline:none;
    transition:border-color 0.2s;
  }
  .cc-input:focus { border-color:rgba(168,85,247,0.65); }
  .cc-input::placeholder { color:#6d4fa3; }
  .cc-send-btn {
    width:42px; height:42px; border-radius:50%; cursor:pointer;
    background:linear-gradient(135deg,#7c3aed,#a855f7);
    border:none; color:#fff; font-size:1.1rem; font-weight:900;
    display:flex; align-items:center; justify-content:center;
    transition:opacity 0.18s, transform 0.15s;
    align-self:flex-end; flex-shrink:0;
  }
  .cc-send-btn:hover:not(:disabled) { opacity:0.85; transform:scale(1.06); }
  .cc-send-btn:disabled { opacity:0.4; cursor:not-allowed; }
  .cc-spinner {
    width:16px; height:16px;
    border:2px solid rgba(255,255,255,0.3);
    border-top-color:#fff; border-radius:50%;
    animation:spin 0.7s linear infinite; display:inline-block;
  }
  @keyframes spin{to{transform:rotate(360deg)}}
  .cc-init-skeleton { display:flex; flex-direction:column; gap:0.5rem; padding:0.5rem 0; }
  .cc-skel-line {
    height:11px; border-radius:6px;
    background:linear-gradient(90deg,rgba(88,28,135,0.3) 25%,rgba(168,85,247,0.18) 50%,rgba(88,28,135,0.3) 75%);
    background-size:200% 100%;
    animation:shimmer 1.4s infinite;
  }
  @keyframes shimmer{to{background-position:-200% 0}}
`;
