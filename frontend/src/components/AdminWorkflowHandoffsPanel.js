import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import "./AdminWorkflowHandoffsPanel.css";
const storageKeys = {
    adminKey: "xr7-admin-handoffs-key",
    adminActor: "xr7-admin-handoffs-actor",
};
const basePath = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export function AdminWorkflowHandoffsPanel() {
    const [adminKey, setAdminKey] = useState("");
    const [adminActor, setAdminActor] = useState("ops@xr7.test");
    const [artistId, setArtistId] = useState("");
    const [query, setQuery] = useState("");
    const [status, setStatus] = useState("");
    const [fromAgent, setFromAgent] = useState("");
    const [toAgent, setToAgent] = useState("");
    const [since, setSince] = useState("");
    const [until, setUntil] = useState("");
    const [limit, setLimit] = useState("50");
    const [rows, setRows] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [lastQuery, setLastQuery] = useState("");
    useEffect(() => {
        const savedKey = window.localStorage.getItem(storageKeys.adminKey);
        const savedActor = window.localStorage.getItem(storageKeys.adminActor);
        if (savedKey)
            setAdminKey(savedKey);
        if (savedActor)
            setAdminActor(savedActor);
    }, []);
    useEffect(() => {
        if (adminKey) {
            window.localStorage.setItem(storageKeys.adminKey, adminKey);
        }
    }, [adminKey]);
    useEffect(() => {
        if (adminActor) {
            window.localStorage.setItem(storageKeys.adminActor, adminActor);
        }
    }, [adminActor]);
    const requestHeaders = useMemo(() => ({
        "X-Admin-Key": adminKey,
        "X-Admin-Actor": adminActor,
    }), [adminActor, adminKey]);
    const buildQueryString = (format) => {
        const params = new URLSearchParams();
        if (artistId.trim())
            params.set("artist_id", artistId.trim());
        if (query.trim())
            params.set("q", query.trim());
        if (status.trim())
            params.set("status", status.trim());
        if (fromAgent.trim())
            params.set("from_agent", fromAgent.trim());
        if (toAgent.trim())
            params.set("to_agent", toAgent.trim());
        if (since)
            params.set("since", new Date(`${since}T00:00:00`).toISOString());
        if (until)
            params.set("until", new Date(`${until}T23:59:59`).toISOString());
        params.set("limit", String(Math.max(1, Number(limit) || 50)));
        params.set("offset", "0");
        params.set("format", format);
        return params.toString();
    };
    const handlePreview = async () => {
        if (!adminKey.trim()) {
            setError("Admin key is required.");
            return;
        }
        const queryString = buildQueryString("json");
        setLoading(true);
        setError("");
        setLastQuery(queryString);
        try {
            const response = await fetch(`${basePath}/admin/workflow/handoffs?${queryString}`, {
                headers: requestHeaders,
            });
            const payload = (await response.json());
            if (!response.ok) {
                setRows([]);
                setTotal(0);
                setError(payload.detail || `Request failed (${response.status}).`);
                return;
            }
            const result = payload;
            setRows(result.items || []);
            setTotal(Number(result.total || 0));
        }
        catch (requestError) {
            setRows([]);
            setTotal(0);
            setError(String(requestError));
        }
        finally {
            setLoading(false);
        }
    };
    const handleExportCsv = async () => {
        if (!adminKey.trim()) {
            setError("Admin key is required.");
            return;
        }
        const queryString = buildQueryString("csv");
        setLoading(true);
        setError("");
        setLastQuery(queryString);
        try {
            const response = await fetch(`${basePath}/admin/workflow/handoffs?${queryString}`, {
                headers: requestHeaders,
            });
            if (!response.ok) {
                let message = `Export failed (${response.status}).`;
                try {
                    const payload = (await response.json());
                    message = payload.detail || message;
                }
                catch {
                    // Ignore parse failures for non-JSON error bodies.
                }
                setError(message);
                return;
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = "workflow_handoffs.csv";
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
            URL.revokeObjectURL(url);
        }
        catch (requestError) {
            setError(String(requestError));
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("main", { className: "handoff-admin-page", children: _jsxs("section", { className: "handoff-admin-shell", children: [_jsxs("header", { className: "handoff-admin-header", children: [_jsx("p", { className: "handoff-admin-eyebrow", children: "XR7 Operator Tools" }), _jsx("h1", { children: "Workflow Handoff Search" }), _jsx("p", { children: "Preview or export two-agent handoffs across artists without hand-building query strings." })] }), _jsxs("section", { className: "handoff-admin-card", children: [_jsxs("div", { className: "handoff-admin-grid handoff-admin-grid--credentials", children: [_jsxs("label", { children: [_jsx("span", { children: "Admin key" }), _jsx("input", { type: "password", value: adminKey, onChange: (event) => setAdminKey(event.target.value), placeholder: "Enter X-Admin-Key" })] }), _jsxs("label", { children: [_jsx("span", { children: "Admin actor" }), _jsx("input", { type: "text", value: adminActor, onChange: (event) => setAdminActor(event.target.value), placeholder: "ops@xr7.test" })] })] }), _jsxs("div", { className: "handoff-admin-grid", children: [_jsxs("label", { children: [_jsx("span", { children: "Artist ID" }), _jsx("input", { type: "text", value: artistId, onChange: (event) => setArtistId(event.target.value), placeholder: "Optional exact artist id" })] }), _jsxs("label", { children: [_jsx("span", { children: "Artist name search" }), _jsx("input", { type: "text", value: query, onChange: (event) => setQuery(event.target.value), placeholder: "Search by artist name" })] }), _jsxs("label", { children: [_jsx("span", { children: "Status" }), _jsx("input", { type: "text", value: status, onChange: (event) => setStatus(event.target.value), placeholder: "active" })] }), _jsxs("label", { children: [_jsx("span", { children: "From agent" }), _jsx("input", { type: "text", value: fromAgent, onChange: (event) => setFromAgent(event.target.value), placeholder: "onboarding_preparation" })] }), _jsxs("label", { children: [_jsx("span", { children: "To agent" }), _jsx("input", { type: "text", value: toAgent, onChange: (event) => setToAgent(event.target.value), placeholder: "recovery_execution" })] }), _jsxs("label", { children: [_jsx("span", { children: "Limit" }), _jsx("input", { type: "number", min: "1", max: "200", value: limit, onChange: (event) => setLimit(event.target.value) })] }), _jsxs("label", { children: [_jsx("span", { children: "Since" }), _jsx("input", { type: "date", value: since, onChange: (event) => setSince(event.target.value) })] }), _jsxs("label", { children: [_jsx("span", { children: "Until" }), _jsx("input", { type: "date", value: until, onChange: (event) => setUntil(event.target.value) })] })] }), _jsxs("div", { className: "handoff-admin-actions", children: [_jsx("button", { type: "button", className: "handoff-admin-button handoff-admin-button--primary", onClick: handlePreview, disabled: loading, children: loading ? "Loading..." : "Preview Results" }), _jsx("button", { type: "button", className: "handoff-admin-button", onClick: handleExportCsv, disabled: loading, children: "Export CSV" })] }), error ? _jsx("p", { className: "handoff-admin-error", children: error }) : null, lastQuery ? _jsxs("p", { className: "handoff-admin-meta", children: ["Last query: /admin/workflow/handoffs?", lastQuery] }) : null] }), _jsxs("section", { className: "handoff-admin-card", children: [_jsxs("div", { className: "handoff-admin-results-head", children: [_jsx("h2", { children: "Preview" }), _jsxs("span", { children: [total, " matching handoffs"] })] }), rows.length ? (_jsx("div", { className: "handoff-admin-table-wrap", children: _jsxs("table", { className: "handoff-admin-table", children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Artist" }), _jsx("th", { children: "Transition" }), _jsx("th", { children: "Status" }), _jsx("th", { children: "Readiness" }), _jsx("th", { children: "Recorded" }), _jsx("th", { children: "Handoff ID" })] }) }), _jsx("tbody", { children: rows.map((row) => (_jsxs("tr", { children: [_jsxs("td", { children: [_jsx("strong", { children: row.artist_name || row.artist_id }), _jsx("div", { children: row.artist_id })] }), _jsxs("td", { children: [row.from_agent, " -> ", row.to_agent] }), _jsx("td", { children: row.status }), _jsxs("td", { children: [row.readiness_score.toFixed(1), " / ", row.readiness_threshold.toFixed(1)] }), _jsx("td", { children: row.created_at ? new Date(row.created_at).toLocaleString() : "n/a" }), _jsx("td", { className: "handoff-admin-mono", children: row.handoff_id })] }, row.id))) })] }) })) : (_jsx("p", { className: "handoff-admin-empty", children: "No handoffs loaded yet. Enter filters and choose Preview Results." }))] })] }) }));
}
export default AdminWorkflowHandoffsPanel;
