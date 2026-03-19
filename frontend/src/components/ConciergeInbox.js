import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ConciergeInbox — In-app messaging with named XR7 analysts.
 *
 * Features:
 * - Real-time-like message thread display
 * - Artist ↔ Analyst message bubbles with timestamps
 * - One-click "Request Human Analyst" escalation button
 * - Optional Calendly 1:1 booking link integration
 * - Voice input button placeholder for mobile
 * - Attachment list display
 */
import { useEffect, useRef, useState } from "react";
function formatTime(iso) {
    try {
        return new Intl.DateTimeFormat("en-US", {
            month: "short",
            day: "numeric",
            hour: "numeric",
            minute: "2-digit",
        }).format(new Date(iso));
    }
    catch {
        return iso;
    }
}
function MessageBubble({ msg }) {
    const isArtist = msg.sender_type === "artist";
    const isSystem = msg.sender_type === "system";
    return (_jsx("div", { className: ["flex", isArtist ? "justify-end" : "justify-start"].join(" "), children: _jsxs("div", { className: [
                "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                isArtist
                    ? "bg-purple-700/80 text-white rounded-tr-sm"
                    : isSystem
                        ? "bg-purple-950/70 text-purple-300 border border-purple-700/30 rounded-tl-sm text-xs italic"
                        : "bg-[rgba(40,10,80,0.8)] border border-purple-600/30 text-purple-100 rounded-tl-sm",
            ].join(" "), children: [!isArtist && !isSystem && (_jsx("p", { className: "text-purple-400 text-xs font-medium mb-0.5", children: msg.sender_name })), _jsx("p", { children: msg.message_body }), msg.attachments && msg.attachments.length > 0 && (_jsx("div", { className: "mt-1.5 space-y-0.5", children: msg.attachments.map((att, i) => (_jsxs("a", { href: att, target: "_blank", rel: "noopener noreferrer", className: "flex items-center gap-1 text-purple-400 text-xs hover:text-purple-300 underline", children: ["\uD83D\uDCCE Attachment ", i + 1] }, i))) })), _jsxs("p", { className: ["text-xs mt-1", isArtist ? "text-purple-300" : "text-purple-500"].join(" "), children: [formatTime(msg.created_at), msg.escalated && (_jsx("span", { className: "ml-2 text-amber-400", children: "\u2191 Escalated" }))] })] }) }));
}
export function ConciergeInbox({ artistId, apiBase = "", analystName = "XR7 Strategy Team", calendlyLink, }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const [escalating, setEscalating] = useState(false);
    const [escalated, setEscalated] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const bottomRef = useRef(null);
    const load = async () => {
        try {
            const res = await fetch(`${apiBase}/artists/${artistId}/concierge/messages?limit=100`);
            if (res.ok) {
                setMessages(await res.json());
            }
        }
        catch {
            setError("Could not load messages.");
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        load();
        // Poll every 15s for new messages (production: replace with WebSocket)
        const interval = setInterval(load, 15000);
        return () => clearInterval(interval);
    }, [artistId, apiBase]);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);
    const sendMessage = async () => {
        const text = input.trim();
        if (!text || sending)
            return;
        setSending(true);
        setError("");
        try {
            const res = await fetch(`${apiBase}/concierge/send`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    artist_id: artistId,
                    message_body: text,
                    request_human_analyst: false,
                }),
            });
            if (res.ok) {
                const msg = await res.json();
                setMessages((prev) => [...prev, msg]);
                setInput("");
            }
            else {
                const data = await res.json().catch(() => ({}));
                setError(data.detail ?? "Failed to send message.");
            }
        }
        catch {
            setError("Network error. Please try again.");
        }
        finally {
            setSending(false);
        }
    };
    const requestHumanAnalyst = async () => {
        setEscalating(true);
        try {
            const res = await fetch(`${apiBase}/artists/${artistId}/concierge/escalate`, {
                method: "POST",
            });
            if (res.ok) {
                setEscalated(true);
                await load();
            }
        }
        catch {
            /* silent */
        }
        finally {
            setEscalating(false);
        }
    };
    return (_jsxs("div", { className: "concierge-inbox flex flex-col h-full min-h-[420px]", children: [_jsxs("div", { className: "concierge-header flex items-center justify-between px-4 py-3 border-b border-purple-800/40", children: [_jsxs("div", { className: "flex items-center gap-2.5", children: [_jsx("div", { className: "w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-purple-900 flex items-center justify-center text-white text-xs font-bold", children: analystName.charAt(0).toUpperCase() }), _jsxs("div", { children: [_jsx("p", { className: "text-purple-100 text-sm font-semibold", children: analystName }), _jsx("p", { className: "text-purple-500 text-xs", children: "XR7 Concierge \u00B7 Founders Circle" })] })] }), _jsx("div", { className: "flex items-center gap-2", children: calendlyLink && (_jsx("a", { href: calendlyLink, target: "_blank", rel: "noopener noreferrer", className: "vip-btn-sm flex items-center gap-1", title: "Book your monthly 1:1 strategy call", children: "\uD83D\uDCC5 Book 1:1" })) })] }), _jsxs("div", { className: "flex-1 overflow-y-auto px-4 py-3 space-y-3", children: [loading && (_jsx("div", { className: "text-purple-500 text-sm text-center animate-pulse py-4", children: "Loading messages\u2026" })), !loading && messages.length === 0 && (_jsxs("div", { className: "text-center py-8 space-y-2", children: [_jsx("p", { className: "text-purple-400 text-sm", children: "Your concierge inbox is ready." }), _jsxs("p", { className: "text-purple-600 text-xs", children: ["Send a message to ", analystName, " \u2014 your dedicated XR7 strategist."] })] })), messages.map((msg) => (_jsx(MessageBubble, { msg: msg }, msg.id))), _jsx("div", { ref: bottomRef })] }), error && (_jsx("div", { className: "px-4 py-1.5 text-red-400 text-xs bg-red-950/30", children: error })), escalated && (_jsxs("div", { className: "px-4 py-2 bg-amber-950/50 border-t border-amber-700/30 text-amber-300 text-xs", children: ["\u2713 Human analyst request sent \u00B7 ", analystName, " will respond within 24 hours"] })), _jsxs("div", { className: "concierge-input-bar flex items-end gap-2 px-3 py-2 border-t border-purple-800/40", children: [_jsxs("div", { className: "flex-1 relative", children: [_jsx("textarea", { value: input, onChange: (e) => setInput(e.target.value), onKeyDown: (e) => {
                                    if (e.key === "Enter" && !e.shiftKey) {
                                        e.preventDefault();
                                        sendMessage();
                                    }
                                }, placeholder: "Message your XR7 Advisor\u2026", rows: 1, className: "concierge-textarea w-full resize-none", disabled: sending, "aria-label": "Message input" }), _jsx("button", { className: "absolute right-2 top-1/2 -translate-y-1/2 text-purple-500 hover:text-purple-300 transition-colors", title: "Voice input (coming soon)", onClick: () => { }, "aria-label": "Voice input", children: "\uD83C\uDFA4" })] }), _jsx("button", { onClick: sendMessage, disabled: !input.trim() || sending, className: "concierge-send-btn", "aria-label": "Send message", children: sending ? "…" : "Send" }), !escalated && (_jsx("button", { onClick: requestHumanAnalyst, disabled: escalating, className: "concierge-escalate-btn", title: "Request a human analyst response", children: escalating ? "…" : "👤 Analyst" }))] }), _jsx("style", { children: `
        .concierge-inbox {
          background: linear-gradient(180deg, rgba(15,5,35,0.97) 0%, rgba(25,8,55,0.97) 100%);
          border: 1px solid rgba(168,85,247,0.20);
          border-radius: 14px;
          overflow: hidden;
        }
        .concierge-header {
          background: rgba(168,85,247,0.06);
        }
        .concierge-textarea {
          background: rgba(168,85,247,0.08);
          border: 1px solid rgba(168,85,247,0.25);
          border-radius: 10px;
          color: #e9d5ff;
          padding: 0.5rem 2.5rem 0.5rem 0.75rem;
          font-size: 0.875rem;
          outline: none;
          transition: border-color 0.2s;
          min-height: 40px;
          max-height: 120px;
        }
        .concierge-textarea:focus {
          border-color: rgba(168,85,247,0.60);
          box-shadow: 0 0 0 2px rgba(168,85,247,0.12);
        }
        .concierge-send-btn {
          padding: 0.45rem 1rem;
          border-radius: 9999px;
          background: linear-gradient(135deg, #7C3AED, #A855F7);
          color: white;
          font-size: 0.8rem;
          font-weight: 600;
          border: none;
          cursor: pointer;
          transition: opacity 0.2s, transform 0.15s;
        }
        .concierge-send-btn:hover:not(:disabled) {
          opacity: 0.90;
          transform: scale(1.04);
        }
        .concierge-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }
        .concierge-escalate-btn {
          padding: 0.45rem 0.75rem;
          border-radius: 9999px;
          background: rgba(245,158,11,0.15);
          border: 1px solid rgba(245,158,11,0.40);
          color: #fcd34d;
          font-size: 0.75rem;
          cursor: pointer;
          transition: background 0.2s;
          white-space: nowrap;
        }
        .concierge-escalate-btn:hover:not(:disabled) {
          background: rgba(245,158,11,0.25);
        }
        .vip-btn-sm {
          font-size: 0.7rem;
          padding: 0.25rem 0.65rem;
          border-radius: 9999px;
          background: rgba(168,85,247,0.15);
          border: 1px solid rgba(168,85,247,0.40);
          color: #d8b4fe;
          text-decoration: none;
          cursor: pointer;
          transition: background 0.2s;
        }
        .vip-btn-sm:hover { background: rgba(168,85,247,0.28); }
      ` })] }));
}
